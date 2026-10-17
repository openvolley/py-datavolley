from __future__ import annotations

import re

from datavolley.types.code import ParsedPlayCode

_EVALUATIONS = {
    "Serve": {
        "=": "Error",
        "/": "Positive, no attack",
        "-": "Negative, opponent free attack",
        "!": "OK, no first tempo possible",
        "+": "Positive, opponent some attack",
        "#": "Ace",
    },
    "Reception": {
        "=": "Error",
        "/": "Poor, no attack",
        "-": "Negative, limited attack",
        "!": "OK, no first tempo possible",
        "+": "Positive, attack",
        "#": "Perfect pass",
    },
    "Attack": {
        "=": "Error",
        "/": "Blocked",
        "-": "Poor, easily dug",
        "!": "Blocked for reattack",
        "+": "Positive, good attack",
        "#": "Winning attack",
    },
    "Block": {
        "=": "Error",
        "/": "Invasion",
        "-": "Poor, opposition to replay",
        "!": "Poor, opposition to replay",
        "+": "Positive, block touch",
        "#": "Winning block",
    },
    "Dig": {
        "=": "Error",
        "/": "Ball directly back over net",
        "-": "No structured attack possible",
        "!": "OK, no first tempo possible",
        "+": "Good dig",
        "#": "Perfect dig",
    },
    "Set": {
        "=": "Error",
        "/": "Poor",
        "-": "Poor",
        "!": "OK",
        "+": "Positive",
        "#": "Perfect",
    },
    "Freeball": {
        "=": "Error",
        "/": "Poor",
        "-": "OK, only high set possible",
        "!": "OK, no first tempo possible",
        "+": "Good",
        "#": "Perfect",
    },
}

_BLOCK_PLAYERS = {
    0: "No block",
    1: "1 player block",
    2: "2 player block",
    3: "3 player block",
    4: "Hole block",
}

_RECEPTION_PLAYERS = {
    1: "Two players receiving, the player on left receives",
    2: "Two players receiving, the player on right receives",
    3: "Three players receiving, the player on left receives",
    4: "Three players receiving, the player in center receives",
    5: "Three players receiving, the player on right receives",
    6: "Four players receiving, the player on left receives",
    7: "Four players receiving, the player on center-left receives",
    8: "Four players receiving, the player on center-right receives",
    9: "Four players receiving, the player on right receives",
}

_SPECIAL_CODES = {
    "Block": {
        "S": "Ball out - side",
        "O": "Ball out - long",
        "F": "Ball on floor",
        "X": "Between hands",
        "N": "Hands - net",
        "I": "Net contact",
        "A": "Antenna",
        "P": "No jump",
        "T": "Position error",
        "Z": "Referee call",
    },
    "Reception": {
        "U": "Unplayable",
        "X": "Body error",
        "P": "Position error",
        "Z": "Referee call",
        "E": "Lack of effort",
    },
    "Freeball": {
        "U": "Unplayable",
        "X": "Body error",
        "P": "Position error",
        "Z": "Referee call",
    },
    "Dig": {
        "U": "Unplayable",
        "X": "Body error",
        "P": "Position error",
        "Z": "Referee call",
        "F": "Ball on floor",
        "O": "Ball out",
        "E": "Lack of effort",
    },
    "Set": {"U": "Cannot be hit", "I": "Net touch", "Z": "Referee call"},
}


def _uses_cones(raw_content: str) -> bool:
    match = re.search(r"\[3MATCH\]\s+([^\r\n]+)", raw_content)
    if not match:
        return False
    parts = match.group(1).split(";")
    return any(parts[index : index + 1] == ["C"] for index in (10, 11))


def _decode_num_players(skill: str, value: int | None) -> str | None:
    if value is None:
        return None
    if skill in {"Attack", "Block"}:
        return _BLOCK_PLAYERS.get(value, f"Unexpected {value}")
    if skill == "Reception":
        return _RECEPTION_PLAYERS.get(value, f"Unexpected {value}")
    return f"Unexpected {value}"


