from __future__ import annotations

from typing import TypedDict


class ParsedPlayCode(TypedDict):
    code: str
    team: str | None
    player_number: int | None
    player_name: str | None
    player_id: str | None
    skill: str | None
    skill_type: str | None
    evaluation_code: str | None
    evaluation: str | None
    set_code: str | None
    set_type: str | None
    set_description: str | None
    start_zone: str | None
    end_zone: str | None
    end_subzone: str | None
    end_cone: int | None
    num_players_numeric: int | None
    num_players: str | None
    skill_subtype: str | None
    attack_code: str | None
    attack_description: str | None
    special_code: str | None
    custom_code: str | None
