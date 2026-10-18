from __future__ import annotations

from datetime import datetime
from typing import Any, NotRequired, TypedDict


class _PlayData(TypedDict):
    match_id: str
    teams: dict[str, str | None]
    players: dict[str, list[dict[str, Any]]]
    attack_combinations: list[dict[str, Any]]
    setter_calls: list[dict[str, Any]]
    plays: list[dict[str, Any]]


class MatchData(_PlayData):
    filename: str
    match_date: datetime | None
    comments: str
    set_scores: dict[str, int]
    match_result: NotRequired[dict[str, Any]]