def _decode_special_code(skill: str, evaluation: str, value: str | None) -> str | None:
    if not value or value == "~":
        return None

    mapping = _SPECIAL_CODES.get(skill)
    if skill == "Attack":
        if evaluation == "=":
            mapping = {
                "S": "Attack out - side",
                "O": "Attack out - long",
                "N": "Attack in net",
                "I": "Net contact",
                "Z": "Referee call",
                "A": "Antenna",
            }
        elif evaluation == "#":
            mapping = {
                "S": "Block out - side",
                "O": "Block out - long",
                "F": "Block on floor",
                "X": "Direct on floor",
                "N": "Let",
            }
        elif evaluation in {"+", "-", "!", "/"}:
            mapping = {"C": "Block control", "N": "Let"}
    elif skill == "Serve":
        mapping = (
            {
                "O": "Ball out - long",
                "L": "Ball out - left",
                "R": "Ball out - right",
                "N": "Ball in net",
                "Z": "Referee call",
            }
            if evaluation == "="
            else {"N": "Let"}
        )

    return mapping.get(value, f"Unexpected {value}") if mapping else None


def parse_play_code(
    raw_content: str, code: str, *, use_cones: bool | None = None
) -> ParsedPlayCode | None:
    """
    Parse a volleyball play code into its components.

    DVW play codes have the format: [*|a][player][skill][evaluation][attack_combo][zone][evaluation_details]

    Examples:
        *19SM+~~~78A~~~00 - Home team player 19, serve (S), positive evaluation (+), middle attack (M)
        a02RM-~~~58AM~~00B - Visiting team player 02, reception (R), negative evaluation (-), middle attack (M)
        *08EH#~~~~8C~~~00 - Home team player 08, attack (E), error (#), high ball (H)

    Args:
        raw_content: Raw DVW file content
        code: The play code string to parse

    Returns:
        Dictionary with parsed code components or None if invalid
    """
    if not code or len(code) < 2:
        return None

    parsed: ParsedPlayCode = {
        "code": code,
        "team": None,
        "player_number": None,
        "player_name": None,
        "player_id": None,
        "skill": None,
        "skill_type": None,
        "evaluation_code": None,
        "evaluation": None,
        "set_code": None,
        "set_type": None,
        "set_description": None,
        "start_zone": None,
        "end_zone": None,
        "end_subzone": None,
        "end_cone": None,
        "num_players_numeric": None,
        "num_players": None,
        "skill_subtype": None,
        "attack_code": None,
        "attack_description": None,
        "special_code": None,
        "custom_code": None,
    }

    # Extract Team using inline team extraction (avoid circular imports)
    teams = _extract_teams_lightweight(raw_content)
    if code.startswith("*"):
        parsed["team"] = teams.get("team_1")
    elif code.startswith("a"):
        parsed["team"] = teams.get("team_2")

    if code[1:2] == "p":
        parsed["skill"] = "Point"
        return parsed

    code_match = re.match(r"^[*a](\d+|\$\$)([SREABDF].*)$", code)
    if not code_match:
        return None

    player_token, payload = code_match.groups()
    if player_token.isdigit():
        parsed["player_number"] = int(player_token)

    # Extract Player details using inline player extraction (avoid circular imports)
    players = _extract_players_lightweight(raw_content)
    if code.startswith("*") and parsed["player_number"]:
        player = next(
            (
                p
                for p in players["home"]
                if p["player_number"] is not None
                and int(p["player_number"]) == parsed["player_number"]
            ),
            None,
        )
        if player:
            parsed["player_name"] = player["full_name"]
            parsed["player_id"] = player["player_id"]
    elif code.startswith("a") and parsed["player_number"]:
        player = next(
            (
                p
                for p in players["visiting"]
                if p["player_number"] is not None
                and int(p["player_number"]) == parsed["player_number"]
            ),
            None,
        )
        if player:
            parsed["player_name"] = player["full_name"]
            parsed["player_id"] = player["player_id"]

    skill_mapping = {
        "S": "Serve",
        "R": "Reception",
        "E": "Set",
        "A": "Attack",
        "D": "Dig",
        "B": "Block",
        "F": "Freeball",
    }
    skill_code = payload[0]
    skill = skill_mapping[skill_code]
    parsed["skill"] = skill
    evaluation_code = payload[2:3]
    if evaluation_code and evaluation_code != "~":
        parsed["evaluation_code"] = evaluation_code
        parsed["evaluation"] = _EVALUATIONS[skill].get(
            evaluation_code, f"Unknown {skill.lower()} evaluation"
        )

    combination = payload[3:5]
    if combination and combination != "~~":
        if skill == "Attack":
            parsed["attack_code"] = combination
        elif skill == "Set":
            parsed["set_code"] = combination

    set_type = payload[5:6]
    if skill == "Set" and set_type and set_type != "~":
        parsed["set_type"] = set_type

    parsed["start_zone"] = payload[6:7] if payload[6:7] not in {"", "~"} else None
    direction = payload[7:8]
    if use_cones is None:
        use_cones = _uses_cones(raw_content)
    if skill == "Attack" and use_cones:
        parsed["end_cone"] = int(direction) if direction.isdigit() else None
    else:
        parsed["end_zone"] = direction if direction not in {"", "~"} else None
        parsed["end_subzone"] = payload[8:9] if payload[8:9] not in {"", "~"} else None

    num_players = payload[10:11]
    if num_players.isdigit():
        parsed["num_players_numeric"] = int(num_players)
    parsed["num_players"] = _decode_num_players(skill, parsed["num_players_numeric"])
    parsed["special_code"] = _decode_special_code(
        skill, evaluation_code, payload[11:12]
    )
    custom_code = payload[12:]
    parsed["custom_code"] = custom_code or None

    # Extract skill_type (position 4) - full description like "High ball attack"
    if parsed["skill"] and len(code) > 4:
        parsed["skill_type"] = extract_skill_type(code, parsed["skill"])

    # Extract Skill subtype
    if parsed["skill"]:
        parsed["skill_subtype"] = extract_skill_subtype(code, parsed["skill"])

    return parsed


