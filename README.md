# py-datavolley

A Python package for parsing and analyzing volleyball scouting data from DataVolley files (\*.dvw).

We modernized [pydatavolley](https://github.com/openvolley/pydatavolley) with a stronger Python workflow. It now uses [Pydantic](https://docs.pydantic.dev/latest/concepts/types/) for more reliable type validation, plus the [Astral](https://docs.astral.sh/) [toolchain—UV](https://docs.astral.sh/uv/) for package management, [Ruff](https://docs.astral.sh/ruff/) for linting/formatting, and [Ty](https://docs.astral.sh/ty/) for type checking.

```bash
mkdir my-analysis
cd my-analysis
uv init
uv add openvolley-pydatavolley
```

```python
import datavolley as dv


def main():
    return dv.read_dv(dv.example_file())


if __name__ == "__main__":
    data = main()
    print(data)

```

Type validation can be controlled per call:

```python
import datavolley as dv

plays, issues = dv.read_dv(
    dv.example_file(),
    validation_mode=dv.ValidationMode.LENIENT,
    normalize_types=True,
    return_issues=True,
)

print(f"plays={len(plays)} issues={len(issues)}")
```

The same options are available in `load_dvw(...)`, and issues are returned as `(match_data, issues)`.

- `validation_mode`: `lenient` (default) continues parsing and collects issues, `strict` raises on validation errors.
- `normalize_types`: converts numeric-like fields to numeric types while preserving nullable behavior for missing values.
- `return_issues`: returns validation issues with field/index metadata for downstream quality checks.

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
