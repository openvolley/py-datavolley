# datavolley/__init__.py
from pathlib import Path

from .core.attack_codes import dv_attack_code2desc
from .core.attack_combos import extract_attack_combinations
from .core.code import extract_skill_subtype, parse_play_code
from .core.coordinates import dv_index2xy
from .core.players import extract_players
from .core.plays import extract_plays, extract_score_from_code
from .core.set_calls import extract_setter_calls
from .core.teams import extract_teams
from .io.plays import plays_data
from .utils.metadata import (
    assign_rally_numbers_to_plays,
    extract_comments,
    extract_date,
    extract_set_scores,
    generate_match_id,
    get_match_result,
    get_rally_number,
)

try:
    from .plot.court import dv_court, dv_heatmap

    _HAS_PLOT = True
except ImportError:
    _HAS_PLOT = False

    def dv_court(*args, **kwargs):
        raise ImportError(
            "Plotting functions require optional dependencies. "
            "Install them with: uv add openvolley-pydatavolley[plot]"
        )

    def dv_heatmap(*args, **kwargs):
        raise ImportError(
            "Plotting functions require optional dependencies. "
            "Install them with: uv add openvolley-pydatavolley[plot]"
        )


# Version info
__version__ = "0.1.5"
__author__ = "Tyler Widdison"

# Explicitly define what's available when someone imports the package
__all__ = [
    # Main loading function
    "load_dvw",
    "read_dv",
    "example_file",
    # Metadata functions
    "extract_date",
    "generate_match_id",
    "extract_set_scores",
    "get_match_result",
    "extract_comments",
    "get_rally_number",
    "assign_rally_numbers_to_plays",
    # Team functions
    "extract_teams",
    # Player functions
    "extract_players",
    # Play functions
    "extract_plays",
    "extract_score_from_code",
    "parse_play_code",
    "extract_skill_subtype",
    # Attack combination functions
    "extract_attack_combinations",
    # Setter call functions
    "extract_setter_calls",
    # Coordinate functions
    "dv_index2xy",
    # Summary function
    "get_match_summary",
    # Attack code helpers
    "dv_attack_code2desc",
    # Plotting functions
    "dv_court",
    "dv_heatmap",
]


def example_file() -> str:
    """
    Get the path to an example DVW file included with the package.

    Returns:
        str: Path to example DVW file
    """
    return str(Path(__file__).parent / "data" / "example_match.dvw")


def load_dvw(file_path: str) -> dict:
    """
    Load and parse a DVW file into a comprehensive match data dictionary.

    Args:
        file_path (str): Path to the DVW file

    Returns:
        dict: Dictionary containing all parsed match data with the following structure:
            {
                "filename": str,
                "match_date": datetime,
                "match_id": str,
                "comments": str,
                "teams": dict,
                "set_scores": dict,
                "match_result": dict,
                "players": dict,
                "attack_combinations": list,
                "setter_calls": list,
                "plays": list  # Now includes rally_number and point_won_by fields
            }

    Example:
        >>> import datavolley as dv
        >>> match_data = dv.load_dvw("path/to/match.dvw")
        >>> print(f"Match between {match_data['teams']['team_1']} vs {match_data['teams']['team_2']}")
        >>> print(f"Final score: {match_data['match_result']}")
        >>> # Rally numbers are automatically included
        >>> for play in match_data['plays'][:5]:
        >>>     print(f"Rally {play['rally_number']}: {play['skill']}")
    """
    # Read the file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"DVW file not found: {file_path}")
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, "r", encoding="latin-1") as f:
            content = f.read()

    # Extract all data
    match_data = {
        "filename": Path(file_path).stem,
        "match_date": extract_date(content),
        "match_id": generate_match_id(content),
        "comments": extract_comments(content),
        "teams": extract_teams(content),
        "set_scores": extract_set_scores(content),
        "players": extract_players(content),
        "attack_combinations": extract_attack_combinations(content),
        "setter_calls": extract_setter_calls(content),
        "plays": extract_plays(content),
    }

    # Add calculated match result
    match_data["match_result"] = get_match_result(match_data["set_scores"])

    # Always add rally numbers and point winners
    if match_data.get("plays"):
        match_data = get_rally_number(match_data)

    return match_data


