# datavolley/core/code.py

import re
from typing import Dict, Optional


def parse_play_code(raw_content: str, code: str) -> Optional[Dict]:
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
    if not code or len(code) < 4:
        return None

    parsed = {
        "code": code,
        "team": None,
        "player_number": None,
        "player_name": None,
        "player_id": None,
        "skill": None,
        "evaluation_code": None,
        "set_code": None,
        "start_zone": None,
        "end_zone": None,
        "end_subzone": None,
        "num_players_numeric": None,
        "skill_subtype": None,
        "attack_code": None,
    }

    # Extract Team using inline team extraction (avoid circular imports)
    teams = _extract_teams_lightweight(raw_content)
    if code.startswith("*"):
        parsed["team"] = teams.get("team_1")
    elif code.startswith("a"):
        parsed["team"] = teams.get("team_2")

    # Extract Player Number (positions 1-2)
    try:
        player_number = code[1:3]
        if player_number.isdigit():
            parsed["player_number"] = int(player_number)
    except (IndexError, ValueError):
        pass

    # Extract Player details using inline player extraction (avoid circular imports)
    players = _extract_players_lightweight(raw_content)
    if code.startswith("*") and parsed["player_number"]:
        player = next(
            (
                p
                for p in players["home"]
                if int(p["player_number"]) == parsed["player_number"]
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
                if int(p["player_number"]) == parsed["player_number"]
            ),
            None,
        )
        if player:
            parsed["player_name"] = player["full_name"]
            parsed["player_id"] = player["player_id"]

    # Extract Skill (position 3)
    if len(code) > 3:
        skill_mapping = {
            "S": "Serve",
            "R": "Reception",
            "E": "Set",
            "A": "Attack",
            "D": "Dig",
            "B": "Block",
            "F": "Freeball",
            "p": "Point",
        }
        skill_code = code[3]
        parsed["skill"] = skill_mapping.get(skill_code, f"Unknown skill: {skill_code}")

    # Extract Evaluation (position 4)
    if len(code) > 4:
        parsed["evaluation_code"] = code[5]

    # Extract Attack combination
    if len(code) > 6 and code[3] == "A" and code[6:8] != "~~":
        parsed["attack_code"] = code[6:8]

    # Extract Set codes
    if len(code) > 6 and code[3] == "E" and code[6:8] != "~~":
        parsed["set_code"] = code[6:8]

    # Extract Blockers
    if len(code) > 13 and parsed["skill"] == "Attack":
        try:
            parsed["num_players_numeric"] = int(code[13])
        except (ValueError, IndexError):
            pass

    # Extract Zones (positions 9-11)
    if len(code) > 9:
        parsed["start_zone"] = code[9] if code[9] != "~" else None
    if len(code) > 10:
        parsed["end_zone"] = code[10] if code[10] != "~" else None
    if len(code) > 11:
        parsed["end_subzone"] = code[11] if code[11] != "~" else None

    # Extract Skill subtype
    if len(code) > 4 and parsed["skill"]:
        skill_abbrev = code[3]
        parsed["skill_subtype"] = extract_skill_subtype(code, skill_abbrev, 4)

    return parsed


def _extract_teams_lightweight(raw_content: str) -> Dict:
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


def _extract_players_lightweight(raw_content: str) -> Dict:
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


def _parse_player_lines_lightweight(section_content: str):
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

                full_name = " ".join(filter(None, [first_name, last_name])) or None

                player = {
                    "player_number": player_number,
                    "player_id": player_id,
                    "full_name": full_name,
                }
                players.append(player)
            except (ValueError, IndexError):
                continue

    return players


def extract_skill_subtype(code: str, skill_abb: str, range_pos: int) -> Optional[str]:
    """
    Extract skill subtype from the code.

    Args:
        code: The play code
        skill_abb: Single character skill abbreviation
        range_pos: Position in code to check for subtype

    Returns:
        Skill subtype description or None
    """
    reception_subtypes = {
        "R": "Right",
        "L": "Left",
        "M": "Midline",
        "W": "Low",
        "O": "Overhead",
    }

    attack_block_subtypes = {
        "0": "No block",
        "1": "1 player block",
        "2": "2 player block",
        "3": "3 player block",
        "4": "Hole block",
    }

    attack_subtypes = {"H": "Hard", "P": "Soft spike", "T": "Tip"}

    set_subtypes = {
        "1": "1 hand set",
        "2": "2 hands set",
        "3": "Bump set",
        "4": "Other set",
        "5": "Underhand set",
    }

    # Create a mapping of skill abbreviations to their subtypes
    skill_mappings = {
        "R": reception_subtypes,
        "A": attack_subtypes,
        "B": attack_block_subtypes,
        "E": set_subtypes,
    }

    # Extract the character at the specified position
    if len(code) > range_pos:
        subtype_code = code[range_pos]

        # Get the appropriate mapping and return the subtype
        if skill_abb in skill_mappings:
            mapping = skill_mappings[skill_abb]
            return mapping.get(subtype_code, f"Unknown subtype: {subtype_code}")

    return None


def get_skill_description(skill_code: str) -> Optional[str]:
    """
    Get human-readable description for skill codes.

    Args:
        skill_code: Single character skill code (S, R, E, A, D, B, F, p)

    Returns:
        Human-readable skill description or None if unknown
    """
    skill_descriptions = {
        "S": "Serve",
        "R": "Reception",
        "E": "Set",
        "A": "Attack",
        "D": "Dig",
        "B": "Block",
        "F": "Freeball",
        "p": "Point",
    }

    return skill_descriptions.get(skill_code)
