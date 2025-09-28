# py-datavolley

A Python package for parsing and analyzing volleyball scouting data from DataVolley files (\*.dvw).

Currently rebuilding [pydatavolley](https://github.com/openvolley/pydatavolley) with modern Python tooling ([Astral ecosystem](https://docs.astral.sh/)) for improved experience: UV for package management, Ruff for linting/formatting and [Ty](https://github.com/astral-sh/ty) for type checking.

# Running

If you want to clone, here's how to set up the development environment using UV:

[UV documentation](https://docs.astral.sh/uv/getting-started/installation/)

# Setup Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

# Installation

Ensure you have uv - this will make the process much easier.

`uv add openvolley-pydatavolley`

```python
import datavolley as dv

dv.read_dv('datavolley_path')

# For convience you may want to use pandas
import pandas as pd

data = dv.read_dv('datavolley_path')

pd.DataFrame(data)

# Or polars
import polars as pl

data = dv.read_dv('datavolley_path')

pl.DataFrame(data)
```

# Development

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/py-datavolley.git
   cd py-datavolley
   ```

2. Create and activate virtual environment:

   ```bash
   # UV automatically creates and manages virtual environments
   uv sync
   ```

3. Install development dependencies:
   ```bash
   # Development dependencies are defined in pyproject.toml
   uv sync --group dev
   ```

# Testing

After the setup process run main with:

```python
# Use example file or your own file
uv run main.py
```

Which will return:

<details>
<summary>Json</summary>

```json
[   {
        "match_id": "106859",
        "video_time": 495,
        "code": "a02RM-~~~58AM~~00B",
        "team": "University of Dayton",
        "player_number": 2,
        "player_name": "Maura Collins",
        "player_id": "-230138",
        "skill": "Reception",
        "skill_subtype": "Jump Float",
        "evaluation_code": "-",
        "setter_position": None,
        "attack_code": None,
        "set_code": None,
        "set_type": None,
        "start_zone": "5",
        "end_zone": "8",
        "end_subzone": "A",
        "num_players_numeric": None,
        "home_team_score": "0",
        "visiting_team_score": "0",
        "home_setter_position": "1",
        "visiting_setter_position": "6",
        "custom_code": None,
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
        "point_phase": None,
        "attack_phase": None,
        "start_coordinate_x": 1.26875,
        "start_coordinate_y": 0.09259600000000001,
        "mid_coordinate_x": None,
        "mid_coordinate_y": None,
        "end_coordinate_x": 1.68125,
        "end_coordinate_y": 5.425924,
        "set_number": "1",
        "home_team": "University of Louisville",
        "visiting_team": "University of Dayton",
        "home_team_id": 17,
        "visiting_team_id": 42,
        "point_won_by": None,
        "serving_team": None,
        "receiving_team": None,
        "rally_number": None,
        "possesion_number": None
    }
]
```

</details>

# Contributing

Please create an issue, fork and create a pull request.
