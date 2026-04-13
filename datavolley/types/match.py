from __future__ import annotations

from datetime import datetime
from typing import Any, NotRequired, TypedDict


class MatchData(TypedDict):
    filename: str
    match_date: datetime | None
    match_id: str
    comments: str
    teams: dict[str, str | None]
    set_scores: dict[str, int]
    match_result: NotRequired[dict[str, Any]]
    players: dict[str, list[dict[str, Any]]]
    attack_combinations: list[dict[str, Any]]
    setter_calls: list[dict[str, Any]]
    plays: list[dict[str, Any]]