def get_match_summary(match_data: dict) -> dict:
    """
    Get a summary of key match information.

    Args:
        match_data (dict): Dictionary from load_dvw()

    Returns:
        dict: Summary information
    """
    teams = match_data.get("teams", {})
    match_result = match_data.get("match_result", {})
    players = match_data.get("players", {})

    return {
        "match_id": match_data.get("match_id"),
        "date": match_data.get("match_date"),
        "teams": {
            "home": teams.get("team_1"),
            "visiting": teams.get("team_2"),
        },
        "final_score": {
            "home_sets": match_result.get("team_1_sets_won", 0),
            "visiting_sets": match_result.get("team_2_sets_won", 0),
        },
        "winner": teams.get("team_1")
        if match_result.get("match_winner") == "team_1"
        else teams.get("team_2")
        if match_result.get("match_winner") == "team_2"
        else "Tie",
        "total_plays": len(match_data.get("plays", [])),
        "home_players": len(players.get("home", [])),
        "visiting_players": len(players.get("visiting", [])),
    }


def read_dv(file_path: str) -> list[dict]:
    """
    Load and parse a DVW file into a list of dictionaries suitable for DataFrame creation.
    Rally numbers and point winners are automatically included.

    Args:
        file_path (str): Path to the DVW file

    Returns:
        list[dict]: List of dictionaries containing play data with coordinate information,
                   including rally_number and point_won_by fields
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"DVW file not found: {file_path}")
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            content = f.read()

    # Load without rally numbers first since we'll process plays then add them
    # First extract raw data
    match_data = {
        "filename": Path(file_path).stem,
        "match_date": extract_date(content),
        "match_id": generate_match_id(content),
        "comments": extract_comments(content),
        "teams": extract_teams(content),
        "set_scores": extract_set_scores(content),
        "players": extract_players(content),
        "attack_combinations": extract_attack_combinations(content),
        "setter_calls": extract_setter_calls(content),
        "plays": extract_plays(content),
    }
    match_data["match_result"] = get_match_result(match_data["set_scores"])

    plays = match_data.get("plays", [])
    teams = match_data.get("teams", {})
    match_id = match_data.get("match_id")

    result = []
    template = plays_data()[0]

    for play in plays:
        play_dict = template.copy()

        for key, value in play.items():
            if key in play_dict:
                play_dict[key] = value

        play_dict["match_id"] = match_id
        play_dict["home_team"] = teams.get("team_1")
        play_dict["visiting_team"] = teams.get("team_2")
        play_dict["home_team_id"] = teams.get("team_1_id")
        play_dict["visiting_team_id"] = teams.get("team_2_id")

        play_dict["home_team_score"] = play.get("home_score")
        play_dict["visiting_team_score"] = play.get("visiting_score")

        code = play.get("code")
        if code:
            parsed_code = parse_play_code(content, code)
            if parsed_code:
                play_dict["team"] = parsed_code.get("team")
                play_dict["player_number"] = parsed_code.get("player_number")
                play_dict["player_name"] = parsed_code.get("player_name")
                play_dict["player_id"] = parsed_code.get("player_id")
                play_dict["skill"] = parsed_code.get("skill")
                play_dict["skill_type"] = parsed_code.get("skill_type")
                play_dict["skill_subtype"] = parsed_code.get("skill_subtype")
                play_dict["evaluation_code"] = parsed_code.get("evaluation_code")
                play_dict["attack_code"] = parsed_code.get("attack_code")
                play_dict["set_code"] = parsed_code.get("set_code")
                play_dict["set_type"] = parsed_code.get("set_type")
                play_dict["start_zone"] = parsed_code.get("start_zone")
                play_dict["end_zone"] = parsed_code.get("end_zone")
                play_dict["end_subzone"] = parsed_code.get("end_subzone")
                play_dict["num_players_numeric"] = parsed_code.get(
                    "num_players_numeric"
                )
                if parsed_code.get("custom_code"):
                    play_dict["custom_code"] = parsed_code.get("custom_code")

        start_coord = play.get("start_coordinate")
        if start_coord is not None:
            coords = dv_index2xy(start_coord)
            if coords:
                play_dict["start_coordinate_x"], play_dict["start_coordinate_y"] = (
                    coords
                )

        mid_coord = play.get("mid_coordinate")
        if mid_coord is not None:
            coords = dv_index2xy(mid_coord)
            if coords:
                play_dict["mid_coordinate_x"], play_dict["mid_coordinate_y"] = coords

        end_coord = play.get("end_coordinate")
        if end_coord is not None:
            coords = dv_index2xy(end_coord)
            if coords:
                play_dict["end_coordinate_x"], play_dict["end_coordinate_y"] = coords

        result.append(play_dict)

    # Always add rally numbers and point winners with actual team names
    home_team = teams.get("team_1", "home")
    visiting_team = teams.get("team_2", "visiting")
    result = assign_rally_numbers_to_plays(result, home_team, visiting_team)

    return result
