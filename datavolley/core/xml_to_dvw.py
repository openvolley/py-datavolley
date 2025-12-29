# datavolley/core/xml_to_dvw.py

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, TypedDict

# ============================================================================
# CONSTANTS / MAPPINGS
# ============================================================================

# Rotation number to setter position mapping
# P1 = Rotation 1, P6 = Rotation 2, P5 = Rotation 3, etc.
ROTATION_TO_SETTER_POSITION = {
    1: 1,  # Rotation 1 -> Setter in P1
    2: 6,  # Rotation 2 -> Setter in P6
    3: 5,  # Rotation 3 -> Setter in P5
    4: 4,  # Rotation 4 -> Setter in P4
    5: 3,  # Rotation 5 -> Setter in P3
    6: 2,  # Rotation 6 -> Setter in P2
}
# Grade to DVW evaluation symbol mapping
GRADE_TO_EVAL = {
    "Perfect": "#",
    "Positive": "+",
    "Average": "!",
    "Poor": "-",
    "Incomplete": "/",
    "Fail": "=",
}

# Serve type to DVW code mapping
SERVE_TYPE_MAP = {
    "Jump Spin": "Q",
    "Jump Float": "M",
    "Standing Float": "H",
    "Standing Float Far": "T",
    "Float": "H",
    "Hybrid": "N",
}

# XML skill name to DVW skill code mapping
SKILL_CODE_MAP = {
    "Serve": "S",
    "Receive": "R",
    "Set": "E",
    "Attack": "A",
    "Dig": "D",
    "Block": "B",
    "Freeball": "F",
    "Cover": "D",
    "Save": "D",
    "Downball": "F",
    "Ball Over": "F",
    "General Error": "~",
}

# Middle Route to DVW code mapping (fallback when no Attack Combination)
MIDDLE_ROUTE_MAP = {
    "Front Quick": "X1",
    "Back Quick": "X2",
    "Front Quick Far": "X7",
    "Slide Near": "CF",
    "Slide Far": "CD",
    "No Middle": "~~",
}

# Attack style to DVW code mapping
ATTACK_STYLE_MAP = {
    "Hit": "H",
    "Tip": "T",
    "Roll": "P",
}

# Attack location to zone mapping (fallback)
ATTACK_LOCATION_TO_ZONE = {
    "Left Side": "4",
    "Right Side": "2",
    "Middle": "3",
    "Pipe": "8",
    "Right Side Back": "9",
}

# Default attack combinations for [3ATTACKCOMBINATION] section
DEFAULT_ATTACK_COMBOS = [
    "V5;4;R;H;Hut;;255;4912;F;;",
    "V6;2;L;H;Red;;255;4988;B;;",
    "V8;9;C;H;High D;;255;4186;B;1;",
    "VP;8;C;H;Pipe;;8388736;4150;P;1;",
    "V0;7;C;H;High A;;8388736;4114;F;1;",
    "VB;8;C;H;High C;;8388736;4163;P;1;",
    "VR;8;C;H;High B;;8388736;4137;P;1;",
    "XO;2;L;Q;5 by the opposite;;32768;4976;B;;",
    "XQ;2;L;Q;5 by O with MB back;;32768;4976;B;;",
    "XS;2;L;N;Slide by the opposite;;32768;4976;B;;",
    "X9;4;R;M;OH hits a 10;;8388608;4924;F;;",
    "XT;3;R;M;OH hits in middle;;8388608;4950;F;;",
    "X3;3;L;M;O hits in middle;;8388608;4950;B;;",
    "X4;2;L;M;O hits a 2nd step 4;;8388608;4976;B;;",
    "XP;8;C;U;Bic;;16711935;4150;P;1;",
    "X0;7;C;U;A (fast ball area 5);;16711935;4114;F;1;",
    "XB;8;C;U;C Quick Ball;;16711935;4163;P;1;",
    "XR;8;C;U;B Quick Ball;;16711935;4138;P;1;",
    "X5;4;R;T;Go;;16711680;4912;F;;",
    "X6;2;L;T;X;;16711680;4988;B;;",
    "X8;9;C;T;D;;16711680;4186;B;1;",
    "X1;3;R;Q;Quick in front (4);;65280;4956;C;;",
    "X7;4;R;Q;2;;65280;4932;C;;",
    "X2;2;L;Q;Quick ball back(5);;65280;4868;C;;",
    "XM;3;C;Q;Quick in Center;;65280;4949;C;;",
    "XG;3;R;Q;7-1 Gun;;65280;4946;C;;",
    "XC;3;R;Q;4- hitter jumps away;;65280;4947;C;;",
    "XD;3;R;Q;2- hitter jumps away;;65280;4941;C;;",
    "XL;2;C;Q;4-setter in area 2;;65280;4963;C;;",
    "CB;2;L;N;Slide near S;;32768;4976;C;;",
    "CF;2;L;N;Slide moved from S;;32768;4970;C;;",
    "CS;2;L;N;Slide far from S;;32768;4986;C;;",
    "PP;3;L;O;Setter Dump;;32896;4964;S;;",
]

# Default setter calls for [3SETTERCALL] section
DEFAULT_SETTER_CALLS = [
    "K1;;Quick ahead;;16711680;3949;4549;4949;;12632256;",
    "KM;;Push;;16711680;3949;3949;4949;6226,5026,5037,6237,;12632256;",
    "K2;;Quick behind;;16711680;3864;4278;4974;;255;",
    "K7;;Gap;;16711680;3923;4426;4930;;255;",
    "KS;;Slide;;16711680;3950;3991;4883;;255;",
]


