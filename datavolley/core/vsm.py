# datavolley/core/vsm.py

import json
import uuid
from typing import Dict, List, Optional


def read_vsm(file_path: str) -> List[Dict]:
    """
    Read and parse a VSM file, returning data in the same format as read_dv.

    Args:
        file_path: Path to the VSM file

    Returns:
        List of play dictionaries in DVW format
    """
    with open(file_path, "r", encoding="utf-8") as f:
        vsm_data = json.load(f)

    return parse_vsm_data(vsm_data)


def parse_vsm_data(vsm_data: Dict) -> List[Dict]:
    """
    Parse VSM data into DVW-compatible play format.

    Args:
        vsm_data: Raw VSM data dictionary

    Returns:
        List of play dictionaries matching the read_dv format
    """
    plays = []

    # Generate match ID
    match_id = vsm_data.get("_id", str(uuid.uuid4().hex[:8]))

    # Extract team information
    teams = extract_team_info(vsm_data)
    home_team = teams["home_team"]
    home_team_id = teams["home_team_id"]
    visiting_team = teams["visiting_team"]
    visiting_team_id = teams["visiting_team_id"]

    # Extract player mappings
    player_map = build_player_map(vsm_data)

    # Process each set
    if "scout" in vsm_data and "sets" in vsm_data["scout"]:
        for set_idx, set_data in enumerate(vsm_data["scout"]["sets"], 1):
            set_number = set_idx

            # Process events in the set
            if "events" in set_data:
                for event in set_data["events"]:
                    # Get lineup and score at start of rally
                    lineup = event.get("lineup", {})
                    score = event.get("score", {})

                    # Extract positions and setter positions
                    home_positions = lineup.get("home", {}).get("positions", {})
                    away_positions = lineup.get("away", {}).get("positions", {})
                    home_setter_at = lineup.get("home", {}).get("setterAt")
                    away_setter_at = lineup.get("away", {}).get("setterAt")

                    # Convert positions to p1-p6 format
                    home_rotation = extract_rotation(home_positions)
                    away_rotation = extract_rotation(away_positions)

                    # Get scores
                    home_score = score.get("home", 0)
                    away_score = score.get("away", 0)

                    # Process plays in the exchange
                    if "exchange" in event and "plays" in event["exchange"]:
                        point_won_by = event["exchange"].get("point")

                        for play in event["exchange"]["plays"]:
                            play_dict = create_play_dict(
                                play=play,
                                match_id=match_id,
                                set_number=set_number,
                                home_team=home_team,
                                home_team_id=home_team_id,
                                visiting_team=visiting_team,
                                visiting_team_id=visiting_team_id,
                                home_score=home_score,
                                away_score=away_score,
                                home_setter_position=home_setter_at,
                                visiting_setter_position=away_setter_at,
                                home_rotation=home_rotation,
                                away_rotation=away_rotation,
                                player_map=player_map,
                                point_won_by=point_won_by,
                            )
                            plays.append(play_dict)

    return plays


def extract_team_info(vsm_data: Dict) -> Dict:
    """
    Extract team names and IDs from VSM data.

    Args:
        vsm_data: Raw VSM data dictionary

    Returns:
        Dictionary with team information
    """
    teams = {
        "home_team": None,
        "home_team_id": None,
        "visiting_team": None,
        "visiting_team_id": None,
    }

    if "team" in vsm_data:
        if "home" in vsm_data["team"]:
            teams["home_team"] = vsm_data["team"]["home"].get("name")
            teams["home_team_id"] = vsm_data["team"]["home"].get("code")

        if "away" in vsm_data["team"]:
            teams["visiting_team"] = vsm_data["team"]["away"].get("name")
            teams["visiting_team_id"] = vsm_data["team"]["away"].get("code")

    return teams