def extract_skill_type(code: str, skill: str) -> str | None:
    """
    Extract skill type description from position 4 of the code.

    This returns descriptions like "High ball attack", "Jump-float serve", etc.

    Args:
        code: The play code
        skill: The skill name (Serve, Reception, Attack, etc.)

    Returns:
        Skill type description or None
    """
    # Point and Freeball don't have type codes
    if skill in ["Point", "Freeball", ""]:
        return None

    if len(code) <= 4:
        return None

    type_code = code[4]

    if skill == "Serve":
        serve_type_map = {
            "H": "Float serve",
            "M": "Jump-float serve",
            "Q": "Jump serve",
            "T": "Topspin serve",
            "O": "Other serve",
            "N": "Hybrid serve",
        }
        return serve_type_map.get(type_code)

    elif skill == "Reception":
        reception_type_map = {
            "H": "Float serve reception",
            "M": "Jump-float serve reception",
            "Q": "Jump serve reception",
            "T": "Topspin serve reception",
            "O": "Other serve reception",
            "N": "Hybrid serve reception",
        }
        return reception_type_map.get(type_code)

    elif skill in ["Attack", "Block", "Dig", "Set"]:
        attack_type_map = {
            "H": f"High ball {skill.lower()}",
            "M": f"Half ball {skill.lower()}",
            "Q": f"Quick ball {skill.lower()}",
            "T": f"Head ball {skill.lower()}",
            "U": f"Super ball {skill.lower()}",
            "F": f"Fast ball {skill.lower()}",
            "N": f"Slide ball {skill.lower()}",
            "O": f"Other {skill.lower()}",
        }
        return attack_type_map.get(type_code)

    return None


