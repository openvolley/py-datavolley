from pathlib import Path

from .core.attack_combos import extract_attack_combinations
from .core.players import extract_players, get_player_by_number, get_starting_lineup
from .core.set_calls import extract_setter_calls
from .core.teams import extract_teams, get_team_by_id, get_team_info
from .utils.metadata import (
    extract_comments,
    extract_date,
    extract_set_scores,
    generate_match_id,
    get_match_result,
)

# Explicitly define what's available when someone imports the package
__all__ = [
    "extract_comments",
    "example_file",
    "load_dvw",
    "extract_date",
    "generate_match_id",
    "extract_set_scores",
    "get_match_result",
    "extract_players",
    "get_starting_lineup",
    "get_player_by_number",
    "extract_teams",
    "get_team_by_id",
    "get_team_info",
]


def example_file() -> str:
    """Get example DVW file path."""
    return str(Path(__file__).parent / "data" / "example_match.dvw")


def load_dvw(file_path: str) -> dict:
    """
    Load and parse a DVW file.

    Args:
        file_path: Path to the DVW file

    Returns:
        Dictionary containing all parsed match data
    """
    with open(file_path, "r", encoding="utf-8") as f:
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
        # "raw_content": content,
    }

    # Add match result
    match_data["match_result"] = get_match_result(match_data["set_scores"])

    return match_data
