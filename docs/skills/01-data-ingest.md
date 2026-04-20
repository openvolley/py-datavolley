---
name: 01-data-ingest
description: Use this skill to ingest DataVolley `.dvw` scout files into structured match data for downstream volleyball analysis.
---

# Skill 01: Data Ingest

This skill defines how raw DataVolley scouting files become structured match, roster, and play data.

`.dvw` files are standard text-based scouting files produced by DataVolley software.
They encode volleyball match information such as match metadata, team rosters, player references, and action codes for events like serve, reception, set, attack, dig, block, and freeball.

In this repository, `.dvw` ingestion must use the existing parser rather than ad hoc text parsing.

## Two Entrypoints

Use the repository's two public parsing entrypoints:

- `datavolley.load_dvw(file_path, ...)`
  - Returns nested match data (`teams`, `players`, `set_scores`, `match_result`, `plays`, etc.).
  - Use when you need match-level context, roster sections, attack combinations, or setter calls.
- `datavolley.read_dv(file_path, ...)`
  - Returns flat enriched play rows (list of dictionaries).
  - Use when you need per-play analysis, filtering by skill/evaluation, CSV export, and player/team aggregations.

Decision rule:

- If output grain is one-row-per-match or nested structures, prefer `load_dvw()`.
- If output grain is one-row-per-play, prefer `read_dv()`.

Relevant implementation paths:

- `datavolley/__init__.py`
- `datavolley/utils/metadata.py`
- `datavolley/core/teams.py`
- `datavolley/core/players.py`
- `datavolley/core/plays.py`
- `datavolley/core/code.py`

For event-level interpretation of scout codes, use:

- `datavolley/core/code.py` -> `parse_play_code(raw_content, code)`

This helper maps codes into skills such as `Serve`, `Reception`, `Set`, `Attack`, `Dig`, `Block`, `Freeball`, and `Point`.

## Execution Pattern (PowerShell)

PowerShell + `python -c` with multiline code and f-strings is fragile.
Use one of these patterns instead:

- Preferred: write a temporary `.py` script file, run it with `python path/to/script.py`, then clean up.
- Alternative: single-quoted here-string piped to stdin: `@' ... '@ | python -`.
- Avoid complex multiline `python -c` commands.

If dependencies are truly required beyond the repository baseline, install with `uv`.

## Workflow

When this skill is triggered, follow this workflow:

1. Locate `.dvw` files in the requested directory or file set.
2. Choose parser by output grain:
   - one-row-per-play -> `read_dv()`
   - nested match package -> `load_dvw()`
3. Do not manually parse `.dvw` files with custom regex/string slicing when parser outputs already provide the needed fields.
4. Preserve canonical parser keys and include file-level provenance (`source_file`).
5. For multiple files, process consistently and return one record per file or a combined play table with `source_file`.
6. Prefer repository utilities over new dependencies.
7. If extra packages are truly needed, use `uv`.
8. Do not block ingest by asking grading-meaning questions unless the user explicitly requested grade-based metrics and mapping is ambiguous.

## Required Extraction Targets

From each parsed `.dvw` file, extract at minimum:

- Match Metadata
- Player Rosters
- Action Codes

### Match Metadata

Capture:

- Teams
- Match date
- Match ID if available
- Set scores if available
- Match result if available

### Player Rosters

Capture:

- Home roster
- Visiting roster
- Player number
- Player name fields
- Player role when available
- Team association

### Action Codes

Capture or derive:

- Raw scout `code`
- Parsed skill/action classification (`skill`, `skill_type`, `skill_subtype` when available)
- `evaluation_code`
- Common volleyball actions such as `Attack`, `Serve`, `Block`, `Reception`, `Set`, `Dig`, and `Freeball`
- Set number and score context when available
- Rally context when available from the parser output

## Evaluation Code Policy

This skill handles ingestion, not authoritative grading semantics.
At ingest time, preserve `evaluation_code` exactly as parsed.

Do not assume mappings such as `# = Kill` or `# = Ace` during ingest.
Only apply semantic grade mappings when they are established by one of the following:

- repository code or documentation,
- a dedicated grading reference skill,
- a user-provided scouting reference,
- or explicit user confirmation.

If downstream analysis requires grade semantics and the mapping is ambiguous or conflicting, ask one targeted clarification before computing the metric.

## Guardrails

- Do not reimplement `.dvw` parsing if the repository parser already covers the need.
- Do not flatten away useful structure too early unless the requested output is explicitly tabular.
- Preserve canonical scout codes in the output for traceability.
- Keep file-level provenance such as filename/path associated with each parsed result.
- Prefer additive transformation over destructive normalization.
- If there are zero `.dvw` files, return a clear no-files-found result instead of failing silently.

## Expected Output

Return structured data in a JSON-friendly shape so later agents can build analysis on top of it.
Use one of the following output patterns.

### `load_dvw()`-style nested output

```json
{
  "source_file": "match_001.dvw",
  "match": {
    "match_id": "106859",
    "match_date": "2025-12-07T19:00:00",
    "teams": {
      "team_1": "University of Louisville",
      "team_2": "University of Dayton"
    },
    "set_scores": {
      "team_1_set_1": 25,
      "team_2_set_1": 21
    },
    "players": {
      "home": [],
      "visiting": []
    },
    "plays": []
  }
}
```

### `read_dv()`-style flat play row output

```json
{
  "source_file": "match_001.dvw",
  "match_id": "106859",
  "video_time": 5135,
  "code": "*17SH!~~~69A~~~+3",
  "team": "University of Louisville",
  "player_number": 17,
  "player_name": "Mia Stander",
  "player_id": "-224841",
  "skill": "Serve",
  "skill_type": "Float serve",
  "skill_subtype": "Float",
  "evaluation_code": "!",
  "setter_position": "4",
  "attack_code": null,
  "set_code": null,
  "set_type": null,
  "start_zone": "6",
  "end_zone": "9",
  "end_subzone": "A",
  "num_players_numeric": null,
  "home_team_score": "21",
  "visiting_team_score": "18",
  "set_number": "3",
  "home_team": "University of Louisville",
  "visiting_team": "University of Dayton",
  "point_won_by": "University of Louisville",
  "rally_number": 1,
  "possession_number": 0
}
```

## Common Analysis Patterns

- One-row-per-play CSV export: use `read_dv()` and include `source_file`.
- Match-level summaries: use `load_dvw()` and aggregate from nested sections.
- Skill filtering (for example attacks only): filter rows where `skill == "Attack"`.
- Grading filters (for example terminal positives): filter on `evaluation_code` and document symbol meaning source.

## Focus Areas

- Reliable ingestion of DataVolley `.dvw` files
- Reuse of the repository's canonical parser
- Extraction of match, roster, and action structures needed for later analysis
- JSON-shaped outputs that can feed augmentation, KPI, and modeling agents

## Primary Sources

- `docs/skills/sources.md`
- Repository parser implementation in `datavolley/__init__.py` and `datavolley/core/*`

## Example Prompt (Batch Parse)

For all `.dvw` files in FOLDER PATH:

1. Locate each `.dvw` file.
2. Do not parse files manually as raw text.
3. Use `datavolley.read_dv()` for one-row-per-play output.
4. Add `source_file` to each output row.
5. If additional Python packages are required, install them with `uv`.