def extract_skill_subtype(code: str, skill: str) -> str | None:
    """
    Extract skill subtype from the code based on skill type.

    Args:
        code: The play code
        skill: The skill name (Serve, Reception, Attack, etc.)

    Returns:
        Skill subtype description or None
    """

    # Serve subtypes (position 4)
    serve_subtype_map = {
        "Q": "Jump Spin",  # Updated to match your requirement
        "M": "Jump Float",
        "T": "Standing Float",
        "H": "Float",  # Updated to match your requirement
        "O": "Serve Other",
        "N": "Hybrid",
    }

    # Attack subtypes (position 12)
    attack_subtypes = {
        "H": "Hard",
        "P": "Soft spike",
        "T": "Tip",
        "O": "Other attack",
    }

    # Set subtypes (position 4)
    set_subtypes = {
        "1": "1 hand set",
        "2": "2 hands set",
        "3": "Bump set",
        "4": "Other set",
        "5": "Underhand set",
    }

    # Block subtypes (position 4)
    block_subtypes = {
        "0": "No block",
        "1": "1 player block",
        "2": "2 player block",
        "3": "3 player block",
        "4": "Hole block",
    }

    if skill == "Serve" and len(code) > 4:
        subtype_code = code[4]
        return serve_subtype_map.get(subtype_code, None)

    elif skill == "Reception" and len(code) > 4:
        # Use the same serve subtype map for reception
        subtype_code = code[4]
        return serve_subtype_map.get(subtype_code, None)

    elif skill == "Attack" and len(code) > 12:
        # Attack subtype is at position 12 (index 12:13)
        # Example: 'a15AN-CF~23DT2~-5F' -> 'T' at position 12
        subtype_code = code[12]
        if subtype_code != "~":
            return attack_subtypes.get(subtype_code, None)
        return None

    elif skill == "Set" and len(code) > 4:
        subtype_code = code[4]
        return set_subtypes.get(subtype_code, None)

    elif skill == "Block" and len(code) > 4:
        subtype_code = code[4]
        return block_subtypes.get(subtype_code, None)

    elif skill == "Dig" and len(code) > 4:
        # Dig uses same subtypes as serve/reception
        subtype_code = code[4]
        return serve_subtype_map.get(subtype_code, None)

    return None


def _extract_teams_lightweight(raw_content: str) -> dict[str, str | None]:
    """
    Lightweight team extraction to avoid circular imports.
    """
    teams_pattern = r"\[3TEAMS\](.*?)(?=\[3|\n\n|$)"
    match = re.search(teams_pattern, raw_content, re.DOTALL)

    if not match:
        return {}

    teams_section = match.group(1).strip()
    lines = [line.strip() for line in teams_section.split("\n") if line.strip()]

    teams_data = {}
    for i, line in enumerate(lines):
        if line:
            parts = line.split(";")
            if len(parts) >= 2:
                if i == 0:
                    teams_data["team_1"] = parts[1] if parts[1] else None
                elif i == 1:
                    teams_data["team_2"] = parts[1] if parts[1] else None

    return teams_data


def _extract_players_lightweight(
    raw_content: str,
) -> dict[str, list[dict[str, str | None]]]:
    """
    Lightweight player extraction to avoid circular imports.
    """
    players = {"home": [], "visiting": []}

    # Extract home team players
    home_pattern = r"\[3PLAYERS-H\](.*?)(?=\[3PLAYERS-V\]|\[3|\n\n|$)"
    home_match = re.search(home_pattern, raw_content, re.DOTALL)

    if home_match:
        home_section = home_match.group(1).strip()
        players["home"] = _parse_player_lines_lightweight(home_section)

    # Extract visiting team players
    visiting_pattern = r"\[3PLAYERS-V\](.*?)(?=\[3|\n\n|$)"
    visiting_match = re.search(visiting_pattern, raw_content, re.DOTALL)

    if visiting_match:
        visiting_section = visiting_match.group(1).strip()
        players["visiting"] = _parse_player_lines_lightweight(visiting_section)

    return players


def _parse_player_lines_lightweight(
    section_content: str,
) -> list[dict[str, str | None]]:
    """
    Lightweight player line parsing.
    """
    players = []
    lines = [line.strip() for line in section_content.split("\n") if line.strip()]

    for line in lines:
        parts = line.split(";")
        if len(parts) >= 10:
            try:
                player_number = parts[1] if len(parts) > 1 and parts[1] else "0"
                last_name = parts[9] if len(parts) > 9 and parts[9] else None
                first_name = parts[10] if len(parts) > 10 and parts[10] else None
                player_id = (
                    parts[8]
                    if len(parts) > 8 and parts[8]
                    else f"player_{player_number}"
                )

                full_name = (
                    " ".join(list(filter(None, [first_name, last_name]))) or None
                )

                player = {
                    "player_number": player_number,
                    "player_id": player_id,
                    "full_name": full_name,
                }
                players.append(player)
            except (ValueError, IndexError):
                continue

    return players
