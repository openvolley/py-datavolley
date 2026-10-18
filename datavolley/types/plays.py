from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime
from typing import Any


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if re.fullmatch(r"-?\d+", stripped):
            return int(stripped)
    return None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def _to_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


def _to_datetime(value: Any) -> datetime | None:
    return value if isinstance(value, datetime) else None


def _extract_zones_from_code(
    code: str | None,
) -> tuple[int | None, int | None, str | None]:
    if not code:
        return (None, None, None)

    start_zone = None
    end_zone = None
    end_subzone = None

    if len(code) > 9 and code[9].isdigit():
        start_zone = int(code[9])
    if len(code) > 10 and code[10].isdigit():
        end_zone = int(code[10])
    if len(code) > 11 and code[11] != "~":
        end_subzone = code[11]

    return (start_zone, end_zone, end_subzone)


# Field name -> type coercer, in output field order.
_COERCERS: dict[str, Callable[[Any], Any]] = {
    "match_id": _to_str,
    "home_team": _to_str,
    "home_team_id": _to_int,
    "visiting_team": _to_str,
    "visiting_team_id": _to_int,
    "point_id": _to_int,
    "team_touch_id": _to_int,
    "time": _to_datetime,
    "video_time": _to_int,
    "code": _to_str,
    "team": _to_str,
    "team_id": _to_int,
    "player_number": _to_int,
    "player_name": _to_str,
    "player_id": _to_int,
    "skill": _to_str,
    "skill_type": _to_str,
    "evaluation_code": _to_str,
    "evaluation": _to_str,
    "attack_code": _to_str,
    "attack_description": _to_str,
    "set_code": _to_str,
    "set_description": _to_str,
    "set_type": _to_str,
    "start_zone": _to_int,
    "end_zone": _to_int,
    "end_subzone": _to_str,
    "end_cone": _to_int,
    "skill_subtype": _to_str,
    "num_players_numeric": _to_int,
    "num_players": _to_str,
    "special_code": _to_str,
    "timeout": bool,
    "end_of_set": bool,
    "substitution": bool,
    "point": bool,
    "home_team_score": _to_int,
    "visiting_team_score": _to_int,
    "home_score_start_of_point": _to_int,
    "visiting_score_start_of_point": _to_int,
    "home_player_id1": _to_int,
    "home_player_id2": _to_int,
    "home_player_id3": _to_int,
    "home_player_id4": _to_int,
    "home_player_id5": _to_int,
    "home_player_id6": _to_int,
    "visiting_player_id1": _to_int,
    "visiting_player_id2": _to_int,
    "visiting_player_id3": _to_int,
    "visiting_player_id4": _to_int,
    "visiting_player_id5": _to_int,
    "visiting_player_id6": _to_int,
    "home_p1": _to_int,
    "home_p2": _to_int,
    "home_p3": _to_int,
    "home_p4": _to_int,
    "home_p5": _to_int,
    "home_p6": _to_int,
    "visiting_p1": _to_int,
    "visiting_p2": _to_int,
    "visiting_p3": _to_int,
    "visiting_p4": _to_int,
    "visiting_p5": _to_int,
    "visiting_p6": _to_int,
    "start_coordinate": _to_str,
    "start_coordinate_x": _to_float,
    "start_coordinate_y": _to_float,
    "mid_coordinate": _to_str,
    "mid_coordinate_x": _to_float,
    "mid_coordinate_y": _to_float,
    "end_coordinate": _to_str,
    "end_coordinate_x": _to_float,
    "end_coordinate_y": _to_float,
    "point_phase": _to_str,
    "attack_phase": _to_str,
    "set_number": _to_int,
    "point_won_by": _to_str,
    "winning_attack": bool,
    "serving_team": _to_str,
    "receiving_team": _to_str,
    "phase": _to_str,
    "home_setter_position": _to_int,
    "visiting_setter_position": _to_int,
    "custom_code": _to_str,
    "file_line_number": _to_int,
    "rally_number": _to_int,
    "possession_number": _to_int,
    "setter_position": _to_int,
}


# Keep the analysis schema in the same column order as the full play schema.
_ANALYSIS_COERCERS = {
    name: coercer
    for name, coercer in _COERCERS.items()
    if name
    not in {
        "time",
        "video_time",
        "custom_code",
        "special_code",
        "num_players",
        "num_players_numeric",
    }
    and "coordinate" not in name
    and not name.startswith(("home_p", "visiting_p"))
}


def normalize_play(play: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_play_fields(play, _COERCERS)
    for key, value in play.items():
        if key not in _COERCERS:
            normalized[key] = value
    return normalized


def _normalize_analysis_play(play: dict[str, Any]) -> dict[str, Any]:
    return _normalize_play_fields(play, _ANALYSIS_COERCERS)


def _normalize_play_fields(
    play: dict[str, Any], coercers: dict[str, Callable[[Any], Any]]
) -> dict[str, Any]:
    normalized = {name: coercer(play.get(name)) for name, coercer in coercers.items()}

    if normalized["player_name"] is None and normalized["player_number"] is not None:
        normalized["player_name"] = f"Player {normalized['player_number']}"

    if normalized["code"]:
        code_start_zone, code_end_zone, code_end_subzone = _extract_zones_from_code(
            normalized["code"]
        )
        if normalized["start_zone"] is None:
            normalized["start_zone"] = code_start_zone
        if normalized["end_zone"] is None and normalized["end_cone"] is None:
            normalized["end_zone"] = code_end_zone
        if normalized["end_subzone"] is None and normalized["end_cone"] is None:
            normalized["end_subzone"] = code_end_subzone

    return normalized
