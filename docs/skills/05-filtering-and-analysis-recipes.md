# Skill 05: Filtering and Analysis Recipes

This skill defines repeatable filtering patterns for common analyst questions.
It focuses on query intent first, then explicit filter logic and denominator rules.
It is designed to reduce one-off slicing mistakes in post-match workflows.

## Recipe 1: Attack After Good or Perfect Reception

- Aim: isolate reception-phase attacks in rallies with strong reception quality.
- Filter: `skill == Attack`, `phase == Reception`, and `reception_quality` in positive/perfect buckets.
- Output: kill rate, error rate, and attack distribution by attacker or rotation.
- Caveat: reception labels vary by data source, so normalize labels before filtering.

## Recipe 2: Players On Court

- Aim: evaluate outcomes for specific lineup combinations.
- Filter: rows where target `player_id` appears in any active lineup slot (`*_player_id1..6`).
- Output: sideout %, breakpoint %, and touch-level rates for lineup windows.
- Caveat: confirm whether IDs are numeric or string-typed before matching.

## Recipe 3: First Transition Attack

- Aim: isolate first attack opportunity by the serving team after reception-phase play.
- Filter: tag first transition at rally level, then keep `skill == Attack` rows where that tag is true.
- Output: first-transition kill %, continuation quality, and block-out rates.
- Caveat: requires coherent `team_touch_id` sequencing within each rally.

## Recipe 4: Rotation and Score-State Slices

- Aim: compare performance by rotation under pressure contexts.
- Filter: segment by setter position/rotation and score bins (`tied`, `within_2`, `20_plus`).
- Output: phase-specific KPIs with confidence intervals or sample-size thresholds.
- Caveat: avoid comparing segments with tiny sample counts.

## Recipe 5: Serve Pressure Tradeoff

- Aim: inspect ace/error tradeoffs by serve type and target.
- Filter: `skill == Serve`, grouped by `skill_type` and destination zone or coordinate buckets.
- Output: ace%, error%, and expected breakpoint rate side by side.
- Caveat: report both raw and expected metrics because sample sizes can be volatile.

## QA Checklist

- Always define denominator at recipe start.
- Keep filters phase-aware (`Reception` vs `Transition`) unless totals are intended.
- Verify that nullable fields are handled explicitly rather than dropped silently.

## Primary Sources

- `docs/skills/sources.md` (OpenVolley filtering/subsetting snippets and examples).
