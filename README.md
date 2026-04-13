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


# Added section for AI agents
Work in progress
## Skills

The skills knowledge base now lives under `docs/skills/` and replaces the previous root-level scratch file.

### Data Ingest (`docs/skills/01-data-ingest.md`)

This skill focuses on reading DataVolley-style files into stable event rows and match metadata. It covers tolerant ingest of DVW, XML, and VSM-shaped sources so analysis can start even with imperfect files. The output is a consistent play schema that keeps raw fields available for later derivation.

### File Validation (`docs/skills/02-file-validation.md`)

This skill focuses on validating and normalizing mixed-type fields without breaking downstream workflows. It defaults to lenient behavior that collects issues while preserving nullable values for incomplete data. It also documents strict-mode behavior for pipelines that require fail-fast guarantees.

### Data Augmentation (`docs/skills/03-data-augmentation.md`)

This skill focuses on enriching parsed events with rally-level context such as phase, possession, and score state. It propagates contextual fields like reception quality so analysts can filter entire rallies consistently. The guiding rule is additive enrichment that does not overwrite canonical intent encoded in scout `code`.

### Feature Engineering (`docs/skills/04-feature-engineering.md`)

This skill focuses on building reusable analytical features from ordered event sequences and lineup state. It includes setter linkage, on-court setter IDs, first-transition markers, and score-pressure bins. The result is a deterministic feature layer that can feed KPIs, dashboards, and models.

### Filtering and Analysis Recipes (`docs/skills/05-filtering-and-analysis-recipes.md`)

This skill focuses on practical query patterns analysts use every day. It covers slices such as attack after good pass, first transition attack, and player-on-court combinations. Each recipe emphasizes repeatable filters, denominator discipline, and quality checks.

### Indicators and KPIs (`docs/skills/06-indicators-and-kpis.md`)

This skill focuses on formal KPI definitions with explicit formulas and denominators. It includes expected sideout rate, expected breakpoint rate, assist rate, and common attack/reception/serve efficiency variants. The objective is cross-report consistency so the same metric always means the same thing.

### Modeling Patterns (`docs/skills/07-modeling-patterns.md`)

This skill focuses on turning engineered features into robust modeling workflows, including xK-style classification patterns. It documents split strategy, leakage controls, baseline-first modeling, and calibration checks. The emphasis is interpretable outputs that support decision-making rather than black-box scores.

### Court Location and Visuals (`docs/skills/08-court-location-and-visuals.md`)

This skill focuses on converting zones, subzones, cones, and coordinates into consistent court-space representations. It covers direction normalization, line-segment plotting, mid-coordinate handling, and heatmap conventions. The goal is trustworthy spatial visuals that align with scouting semantics.
