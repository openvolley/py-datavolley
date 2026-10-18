# datavolley/__init__.py
from pathlib import Path
from typing import Any

from .core.attack_codes import dv_attack_code2desc
from .core.attack_combos import extract_attack_combinations
from .core.code import (
    _parse_play_code,
    _uses_cones,
    extract_skill_subtype,
    parse_play_code,
)
from .core.coordinates import dv_index2xy
from .core.players import extract_players
from .core.plays import _extract_plays, extract_plays, extract_score_from_code
from .core.set_calls import extract_setter_calls
from .core.teams import extract_teams
from .io.plays import plays_data
from .types import MatchData, normalize_play
from .types.match import _PlayData
from .types.plays import _ANALYSIS_COERCERS, _normalize_analysis_play
from .utils.metadata import (
    _assign_rally_numbers_to_plays,
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


def _enrich_plays(
    raw_content: str, match_data: _PlayData, *, analysis_only: bool = False
) -> list[dict[str, Any]]:
    teams = match_data["teams"]
    home_team = teams.get("team_1")
    visiting_team = teams.get("team_2")
    attack_descriptions = {
        item.get("code"): item.get("description")
        for item in match_data["attack_combinations"]
        if item.get("code")
    }
    set_descriptions = {
        item.get("code"): item.get("description")
        for item in match_data["setter_calls"]
        if item.get("code")
    }
    use_cones = _uses_cones(raw_content)
    player_lookup: dict[tuple[str, int], tuple[str | None, str | None]] = {}
    for side, prefix in (("home", "*"), ("visiting", "a")):
        for player in match_data["players"].get(side, []):
            number = player.get("player_number")
            if number is not None:
                try:
                    number = int(number)
                except ValueError:
                    continue
                # Match the first roster entry, including zero-padded numbers.
                player_lookup.setdefault(
                    (prefix, number),
                    (player.get("full_name"), player.get("player_id")),
                )
    template = plays_data()[0]
    if analysis_only:
        template = {
            name: value
            for name, value in template.items()
            if name in _ANALYSIS_COERCERS
        }
    result = []

    for play in match_data["plays"]:
        play_dict = template.copy()
        for key, value in play.items():
            if key in play_dict:
                play_dict[key] = value

        play_dict["match_id"] = match_data["match_id"]
        play_dict["home_team"] = home_team
        play_dict["visiting_team"] = visiting_team
        play_dict["home_team_id"] = teams.get("team_1_id")
        play_dict["visiting_team_id"] = teams.get("team_2_id")
        play_dict["home_team_score"] = play.get("home_score")
        play_dict["visiting_team_score"] = play.get("visiting_score")

        code = play.get("code") or ""
        if code.startswith("*") and not code.startswith("**"):
            play_dict["team"] = home_team
            play_dict["team_id"] = teams.get("team_1_id")
        elif code.startswith("a"):
            play_dict["team"] = visiting_team
            play_dict["team_id"] = teams.get("team_2_id")

        parsed_code = _parse_play_code(
            raw_content,
            code,
            use_cones=use_cones,
            teams=teams,
            player_lookup=player_lookup,
            analysis_only=analysis_only,
        )
        if parsed_code:
            for key, value in parsed_code.items():
                if key in play_dict and (key != "custom_code" or value):
                    play_dict[key] = value
            play_dict["winning_attack"] = (
                parsed_code.get("evaluation") == "Winning attack"
            )

            attack_code = parsed_code.get("attack_code")
            if attack_code:
                play_dict["attack_description"] = attack_descriptions.get(
                    attack_code, "unknown attack code"
                )
            set_code = parsed_code.get("set_code")
            if set_code:
                play_dict["set_description"] = set_descriptions.get(
                    set_code, "unknown set code"
                )

        if not analysis_only:
            for coordinate in ("start", "mid", "end"):
                value = play.get(f"{coordinate}_coordinate")
                if value is not None:
                    xy = dv_index2xy(value)
                    if xy:
                        play_dict[f"{coordinate}_coordinate_x"] = xy[0]
                        play_dict[f"{coordinate}_coordinate_y"] = xy[1]

        result.append(play_dict)

    result = _assign_rally_numbers_to_plays(
        result,
        home_team,
        visiting_team,
        match_data["players"],
        include_lineups=not analysis_only,
    )
    normalize = _normalize_analysis_play if analysis_only else normalize_play
    return [normalize(play) for play in result]


def _read_dvw_content(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"DVW file not found: {file_path}")
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()


def load_dvw(file_path: str) -> MatchData:
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
    content = _read_dvw_content(file_path)

    match_data: MatchData = {
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
    match_data["plays"] = _enrich_plays(content, match_data)

    return match_data


def get_match_summary(match_data: MatchData) -> dict:
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


def read_dv(file_path: str) -> list[dict[str, Any]]:
    """
    Load and parse a DVW file into a list of dictionaries suitable for DataFrame creation.
    Rally numbers and point winners are automatically included.

    Args:
        file_path (str): Path to the DVW file

    Returns:
            list[dict]: List of dictionaries containing play data with coordinate information,
                including rally_number and point_won_by fields.
    """
    return load_dvw(file_path)["plays"]


def read_plays(file_path: str) -> list[dict[str, Any]]:
    """Read normalized, analysis-focused play rows without a full match result.

    Includes team/player identity, skills, evaluations, attack/set descriptions,
    zones/cones, event flags, scores, phases, setter positions, and rally/point/
    possession/team-touch identifiers. Each row includes ``source_file``.

    Skips timestamps, video times, coordinates, lineup shirt numbers/player IDs,
    custom/special codes, and blocker/receiver counts. Match-level date, comments,
    set-score summaries, and match results are not parsed. All scout events are
    retained so rally and possession context is available before filtering.
    """
    content = _read_dvw_content(file_path)
    play_data: _PlayData = {
        "match_id": generate_match_id(content),
        "teams": extract_teams(content),
        "players": extract_players(content),
        "attack_combinations": extract_attack_combinations(content),
        "setter_calls": extract_setter_calls(content),
        "plays": _extract_plays(content, analysis_only=True),
    }
    plays = _enrich_plays(content, play_data, analysis_only=True)
    source_file = str(file_path)
    for play in plays:
        play["source_file"] = source_file
    return plays


def read_raw_plays(file_path: str) -> list[dict[str, Any]]:
    """Read scout rows using ``extract_plays()``, adding ``source_file``.

    Returns raw codes, scout columns, event flags, line numbers, event datetimes,
    and running scores. Numeric scout strings are not normalized. Team/player
    names, decoded skills, and derived rally/point/possession IDs are not added.
    """
    plays = extract_plays(_read_dvw_content(file_path))
    source_file = str(file_path)
    for play in plays:
        play["source_file"] = source_file
    return plays
