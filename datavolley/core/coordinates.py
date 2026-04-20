from __future__ import annotations


def dv_index2xy(index: str | int | None) -> tuple[float, float] | None:
    """Convert a DataVolley coordinate index to (x, y) court coordinates.

    The coordinate index is a 4-character string from a DVW file (e.g. "0431")
    or the integer equivalent (e.g. 431). Values containing "-" (like "-1-1")
    or empty strings indicate missing coordinates.

    The grid is 100 x 101 = 10100 cells. Court coordinates use the convention:
    - X: ~0.125 to ~3.875 (court sidelines at 0.5 and 3.5)
    - Y: ~0.074 to ~6.926 (baselines at 0.5 and 6.5, net at 3.5)

    Args:
        index: Coordinate index string or integer (range 1-10100).

    Returns:
        Tuple of (x, y) court coordinates, or None if index is invalid/missing.
    """
    if index is None:
        return None

    index_str = str(index).strip()
    if not index_str or "-" in index_str:
        return None

    try:
        idx = int(index_str)
    except (ValueError, TypeError):
        return None

    if idx < 1 or idx > 10100:
        return None

    i = (idx - 1) % 100 + 1
    j = (idx - 1) // 100 + 1

    x = 0.5 + 3.0 * (i - 10.5) / 80
    y = 0.5 + 6.0 * (j - 10.5) / 81

    return (x, y)
