# py-datavolley

### TLDR;

```python
uv add openvolley-pydatavolley

# data = dv.read_dv(path_of_dvw_file)
data = dv.read_dv(dv.example_file())
print(data)
```

<details>
<summary>Will return (this is a sample and not the entire example file) </summary>

```json
[
  {
    "match_id": "106859",
    "video_time": 495,
    "code": "a02RM-~~~58AM~~00B",
    "team": "University of Dayton",
    "player_number": 2,
    "player_name": "Maura Collins",
    "player_id": "-230138",
    "skill": "Reception",
    "skill_type": "Jump-float serve reception",
    "skill_subtype": "Jump Float",
    "evaluation_code": "-",
    "setter_position": "6",
    "attack_code": null,
    "set_code": null,
    "set_type": null,
    "start_zone": "5",
    "end_zone": "8",
    "end_subzone": "A",
    "num_players_numeric": null,
    "home_team_score": "0",
    "visiting_team_score": "0",
    "home_setter_position": "1",
    "visiting_setter_position": "6",
    "custom_code": "00B",
    "home_p1": "19",
    "home_p2": "9",
    "home_p3": "11",
    "home_p4": "15",
    "home_p5": "10",
    "home_p6": "7",
    "visiting_p1": "1",
    "visiting_p2": "16",
    "visiting_p3": "17",
    "visiting_p4": "10",
    "visiting_p5": "6",
    "visiting_p6": "8",
    "start_coordinate": "0431",
    "mid_coordinate": "-1-1",
    "end_coordinate": "7642",
    "point_phase": "Reception",
    "attack_phase": null,
    "start_coordinate_x": 1.26875,
    "start_coordinate_y": 0.092596,
    "mid_coordinate_x": null,
    "mid_coordinate_y": null,
    "end_coordinate_x": 1.68125,
    "end_coordinate_y": 5.425924,
    "set_number": "1",
    "home_team": "University of Louisville",
    "visiting_team": "University of Dayton",
    "home_team_id": 17,
    "visiting_team_id": 42,
    "point_won_by": "University of Louisville",
    "serving_team": "University of Louisville",
    "receiving_team": "University of Dayton",
    "rally_number": 1,
    "possession_number": 1
  }
]
```

</details>

<hr>
<hr>

### py-datavolley package

A Python package for parsing and analyzing volleyball scouting data from DataVolley files (\*.dvw).

