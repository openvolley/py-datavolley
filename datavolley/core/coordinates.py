# datavolley/core/coordinates.py

import math
from typing import List, Tuple, Union


def dv_index2xy(
    i: Union[int, List[int]],
) -> Union[Tuple[float, float], List[Tuple[float, float]]]:
    """
    Converts a given index to x and y coordinates
    based on a specific transformation formula.

    Args:
        i (int or list of ints):
        Index or list of indices to be converted.

    Returns:
        tuple or list of tuples:
        For single index: (x, y) tuple with coordinates.
        For list of indices: List of (x, y) tuples.

    Example:
        index = 150
        coordinates = dv_index2xy(index)
        print(coordinates)
        # Output: (0.5225, 0.34438)

        indices = [1, 50, 150]
        coordinates = dv_index2xy(indices)
        print(coordinates)
        # Output: [(0.14375, -0.2037), (1.86562, -0.2037), (0.5225, 0.34438)]
    """

    def _calculate_xy(index):
        """Calculate x, y coordinates for a single index."""
        if index is None:
            return None

        try:
            index = int(index)
        except (ValueError, TypeError):
            return None

        x = ((index - 1 - math.floor((index - 1) / 100) * 100) / 99) * 3.7125 + 0.14375
        y = (math.floor((index - 1) / 100) / 100) * 7.4074 - 0.2037
        return (float(x), float(y))

    # Handle single index
    if isinstance(i, (int, str)) or i is None:
        return _calculate_xy(i)

    # Handle list of indices
    if isinstance(i, (list, tuple)):
        return [_calculate_xy(index) for index in i]

    # Handle single index passed as other types
    return _calculate_xy(i)
