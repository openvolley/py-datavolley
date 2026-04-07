# Skill 04: Feature Engineering

This skill turns validated play-by-play rows into reusable analytical features.
It prioritizes deterministic transforms so repeated runs produce identical outputs.
It keeps all derived fields additive, preserving the original parsed event values.

## Why This Skill Exists

- Parsed events are useful, but most tactical questions need rally-level and lineup-level context.
- Feature engineering creates stable fields that power KPI calculations and model training.
- Good feature design removes repeated ad-hoc transformations from notebooks.

## Canonical Inputs

- Identity: `match_id`, `point_id`, `team`, `player_id`, `skill`.
- Sequence: `team_touch_id`, `rally_number`, `possession_number`, `phase`.
- Lineups: `home_player_id1`..`home_player_id6`, `visiting_player_id1`..`visiting_player_id6`.
- Setter state: `home_setter_position`, `visiting_setter_position`.
- Outcomes: `evaluation`, `point_won_by`, `home_team_score`, `visiting_team_score`.

## Core Feature Patterns

### 1) Setter linkage for attacks

- If a row is an `Attack` and the previous same-team row is a `Set`, copy the set row `player_id` to `set_player_id`.
- Keep `set_player_id` nullable when set rows are missing in the source scout file.

### 2) Setter-on-court IDs

- Build `home_setter_id` and `visiting_setter_id` by selecting lineup slot `player_id{setter_position}`.
- This allows setter-level analysis even when set touches are not fully scouted.

### 3) Rally reception quality propagation

- Extract reception quality from the rally reception row (`skill == Reception`).
- Join it back to all rows in the same (`match_id`, `point_id`) as `reception_quality`.

### 4) First-transition markers

- Take reception-phase `team_touch_id` and mark the next touch in the same rally as first transition.
- Use this for transition attack rates and sideout-to-breakpoint transition studies.

### 5) Score-state bins

- Derive score differential and pressure windows (`tied`, `within_2`, `20_plus`).
- Keep both raw values and binned values so downstream consumers can choose granularity.

## QA Checks

- Treat (`match_id`, `point_id`) as the rally key; never rely on `point_id` alone.
- Check sequence continuity inside rallies before creating lag/lead features.
- Validate that derived setter IDs exist in lineup columns for the same row.
- Do not overwrite event intent already encoded in scout `code`.

## Primary Sources

- `docs/skills/sources.md` (OpenVolley data augmentation and filtering snippets).
