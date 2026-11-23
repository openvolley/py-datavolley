# datavolley/__init__.py
from pathlib import Path
from typing import Any

from .core.attack_codes import dv_attack_code2desc
from .core.attack_combos import extract_attack_combinations
from .core.code import extract_skill_subtype, parse_play_code
from .core.coordinates import dv_index2xy
from .core.players import extract_players
from .core.plays import extract_plays, extract_score_from_code
from .core.set_calls import extract_setter_calls
from .core.teams import extract_teams
from .io.dvw import load_dvw, read_plays, read_raw_plays
from .io.volleystation import load_vsm as _load_vsm
from .types import MatchData
from .utils.metadata import (
    assign_rally_numbers_to_plays,
    extract_comments,
    extract_date,
    extract_set_scores,
    generate_match_id,
    get_match_result,
    get_rally_number,
)

# Version info
__version__ = "1.0.0"
__author__ = "Tyler Widdison"

# Explicitly define what's available when someone imports the package
__all__ = [
    "assign_rally_numbers_to_plays",
    "dv_attack_code2desc",
    "dv_index2xy",
    "example_file",
    "example_file_list",
    "extract_attack_combinations",
    "extract_comments",
    "extract_date",
    "extract_players",
    "extract_plays",
    "extract_score_from_code",
    "extract_set_scores",
    "extract_setter_calls",
    "extract_skill_subtype",
    "extract_teams",
    "generate_match_id",
    "get_match_result",
    "get_match_summary",
    "get_rally_number",
    "load_dv",
    "load_dvw",
    "parse_play_code",
    "read_dv",
    "read_plays",
    "read_raw_plays",
]


def example_file() -> str:
    """
    Get the path to an example DVW file included with the package.

    Returns:
        str: Path to example DVW file
    """
    return str(Path(__file__).parent / "data" / "example_match.dvw")


def example_file_list() -> list[str]:
    """Return paths to all DVW files included with the package."""
    data_dir = Path(__file__).parent / "data"
    return [
        str(path)
        for path in sorted(data_dir.glob("*.dvw"), key=lambda p: p.name.casefold())
    ]


def load_dv(file_path: str | Path) -> MatchData:
    """Read a full match dictionary, automatically selecting DVW or indoor VSM."""
    if Path(file_path).suffix.lower() == ".vsm":
        return _load_vsm(file_path)
    return load_dvw(str(file_path))


def get_match_summary(match_data: MatchData) -> dict:
    """
    Get a summary of key match information.

    Args:
        match_data (dict): Dictionary from load_dv() or load_dvw()

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


def read_dv(file_path: str | Path) -> list[dict[str, Any]]:
    """
    Load a DVW or indoor VSM file into dictionaries suitable for DataFrame creation.
    Rally numbers and point winners are automatically included.

    Args:
        file_path (str | Path): Path to the DVW or VSM file

    Returns:
            list[dict]: List of dictionaries containing play data with coordinate information,
                including rally_number and point_won_by fields.
    """
    return load_dv(file_path)["plays"]
