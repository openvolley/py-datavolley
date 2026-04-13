"""Helper functions for attack code descriptions and mappings."""

from __future__ import annotations

from typing import Literal, overload

AttackCode = Literal[
    "X5",
    "X6",
    "X8",
    "X0",
    "XP",
    "X3",
    "X1",
    "X2",
    "X7",
    "XO",
    "X9",
    "CB",
    "CD",
    "V5",
    "V6",
    "V8",
    "V0",
    "VP",
    "V3",
    "VO",
    "C0",
    "C5",
    "C6",
    "C8",
    "CF",
    "PP",
    "P2",
    "PR",
]

_DESC_MAP: dict[str, str] = {
    "X5": "Shoot in 4",
    "X6": "Shoot in 2",
    "X8": "Shoot in 1",
    "X0": "Shoot in 5",
    "XP": "Pipe",
    "X3": "Meter ball in 3",
    "X1": "Quick",
    "X2": "Quick set behind",
    "X7": "Quick - push",
    "XO": "Pipe behind",
    "X9": "Interval ball in 4",
    "CB": "Slide close",
    "CD": "Slide close",
    "V5": "High set in 4",
    "V6": "High set in 2",
    "V8": "High set in 1",
    "V0": "High set in 5",
    "VP": "High Pipe",
    "V3": "High set in 3",
    "VO": "High pipe behind",
    "C0": "Medium ball in 5",
    "C5": "Medium ball in 4",
    "C6": "Medium ball in 2",
    "C8": "Medium ball in 1",
    "CF": "Slide far",
    "PP": "Setter tip",
    "P2": "Second hit to opponent court",
    "PR": "Attack on opponent freeball",
}


@overload
def dv_attack_code2desc(code: AttackCode) -> str: ...


@overload
def dv_attack_code2desc(code: str) -> str | None: ...


@overload
def dv_attack_code2desc(code: list[str]) -> dict[str, str | None]: ...


def dv_attack_code2desc(
    code: str | list[str],
) -> str | None | dict[str, str | None]:
    """
    Get nominal descriptions for standard attack codes.

    Args:
        code: Attack code string or list of attack codes ("X5", "VP", etc.)

    Returns:
        If single code: description string
        If list of codes: dict mapping codes to descriptions
        Unrecognized codes will have None as description

    Examples:
        >>> dv_attack_code2desc("X5")
        'Shoot in 4'
        >>> dv_attack_code2desc(["X5", "X7", "PP"])
        {'X5': 'Shoot in 4', 'X7': 'Quick - push', 'PP': 'Setter tip'}
    """
    if isinstance(code, str):
        return _DESC_MAP.get(code)
    return {c: _DESC_MAP.get(c) for c in code}
