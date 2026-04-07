from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    field_validator,
    model_validator,
)


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


class ValidationMode(str, Enum):
    LENIENT = "lenient"
    STRICT = "strict"


class ParseIssue(BaseModel):
    index: int | None = None
    field: str
    message: str
    value: Any = None


class PlayRaw(BaseModel):
    model_config = ConfigDict(extra="allow")

    match_id: str | int | None = None
    video_time: str | int | float | None = None
    code: str | None = None
    team: str | None = None
    player_number: str | int | None = None
    player_name: str | None = None
    player_id: str | int | None = None
    skill: str | None = None
    skill_subtype: str | None = None
    skill_type: str | None = None
    evaluation_code: str | None = None
    setter_position: str | int | None = None
    attack_code: str | None = None
    set_code: str | None = None
    set_type: str | None = None
    start_zone: str | int | None = None
    end_zone: str | int | None = None
    end_subzone: str | None = None
    num_players_numeric: str | int | None = None
    home_team_score: str | int | None = None
    visiting_team_score: str | int | None = None
    home_setter_position: str | int | None = None
    visiting_setter_position: str | int | None = None
    custom_code: str | None = None
    home_p1: str | int | None = None
    home_p2: str | int | None = None
    home_p3: str | int | None = None
    home_p4: str | int | None = None
    home_p5: str | int | None = None
    home_p6: str | int | None = None
    visiting_p1: str | int | None = None
    visiting_p2: str | int | None = None
    visiting_p3: str | int | None = None
    visiting_p4: str | int | None = None
    visiting_p5: str | int | None = None
    visiting_p6: str | int | None = None
    start_coordinate: str | int | None = None
    mid_coordinate: str | int | None = None
    end_coordinate: str | int | None = None
    point_phase: str | None = None
    attack_phase: str | None = None
    start_coordinate_x: str | int | float | None = None
    start_coordinate_y: str | int | float | None = None
    mid_coordinate_x: str | int | float | None = None
    mid_coordinate_y: str | int | float | None = None
    end_coordinate_x: str | int | float | None = None
    end_coordinate_y: str | int | float | None = None
    set_number: str | int | None = None
    home_team: str | None = None
    visiting_team: str | None = None
    home_team_id: str | int | None = None
    visiting_team_id: str | int | None = None
    point_won_by: str | None = None
    serving_team: str | None = None
    receiving_team: str | None = None
    rally_number: str | int | None = None
    possession_number: str | int | None = None