# ============================================================================
# XML PARSING FUNCTIONS
# ============================================================================


class InstanceData(TypedDict):
    id: str
    start: float
    end: float
    code: str
    labels: Dict[str, str]


class PlayData(TypedDict):
    type: str
    set_number: int
    video_time: float
    home_setter_pos: int
    visit_setter_pos: int
    home_lineup: List[str]
    visit_lineup: List[str]


def parse_xml_file(xml_file: str) -> ET.Element:
    """
    Parse XML file and return root element.

    Args:
        xml_file: Path to XML file

    Returns:
        Root element of parsed XML tree
    """
    tree = ET.parse(xml_file)
    return tree.getroot()


def extract_instances(root: ET.Element) -> List[InstanceData]:
    """
    Extract all instances with their labels as dictionaries.

    Args:
        root: Root element of XML tree

    Returns:
        List of instance dictionaries with 'code', 'start', 'end', 'labels'
    """
    instances = []

    # Find ALL_INSTANCES element
    all_instances = root.find("ALL_INSTANCES")
    if all_instances is None:
        return instances

    for instance in all_instances.findall("instance"):
        labels: Dict[str, str] = {}

        # Extract all labels
        for label in instance.findall("label"):
            group = label.findtext("group", "")
            text = label.findtext("text", "")
            if group and text:
                labels[group] = text

        inst_data: InstanceData = {
            "id": instance.findtext("id", ""),
            "start": float(instance.findtext("start", "0")),
            "end": float(instance.findtext("end", "0")),
            "code": instance.findtext("code", ""),
            "labels": labels,
        }

        instances.append(inst_data)

    return instances


# ============================================================================
# DATA EXTRACTION FUNCTIONS
# ============================================================================


def get_team_prefixes(instances: List[InstanceData]) -> Tuple[str, str]:
    """
    Detect team prefixes from instance codes (e.g., 'USA1', 'USA2' or 'UNL', 'TAMU').

    Args:
        instances: List of instance dictionaries

    Returns:
        Tuple of (home_prefix, away_prefix)
    """
    home_prefix = None
    away_prefix = None

    for inst in instances:
        code = inst.get("code", "")
        labels = inst.get("labels", {})

        # Look for skill instances that have Team label
        if " Serve" in code or " Attack" in code or " Receive" in code:
            parts = code.split(" ")
            prefix = parts[0]
            team = labels.get("Team", "")

            if team == "Home" and home_prefix is None:
                home_prefix = prefix
            elif team == "Away" and away_prefix is None:
                away_prefix = prefix

        if home_prefix and away_prefix:
            break

    # Fallback defaults
    if home_prefix is None:
        home_prefix = "USA1"
    if away_prefix is None:
        away_prefix = "USA2"

    return (home_prefix, away_prefix)


def extract_match_info(
    instances: List[InstanceData], xml_file: str, team_prefixes: Tuple[str, str]
) -> Dict[str, str]:
    """
    Extract match metadata from instances and filename.

    Args:
        instances: List of instance dictionaries
        xml_file: Path to XML file (for date extraction from filename)
        team_prefixes: Tuple of (home_prefix, away_prefix)

    Returns:
        Dictionary with match info (date, year, home_team, away_team, match_id)
    """
    home_prefix, away_prefix = team_prefixes
    match_info = {
        "date": datetime.now().strftime("%m/%d/%Y"),
        "year": str(datetime.now().year),
        "home_team": home_prefix,
        "home_prefix": team_prefixes[0],
        "away_team": away_prefix,
        "away_prefix": team_prefixes[1],
        "match_id": "",
    }

    # Try to extract date from filename (format: YYYY-MM-DD or similar)
    filename = os.path.basename(xml_file)
    date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", filename)
    if date_match:
        year, month, day = date_match.groups()
        match_info["date"] = f"{month}/{day}/{year}"
        match_info["year"] = year

    # Try to extract match ID from filename (e.g., "717292" in "&2025-12-14 717292 UNL-TAMU(VM).xml")
    match_id_match = re.search(r"\s(\d{6,})\s", filename)
    if match_id_match:
        match_info["match_id"] = match_id_match.group(1)

    # Try to get team names from instances
    for inst in instances:
        labels = inst.get("labels", {})
        team_name = labels.get("Team Name", "")
        team = labels.get("Team", "")

        if team_name and team_name != "All":
            if team == "Home":
                match_info["home_team"] = team_name
            elif team == "Away":
                match_info["away_team"] = team_name

    return match_info


