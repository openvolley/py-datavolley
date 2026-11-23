"""Indoor VolleyStation JSON reader using the same output schema as DVW.

Format conversions follow openvolley/datavolley's R/volleystation.R.
VolleyStation event scores and lineups remain authoritative, including corrections.
"""

import hashlib
import json
import re
from bisect import bisect_right
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from datavolley.core.code import (
    _EVALUATIONS,
    _decode_num_players,
    _decode_special_code,
    extract_skill_subtype,
    extract_skill_type,
)
from datavolley.core.coordinates import dv_xy2index
from datavolley.types import MatchData, normalize_play
from datavolley.types.plays import _to_float, _to_int, _to_str
from datavolley.utils.metadata import (
    _assign_play_phases,
    _assign_team_touch_ids,
    get_match_result,
)

_SKILLS = {
    "S": "Serve",
    "R": "Reception",
    "E": "Set",
    "A": "Attack",
    "B": "Block",
    "D": "Dig",
    "F": "Freeball",
}
_ROLES = ("libero", "outside", "opposite", "middle", "setter", "unknown")
_SUBTYPES = {
    "Reception": {
        "L": "On left",
        "R": "On right",
        "W": "Low",
        "O": "Overhand",
        "M": "Middle line",
    },
    "Set": {
        "1": "1 hand set",
        "2": "2 hands set",
        "3": "Bump set",
        "4": "Other set",
        "5": "Underhand set",
    },
    "Block": {"A": "Block assist", "T": "Block attempt"},
    "Dig": {
        "S": "On spike",
        "C": "Spike cover",
        "B": "After block",
        "E": "Emergency",
        "T": "Tip",
        "P": "Soft spike",
        "H": "Hard spike",
    },
}


def _records(value: Any) -> list[dict[str, Any]]:
    # Some exports wrap a roster or other collection in an extra singleton list.
    while isinstance(value, list) and len(value) == 1 and isinstance(value[0], list):
        value = value[0]
    if not value:
        return []
    if isinstance(value, dict):
        return [value]
    return value


def _datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _clock(value: Any, created: datetime | None) -> datetime | None:
    offset = _to_float(value)
    return (
        created + timedelta(seconds=offset / 10)
        if created is not None and offset is not None
        else None
    )


def _video_time(value: Any) -> int | None:
    value = _to_float(value)
    return round(value / 10) if value is not None else None


def _positions(value: Any) -> list[int | None]:
    if isinstance(value, dict):
        return [_to_int(value.get(str(i))) for i in range(1, 7)]
    return [_to_int(value[i]) if value and i < len(value) else None for i in range(6)]


def _line_numbers(content: str) -> dict[str, int | None]:
    newlines = [match.start() for match in re.finditer("\n", content)]
    result = {}
    for match in re.finditer(r'"_id"\s*:\s*("(?:[^"\\]|\\.)*")', content):
        identifier = json.loads(match[1])
        result[identifier] = (
            None if identifier in result else bisect_right(newlines, match.start()) + 1
        )
    return result


def _roster(team: dict, name: str) -> list[dict[str, Any]]:
    result = []
    liberos = team.get("libero") or []
    while (
        isinstance(liberos, list) and len(liberos) == 1 and isinstance(liberos[0], list)
    ):
        liberos = liberos[0]
    if not isinstance(liberos, list):
        liberos = [liberos]
    liberos = {_to_int(number) for number in liberos}
    for player in _records(team.get("players")):
        number = _to_str(player.get("shirtNumber")) or "0"
        first = _to_str(player.get("firstName"))
        last = _to_str(player.get("lastName"))
        position = _to_int(player.get("position"))
        role = (
            _ROLES[position]
            if position is not None and 0 <= position < len(_ROLES)
            else None
        )
        if role is None and _to_int(number) in liberos:
            role = "libero"
        result.append(
            {
                "team": name,
                "player_number": number,
                "player_id": _to_str(player.get("code")) or f"player_{number}",
                "last_name": last,
                "first_name": first,
                "role": role,
                "full_name": " ".join(part for part in (first, last) if part) or None,
            }
        )
    return result