class PlayNormalized(BaseModel):
    model_config = ConfigDict(extra="allow")

    match_id: str | None = None
    video_time: int | None = None
    code: str | None = None
    team: str | None = None
    player_number: int | None = None
    player_name: str | None = None
    player_id: int | None = None
    skill: str | None = None
    skill_subtype: str | None = None
    skill_type: str | None = None
    evaluation_code: str | None = None
    setter_position: int | None = None
    attack_code: str | None = None
    set_code: str | None = None
    set_type: str | None = None
    start_zone: int | None = None
    end_zone: int | None = None
    end_subzone: str | None = None
    num_players_numeric: int | None = None
    home_team_score: int | None = None
    visiting_team_score: int | None = None
    home_setter_position: int | None = None
    visiting_setter_position: int | None = None
    custom_code: str | None = None
    home_p1: int | None = None
    home_p2: int | None = None
    home_p3: int | None = None
    home_p4: int | None = None
    home_p5: int | None = None
    home_p6: int | None = None
    visiting_p1: int | None = None
    visiting_p2: int | None = None
    visiting_p3: int | None = None
    visiting_p4: int | None = None
    visiting_p5: int | None = None
    visiting_p6: int | None = None
    start_coordinate: str | None = None
    mid_coordinate: str | None = None
    end_coordinate: str | None = None
    point_phase: str | None = None
    attack_phase: str | None = None
    start_coordinate_x: float | None = None
    start_coordinate_y: float | None = None
    mid_coordinate_x: float | None = None
    mid_coordinate_y: float | None = None
    end_coordinate_x: float | None = None
    end_coordinate_y: float | None = None
    set_number: int | None = None
    home_team: str | None = None
    visiting_team: str | None = None
    home_team_id: int | None = None
    visiting_team_id: int | None = None
    point_won_by: str | None = None
    serving_team: str | None = None
    receiving_team: str | None = None
    rally_number: int | None = None
    possession_number: int | None = None

    @field_validator(
        "video_time",
        "player_number",
        "player_id",
        "setter_position",
        "start_zone",
        "end_zone",
        "num_players_numeric",
        "home_team_score",
        "visiting_team_score",
        "home_setter_position",
        "visiting_setter_position",
        "home_p1",
        "home_p2",
        "home_p3",
        "home_p4",
        "home_p5",
        "home_p6",
        "visiting_p1",
        "visiting_p2",
        "visiting_p3",
        "visiting_p4",
        "visiting_p5",
        "visiting_p6",
        "set_number",
        "home_team_id",
        "visiting_team_id",
        "rally_number",
        "possession_number",
        mode="before",
    )
    @classmethod
    def _normalize_int(cls, value: Any) -> int | None:
        return _to_int(value)

    @field_validator(
        "start_coordinate_x",
        "start_coordinate_y",
        "mid_coordinate_x",
        "mid_coordinate_y",
        "end_coordinate_x",
        "end_coordinate_y",
        mode="before",
    )
    @classmethod
    def _normalize_float(cls, value: Any) -> float | None:
        return _to_float(value)

    @field_validator(
        "match_id",
        "code",
        "team",
        "player_name",
        "skill",
        "skill_subtype",
        "skill_type",
        "evaluation_code",
        "attack_code",
        "set_code",
        "set_type",
        "end_subzone",
        "custom_code",
        "start_coordinate",
        "mid_coordinate",
        "end_coordinate",
        "point_phase",
        "attack_phase",
        "home_team",
        "visiting_team",
        "point_won_by",
        "serving_team",
        "receiving_team",
        mode="before",
    )
    @classmethod
    def _normalize_str(cls, value: Any) -> str | None:
        return _to_str(value)

    @model_validator(mode="after")
    def _fill_derived_fields(self) -> PlayNormalized:
        if self.player_name is None and self.player_number is not None:
            self.player_name = f"Player {self.player_number}"

        if self.code:
            code_start_zone, code_end_zone, code_end_subzone = _extract_zones_from_code(
                self.code
            )
            if self.start_zone is None:
                self.start_zone = code_start_zone
            if self.end_zone is None:
                self.end_zone = code_end_zone
            if self.end_subzone is None:
                self.end_subzone = code_end_subzone

        return self


def _issues_from_validation_error(
    error: ValidationError, index: int
) -> list[ParseIssue]:
    issues: list[ParseIssue] = []
    for item in error.errors():
        location = item.get("loc", ())
        field = str(location[0]) if location else "play"
        issues.append(
            ParseIssue(
                index=index,
                field=field,
                message=item.get("msg", "Invalid value"),
                value=item.get("input"),
            )
        )
    return issues


def validate_and_normalize_plays(
    plays: list[dict[str, Any]],
    mode: ValidationMode | str = ValidationMode.LENIENT,
    normalize: bool = False,
) -> tuple[list[dict[str, Any]], list[ParseIssue]]:
    validation_mode = mode if isinstance(mode, ValidationMode) else ValidationMode(mode)

    parsed: list[dict[str, Any]] = []
    issues: list[ParseIssue] = []

    for index, play in enumerate(plays):
        if normalize:
            model_cls: type[BaseModel] = PlayNormalized
        else:
            model_cls = PlayRaw

        try:
            model = model_cls.model_validate(play)
            if normalize:
                parsed.append(model.model_dump())
            else:
                parsed.append(play)
        except ValidationError as error:
            issues.extend(_issues_from_validation_error(error, index))

            if validation_mode == ValidationMode.STRICT:
                raise

            parsed.append(play)

    return parsed, issues