def extract_players(
    instances: List[InstanceData], team_prefixes: Tuple[str, str]
) -> Dict[str, List[Dict[str, str]]]:
    """
    Extract unique players for each team from instances.

    Args:
        instances: List of instance dictionaries
        team_prefixes: Tuple of (home_prefix, away_prefix)

    Returns:
        Dictionary with 'home' and 'visiting' player lists
    """
    home_prefix, away_prefix = team_prefixes
    home_players = {}  # jersey -> player dict
    away_players = {}

    home_jersey_key = f"{home_prefix} Player Jersey"
    home_name_key = f"{home_prefix} Player Name"
    away_jersey_key = f"{away_prefix} Player Jersey"
    away_name_key = f"{away_prefix} Player Name"

    for inst in instances:
        labels = inst.get("labels", {})

        # Check for home player
        if home_jersey_key in labels and home_name_key in labels:
            jersey = labels[home_jersey_key]
            name = labels[home_name_key]
            if jersey and jersey not in home_players:
                # Parse name (format: "Last, First" or "Last")
                name_parts = name.split(", ")
                last = name_parts[0] if name_parts else name
                first = name_parts[1] if len(name_parts) > 1 else ""
                home_players[jersey] = {
                    "jersey": jersey,
                    "name": name,
                    "last": last,
                    "first": first,
                }

        # Check for away player
        if away_jersey_key in labels and away_name_key in labels:
            jersey = labels[away_jersey_key]
            name = labels[away_name_key]
            if jersey and jersey not in away_players:
                name_parts = name.split(", ")
                last = name_parts[0] if name_parts else name
                first = name_parts[1] if len(name_parts) > 1 else ""
                away_players[jersey] = {
                    "jersey": jersey,
                    "name": name,
                    "last": last,
                    "first": first,
                }

    return {
        "home": list(home_players.values()),
        "visiting": list(away_players.values()),
    }


def get_skill_from_code(code: str) -> Optional[str]:
    """
    Extract skill name from instance code.

    Args:
        code: Instance code (e.g., 'USA1 Serve', 'TAMU Attack')

    Returns:
        Skill name or None if not a skill instance
    """
    skills = [
        "Serve",
        "Receive",
        "Set",
        "Attack",
        "Dig",
        "Block",
        "Freeball",
        "Cover",
        "Save",
        "Downball",
        "Ball Over",
        "General Error",
    ]

    for skill in skills:
        if f" {skill}" in code:
            return skill

    return None


def parse_game_score(score_str: str) -> Tuple[int, int]:
    """
    Parse game score string to tuple.

    Args:
        score_str: Score string in format "X-YZ" where X is home score position

    Returns:
        Tuple of (home_score, away_score)
    """
    if not score_str:
        return (0, 0)

    # Format is "0-10" meaning position in score, need to track actual score
    # Actually the format appears to be a tracking code, not actual score
    # We'll need to track score from Rally Won labels
    try:
        parts = score_str.split("-")
        if len(parts) == 2:
            # The format seems to be home-away but as a code
            return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        pass

    return (0, 0)


# ============================================================================
# ZONE FORMATTING
# ============================================================================


# ============================================================================
# DVW CODE BUILDING
# ============================================================================


def build_scout_code(play: Dict[str, Any]) -> str:
    """
    Build the simplified DVW scout code from play data.

    Simplified format keeps only: team, jersey, skill, skill_type, evaluation
    Removes: combos (use ~~), setter calls (use ~~), zones, score diff, row/touch indicators

    Args:
        play: Play dictionary with skill info

    Returns:
        DVW scout code string (simplified)
    """
    team_prefix = "*" if play.get("team") == "home" else "a"
    jersey = play.get("jersey", "~~")

    # Ensure jersey is 2 characters
    if len(jersey) == 1:
        jersey = "0" + jersey
    elif len(jersey) == 0:
        jersey = "~~"

    skill = play.get("skill_code", "~")
    skill_type = play.get("skill_type", "~")
    evaluation = play.get("evaluation", "~")

    # Simplified format: [team][jersey][skill][type][eval] followed by tildes for padding
    # All skill types now use the same simplified format
    # Remove zones, combos, setter calls, score diff, row/touch indicators

    if skill == "S":  # Serve
        # Simplified: a16SM-~~~~~~~~~~~ (no zones, no score diff)
        code = f"{team_prefix}{jersey}S{skill_type}{evaluation}~~~~~~~~~~~"

    elif skill == "R":  # Receive
        # Simplified: *11RM+~~~~~~~~~~~ (no zones, no touched ball indicator)
        code = f"{team_prefix}{jersey}R{skill_type}{evaluation}~~~~~~~~~~~"

    elif skill == "E":  # Set
        # Simplified: *02ET#~~~~~~~~~~~ (no setter call, no zones)
        code = f"{team_prefix}{jersey}E{skill_type}{evaluation}~~~~~~~~~~~"

    elif skill == "A":  # Attack
        # Simplified: *09AT#~~~~~~~~~~~ (no combo, no zones, no row indicator)
        code = f"{team_prefix}{jersey}A{skill_type}{evaluation}~~~~~~~~~~~"

    elif skill == "D":  # Dig
        # Simplified: a12DT=~~~~~~~~~~~ (no zones, no touched ball indicator)
        code = f"{team_prefix}{jersey}D{skill_type}{evaluation}~~~~~~~~~~~"

    elif skill == "B":  # Block
        # Simplified: a01BT=~~~~~~~~~~~ (no zones)
        code = f"{team_prefix}{jersey}B{skill_type}{evaluation}~~~~~~~~~~~"

    elif skill == "F":  # Freeball
        # Simplified: a12FH+~~~~~~~~~~~ (no zones, no touched ball indicator)
        code = f"{team_prefix}{jersey}F{skill_type}{evaluation}~~~~~~~~~~~"

    else:
        # Generic format for unknown skills
        code = f"{team_prefix}{jersey}{skill}{skill_type}{evaluation}~~~~~~~~~~~"

    return code


