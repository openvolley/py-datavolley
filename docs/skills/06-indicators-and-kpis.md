# Skill 06: Indicators and KPIs

This skill standardizes KPI definitions so results are comparable across analysts and reports.
It documents formulas, denominators, and context assumptions for each metric.
It separates observed rates from expected-value rates to avoid interpretation drift.

## KPI Definition Rules

- Every KPI must define numerator, denominator, and required filters.
- Every KPI must state whether it is rally-level, touch-level, player-level, or team-level.
- Every KPI should declare sample-size guidance for stable interpretation.

## Core KPIs

### Expected Sideout Rate

- Build a reference table: `P(receiving team wins rally | reception evaluation = r)`.
- Assign each reception a lookup value from that table.
- Expected sideout for player/team is the mean of those lookup values.

### Expected Breakpoint Rate

- Build a reference table: `P(serving team wins rally | serve evaluation = r)`.
- Assign each serve a lookup value from that table.
- Expected breakpoint for player/team is the mean of those lookup values.

### Set Assist Rate

- Count set rows where the next same-team attack is a winning attack.
- Formula: `assist_rate = assisted_kills / total_sets`.
- Note: this assumes set and attack touches are both reliably scouted.

### Attack Efficiency and Efficacy Variants

- Efficiency baseline: `(kills - attack_errors - blocked) / attack_attempts`.
- Efficacy variant can include continuation outcomes, e.g. positive minus negative continuations.
- Keep naming explicit when using custom variants (`efficiency_std`, `efficacy_continuation`).

## Denominator and Label Hygiene

- Normalize evaluation labels before computing KPIs across mixed data sources.
- Keep phase-aware KPI variants separate from totals (`Reception`, `Transition`).
- Publish denominator counts beside KPI values in all reports.

## QA Checklist

- Verify reference data window for expected metrics (league/season context).
- Recompute KPI values from raw rows in spot checks.
- Flag metrics with low sample sizes rather than hiding them.

## Primary Sources

- `docs/skills/sources.md` (OpenVolley indicators/statistics snippets and metric references).
