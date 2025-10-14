"""
Volleyball court plotting functions for datavolley.

This module provides functions to draw volleyball courts and visualize play data,
similar to the R datavolley package's ggcourt() function.

Main functions:
- dv_court(): Draw a volleyball court with optional data points
- dv_heatmap(): Create heatmaps showing point density across court zones
"""

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

try:
    from shapely.geometry import Point, Polygon

    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def dv_court(
    half: bool = False,
    court_color: str = "white",
    line_color: str = "black",
    zones: bool = False,
    zone_labels: bool = False,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """
    Draw a volleyball court.

    Args:
        half: If True, draw only the top half of the court (default: False)
        court_color: Background color of the court (default: "white")
        line_color: Color of the court lines (default: "black")
        zones: If True, draw zone dividers (default: False)
        zone_labels: If True, add zone number labels (default: False)
        ax: Matplotlib axes to draw on. If None, creates new figure

    Returns:
        matplotlib.axes.Axes: The axes with the court drawn

    Example:
        >>> import matplotlib.pyplot as plt
        >>> from datavolley.plot import dv_court
        >>> ax = dv_court(zones=True, zone_labels=True)
        >>> plt.show()
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(4, 7))

    ax.set_facecolor(court_color)

    if half:
        _draw_half_court(ax, line_color, zones)
        y_min, y_max = 3.5, 7
    else:
        _draw_full_court(ax, line_color, zones)
        y_min, y_max = 0, 7

    if zone_labels:
        _add_zone_labels(ax, half=half)

    ax.set_xlim(0, 4)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])

    return ax


def dv_heatmap(
    coordinates: List[Tuple[float, float]],
    zones: bool = True,
    subzones: bool = False,
    half: bool = False,
    color_low: str = "white",
    color_mid: str = "lightblue",
    color_high: str = "blue",
    threshold_mid: int = 10,
    threshold_high: int = 35,
    ax: Optional[plt.Axes] = None,
    invert_y: bool = False,
) -> plt.Axes:
    """
    Create a heatmap showing point density across court zones.

    Requires shapely package for zone calculations.

    Args:
        coordinates: List of (x, y) coordinate tuples
        zones: If True, use main zones (6 zones per half)
        subzones: If True, subdivide each zone into 4 subzones
        half: If True, show only top half of court
        color_low: Color for zones with no points
        color_mid: Color for zones with few points
        color_high: Color for zones with many points
        threshold_mid: Point count threshold for mid color
        threshold_high: Point count threshold for high color
        ax: Matplotlib axes to draw on
        invert_y: If True, invert the y-axis

    Returns:
        matplotlib.axes.Axes: The axes with the heatmap

    Example:
        >>> from datavolley.plot import dv_heatmap
        >>> coords = [(1.5, 4.5), (2.0, 5.0), (2.5, 5.5)]
        >>> ax = dv_heatmap(coords, zones=True)
        >>> plt.show()
    """
    if not HAS_SHAPELY:
        raise ImportError(
            "dv_heatmap requires the shapely package. "
            "Install it with: pip install shapely"
        )

    if ax is None:
        _, ax = plt.subplots(figsize=(4, 7))

    if subzones:
        zone_polygons = _define_subzones()
        threshold_mid = threshold_mid if threshold_mid < 35 else 10
        threshold_high = threshold_high if threshold_high < 35 else 20
    else:
        zone_polygons = _define_zones()

    counts = _count_points_in_zones(coordinates, zone_polygons)

    _color_zones(
        ax,
        zone_polygons,
        counts,
        color_low,
        color_mid,
        color_high,
        threshold_mid,
        threshold_high,
    )

    ax.plot([0.25, 3.75], [3.5, 3.5], color="black", linewidth=3, zorder=10)

    if half:
        ax.set_ylim(3.5, 7)
    else:
        ax.set_ylim(0, 7)

    ax.set_xlim(0, 4)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])

    if invert_y:
        ax.invert_yaxis()

    return ax


def _draw_full_court(ax: plt.Axes, line_color: str, zones: bool) -> None:
    """Draw a full volleyball court."""
    ax.plot([0.25, 3.75], [3.5, 3.5], color=line_color, linewidth=2, zorder=1)

    outer_boundary = np.array(
        [[0.5, 0.5], [3.5, 0.5], [3.5, 6.5], [0.5, 6.5], [0.5, 0.5]]
    )
    ax.plot(outer_boundary[:, 0], outer_boundary[:, 1], color=line_color, linewidth=1.5)

    three_meter_lines = np.array([[0.5, 2.5], [3.5, 2.5], [3.5, 4.5], [0.5, 4.5]])
    ax.plot(
        three_meter_lines[:, 0], three_meter_lines[:, 1], color=line_color, linewidth=1
    )

    if zones:
        for i in range(1, 3):
            ax.plot(
                [i + 0.5, i + 0.5],
                [0.5, 6.5],
                color=line_color,
                linewidth=0.5,
                alpha=0.5,
            )
        for i in range(1, 6):
            if i not in [2, 4]:
                ax.plot(
                    [0.5, 3.5],
                    [i + 0.5, i + 0.5],
                    color=line_color,
                    linewidth=0.5,
                    alpha=0.5,
                )


def _draw_half_court(ax: plt.Axes, line_color: str, zones: bool) -> None:
    """Draw the top half of a volleyball court."""
    ax.plot([0.25, 3.75], [3.5, 3.5], color=line_color, linewidth=2, zorder=1)

    upper_boundary = np.array(
        [[0.5, 3.5], [3.5, 3.5], [3.5, 6.5], [0.5, 6.5], [0.5, 3.5]]
    )
    ax.plot(upper_boundary[:, 0], upper_boundary[:, 1], color=line_color, linewidth=1.5)

    three_meter_line = np.array([[0.5, 4.5], [3.5, 4.5]])
    ax.plot(
        three_meter_line[:, 0], three_meter_line[:, 1], color=line_color, linewidth=1
    )

    if zones:
        for i in range(1, 3):
            ax.plot(
                [i + 0.5, i + 0.5],
                [3.5, 6.5],
                color=line_color,
                linewidth=0.5,
                alpha=0.5,
            )
        for i in [4, 5]:
            ax.plot(
                [0.5, 3.5],
                [i + 0.5, i + 0.5],
                color=line_color,
                linewidth=0.5,
                alpha=0.5,
            )


def _add_zone_labels(ax: plt.Axes, half: bool = False) -> None:
    """Add zone number labels to the court."""
    zone_positions = {
        1: (3.0, 6.0),
        2: (2.0, 6.0),
        3: (1.0, 6.0),
        4: (1.0, 5.0),
        5: (1.0, 4.0),
        6: (2.0, 5.0),
        7: (2.0, 1.0),
        8: (2.0, 2.0),
        9: (3.0, 1.0),
    }

    if half:
        zones_to_show = [1, 2, 3, 4, 5, 6]
    else:
        zones_to_show = list(zone_positions.keys())

    for zone, (x, y) in zone_positions.items():
        if zone in zones_to_show:
            ax.text(
                x,
                y,
                str(zone),
                ha="center",
                va="center",
                fontsize=12,
                fontweight="bold",
                color="gray",
                alpha=0.6,
            )


def _define_zones() -> List[np.ndarray]:
    """Define the 18 main zones (6 per side, 3 across)."""
    zones = []
    for row in range(6):
        for col in range(3):
            x_min = 0.5 + col
            x_max = x_min + 1
            y_min = 0.5 + row
            y_max = y_min + 1
            zone = np.array(
                [
                    [x_min, y_min],
                    [x_max, y_min],
                    [x_max, y_max],
                    [x_min, y_max],
                    [x_min, y_min],
                ]
            )
            zones.append(zone)
    return zones


def _define_subzones() -> List[np.ndarray]:
    """Define subzones (4 per main zone = 72 total subzones)."""
    main_zones = _define_zones()
    subzones = []

    for zone in main_zones:
        x_min, y_min = zone[0]
        x_max, y_max = zone[2]
        x_mid = (x_min + x_max) / 2
        y_mid = (y_min + y_max) / 2

        subzone_coords = [
            [
                [x_min, y_min],
                [x_mid, y_min],
                [x_mid, y_mid],
                [x_min, y_mid],
                [x_min, y_min],
            ],
            [
                [x_mid, y_min],
                [x_max, y_min],
                [x_max, y_mid],
                [x_mid, y_mid],
                [x_mid, y_min],
            ],
            [
                [x_min, y_mid],
                [x_mid, y_mid],
                [x_mid, y_max],
                [x_min, y_max],
                [x_min, y_mid],
            ],
            [
                [x_mid, y_mid],
                [x_max, y_mid],
                [x_max, y_max],
                [x_mid, y_max],
                [x_mid, y_mid],
            ],
        ]

        for coords in subzone_coords:
            subzones.append(np.array(coords))

    return subzones


def _count_points_in_zones(
    coordinates: List[Tuple[float, float]], zones: List[np.ndarray]
) -> List[int]:
    """Count how many points fall in each zone."""
    counts = [0] * len(zones)
    for coord in coordinates:
        point = Point(coord)
        for i, zone in enumerate(zones):
            if point.within(Polygon(zone)):
                counts[i] += 1
                break
    return counts


def _color_zones(
    ax: plt.Axes,
    zones: List[np.ndarray],
    counts: List[int],
    color_low: str,
    color_mid: str,
    color_high: str,
    threshold_mid: int,
    threshold_high: int,
) -> None:
    """Color zones based on point counts."""
    for zone, count in zip(zones, counts):
        if count == 0:
            color = color_low
        elif count < threshold_mid:
            color = color_mid
        elif count < threshold_high:
            color = color_high
        else:
            color = color_high

        ax.fill(zone[:, 0], zone[:, 1], color=color, alpha=0.6, zorder=1)
        ax.plot(
            zone[:, 0], zone[:, 1], color="black", linewidth=0.5, alpha=0.3, zorder=2
        )