def build_full_line(code: str, play: Dict[str, Any]) -> str:
    """
    Build complete DVW scout line with all fields (simplified format).

    Simplified format removes coordinates (empty fields) and adds trailing semicolon.

    Args:
        code: DVW scout code
        play: Play dictionary with metadata

    Returns:
        Full DVW scout line with semicolon-separated fields
    """
    # Get metadata
    set_num = str(play.get("set_number", 1))
    home_setter_pos = str(play.get("home_setter_pos", 1))
    visit_setter_pos = str(play.get("visit_setter_pos", 1))
    video_time = str(int(play.get("video_time", 0)))

    # Get lineups (use actual jersey numbers, no zero-padding)
    home_lineup = play.get("home_lineup", [])
    visit_lineup = play.get("visit_lineup", [])

    # Build the line with simplified format (no coordinates)
    # Format: code;;;;;;;;set_num;home_pos;visit_pos;set_num;video_time;;lineup...;
    parts = [
        code,
        "",  # 1
        "",  # 2
        "",  # 3
        "",  # 4 (coordinate fields removed - just empty)
        "",  # 5
        "",  # 6
        "",  # 7
        set_num,
        home_setter_pos,
        visit_setter_pos,
        set_num,
        video_time,
        "",  # empty before lineup
    ]

    # Add lineup positions (no zero-padding)
    for pos in home_lineup:
        parts.append(str(int(pos)) if pos and pos != "~" else "")
    for pos in visit_lineup:
        parts.append(str(int(pos)) if pos and pos != "~" else "")

    # Add trailing semicolon
    parts.append("")

    return ";".join(parts)


def build_set_end_line(play: Dict[str, Any]) -> str:
    """
    Build set end marker line.

    Args:
        play: Play dictionary with set info

    Returns:
        DVW set end marker line (e.g., '**1set;;;;...')
    """
    set_num = play.get("set_number", 1)
    next_set = set_num + 1
    home_setter_pos = str(play.get("home_setter_pos", 1))
    visit_setter_pos = str(play.get("visit_setter_pos", 1))
    video_time = str(int(play.get("video_time", 0)))

    home_lineup = play.get("home_lineup", [])
    visit_lineup = play.get("visit_lineup", [])

    parts = [
        f"**{set_num}set",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        str(next_set),
        home_setter_pos,
        visit_setter_pos,
        str(set_num),
        video_time,
        "",
    ]

    for pos in home_lineup:
        parts.append(str(int(pos)) if pos and pos != "~" else "")
    for pos in visit_lineup:
        parts.append(str(int(pos)) if pos and pos != "~" else "")

    return ";".join(parts)


def build_rotation_lines(
    play: Dict[str, Any], players: Dict[str, List[Dict[str, str]]]
) -> List[str]:
    """
    Build rotation indicator lines.

    Args:
        play: Play dictionary with rotation info
        players: Dictionary with 'home' and 'visiting' player lists

    Returns:
        List of 4 rotation lines (*P, *z, aP, az)
    """
    home_setter_pos = play.get("home_setter_pos", 1)
    visit_setter_pos = play.get("visit_setter_pos", 1)
    set_num = str(play.get("set_number", 1))
    video_time = str(int(play.get("video_time", 0)))

    home_lineup = play.get("home_lineup", [])
    visit_lineup = play.get("visit_lineup", [])

    # Get setter jersey from lineup based on position
    # Setter position tells us which court position (1-6) the setter is in
    # The lineup is ordered by court position, so setter_pos index gives setter's jersey
    home_setter_jersey = "~~"
    visit_setter_jersey = "~~"

    # Setter is identified by position - need to find who's in that position
    if home_lineup and len(home_lineup) >= home_setter_pos:
        jersey = (
            home_lineup[home_setter_pos - 1]
            if home_setter_pos <= len(home_lineup)
            else ""
        )
        if jersey and jersey != "~":
            # Use 2 digits, but no leading zero (e.g., "2", not "02")
            home_setter_jersey = str(int(jersey)).zfill(2)

    if visit_lineup and len(visit_lineup) >= visit_setter_pos:
        jersey = (
            visit_lineup[visit_setter_pos - 1]
            if visit_setter_pos <= len(visit_lineup)
            else ""
        )
        if jersey and jersey != "~":
            # Use 2 digits, but no leading zero (e.g., "16", not "16")
            visit_setter_jersey = str(int(jersey)).zfill(2)

    # Build base parts (everything after the code)
    # Real DVW format: ;;;;;;;;set_num;home_pos;visit_pos;set_num;video_time;;lineup...;
    # That's 4 empty fields, then 4 more empty fields = 8 empty semicolons
    def build_base_parts():
        parts = [
            "",  # 1
            "",  # 2
            "",  # 3
            "",  # 4
            "",  # 5
            "",  # 6
            "",  # 7
            "",  # 8
            set_num,
            str(home_setter_pos),
            str(visit_setter_pos),
            set_num,
            video_time,
            "",
        ]
        # Add lineup without leading zeros
        for pos in home_lineup:
            parts.append(str(int(pos)) if pos and pos != "~" else "")
        for pos in visit_lineup:
            parts.append(str(int(pos)) if pos and pos != "~" else "")

        # Add trailing semicolon
        parts.append("")

        return ";".join(parts)

    base = build_base_parts()

    # Check if this is the first rotation of a set (needs >LUp suffix)
    is_first_rotation = play.get("is_first_rotation", False)
    suffix = ">LUp" if is_first_rotation else ""

    # Order: away team first (aP, az), then home team (*P, *z)
    lines = [
        f"aP{visit_setter_jersey}{suffix};{base}",
        f"az{visit_setter_pos}{suffix};{base}",
        f"*P{home_setter_jersey}{suffix};{base}",
        f"*z{home_setter_pos}{suffix};{base}",
    ]

    return lines