def _zone_index(start: dict) -> int | None:
    zone = _to_int(start.get("zone"))
    centers = {
        1: (3, 1),
        2: (3, 3),
        3: (2, 3),
        4: (1, 3),
        5: (1, 1),
        6: (2, 1),
        7: (1, 2),
        8: (2, 2),
        9: (3, 2),
    }
    if zone not in centers:
        return None
    x, y = centers[zone]
    subzone = (_to_str(start.get("subZone")) or "").upper()
    x += 0.25 if subzone in {"A", "B"} else -0.25 if subzone in {"C", "D"} else 0
    y += -0.25 if subzone in {"A", "D"} else 0.25 if subzone in {"B", "C"} else 0
    return dv_xy2index(x, y)


def _attack_definitions(data: dict) -> list[dict[str, Any]]:
    return [
        {
            "code": _to_str(item.get("code")),
            "zone": _to_int((item.get("start") or {}).get("zone")),
            "position": None,
            "type": _to_str(item.get("hitType")),
            "description": _to_str(item.get("name")),
            "field_5": None,
            "color_code": None,
            "position_code": _zone_index(item.get("start") or {}),
            "set_direction": _to_str(item.get("targetAttacker")),
            "backrow": False,
            "field_10": None,
            # VSM definitions have no raw semicolon-separated DVW columns.
            "raw_data": [],
        }
        for item in _records(data.get("attackCombinations"))
    ]


def _setter_definitions(data: dict) -> list[dict[str, Any]]:
    return [
        {
            "code": _to_str(item.get("code")),
            "field_1": "",
            "description": _to_str(item.get("name")),
            "field_3": None,
            "color_code": None,
            "position_1": None,
            "position_2": None,
            "position_3": None,
            "additional_codes": None,
            "field_9": None,
            "raw_data": [],
            "additional_codes_list": [],
        }
        for item in _records(data.get("setterCalls"))
    ]


def _final_score(match_set: dict) -> tuple[int, int] | None:
    score = match_set.get("score") or {}
    home, away = _to_int(score.get("home")), _to_int(score.get("away"))
    # VS can leave a 0-0 final-score record behind after undoing a completed set.
    if home is None or away is None or (home == 0 and away == 0):
        return None
    return home, away


def load_vsm(file_path: str | Path) -> MatchData:
    """Load an indoor VSM into the existing full-match dictionary schema."""
    try:
        content = Path(file_path).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise FileNotFoundError(f"VSM file not found: {file_path}") from None
    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid VSM JSON in {file_path}: {error.msg} (line {error.lineno})"
        ) from error
    if not isinstance(data, dict):
        raise ValueError(f"VSM file must contain a JSON object: {file_path}")  # noqa: TRY004 - invalid file contents, not an argument type
    sets = _records((data.get("scout") or {}).get("sets"))
    game_type = data.get("gameType")
    if game_type is None and any(
        len(
            ((item.get("startingLineup") or {}).get("home") or {}).get("positions")
            or []
        )
        == 6
        for item in sets
    ):
        game_type = "indoor"
    if game_type != "indoor":
        raise ValueError(
            f"Unsupported VSM gameType {game_type!r}; only indoor is supported: {file_path}"
        )
    team = data.get("team") or {}
    home, away = team.get("home") or {}, team.get("away") or {}
    home_name = _to_str(home.get("name")) or "Home"
    away_name = _to_str(away.get("name")) or "Visiting"
    identity = [
        data.get("startDate"),
        home.get("code"),
        away.get("code"),
        home_name,
        away_name,
        data.get("matchNumber"),
    ]
    identifier = (
        _to_str(data.get("_id"))
        or hashlib.sha256(
            json.dumps(identity, ensure_ascii=False).encode()
        ).hexdigest()[:16]
    )
    set_scores = {}
    for number, match_set in enumerate(sets, 1):
        score = _final_score(match_set)
        if score is not None:
            set_scores[f"team_1_set_{number}"], set_scores[f"team_2_set_{number}"] = (
                score
            )
    match: MatchData = {
        "filename": Path(file_path).stem,
        "match_date": _datetime(data.get("startDate")),
        "match_id": identifier,
        "comments": _to_str(data.get("comment")) or "",
        "teams": {
            "team_1_id": _to_str(home.get("code")),
            "team_1": home_name,
            "team_2_id": _to_str(away.get("code")),
            "team_2": away_name,
        },
        "set_scores": set_scores,
        "players": {
            "home": _roster(home, home_name),
            "visiting": _roster(away, away_name),
        },
        "attack_combinations": _attack_definitions(data),
        "setter_calls": _setter_definitions(data),
        "plays": [],
        "match_result": get_match_result(set_scores),
    }
    match["plays"] = _read_plays(
        sets, match, _datetime(data.get("createdAt")), _line_numbers(content)
    )
    return match


