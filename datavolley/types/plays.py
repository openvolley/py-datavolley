from __future__ import annotations

import re
from collections.abc import Callable
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
    "video_time": _to_int,
    "code": _to_str,
    "team": _to_str,
    "player_number": _to_int,
    "player_name": _to_str,
    "player_id": _to_int,
    "skill": _to_str,
    "skill_subtype": _to_str,
    "skill_type": _to_str,
    "evaluation_code": _to_str,
    "setter_position": _to_int,
    "attack_code": _to_str,
    "set_code": _to_str,
    "set_type": _to_str,
    "start_zone": _to_int,
    "end_zone": _to_int,
    "end_subzone": _to_str,
    "num_players_numeric": _to_int,
    "home_team_score": _to_int,
    "visiting_team_score": _to_int,
    "home_setter_position": _to_int,
    "visiting_setter_position": _to_int,
    "custom_code": _to_str,
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
    "mid_coordinate": _to_str,
    "end_coordinate": _to_str,
    "point_phase": _to_str,
    "attack_phase": _to_str,
    "start_coordinate_x": _to_float,
    "start_coordinate_y": _to_float,
    "mid_coordinate_x": _to_float,
    "mid_coordinate_y": _to_float,
    "end_coordinate_x": _to_float,
    "end_coordinate_y": _to_float,
    "set_number": _to_int,
    "home_team": _to_str,
    "visiting_team": _to_str,
    "home_team_id": _to_int,
    "visiting_team_id": _to_int,
    "point_won_by": _to_str,
    "serving_team": _to_str,
    "receiving_team": _to_str,
    "rally_number": _to_int,
    "possession_number": _to_int,
}


def normalize_play(play: dict[str, Any]) -> dict[str, Any]:
    normalized = {name: coercer(play.get(name)) for name, coercer in _COERCERS.items()}

    for key, value in play.items():
        if key not in _COERCERS:
            normalized[key] = value

    if normalized["player_name"] is None and normalized["player_number"] is not None:
        normalized["player_name"] = f"Player {normalized['player_number']}"

    if normalized["code"]:
        code_start_zone, code_end_zone, code_end_subzone = _extract_zones_from_code(
            normalized["code"]
        )
        if normalized["start_zone"] is None:
            normalized["start_zone"] = code_start_zone
        if normalized["end_zone"] is None:
            normalized["end_zone"] = code_end_zone
        if normalized["end_subzone"] is None:
            normalized["end_subzone"] = code_end_subzone

    return normalized