# ============================================================================
# PLAY PROCESSING
# ============================================================================


def process_instances_to_plays(
    instances: List[InstanceData],
    players: Dict[str, List[Dict[str, str]]],
    team_prefixes: Tuple[str, str],
) -> List[Dict[str, Any]]:
    """
    Convert XML instances to DVW play dictionaries.

    Args:
        instances: List of instance dictionaries
        players: Dictionary with player info
        team_prefixes: Tuple of (home_prefix, away_prefix)

    Returns:
        List of play dictionaries ready for DVW conversion
    """
    home_prefix, away_prefix = team_prefixes
    plays = []

    current_set = 1
    current_home_rot = 1
    current_visit_rot = 1
    home_score = 0  # Per-set score
    away_score = 0  # Per-set score
    last_rally_start = None
    need_rotation_lines = True
    is_first_rotation_of_set = True  # Track first rotation for >LUp suffix

    # Build jersey-based lookups for players
    home_jerseys = [p.get("jersey", "~") for p in players.get("home", [])][:6]
    visit_jerseys = [p.get("jersey", "~") for p in players.get("visiting", [])][:6]

    # Pad to 6 if needed
    while len(home_jerseys) < 6:
        home_jerseys.append("~")
    while len(visit_jerseys) < 6:
        visit_jerseys.append("~")

    for inst in instances:
        code = inst.get("code", "")
        labels = inst.get("labels", {})
        start_time = inst.get("start", 0)

        # Handle Rally instances for score/rotation tracking
        if code == "Rally":
            # Check for set change
            new_set = int(labels.get("Set", str(current_set)))
            if new_set != current_set:
                # Generate set end marker
                plays.append({
                    "type": "set_end",
                    "set_number": current_set,
                    "home_setter_pos": ROTATION_TO_SETTER_POSITION.get(
                        current_home_rot, 1
                    ),
                    "visit_setter_pos": ROTATION_TO_SETTER_POSITION.get(
                        current_visit_rot, 1
                    ),
                    "video_time": start_time,
                    "home_lineup": home_jerseys,
                    "visit_lineup": visit_jerseys,
                })
                current_set = new_set
                # Reset scores for new set
                home_score = 0
                away_score = 0
                need_rotation_lines = True
                is_first_rotation_of_set = True

            # Update rotations
            home_rot_key = f"{home_prefix} Rotation"
            visit_rot_key = f"{away_prefix} Rotation"
            new_home_rot = int(labels.get(home_rot_key, str(current_home_rot)))
            new_visit_rot = int(labels.get(visit_rot_key, str(current_visit_rot)))

            # Check if rotation changed
            if (
                new_home_rot != current_home_rot
                or new_visit_rot != current_visit_rot
                or need_rotation_lines
            ):
                current_home_rot = new_home_rot
                current_visit_rot = new_visit_rot

                # Add rotation indicator
                plays.append({
                    "type": "rotation",
                    "home_rotation": current_home_rot,
                    "visit_rotation": current_visit_rot,
                    "home_setter_pos": ROTATION_TO_SETTER_POSITION.get(
                        current_home_rot, 1
                    ),
                    "visit_setter_pos": ROTATION_TO_SETTER_POSITION.get(
                        current_visit_rot, 1
                    ),
                    "set_number": current_set,
                    "video_time": start_time,
                    "home_lineup": home_jerseys,
                    "visit_lineup": visit_jerseys,
                    "is_first_rotation": is_first_rotation_of_set,
                })
                need_rotation_lines = False
                is_first_rotation_of_set = False  # Only first rotation gets >LUp

            last_rally_start = start_time
            continue

        # Skip non-skill instances (Offense/Defense First Ball, Transition, etc.)
        skill = get_skill_from_code(code)
        if not skill:
            continue

        # Determine team
        if code.startswith(home_prefix):
            team = "home"
            jersey_key = f"{home_prefix} Player Jersey"
            name_key = f"{home_prefix} Player Name"
        elif code.startswith(away_prefix):
            team = "away"
            jersey_key = f"{away_prefix} Player Jersey"
            name_key = f"{away_prefix} Player Name"
        else:
            continue

        # Build play dictionary
        jersey = labels.get(jersey_key, "~~")
        if len(jersey) == 1:
            jersey = "0" + jersey

        # Use score difference from XML labels
        score_diff_str = labels.get("Score Difference", "0")
        try:
            score_diff = int(score_diff_str)
        except ValueError:
            score_diff = 0

        # Adjust sign based on team and score status
        score_status = labels.get("Score Status", "")
        if team == "away":
            # For away team, if they're "Down", the diff should be negative
            if score_status == "Down":
                score_diff = -abs(score_diff)
            elif score_status == "Up":
                score_diff = abs(score_diff)
        else:
            # For home team, "Up" means positive, "Down" means negative
            if score_status == "Down":
                score_diff = -abs(score_diff)
            elif score_status == "Up":
                score_diff = abs(score_diff)

        play = {
            "type": "skill",
            "team": team,
            "jersey": jersey,
            "player_name": labels.get(name_key, ""),
            "skill": skill,
            "skill_code": SKILL_CODE_MAP.get(skill, "~"),
            "video_time": start_time,
            "set_number": current_set,
            "home_setter_pos": ROTATION_TO_SETTER_POSITION.get(current_home_rot, 1),
            "visit_setter_pos": ROTATION_TO_SETTER_POSITION.get(current_visit_rot, 1),
            "home_lineup": home_jerseys,
            "visit_lineup": visit_jerseys,
            "score_diff": score_diff,
            "home_score": home_score,
            "away_score": away_score,
        }

        # Add skill-specific attributes
        if skill == "Serve":
            serve_type = labels.get("Serve Type", "")
            play["skill_type"] = SERVE_TYPE_MAP.get(serve_type, "H")
            play["evaluation"] = GRADE_TO_EVAL.get(labels.get("Serve Grade", ""), "~")
            play["zone"] = labels.get("Zone", "") or labels.get("From Zone", "")
            play["end_zone"] = labels.get("To Zone", "")
            play["custom"] = labels.get("Custom Code", "~")

        elif skill == "Receive":
            serve_type = labels.get("Serve Type", "")
            play["skill_type"] = SERVE_TYPE_MAP.get(serve_type, "H")
            play["evaluation"] = GRADE_TO_EVAL.get(labels.get("Receive Grade", ""), "~")
            play["zone"] = labels.get("Zone", "")
            play["end_zone"] = labels.get("To Zone", "")

        elif skill == "Set":
            attack_type = labels.get("Attack Type", "Out of System")
            play["skill_type"] = "Q" if attack_type == "In System" else "H"
            play["evaluation"] = GRADE_TO_EVAL.get(labels.get("Set Grade", ""), "~")
            play["zone"] = labels.get("Zone", "")

            # Setter call from Middle Route
            middle_route = labels.get("Middle Route", "")
            if middle_route:
                # Try to map middle route to setter call
                route_key = (
                    middle_route.split("-")[0] if "-" in middle_route else middle_route
                )
                if route_key in MIDDLE_ROUTE_MAP:
                    play["setter_call"] = MIDDLE_ROUTE_MAP[route_key]
                elif "Quick" in middle_route:
                    play["setter_call"] = "K1"
                elif "Slide" in middle_route:
                    play["setter_call"] = "KC"
                else:
                    play["setter_call"] = "~~"
            else:
                play["setter_call"] = "~~"

        elif skill == "Attack":
            attack_type = labels.get("Attack Type", "Out of System")
            play["skill_type"] = "Q" if attack_type == "In System" else "H"
            play["evaluation"] = GRADE_TO_EVAL.get(labels.get("Attack Grade", ""), "~")
            play["zone"] = labels.get("Zone", "")
            play["end_zone"] = labels.get("To Zone", "")
            play["attack_style"] = ATTACK_STYLE_MAP.get(
                labels.get("Attack Style", ""), "~"
            )

            # Attack combination
            attack_combo = labels.get("Attack Combination", "")
            if attack_combo:
                combo_prefix = (
                    attack_combo.split("-")[0]
                    if "-" in attack_combo
                    else attack_combo[:2]
                )
                play["attack_combo"] = combo_prefix, "~~"
            else:
                # Fallback to Middle Route
                middle_route = labels.get("Middle Route", "")
                if middle_route:
                    route_key = (
                        middle_route.split("-")[0]
                        if "-" in middle_route
                        else middle_route
                    )
                    play["attack_combo"] = MIDDLE_ROUTE_MAP.get(route_key, "~~")
                else:
                    # Use attack type to determine combo
                    if attack_type == "In System":
                        play["attack_combo"] = "X5"
                    else:
                        play["attack_combo"] = "V5"

        elif skill == "Dig":
            serve_type = labels.get("Serve Type", "")
            play["skill_type"] = SERVE_TYPE_MAP.get(serve_type, "H")
            play["evaluation"] = GRADE_TO_EVAL.get(labels.get("Dig Grade", ""), "~")
            play["zone"] = labels.get("Zone", "")
            play["end_zone"] = labels.get("To Zone", "")

        elif skill == "Block":
            attack_type = labels.get("Attack Type", "Out of System")
            play["skill_type"] = "Q" if attack_type == "In System" else "H"
            play["evaluation"] = GRADE_TO_EVAL.get(labels.get("Block Grade", ""), "~")
            play["zone"] = labels.get("Zone", "")

        elif skill == "Freeball":
            play["skill_type"] = "H"
            play["evaluation"] = GRADE_TO_EVAL.get(
                labels.get("Freeball Grade", ""), "~"
            )
            play["zone"] = labels.get("Zone", "")
            play["end_zone"] = labels.get("To Zone", "")

        elif skill == "Cover":
            play["skill_type"] = "H"
            play["evaluation"] = GRADE_TO_EVAL.get(labels.get("Cover Grade", ""), "~")
            play["zone"] = labels.get("Zone", "")
            play["end_zone"] = labels.get("To Zone", "")

        else:
            play["skill_type"] = "~"
            play["evaluation"] = "~"

        plays.append(play)

        # Check if this play ends with a point (terminal skill with Rally Won)
        rally_won = labels.get("Rally Won", "")
        if rally_won and play["skill_code"] in ["A", "B", "S"]:
            # Determine who scored
            if (team == "home" and rally_won == "Won") or (
                team == "away" and rally_won == "Lost"
            ):
                home_score += 1
                point_prefix = "*"
            elif (team == "away" and rally_won == "Won") or (
                team == "home" and rally_won == "Lost"
            ):
                away_score += 1
                point_prefix = "a"
            else:
                continue

            plays.append({
                "type": "point",
                "point_code": f"{point_prefix}p{home_score:02d}:{away_score:02d}",
                "home_setter_pos": play["home_setter_pos"],
                "visit_setter_pos": play["visit_setter_pos"],
                "set_number": current_set,
                "video_time": start_time,
                "home_lineup": home_jerseys,
                "visit_lineup": visit_jerseys,
            })

    return plays