def build_player_map(vsm_data: Dict) -> Dict:
    """
    Build a mapping of player numbers to player information.

    Args:
        vsm_data: Raw VSM data dictionary

    Returns:
        Dictionary mapping player numbers to names and IDs
    """
    player_map = {}

    if "team" in vsm_data:
        # Home team players
        if "home" in vsm_data["team"] and "players" in vsm_data["team"]["home"]:
            for player in vsm_data["team"]["home"]["players"]:
                player_num = str(player.get("shirtNumber", ""))
                player_info = {
                    "name": f"{player.get('firstName', '')} {player.get('lastName', '')}".strip(),
                    "id": player.get("code"),
                    "first_name": player.get("firstName"),
                    "last_name": player.get("lastName"),
                    "number": player_num,
                }
                # Store with both formats - as-is and with leading zero for single digits
                player_map[f"home_{player_num}"] = player_info
                if player_num.isdigit() and len(player_num) == 1:
                    player_map[f"home_0{player_num}"] = player_info

        # Away team players
        if "away" in vsm_data["team"] and "players" in vsm_data["team"]["away"]:
            for player in vsm_data["team"]["away"]["players"]:
                player_num = str(player.get("shirtNumber", ""))
                player_info = {
                    "name": f"{player.get('firstName', '')} {player.get('lastName', '')}".strip(),
                    "id": player.get("code"),
                    "first_name": player.get("firstName"),
                    "last_name": player.get("lastName"),
                    "number": player_num,
                }
                # Store with both formats - as-is and with leading zero for single digits
                player_map[f"away_{player_num}"] = player_info
                if player_num.isdigit() and len(player_num) == 1:
                    player_map[f"away_0{player_num}"] = player_info

    return player_map


def extract_rotation(positions: Dict) -> Dict:
    """
    Extract rotation positions from lineup data.

    Args:
        positions: Dictionary with position numbers as keys

    Returns:
        Dictionary with p1-p6 format
    """
    rotation = {}
    for i in range(1, 7):
        rotation[f"p{i}"] = (
            str(positions.get(str(i), "")) if positions.get(str(i)) else None
        )

    return rotation