Rebuilt [pydatavolley](https://github.com/openvolley/pydatavolley) with modern Python tooling ([Astral ecosystem](https://docs.astral.sh/)) for improved experience: UV for package management, Ruff for linting/formatting and [Ty](https://github.com/astral-sh/ty) for type checking.

## Quick Reference

```bash
# Start a new project
uv init my-analysis && cd my-analysis
uv add openvolley-pydatavolley[plot]

# Load and analyze data
uv run python -c "
import datavolley as dv
data = dv.read_dv('match.dvw')
print(f'Loaded {len(data)} plays')
"
```

## Table of Contents

- [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Quick Start](#quick-start)
  - [With Pandas or Polars](#with-pandas-or-polars)
  - [Without uv](#without-uv)
- [Plotting](#plotting)
  - [Examples](#examples)
  - [Example Outputs](#example-outputs)
- [Development](#development)
- [Contributing](#contributing)

## Prerequisites

This package works best with [uv](https://docs.astral.sh/uv/) - a fast Python package manager.

### Install uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

See [uv documentation](https://docs.astral.sh/uv/getting-started/installation/) for more details.

# Usage

## Quick Start

If you have [uv](https://docs.astral.sh/uv/) installed (recommended):

```bash
# Create a new project
uv init my-volleyball-analysis
cd my-volleyball-analysis

# Add the package
uv add openvolley-pydatavolley

# Plotting: Add plotting dependencies
uv add openvolley-pydatavolley[plot]
```

Create `main.py`:

```python
import datavolley as dv

# Load a match
data = dv.read_dv('path/to/match.dvw')
# data = dv.read_dv(dv.example_file())

# Access play data
for play in data[:5]:
    print(f"{play['skill']}: {play['player_name']} - {play['evaluation_code']}")

# Filter by skill
serves = [p for p in data if p.get('skill') == 'Serve']
attacks = [p for p in data if p.get('skill') == 'Attack']

print(f"Total serves: {len(serves)}")
print(f"Total attacks: {len(attacks)}")
```

Run your analysis:

```bash
uv run main.py
```

## With Pandas or Polars

Convert to DataFrame for easier analysis:

```python
import datavolley as dv
import pandas as pd

data = dv.read_dv('match.dvw')
df = pd.DataFrame(data)

# Analyze attacks
attacks = df[df['skill'] == 'Attack']
print(attacks.groupby('player_name')['evaluation_code'].value_counts())
```

Or with Polars:

```python
import datavolley as dv
import polars as pl

data = dv.read_dv('match.dvw')
df = pl.DataFrame(data)

# Fast filtering and aggregation
attacks = df.filter(pl.col('skill') == 'Attack')
print(attacks.group_by('player_name').agg(pl.len()))
```

## Without uv

If you prefer pip:

```bash
pip install openvolley-pydatavolley
pip install openvolley-pydatavolley[plot]  # With plotting
```

# Development

Want to contribute or modify the package? Here's how to set up a development environment:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/openvolley/py-datavolley.git
   cd py-datavolley
   ```

2. **Install dependencies:**

   ```bash
   # UV automatically creates and manages virtual environments
   uv sync
   ```

3. **Run the example:**

   ```bash
   uv run main.py
   ```

4. **Run linting and formatting:**

   ```bash
   ruff check datavolley/
   ruff format datavolley/
   ty check datavolley/
   ```

## Example Output

Running `uv run main.py` with the included example file will output:

<details>
<summary>Sample Play Data</summary>

```json
[
  {
    "match_id": "106859",
    "video_time": 495,
    "code": "a02RM-~~~58AM~~00B",
    "team": "University of Dayton",
    "player_number": 2,
    "player_name": "Maura Collins",
    "player_id": "-230138",
    "skill": "Reception",
    "skill_type": "Jump-float serve reception",
    "skill_subtype": "Jump Float",
    "evaluation_code": "-",
    "setter_position": "6",
    "attack_code": null,
    "set_code": null,
    "set_type": null,
    "start_zone": "5",
    "end_zone": "8",
    "end_subzone": "A",
    "num_players_numeric": null,
    "home_team_score": "0",
    "visiting_team_score": "0",
    "home_setter_position": "1",
    "visiting_setter_position": "6",
    "custom_code": "00B",
    "home_p1": "19",
    "home_p2": "9",
    "home_p3": "11",
    "home_p4": "15",
    "home_p5": "10",
    "home_p6": "7",
    "visiting_p1": "1",
    "visiting_p2": "16",
    "visiting_p3": "17",
    "visiting_p4": "10",
    "visiting_p5": "6",
    "visiting_p6": "8",
    "start_coordinate": "0431",
    "mid_coordinate": "-1-1",
    "end_coordinate": "7642",
    "point_phase": "Reception",
    "attack_phase": null,
    "start_coordinate_x": 1.26875,
    "start_coordinate_y": 0.092596,
    "mid_coordinate_x": null,
    "mid_coordinate_y": null,
    "end_coordinate_x": 1.68125,
    "end_coordinate_y": 5.425924,
    "set_number": "1",
    "home_team": "University of Louisville",
    "visiting_team": "University of Dayton",
    "home_team_id": 17,
    "visiting_team_id": 42,
    "point_won_by": "University of Louisville",
    "serving_team": "University of Louisville",
    "receiving_team": "University of Dayton",
    "rally_number": 1,
    "possession_number": 1
  }
]
```

</details>

# Plotting

The package includes plotting capabilities for visualizing volleyball match data on court diagrams.

## Installation

Install with plotting dependencies:

```bash
uv add openvolley-pydatavolley[plot]
```

Or install dependencies separately:

```bash
uv add matplotlib numpy shapely
```

## Examples

### Draw a Court

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datavolley as dv

# Draw a basic court
ax = dv.dv_court(zones=True, zone_labels=True)
plt.savefig('court.png')
```

### Create Attack Heatmaps

```python
import datavolley as dv

# Load match data
data = dv.read_dv('match.dvw')

# Get attack landing coordinates
attacks = [p for p in data if p.get('skill') == 'Attack']
coords = [(p['end_coordinate_x'], p['end_coordinate_y'])
          for p in attacks if p.get('end_coordinate_x')]

# Create heatmap
ax = dv.dv_heatmap(coords, zones=True)
plt.title(f'Attack Landing Zones (n={len(coords)})')
plt.savefig('attack_heatmap.png')
```

### Plot Attack Trajectories

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datavolley as dv

data = dv.read_dv(dv.example_file())

# Filter X5 attacks
attacks = [p for p in data
           if p.get('skill') == 'Attack' and p.get('attack_code') == 'X5']

# Plot trajectories
fig, ax = plt.subplots(figsize=(6, 10))
dv.dv_court(zones=True, ax=ax)

for attack in attacks:
    if all([attack.get('start_coordinate_x'), attack.get('end_coordinate_x')]):
        # Plot start (red) and end (blue) points
        ax.scatter(attack['start_coordinate_x'], attack['start_coordinate_y'],
                   color='red', s=50, alpha=0.6)
        ax.scatter(attack['end_coordinate_x'], attack['end_coordinate_y'],
                   color='blue', s=50, alpha=0.6)
        # Draw trajectory line
        ax.plot([attack['start_coordinate_x'], attack['end_coordinate_x']],
                [attack['start_coordinate_y'], attack['end_coordinate_y']],
                color='gray', linestyle='--', linewidth=1, alpha=0.5)

ax.set_title('X5 Attack Trajectories')
plt.savefig('x5_attacks.png', dpi=150)
```

### Example Outputs

<table>
  <tr>
    <td><img src="examples/x5_attack_trajectories.png" alt="X5 Attack Trajectories" width="350"/></td>
    <td><img src="examples/attack_comparison.png" alt="Attack Comparison" width="350"/></td>
  </tr>
  <tr>
    <td align="center"><b>X5 Attack Trajectories</b><br/>Shows ball path from set to landing</td>
    <td align="center"><b>Attack Code Comparison</b><br/>Compare patterns across attack types</td>
  </tr>
</table>

More examples available in the `examples/` directory:

- `attack_analysis_complete.py` - Complete attack trajectory analysis
- `attack_comparison.py` - Compare multiple attack codes side-by-side
  zones
- `attack_heatmap.py` - Heatmaps for attack set locations and landing
- `team_attacks.py` - Compare attack patterns between teams

See [`examples/README.md`](examples/README.md) for detailed documentation.

# Contributing

Please create an issue, fork and create a pull request.