def calculate_set_results(
    plays: List[Dict[str, Any]],
) -> Tuple[Tuple[int, int], List[Tuple[int, int]]]:
    """
    Calculate sets won and final scores for each set.

    Args:
        plays: List of play dictionaries

    Returns:
        Tuple of (sets_won, set_scores) where:
        - sets_won: (home_sets_won, away_sets_won)
        - set_scores: List of (home_score, away_score) for each set
    """
    set_scores = []
    current_set = 1
    home_score = 0
    away_score = 0

    for play in plays:
        if play.get("type") == "set_end":
            # Save the final score for this set
            set_scores.append((home_score, away_score))
            current_set = play.get("set_number", current_set) + 1
            home_score = 0
            away_score = 0
        elif play.get("type") == "point":
            point_code = play.get("point_code", "")
            match = re.match(r"[*a]p(\d+):(\d+)", point_code)
            if match:
                home_score = int(match.group(1))
                away_score = int(match.group(2))

    # Add the last set if not already added
    if home_score > 0 or away_score > 0:
        set_scores.append((home_score, away_score))

    # Calculate sets won
    home_sets_won = 0
    away_sets_won = 0
    for h, a in set_scores:
        if h > a:
            home_sets_won += 1
        elif a > h:
            away_sets_won += 1

    return ((home_sets_won, away_sets_won), set_scores)