def _coordinates(source: dict) -> dict[str, Any]:
    result = {
        f"{name}_coordinate{suffix}": None
        for name in ("start", "mid", "end")
        for suffix in ("", "_x", "_y")
    }
    path = _records(source.get("travelPath"))
    if not path:
        return result
    if len(path) not in {2, 3}:
        raise ValueError("VSM travelPath must contain 2 or 3 points")
    names = ("start", "end") if len(path) == 2 else ("start", "mid", "end")
    for name, point in zip(names, path, strict=True):
        x, y = _to_float(point.get("x")), _to_float(point.get("y"))
        x = x / 293.3333 + 0.447159 if x is not None else None
        y = y / 297 + 0.469697 if y is not None else None
        result[f"{name}_coordinate_x"], result[f"{name}_coordinate_y"] = x, y
        result[f"{name}_coordinate"] = dv_xy2index(x, y)
    return result


def _row(
    context: dict,
    teams: dict,
    code: str | None,
    prefix: str | None = None,
    **fields: Any,
) -> dict[str, Any]:
    row = {**context, "code": code, **fields}
    if prefix in {"*", "a"}:
        side, number = ("home", 1) if prefix == "*" else ("visiting", 2)
        row.update(
            team=teams[f"team_{number}"],
            team_id=teams[f"team_{number}_id"],
            setter_position=context.get(f"{side}_setter_position"),
        )
    return row


def _token(value: Any, width: int = 1) -> str:
    return (_to_str(value) or "~")[:width].ljust(width, "~")


def _scout_code(source: dict, row: dict) -> str | None:
    if source.get("team") not in {"*", "a"}:
        return None
    number = row["player_number"]
    hit_type = _to_str(source.get("hitType"))
    if hit_type in {None, "~"}:
        hit_type = "H"
    subtype = _to_str(source.get("skillType"))
    if source["skill"] == "A" and subtype in {None, "~"}:
        subtype = "H"
    return (
        source["team"]
        + f"{number if number is not None else 0:02d}"
        + source["skill"]
        + hit_type
        + _token(row["evaluation_code"])
        + _token(source.get("combination"), 2)
        + _token(row["set_type"])
        + _token(row["start_zone"])
        + _token(row["end_zone"])
        + _token(row["end_subzone"])
        + _token(subtype)
        + _token(row["num_players_numeric"])
        + _token(source.get("special"))
        + (_to_str(source.get("custom")) or "")
    ).rstrip("~")


