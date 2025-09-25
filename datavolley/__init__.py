# datavolley/__init__.py
from pathlib import Path

from .core.attack_combos import extract_attack_combinations
from .core.code import extract_skill_subtype, parse_play_code
from .core.coordinates import dv_index2xy
from .core.players import extract_players
from .core.plays import extract_plays, extract_score_from_code
from .core.set_calls import extract_setter_calls
from .core.teams import extract_teams
from .utils.metadata import (
    extract_comments,
    extract_date,
    extract_set_scores,
    generate_match_id,
    get_match_result,
)

# Version info
__version__ = "0.1.2"
__author__ = "Tyler Widdison"

# Explicitly define what's available when someone imports the package
__all__ = [
    # Main loading function
    "load_dvw",
    "example_file",
    # Metadata functions
    "extract_date",
    "generate_match_id",
    "extract_set_scores",
    "get_match_result",
    "extract_comments",
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
                "plays": list
            }

    Example:
        >>> import datavolley as dv
        >>> match_data = dv.load_dvw("path/to/match.dvw")
        >>> print(f"Match between {match_data['teams']['team_1']} vs {match_data['teams']['team_2']}")
        >>> print(f"Final score: {match_data['match_result']}")
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