def create_play_dict(
    play: Dict,
    match_id: str,
    set_number: int,
    home_team: str,
    home_team_id: str,
    visiting_team: str,
    visiting_team_id: str,
    home_score: int,
    away_score: int,
    home_setter_position: int,
    visiting_setter_position: int,
    home_rotation: Dict,
    away_rotation: Dict,
    player_map: Dict,
    point_won_by: Optional[str] = None,
    serving_team: Optional[str] = None,
    receiving_team: Optional[str] = None,
) -> Dict:
    """
    Create a single play dictionary in DVW format.

    Args:
        play: Single play data from VSM
        match_id: Match ID
        set_number: Current set number
        home_team: Home team name
        home_team_id: Home team ID
        visiting_team: Visiting team name
        visiting_team_id: Visiting team ID
        home_score: Home team score at start of rally
        away_score: Away team score at start of rally
        home_setter_position: Home team setter position
        visiting_setter_position: Away team setter position
        home_rotation: Home team rotation (p1-p6)
        away_rotation: Away team rotation (p1-p6)
        player_map: Player number to name/ID mapping
        point_won_by: Team that won the point ('*' or 'a')

    Returns:
        Play dictionary in DVW format
    """
    # Determine team name based on team code
    team_code = play.get("team")
    if team_code == "*":
        team = home_team
        team_prefix = "home"
    elif team_code == "a":
        team = visiting_team
        team_prefix = "away"
    else:
        team = None
        team_prefix = None

    # Get player information
    player_number = str(play.get("player", "")) if play.get("player") else None
    player_name = None
    player_id = None

    if team_prefix and player_number:
        # Try with the player number as-is
        player_key = f"{team_prefix}_{player_number}"
        if player_key in player_map:
            player_info = player_map[player_key]
            player_name = player_info.get("name")
            player_id = player_info.get("id")
        else:
            # Try removing leading zeros
            player_num_int = (
                str(int(player_number)) if player_number.isdigit() else player_number
            )
            player_key_alt = f"{team_prefix}_{player_num_int}"
            if player_key_alt in player_map:
                player_info = player_map[player_key_alt]
                player_name = player_info.get("name")
                player_id = player_info.get("id")

    # Get skill and evaluation
    skill = play.get("skill")
    evaluation_code = play.get("effect")

    # Map skill_subtype based on skill type
    skill_subtype = None
    if skill == "S":  # Serve
        skill_subtype = map_serve_subtype(play.get("hitType"))
    elif skill == "R":  # Reception
        skill_subtype = map_reception_subtype(play.get("skillType"))
    elif skill == "A":  # Attack
        skill_subtype = map_attack_subtype(play.get("skillType"))
    elif skill == "E":  # Set
        skill_subtype = map_set_subtype(play.get("skillType"))
    elif skill == "B":  # Block
        skill_subtype = map_block_subtype(play.get("skillType"))
    elif skill == "D":  # Dig
        skill_subtype = map_dig_subtype(play.get("skillType"))

    # Determine setter position for the acting team
    if team_code == "*":
        setter_position = home_setter_position
    elif team_code == "a":
        setter_position = visiting_setter_position
    else:
        setter_position = None

    # Extract attack_code and set_code based on skill
    attack_code = None
    set_code = None
    if skill == "A":  # Attack
        attack_code = play.get("combination")
    elif skill == "E":  # Set
        set_code = play.get("combination")

    # Extract coordinates from travelPath
    start_coordinate_x = None
    start_coordinate_y = None
    mid_coordinate_x = None
    mid_coordinate_y = None
    end_coordinate_x = None
    end_coordinate_y = None

    travel_path = play.get("travelPath", [])
    if travel_path:
        if len(travel_path) > 0:
            start_coordinate_x = travel_path[0].get("x")
            start_coordinate_y = travel_path[0].get("y")
        if len(travel_path) > 1:
            end_coordinate_x = travel_path[-1].get("x")
            end_coordinate_y = travel_path[-1].get("y")
        if len(travel_path) > 2:
            mid_idx = len(travel_path) // 2
            mid_coordinate_x = travel_path[mid_idx].get("x")
            mid_coordinate_y = travel_path[mid_idx].get("y")

    # Determine point winner team name
    point_won_by_name = None
    if point_won_by == "*":
        point_won_by_name = home_team
    elif point_won_by == "a":
        point_won_by_name = visiting_team

    # Build the play dictionary
    play_dict = {
        "match_id": match_id,
        "video_time": play.get("time"),
        "code": None,  # VSM doesn't have DVW-style codes
        "team": team,
        "player_number": player_number,
        "player_name": player_name,
        "player_id": player_id,
        "skill": skill,
        "skill_subtype": skill_subtype,
        "evaluation_code": evaluation_code,
        "setter_position": setter_position,
        "attack_code": attack_code,
        "set_code": set_code,
        "set_type": None,  # Leave as None for now
        "start_zone": play.get("startZone"),
        "end_zone": play.get("endZone"),
        "end_subzone": play.get("endSubZone"),
        "num_players_numeric": play.get("players"),
        "home_team_score": home_score,
        "visiting_team_score": away_score,
        "home_setter_position": home_setter_position,
        "visiting_setter_position": visiting_setter_position,
        "custom_code": play.get("custom"),
        "home_p1": home_rotation.get("p1"),
        "home_p2": home_rotation.get("p2"),
        "home_p3": home_rotation.get("p3"),
        "home_p4": home_rotation.get("p4"),
        "home_p5": home_rotation.get("p5"),
        "home_p6": home_rotation.get("p6"),
        "visiting_p1": away_rotation.get("p1"),
        "visiting_p2": away_rotation.get("p2"),
        "visiting_p3": away_rotation.get("p3"),
        "visiting_p4": away_rotation.get("p4"),
        "visiting_p5": away_rotation.get("p5"),
        "visiting_p6": away_rotation.get("p6"),
        "start_coordinate": None,  # VSM uses x,y separately
        "mid_coordinate": None,
        "end_coordinate": None,
        "point_phase": None,
        "attack_phase": None,
        "start_coordinate_x": start_coordinate_x,
        "start_coordinate_y": start_coordinate_y,
        "mid_coordinate_x": mid_coordinate_x,
        "mid_coordinate_y": mid_coordinate_y,
        "end_coordinate_x": end_coordinate_x,
        "end_coordinate_y": end_coordinate_y,
        "set_number": set_number,
        "home_team": home_team,
        "visiting_team": visiting_team,
        "home_team_id": home_team_id,
        "visiting_team_id": visiting_team_id,
        "point_won_by": point_won_by_name,
        "serving_team": serving_team,
        "receiving_team": receiving_team,
        "rally_number": None,  # Not directly available in VSM
        "possesion_number": None,  # Not directly available in VSM
    }

    return play_dict


