# datavolley/io/plays.py

from typing import Dict, List


def plays_data() -> List[Dict]:
    """
    Return the structure for plays data extraction.

    Returns:
        List containing the play data dictionary structure
    """
    return [
        {
            "match_id": None,
            # "video_file_number": None,
            "video_time": None,
            "code": None,
            "team": None,
            "player_number": None,
            "player_name": None,
            "player_id": None,
            "skill": None,
            "skill_subtype": None,
            "evaluation_code": None,
            "setter_position": None,
            "attack_code": None,
            "set_code": None,
            "set_type": None,
            "start_zone": None,
            "end_zone": None,
            "end_subzone": None,
            "num_players_numeric": None,
            "home_team_score": None,
            "visiting_team_score": None,
            "home_setter_position": None,
            "visiting_setter_position": None,
            "custom_code": None,
            "home_p1": None,
            "home_p2": None,
            "home_p3": None,
            "home_p4": None,
            "home_p5": None,
            "home_p6": None,
            "visiting_p1": None,
            "visiting_p2": None,
            "visiting_p3": None,
            "visiting_p4": None,
            "visiting_p5": None,
            "visiting_p6": None,
            "start_coordinate": None,
            "mid_coordinate": None,
            "end_coordinate": None,
            "point_phase": None,
            "attack_phase": None,
            "start_coordinate_x": None,
            "start_coordinate_y": None,
            "mid_coordinate_x": None,
            "mid_coordinate_y": None,
            "end_coordinate_x": None,
            "end_coordinate_y": None,
            "set_number": None,
            "home_team": None,
            "visiting_team": None,
            "home_team_id": None,
            "visiting_team_id": None,
            "point_won_by": None,
            "serving_team": None,
            "receiving_team": None,
            "rally_number": None,
        }
    ]