# ============================================================================
# SECTION BUILDERS
# ============================================================================


def build_header_section() -> str:
    """Build [3DATAVOLLEYSCOUT] section."""
    now = datetime.now()
    date_str = now.strftime("%m/%d/%Y %H.%M.%S")

    # Use `: ` (colon-space) as separator to match real DVW format
    return f"""[3DATAVOLLEYSCOUT]
FILEFORMAT: 2.0
GENERATOR-DAY: {date_str}
GENERATOR-IDP: 
GENERATOR-PRG: 
GENERATOR-REL: 
GENERATOR-VER: 
GENERATOR-NAM: openvolley
LASTCHANGE-DAY: {date_str}
LASTCHANGE-IDP: 
LASTCHANGE-PRG: 
LASTCHANGE-REL: 
LASTCHANGE-VER: 
LASTCHANGE-NAM: """


def build_match_section(match_info: Dict[str, str]) -> str:
    """Build [3MATCH] section."""
    date_str = match_info.get("date", "01/01/2025")
    year = match_info.get("year", "2025")
    match_id = match_info.get("match_id", "")
    # Use season format like "2015/2016" or just year
    season = f"{int(year) - 1}/{year}" if year else "2024/2025"

    return f"""[3MATCH]
{date_str};08.00.00;{season};;;;;{match_id};;1;;Z;
;;;;;;;;"""


def build_teams_section(match_info: Dict[str, str], sets_won: Tuple[int, int]) -> str:
    """Build [3TEAMS] section.

    Args:
        match_info: Match metadata
        sets_won: Tuple of (home_sets_won, away_sets_won)
    """
    home_name = match_info.get("home_team", "Home")
    away_name = match_info.get("away_team", "Away")

    # Use sequential team IDs (could extract from match_info if available)
    return f"""[3TEAMS]
1;{home_name};{sets_won[0]};;;;
2;{away_name};{sets_won[1]};;;;"""


def build_more_section() -> str:
    """Build [3MORE] section."""
    return """[3MORE]
;;;;;github.com/openvolley/py-datavolley;
;;;"""


def build_comments_section() -> str:
    """Build [3COMMENTS] section."""
    return "[3COMMENTS]"


def build_set_section(set_scores: List[Tuple[int, int]]) -> str:
    """Build [3SET] section with score checkpoints.

    Args:
        set_scores: List of (home_score, away_score) for each set
    """
    lines = ["[3SET]"]

    # Pad to 5 sets
    while len(set_scores) < 5:
        set_scores.append((0, 0))

    for i, (home, away) in enumerate(set_scores[:5]):
        if home == 0 and away == 0:
            # Empty set
            lines.append("True;;;;;25;")
        else:
            # Calculate score checkpoints (at 8, 16, 21, final)
            # For simplicity, we'll estimate based on final score
            winner_score = max(home, away)
            loser_score = min(home, away)

            # Estimate intermediate scores proportionally
            if winner_score >= 25:
                # Regular set
                ratio = loser_score / winner_score if winner_score > 0 else 0
                at_8 = f"8-{int(8 * ratio)}" if home > away else f"{int(8 * ratio)}-8"
                at_16 = (
                    f"16-{int(16 * ratio)}" if home > away else f"{int(16 * ratio)}-16"
                )
                at_21 = (
                    f"21-{int(21 * ratio)}" if home > away else f"{int(21 * ratio)}-21"
                )
                final = f"{home}-{away}"
                lines.append(f"True;{at_8};{at_16};{at_21};{final};{winner_score};")
            else:
                # 5th set (to 15)
                ratio = loser_score / winner_score if winner_score > 0 else 0
                at_8 = f"8-{int(8 * ratio)}" if home > away else f"{int(8 * ratio)}-8"
                final = f"{home}-{away}"
                lines.append(f"True;{at_8};;;{final};{winner_score};")

    return "\n".join(lines)


