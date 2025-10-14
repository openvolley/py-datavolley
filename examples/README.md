# Plotting Examples

This directory contains example scripts demonstrating how to visualize volleyball match data.

## Prerequisites

Install plotting dependencies:

```bash
uv add matplotlib numpy shapely
```

Or install with the plot extra:

```bash
uv add openvolley-pydatavolley[plot]
```

## Examples

### Basic Plotting

**`plot_example.py`** - Overview of plotting capabilities

- Basic court drawing (full and half court)
- Courts with zones and labels
- Heatmaps for serves and attacks

```bash
uv run examples/plot_example.py
```

### Attack Analysis

**`attack_analysis_complete.py`** - Complete attack trajectory analysis

- Filter attacks by attack code (e.g., X5)
- Plot attack trajectories (start location → landing point)
- Show start and end coordinates

```bash
uv run examples/attack_analysis_complete.py
```

**`attack_plotting.py`** - Basic X5 attack trajectories

- Simple trajectory visualization
- Red dots = start location, Blue dots = landing point
- Gray dashed lines = ball trajectory

```bash
uv run examples/attack_plotting.py
```

**`attack_comparison.py`** - Compare multiple attack codes

- Side-by-side comparison of X5, X6, V5, V6
- Shows attack descriptions and counts
- Helps identify attack patterns

```bash
uv run examples/attack_comparison.py
```

**`attack_heatmap.py`** - Attack heatmaps

- Separate heatmaps for start locations and landing zones
- Color-coded by frequency
- Good for identifying hot zones

```bash
uv run examples/attack_heatmap.py
```

### Team Analysis

**`team_attacks.py`** - Team-based attack comparison

- Compare attack patterns between teams
- Side-by-side heatmaps
- Useful for scouting reports

```bash
uv run examples/team_attacks.py
```

## Output

All examples save PNG files to the current directory:

- `court_examples.png`
- `x5_attack_trajectories.png`
- `attack_comparison.png`
- `x5_heatmaps.png`
- `team_attacks.png`

## Common Patterns

### Load and Filter Data

```python
import datavolley as dv

# Load data
data = dv.read_dv("your_match.dvw")

# Filter by skill
attacks = [p for p in data if p.get("skill") == "Attack"]

# Filter by attack code
x5_attacks = [p for p in attacks if p.get("attack_code") == "X5"]

# Filter by team
team_attacks = [p for p in attacks if p.get("team") == "Team Name"]

# Filter by evaluation
good_attacks = [p for p in attacks if p.get("evaluation_code") in ["#", "+"]]
```

### Extract Coordinates

```python
# End coordinates (where ball landed)
end_coords = [
    (p["end_coordinate_x"], p["end_coordinate_y"])
    for p in attacks
    if p.get("end_coordinate_x") is not None
]

# Start coordinates (where ball was set from)
start_coords = [
    (p["start_coordinate_x"], p["start_coordinate_y"])
    for p in attacks
    if p.get("start_coordinate_x") is not None
]
```

### Create Plots

```python
import matplotlib
matplotlib.use('Agg')  # Use if you get tkinter errors
import matplotlib.pyplot as plt

# Basic court
ax = dv.dv_court(zones=True, zone_labels=True)
plt.savefig("court.png")

# Heatmap
ax = dv.dv_heatmap(end_coords, zones=True)
plt.title("Attack Landing Zones")
plt.savefig("heatmap.png")

# Custom trajectory plot
fig, ax = plt.subplots(figsize=(6, 10))
dv.dv_court(zones=True, ax=ax)

for attack in attacks:
    if all([attack.get("start_coordinate_x"), attack.get("end_coordinate_x")]):
        ax.plot(
            [attack["start_coordinate_x"], attack["end_coordinate_x"]],
            [attack["start_coordinate_y"], attack["end_coordinate_y"]],
            'gray', alpha=0.5
        )

plt.savefig("custom.png")
```

## Troubleshooting

### TkInter Error

If you see `_tkinter.TclError: Can't find a usable init.tcl`, add this at the top of your script:

```python
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
```

### Shapely Not Installed

If you get `ImportError: dv_heatmap requires the shapely package`, install it:

```bash
uv add shapely
```

### No Data Showing

Make sure coordinates exist:

```python
# Check if coordinates are present
coords = [(p["end_coordinate_x"], p["end_coordinate_y"])
          for p in data if p.get("end_coordinate_x")]
print(f"Found {len(coords)} plays with coordinates")
```

## Tips

1. **Use filters** to focus on specific plays (team, player, evaluation)
2. **Check coordinate availability** before plotting
3. **Use subplots** to compare multiple views
4. **Adjust thresholds** in heatmaps to highlight patterns
5. **Save high-DPI images** with `dpi=150` or higher for presentations
