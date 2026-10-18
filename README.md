# py-datavolley

Parse DataVolley `.dvw` scouting files into Python dictionaries for volleyball analysis.

**Python 3.11+ · Zero runtime dependencies · Optional interactive charts**

## Install

```bash
uv add openvolley-pydatavolley
```

For charts with [Lets-Plot](https://lets-plot.org/), install the `viz` extra:

```bash
uv add "openvolley-pydatavolley[viz]"
```

## Quick start

Read a bundled match and select its attacks:

```python
import datavolley as dv

plays = dv.read_plays(dv.example_file())
attacks = [play for play in plays if play["skill"] == "Attack"]

print(f"{len(plays)} events, {len(attacks)} attacks")
```

Replace `dv.example_file()` with your own file path to analyze another match. Use `dv.example_file_list()` to find all bundled examples.

Plays are plain dictionaries: work with them directly or pass them to pandas or Polars. Normalized readers convert numeric fields to Python numbers, trim strings, use `None` for missing data, and derive zones from scout codes when available.

## Choose a reader

Start with `read_plays()` for play-focused analysis.

| Function | Output | Best for |
| --- | --- | --- |
| `read_plays(path)` | 50-field normalized analysis rows, including `source_file` | Filtering plays and rallies, grouping, summaries, and reports |
| `read_raw_plays(path)` | Raw scout rows plus `source_file` | Inspecting scout codes and columns with minimal enrichment |
| `read_dv(path)` | Full 88-field normalized play rows | Coordinates, video/event times, complete lineups, and detailed scout fields |
| `load_dvw(path)` | Full match dictionary, including normalized plays | Match metadata, rosters, set scores, and results |

Readers retain all scout events, including points, timeouts, substitutions, and lineup records. Filter after reading to preserve rally, possession, score, and phase context.

### Select complete rallies

Using `plays` and `attacks` from the quick start, keep every event in rallies containing a winning attack:

```python
winning_attacks = [play for play in attacks if play["winning_attack"]]
rallies = {(play["set_number"], play["rally_number"]) for play in winning_attacks}
selected = [
    play for play in plays if (play["set_number"], play["rally_number"]) in rallies
]
```

### Inspect raw scout rows

```python
import datavolley as dv

rows = dv.read_raw_plays(dv.example_file())
print(rows[0]["code"], rows[0]["file_line_number"], rows[0]["source_file"])
```

Raw rows include scout codes, phase columns, event flags, rotation slots, coordinates, video times, event datetimes, line numbers, and running scores. Numeric scout columns such as scores and rotation slots remain strings. Team/player names, decoded skills, and derived rally/point/possession identifiers are not added.

## Plotting

[**Open the interactive demo →**](https://openvolley.github.io/py-datavolley/)

[![Score progression for Louisville and Dayton across three sets. Click to open the interactive plot.](docs/score-progression.png)](https://openvolley.github.io/py-datavolley/)

GitHub displays the static preview above; the linked HTML page runs the interactive Lets-Plot chart. The example uses point events, so each rally contributes one score update and unplayed sets are omitted.

<details>
<summary>Recreate the plot</summary>

With the `viz` extra installed:

```python
import datavolley as dv
from lets_plot import (
    LetsPlot,
    aes,
    facet_wrap,
    geom_step,
    ggplot,
    ggsize,
    labs,
    theme,
    theme_minimal,
)

points = [play for play in dv.read_plays(dv.example_file()) if play["point"]]
rows = {"set": [], "rally": [], "team": [], "score": []}
for play in points:
    set_label = f"Set {play['set_number']}"
    teams = [play["home_team"], play["visiting_team"]]
    if play["rally_number"] == 1:
        rows["set"] += [set_label] * 2
        rows["rally"] += [0, 0]
        rows["team"] += teams
        rows["score"] += [0, 0]
    rows["set"] += [set_label] * 2
    rows["rally"] += [play["rally_number"]] * 2
    rows["team"] += teams
    rows["score"] += [play["home_team_score"], play["visiting_team_score"]]

fig = (
    ggplot(rows, aes("rally", "score", color="team"))
    + geom_step()
    + facet_wrap("set", ncol=3, scales="free_x")
    + labs(title="Score progression by set", x="Rally", y="Score", color="Team")
    + theme_minimal()
    + theme(legend_position="bottom")
    + ggsize(960, 400)
)

LetsPlot.setup_show_ext()
fig.show()
```

`fig.show()` opens the interactive chart in your default browser. To save it instead, use `fig.to_html("score-progression.html")`. Without a path, `fig.to_html()` returns the HTML as a string. Use `fig.to_png("score-progression.png")` for a static image.

The same example is available as [`examples/score_progression.py`](examples/score_progression.py). From a repository checkout, regenerate the preview and demo with:

```bash
uv run --extra viz python examples/score_progression.py
```

The script writes both assets to `docs/`. To publish the demo, set GitHub **Settings → Pages → Deploy from a branch → `main` → `/docs`** after the files are on `main`.

</details>

## Full match data

Use `load_dvw()` when you need match metadata alongside the plays:

```python
import datavolley as dv

match = dv.load_dvw(dv.example_file())
print(match["teams"])
print(match["match_result"])
```

| Key | Type | Contents |
| --- | --- | --- |
| `filename` | `str` | Input filename without its extension |
| `match_date` | `datetime` or `None` | Match date and time, if available |
| `match_id` | `str` | Match identifier from the file, or a generated fallback |
| `comments` | `str` | Match comments; empty if absent |
| `teams` | `dict` | Home/visiting team names and IDs |
| `set_scores` | `dict[str, int]` | Final scores by team and set |
| `players` | `dict[str, list[dict]]` | Rosters under `home` and `visiting` |
| `attack_combinations` | `list[dict]` | Attack codes and descriptions |
| `setter_calls` | `list[dict]` | Setter-call definitions |
| `plays` | `list[dict]` | The same normalized rows returned by `read_dv()` |
| `match_result` | `dict` | Sets won, sets played, and match winner; empty if scores are absent |

## Data reference

### Analysis fields

`read_plays()` shares field values and types with `read_dv()` and adds `source_file`, the input path as a string. It reads the team/roster and attack/set definitions needed to enrich plays.

<details>
<summary>All 50 analysis fields, grouped by purpose</summary>

| Group | Fields |
| --- | --- |
| Identifiers | `match_id`, `set_number`, `point_id`, `team_touch_id`, `rally_number`, `possession_number` |
| Teams | `home_team`, `home_team_id`, `visiting_team`, `visiting_team_id`, `team`, `team_id` |
| Player | `player_number`, `player_name`, `player_id` |
| Action | `code`, `skill`, `skill_type`, `skill_subtype`, `evaluation_code`, `evaluation` |
| Attack/set | `attack_code`, `attack_description`, `set_code`, `set_description`, `set_type` |
| Zones | `start_zone`, `end_zone`, `end_subzone`, `end_cone` |
| Event flags | `point`, `timeout`, `substitution`, `end_of_set`, `winning_attack` |
| Scores | `home_team_score`, `visiting_team_score`, `home_score_start_of_point`, `visiting_score_start_of_point` |
| Context | `point_phase`, `attack_phase`, `phase`, `point_won_by`, `serving_team`, `receiving_team` |
| Setter positions | `home_setter_position`, `visiting_setter_position`, `setter_position` |
| Provenance | `file_line_number`, `source_file` |

</details>

For the full play schema, use `read_dv()`. The analysis reader skips timestamp and coordinate conversion, lineup extraction/ID resolution, custom/special-code details, and blocker/receiver counts. It also skips match dates, comments, set-score summaries, and match results.

### Sample normalized play

<details>
<summary>Selected fields from a play in the bundled match</summary>

These fields come from one `read_dv()` row, also available through `load_dvw(...)["plays"]`. The full row contains 88 fields.

```python
{
    "match_id": "106859",
    "set_number": 1,
    "rally_number": 12,
    "possession_number": 3,
    "code": "*08EH#~~~~3D~~~+5",
    "team": "University of Louisville",
    "player_number": 8,
    "player_name": "Lexi Hamilton",
    "skill": "Set",
    "evaluation_code": "#",
    "evaluation": "Perfect",
    "end_zone": 3,
    "end_subzone": "D",
    "home_team_score": 9,
    "visiting_team_score": 3,
    "phase": "Transition",
    "winning_attack": False,
    "file_line_number": 241,
}
```

</details>

## About this fork

A modernized fork of [pydatavolley](https://github.com/openvolley/pydatavolley), built with [uv](https://docs.astral.sh/uv/) for package management, [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, and [ty](https://docs.astral.sh/ty/) for type checking.