def build_players_section(players: List[Dict[str, str]], team_index: int) -> str:
    """
    Build [3PLAYERS-H] or [3PLAYERS-V] section.

    Format: team_idx;jersey;player_idx;rot1;rot2;rot3;rot4;rot5;player_id;lastname;firstname;display_name;libero_marker;libero_flag;False;;;

    Real DVW example:
    0;2;2;6;6;6;6;6;-417287;Reilly;Bergen;Reilly;;;False;;;
    0;6;6;*;*;*;*;*;-417288;Choboy;Laney;Choboy;L;1;False;;;

    Args:
        players: List of player dictionaries
        team_index: 0 for home, 1 for visiting

    Returns:
        Player section string
    """
    section_name = "[3PLAYERS-H]" if team_index == 0 else "[3PLAYERS-V]"
    lines = [section_name]

    player_idx_offset = (
        0 if team_index == 0 else 19
    )  # Home starts at 0, away starts at 19

    for idx, player in enumerate(players, 1):
        jersey_raw = player.get("jersey", str(idx))
        # Convert to int and back to remove leading zeros
        try:
            jersey = str(int(jersey_raw))
        except ValueError:
            jersey = jersey_raw

        # Player index - sequential
        player_idx = player_idx_offset + idx

        # Rotation positions - 5 columns (one per set)
        # Empty for now (no rotation data tracked from XML)
        rot_cols = ";;;;;"  # 5 empty rotation columns

        # Player ID - negative integer
        player_id = -(100000 + team_index * 50000 + idx)

        # Names
        first = player.get("first", "")
        last = player.get("last", f"Player{idx}")
        display_name = last  # Display name is last name only

        # Libero markers (could detect from role if available)
        libero_marker = ""
        libero_flag = ""

        # Format: team_idx;jersey;player_idx;rot1;rot2;rot3;rot4;rot5;player_id;lastname;firstname;display_name;libero_marker;libero_flag;False;;;
        line = f"{team_index};{jersey};{player_idx};{rot_cols};{player_id};{last};{first};{display_name};{libero_marker};{libero_flag};False;;;"
        lines.append(line)

    return "\n".join(lines)


def build_attack_combo_section() -> str:
    """Build [3ATTACKCOMBINATION] section."""
    lines = ["[3ATTACKCOMBINATION]"]
    lines.extend(DEFAULT_ATTACK_COMBOS)
    return "\n".join(lines)


def build_setter_call_section() -> str:
    """Build [3SETTERCALL] section."""
    lines = ["[3SETTERCALL]"]
    lines.extend(DEFAULT_SETTER_CALLS)
    return "\n".join(lines)


def build_winning_symbols_section() -> str:
    """Build [3WINNINGSYMBOLS] section."""
    # Default winning symbols pattern
    return """[3WINNINGSYMBOLS]
=~~~#~~~=~~~~~~~=/~~#~~~=/~~#~~~~~~~~~~~=/~~~~~~=~~~~~~~"""


def build_reserve_section() -> str:
    """Build [3RESERVE] section."""
    return "[3RESERVE]"


def build_scout_section(
    plays: List[Dict[str, Any]], players: Dict[str, List[Dict[str, str]]]
) -> str:
    """
    Build [3SCOUT] section with all play codes.

    Args:
        plays: List of play dictionaries
        players: Dictionary with player info

    Returns:
        Scout section string
    """
    lines = ["[3SCOUT]"]

    for play in plays:
        play_type = play.get("type")

        if play_type == "rotation":
            # Generate rotation indicator lines
            rotation_lines = build_rotation_lines(play, players)
            lines.extend(rotation_lines)

        elif play_type == "skill":
            code = build_scout_code(play)
            full_line = build_full_line(code, play)
            lines.append(full_line)

        elif play_type == "point":
            # Skip point lines per user request (simplified format)
            pass

        elif play_type == "set_end":
            set_line = build_set_end_line(play)
            lines.append(set_line)

    return "\n".join(lines)


# ============================================================================
# MAIN FUNCTION
# ============================================================================


def xml_to_dvw(xml_file: str) -> str:
    """
    Convert VolleyStation XML to DataVolley DVW format.

    Args:
        xml_file: Path to input XML file

    Returns:
        Path to output DVW file
    """
    # 1. Parse XML
    root = parse_xml_file(xml_file)

    # 2. Extract all instances
    instances = extract_instances(root)

    if not instances:
        raise ValueError(f"No instances found in XML file: {xml_file}")

    # 3. Detect team prefixes (USA1/USA2 or UNL/TAMU, etc.)
    team_prefixes = get_team_prefixes(instances)

    # 4. Extract match info
    match_info = extract_match_info(instances, xml_file, team_prefixes)

    # 5. Extract players
    players = extract_players(instances, team_prefixes)

    # 6. Process instances to plays
    plays = process_instances_to_plays(instances, players, team_prefixes)

    # 7. Calculate sets won and set scores
    sets_won, set_scores = calculate_set_results(plays)

    # 8. Build all sections
    sections = [
        build_header_section(),
        build_match_section(match_info),
        build_teams_section(match_info, sets_won),
        build_more_section(),
        build_comments_section(),
        build_set_section(set_scores),
        build_players_section(players.get("home", []), 0),
        build_players_section(players.get("visiting", []), 1),
        build_attack_combo_section(),
        build_setter_call_section(),
        build_winning_symbols_section(),
        build_reserve_section(),
        build_scout_section(plays, players),
    ]

    # 9. Write output file
    output_path = os.path.splitext(xml_file)[0] + ".dvw"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sections))

    return output_path
