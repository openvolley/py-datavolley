# Volleyball Court Plotting

This module provides functions to visualize volleyball match data on court diagrams.

## Installation

The plotting functions require optional dependencies:

```bash
uv add openvolley-pydatavolley[plot]
```

Or install dependencies manually:

```bash
uv add matplotlib numpy shapely
```

## Basic Usage

### Draw a Basic Court

```python
import datavolley as dv
import matplotlib.pyplot as plt

# Draw a full court
ax = dv.dv_court()
plt.show()

# Draw half court with zones
ax = dv.dv_court(half=True, zones=True, zone_labels=True)
plt.show()
```

### Create Heatmaps

```python
import datavolley as dv

# Load match data
data = dv.read_dv("match.dvw")

# Get attack landing coordinates
attacks = [p for p in data if p.get("skill") == "Attack"]
coords = [
    (p.get("end_coordinate_x"), p.get("end_coordinate_y"))
    for p in attacks
    if p.get("end_coordinate_x") is not None
]

# Create heatmap
ax = dv.dv_heatmap(coords, zones=True)
plt.title(f"Attack Landing Zones ({len(coords)} attacks)")
plt.show()
```

## Functions

### `dv_court()`

Draw a volleyball court.

**Parameters:**

- `half` (bool): If True, draw only top half of court
- `court_color` (str): Background color (default: "white")
- `line_color` (str): Line color (default: "black")
- `zones` (bool): Show zone dividers (default: False)
- `zone_labels` (bool): Show zone numbers (default: False)
- `ax` (plt.Axes): Matplotlib axes to draw on

**Returns:** matplotlib.axes.Axes

### `dv_heatmap()`

Create a heatmap showing point density across court zones.

**Parameters:**

- `coordinates` (List[Tuple[float, float]]): List of (x, y) coordinates
- `zones` (bool): Use main zones (default: True)
- `subzones` (bool): Use subzones for more detail (default: False)
- `half` (bool): Show only top half (default: False)
- `color_low` (str): Color for empty zones (default: "white")
- `color_mid` (str): Color for few points (default: "lightblue")
- `color_high` (str): Color for many points (default: "blue")
- `threshold_mid` (int): Threshold for mid color (default: 10)
- `threshold_high` (int): Threshold for high color (default: 35)
- `ax` (plt.Axes): Matplotlib axes to draw on
- `invert_y` (bool): Invert y-axis (default: False)

**Returns:** matplotlib.axes.Axes

## Examples

### Multiple Subplots

```python
import matplotlib.pyplot as plt
import datavolley as dv

data = dv.read_dv("match.dvw")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Serves
serves = [p for p in data if p.get("skill") == "Serve"]
serve_coords = [(p.get("end_coordinate_x"), p.get("end_coordinate_y"))
                for p in serves if p.get("end_coordinate_x")]
dv.dv_heatmap(serve_coords, ax=axes[0])
axes[0].set_title("Serves")

# Attacks
attacks = [p for p in data if p.get("skill") == "Attack"]
attack_coords = [(p.get("end_coordinate_x"), p.get("end_coordinate_y"))
                 for p in attacks if p.get("end_coordinate_x")]
dv.dv_heatmap(attack_coords, ax=axes[1])
axes[1].set_title("Attacks")

# Digs
digs = [p for p in data if p.get("skill") == "Dig"]
dig_coords = [(p.get("start_coordinate_x"), p.get("start_coordinate_y"))
              for p in digs if p.get("start_coordinate_x")]
dv.dv_heatmap(dig_coords, ax=axes[2])
axes[2].set_title("Digs")

plt.tight_layout()
plt.show()
```

### Filter by Team/Player

```python
import datavolley as dv

data = dv.read_dv("match.dvw")

# Get specific team's attacks
team_name = "Team A"
team_attacks = [p for p in data
                if p.get("skill") == "Attack" and p.get("team") == team_name]

coords = [(p.get("end_coordinate_x"), p.get("end_coordinate_y"))
          for p in team_attacks if p.get("end_coordinate_x")]

ax = dv.dv_heatmap(coords, zones=True)
plt.title(f"{team_name} - Attack Zones")
plt.show()
```

## Coordinate System

The court uses a coordinate system where:

- X-axis: 0.5 to 3.5 (left to right)
- Y-axis: 0.5 to 6.5 (bottom to top)
- Net: y = 3.5
- 3-meter lines: y = 2.5 and y = 4.5

Zones are numbered 1-9:

- Lower court: 7, 8, 9 (back row)
- Mid court: 4, 3, 2 (front row)
- Net line: at y = 3.5
- Upper court: 2, 3, 4 (front row)
- Upper back: 5, 6, 1 (back row)