def _skill_row(
    source: dict,
    context: dict,
    match: MatchData,
    previous: dict | None,
    created: datetime | None,
    lines: dict,
) -> dict[str, Any]:
    row = _row(
        context,
        match["teams"],
        None,
        source.get("team"),
        time=_clock(source.get("originalTime"), created),
        video_time=_video_time(source.get("time")),
        file_line_number=lines.get(source.get("_id"), context.get("file_line_number")),
    )
    if _to_str(source.get("invalid")):
        row["code"] = _to_str(source.get("code")) or ">" + str(
            source["invalid"]
        ).strip().lstrip(">")
        return row
    skill = _SKILLS.get(source.get("skill"), source.get("skill"))
    if source.get("skill") not in _SKILLS:
        row.update(code=_to_str(source.get("code")), skill=skill)
        return row
    number = _to_int(source.get("player"))
    if number is not None and not 0 <= number <= 99:
        number = None
    effect = _to_str(source.get("effect"))
    effect = "+" if effect in {None, "~"} else effect
    row.update(
        skill=skill,
        player_number=number,
        evaluation_code=effect,
        evaluation=_EVALUATIONS[skill].get(
            effect, f"Unknown {skill.lower()} evaluation"
        ),
        start_zone=_to_int(source.get("startZone")),
        end_zone=_to_int(source.get("endZone")),
        end_subzone=(_to_str(source.get("endSubZone")) or "").upper() or None,
        num_players_numeric=_to_int(source.get("players")),
        custom_code=_to_str(source.get("custom")),
        **_coordinates(source),
    )
    # VS locations describe each touch; DVW reception/dig locations describe the
    # preceding opponent serve/attack trajectory instead.
    if (
        previous
        and (skill, previous.get("skill"))
        in {("Reception", "Serve"), ("Dig", "Attack")}
        and source.get("team") in {"*", "a"}
        and source["team"] != (previous.get("code") or "")[:1]
    ):
        for key in (
            "start_zone",
            "end_zone",
            "end_subzone",
            *(key for key in row if "coordinate" in key),
        ):
            row[key] = previous.get(key)
    if skill in {"Set", "Block"}:
        # Some VS exports already use endZone/endSubZone for these skills.
        start_zone = _to_int(source.get("startZone"))
        start_subzone = (_to_str(source.get("startSubZone")) or "").upper()
        row.update(
            start_zone=None,
            end_zone=start_zone if start_zone is not None else row["end_zone"],
            end_subzone=start_subzone or row["end_subzone"],
        )
    combination = _to_str(source.get("combination"))
    definitions = (
        match["attack_combinations"] if skill == "Attack" else match["setter_calls"]
    )
    definition = next((item for item in definitions if item["code"] == combination), {})
    row["set_type"] = _to_str(source.get("targetAttacker")) or (
        definition.get("set_direction") if skill == "Attack" else None
    )
    if skill == "Attack":
        row.update(
            attack_code=combination,
            attack_description=definition.get("description", "unknown attack code")
            if combination
            else None,
        )
    elif skill == "Set":
        row.update(
            set_code=combination,
            set_description=definition.get("description", "unknown set code")
            if combination
            else None,
        )
    row["code"] = _scout_code(source, row)
    row["skill_type"] = extract_skill_type(row["code"] or "", skill)
    subtype = _to_str(source.get("skillType"))
    row["skill_subtype"] = (
        _SUBTYPES[skill].get(subtype)
        if subtype and skill in _SUBTYPES
        else extract_skill_subtype(row["code"] or "", skill)
    )
    row["num_players"] = _decode_num_players(skill, row["num_players_numeric"])
    row["special_code"] = _decode_special_code(
        skill, effect, _to_str(source.get("special"))
    )
    row["winning_attack"] = skill == "Attack" and effect == "#"
    return row


def _event_times(events: list[dict]) -> list[dict]:
    times: list[dict] = [{} for _ in events]
    for field in ("time", "originalTime"):
        bounds = []
        for event in events:
            values = [
                _to_float(play.get(field))
                for play in _records((event.get("exchange") or {}).get("plays"))
            ]
            values = [value for value in values if value is not None]
            bounds.append((min(values), max(values)) if values else (None, None))
        next_start: list[float | None] = [None] * len(events)
        following = None
        for i in range(len(events) - 1, -1, -1):
            next_start[i] = following
            if bounds[i][0] is not None:
                following = bounds[i][0]
        previous = None
        for i, (start, end) in enumerate(bounds):
            neighbors = [
                value for value in (previous, next_start[i]) if value is not None
            ]
            start = start if start is not None else min(neighbors, default=None)
            end = end if end is not None else max(neighbors, default=None)
            times[i][field] = {
                "start": start,
                "end": end,
                "timeout": previous if previous is not None else start,
            }
            if bounds[i][1] is not None:
                previous = bounds[i][1]
    return times


def _lineup(source: dict, previous: dict) -> dict:
    result = previous.copy()
    for source_side, side in (("home", "home"), ("away", "visiting")):
        values = source.get(source_side) or {}
        if "positions" in values:
            result.update(
                {
                    f"{side}_p{i}": number
                    for i, number in enumerate(_positions(values["positions"]), 1)
                }
            )
        if "setterAt" in values:
            position = _to_int(values["setterAt"])
            result[f"{side}_setter_position"] = (
                position if position is not None and 1 <= position <= 6 else None
            )
    return result


