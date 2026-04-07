# Skill 03: Data Augmentation

This skill covers turning validated events into richer tactical and contextual features.
It adds derived structure while keeping original values available for auditing.
It enables analysts to move from row-level scouting data to phase-level insights.

## Focus Areas

- Rally segmentation and possession tracking.
- Side-out vs transition phase assignment.
- Score-state tagging (lead/trail/tied and pressure windows).
- Rotation context and lineup-aware annotations.

## Guardrails

- Do not overwrite canonical event intent expressed in scout `code` values.
- Prefer additive fields with explicit naming and lineage.
- Keep augmentation deterministic so repeated runs are reproducible.

## Expected Outputs

- Enriched event data ready for indicators, reporting, and modeling.
- Clear derivation logic that can be versioned and tested.

## Primary Sources

- `docs/skills/sources.md` (OpenVolley augmentation snippets, scouting manuals).