# Skill subtype mapping functions
def map_serve_subtype(hitType: Optional[str]) -> Optional[str]:
    """Map serve hitType codes to readable names."""
    if not hitType:
        return None
    serve_subtype_map = {
        "Q": "Jump Spin",
        "M": "Jump Float",
        "T": "Standing Float",
        "H": "Float",
        "O": "Serve Other",
        "N": "Hybrid",
    }
    return serve_subtype_map.get(hitType)


def map_reception_subtype(skillType: Optional[str]) -> Optional[str]:
    """Map reception skillType codes to readable names."""
    if not skillType:
        return None
    reception_subtype_map = {
        "L": "Low",
        "M": "Medium",
        "H": "High",
        "R": "Right",
        "W": "Wide",
        "S": "Short",
        "C": "Center",
        "B": "Behind",
    }
    return reception_subtype_map.get(skillType)


def map_attack_subtype(skillType: Optional[str]) -> Optional[str]:
    """Map attack skillType codes to readable names."""
    if not skillType:
        return None
    attack_subtype_map = {
        "H": "Hard",
        "P": "Soft spike",
        "T": "Tip",
        "O": "Other attack",
    }
    return attack_subtype_map.get(skillType)


def map_set_subtype(skillType: Optional[str]) -> Optional[str]:
    """Map set skillType codes to readable names."""
    if not skillType:
        return None
    set_subtype_map = {
        "1": "1 hand set",
        "2": "2 hands set",
        "3": "Bump set",
        "4": "Other set",
        "5": "Underhand set",
    }
    return set_subtype_map.get(skillType)


def map_block_subtype(skillType: Optional[str]) -> Optional[str]:
    """Map block skillType codes to readable names."""
    if not skillType:
        return None
    block_subtype_map = {
        "0": "No block",
        "1": "1 player block",
        "2": "2 player block",
        "3": "3 player block",
        "4": "Hole block",
    }
    return block_subtype_map.get(skillType)


def map_dig_subtype(skillType: Optional[str]) -> Optional[str]:
    """Map dig skillType codes to readable names."""
    if not skillType:
        return None
    dig_subtype_map = {
        "S": "Standard",
        "B": "Behind",
        "C": "Cover",
        "L": "Low",
        "M": "Medium",
        "H": "High",
    }
    return dig_subtype_map.get(skillType)


# Integration with existing infrastructure
def read_vsm_as_dv(file_path: str) -> Dict:
    """
    Read VSM file and return in the same structure as read_dv.

    This function provides compatibility with existing DVW infrastructure,
    returning the same structure that read_dv would return.

    Args:
        file_path: Path to the VSM file

    Returns:
        Dictionary with 'plays' key containing list of play dictionaries
    """
    plays = read_vsm(file_path)
    return {"plays": plays}


# Utility function to extract metadata
def extract_vsm_metadata(vsm_data: Dict) -> Dict:
    """
    Extract metadata from VSM file for additional context.

    Args:
        vsm_data: Raw VSM data dictionary

    Returns:
        Dictionary with metadata
    """
    metadata = {
        "match_id": vsm_data.get("_id"),
        "competition": vsm_data.get("competition", {}).get("name")
        if vsm_data.get("competition")
        else None,
        "season": vsm_data.get("season"),
        "date": vsm_data.get("date"),
        "venue": vsm_data.get("venue", {}).get("name")
        if vsm_data.get("venue")
        else None,
    }

    # Extract final scores from sets
    if "scout" in vsm_data and "sets" in vsm_data["scout"]:
        set_scores = []
        for set_data in vsm_data["scout"]["sets"]:
            if "score" in set_data:
                set_scores.append({
                    "home": set_data["score"].get("home"),
                    "away": set_data["score"].get("away"),
                })
        metadata["set_scores"] = set_scores

    return metadata