def _lineup_codes(
    current: dict, previous: dict, *, initial: bool
) -> list[tuple[str, str]]:
    result = []
    for side, prefix in (("home", "*"), ("visiting", "a")):
        position = current.get(f"{side}_setter_position")
        old_position = previous.get(f"{side}_setter_position")
        number = current.get(f"{side}_p{position}")
        old_number = previous.get(f"{side}_p{old_position}")
        suffix = ">LUp" if initial else ""
        if number is not None and (initial or number != old_number):
            result.append((f"{prefix}P{number:02d}{suffix}", prefix))
        if position is not None and (initial or position != old_position):
            result.append((f"{prefix}z{position}{suffix}", prefix))
    return result


def _read_plays(
    sets: list[dict], match: MatchData, created: datetime | None, lines: dict
) -> list[dict[str, Any]]:
    result = []
    point_id = 0
    teams = match["teams"]
    for set_number, match_set in enumerate(sets, 1):
        current = _lineup(match_set.get("startingLineup") or {}, {})
        events = _records(match_set.get("events"))
        if not events and current:
            events = [{"lineup": match_set.get("startingLineup")}]
        timings = _event_times(events)
        last_scores = (0, 0)
        rally = 0
        context = {}
        for event_index, (event, timing) in enumerate(
            zip(events, timings, strict=True)
        ):
            previous = current
            current = _lineup(event.get("lineup") or {}, previous)
            substitutions = _records(event.get("substitution"))
            for sub in substitutions:
                side = {"*": "home", "a": "visiting"}.get(sub.get("team"))
                outgoing, incoming = (
                    _to_int(sub.get("playerOut")),
                    _to_int(sub.get("playerIn")),
                )
                if (
                    side
                    and incoming is not None
                    and incoming
                    not in [current.get(f"{side}_p{i}") for i in range(1, 7)]
                ):
                    for i in range(1, 7):
                        if (
                            outgoing is not None
                            and current.get(f"{side}_p{i}") == outgoing
                        ):
                            current[f"{side}_p{i}"] = incoming
            exchange = event.get("exchange") or {}
            sources = _records(exchange.get("plays"))
            winner = exchange.get("point")
            if sources or winner in {"*", "a"}:
                rally += 1
            score = event.get("score") or {}
            scores = tuple(_to_int(score.get(side)) for side in ("home", "away"))
            scores = tuple(
                value
                if value is not None
                else last_scores[i] + int(winner == ("*", "a")[i])
                for i, value in enumerate(scores)
            )
            serving = next(
                (
                    source.get("team")
                    for source in sources
                    if source.get("skill") == "S"
                ),
                None,
            )
            serving_number = {"*": 1, "a": 2}.get(serving)
            winner_number = {"*": 1, "a": 2}.get(winner)
            context = {
                "match_id": match["match_id"],
                "set_number": set_number,
                "point_id": point_id,
                "rally_number": max(rally, 1),
                "home_team": teams["team_1"],
                "visiting_team": teams["team_2"],
                "home_team_id": teams["team_1_id"],
                "visiting_team_id": teams["team_2_id"],
                "home_team_score": scores[0],
                "visiting_team_score": scores[1],
                "home_score_start_of_point": last_scores[0],
                "visiting_score_start_of_point": last_scores[1],
                "point_won_by": teams.get(f"team_{winner_number}"),
                "serving_team": teams.get(f"team_{serving_number}"),
                "receiving_team": teams.get(f"team_{3 - serving_number}")
                if serving_number is not None
                else None,
                "time": _clock(timing["originalTime"]["start"], created),
                "video_time": _video_time(timing["time"]["start"]),
                "file_line_number": lines.get(event.get("_id")),
                **current,
            }
            rows = [
                _row(context, teams, code, prefix)
                for code, prefix in _lineup_codes(
                    current, previous, initial=event_index == 0
                )
            ]
            for timeout in _records(event.get("timeout")):
                prefix = timeout.get("team")
                rows.append(
                    _row(
                        context,
                        teams,
                        f"{prefix}T" if prefix in {"*", "a"} else None,
                        prefix,
                        skill="Timeout",
                        timeout=True,
                        time=_clock(timing["originalTime"]["timeout"], created),
                        video_time=_video_time(timing["time"]["timeout"]),
                    )
                )
            for sub in substitutions:
                prefix = sub.get("team")
                outgoing, incoming = (
                    _to_int(sub.get("playerOut")),
                    _to_int(sub.get("playerIn")),
                )
                code = (
                    f"{prefix}c{outgoing if outgoing is not None else 0:02d}:{incoming if incoming is not None else 0:02d}"
                    if prefix in {"*", "a"}
                    else None
                )
                rows.append(_row(context, teams, code, prefix, substitution=True))
            skill_previous = None
            for source in sources:
                row = _skill_row(source, context, match, skill_previous, created, lines)
                rows.append(row)
                skill_previous = row
            point_prefix = winner if winner in {"*", "a"} else None
            if point_prefix is None and scores != last_scores:
                point_prefix = "*" if scores[0] != last_scores[0] else "a"
            if point_prefix is not None:
                rows.append(
                    _row(
                        context,
                        teams,
                        f"{point_prefix}p{scores[0]:02d}:{scores[1]:02d}",
                        point_prefix,
                        skill="Point",
                        point=True,
                        time=_clock(timing["originalTime"]["end"], created),
                        video_time=_video_time(timing["time"]["end"]),
                    )
                )
            if not rows:
                rows.append(_row(context, teams, None))
            possession, last_team = 0, None
            for row in rows:
                if row.get("skill") in _SKILLS.values():
                    if (
                        last_team is not None
                        and row.get("team") is not None
                        and row["team"] != last_team
                    ):
                        possession += 1
                    last_team = row.get("team")
                row["possession_number"] = possession
            result.extend(rows)
            last_scores = scores
            point_id += 1
        final = _final_score(match_set)
        if events and final is not None:
            context = {
                **context,
                "point_id": point_id,
                "home_team_score": final[0],
                "visiting_team_score": final[1],
                "home_score_start_of_point": last_scores[0],
                "visiting_score_start_of_point": last_scores[1],
                "point_won_by": None,
                "serving_team": None,
                "receiving_team": None,
                "possession_number": 0,
                "time": result[-1].get("time"),
                "video_time": result[-1].get("video_time"),
            }
            result.append(_row(context, teams, f"**{set_number}set", end_of_set=True))
            point_id += 1
    _assign_team_touch_ids(result)
    _assign_play_phases(result)
    servers = {
        row["point_id"]: (row.get("code") or "")[:1]
        for row in result
        if row.get("skill") == "Serve"
    }
    lookups = {}
    for side in ("home", "visiting"):
        lookup = {}
        for player in match["players"][side]:
            number = _to_int(player["player_number"])
            if number is not None:
                lookup.setdefault(number, player)
        lookups[side] = lookup
    for row in result:
        prefix = (row.get("code") or "")[:1]
        side = {"*": "home", "a": "visiting"}.get(prefix)
        player = (
            lookups[side].get(row.get("player_number"), {})
            if side and row.get("player_number") is not None
            else {}
        )
        row.update(
            player_id=player.get("player_id"), player_name=player.get("full_name")
        )
        for side in ("home", "visiting"):
            for position in range(1, 7):
                row[f"{side}_player_id{position}"] = (
                    lookups[side]
                    .get(row.get(f"{side}_p{position}"), {})
                    .get("player_id")
                )
        if side is not None and servers.get(row["point_id"]) in {"*", "a"}:
            serving = prefix == servers[row["point_id"]]
            # DV point_phase describes the team scoring, not the team touching:
            # an error by the serving team therefore counts as a sideout.
            if row.get("evaluation") in {"Ace", "Winning attack", "Winning block"}:
                row["point_phase"] = "Breakpoint" if serving else "Sideout"
            elif row.get("evaluation") in {"Error", "Blocked", "Invasion"}:
                row["point_phase"] = "Sideout" if serving else "Breakpoint"
            if row.get("skill") == "Attack" and row["phase"] == "Transition":
                row["attack_phase"] = (
                    "Transition breakpoint" if serving else "Transition sideout"
                )
        if row.get("skill") == "Attack" and row["phase"] == "Reception":
            row["attack_phase"] = "Reception"
    return [normalize_play(row, preserve_ids=True) for row in result]
