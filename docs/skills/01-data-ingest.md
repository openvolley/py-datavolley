# Skill 01: Data Ingest

This skill defines how raw volleyball scouting files become parseable event records and metadata.
It emphasizes resilience across partial files, inconsistent tags, and mixed value types.
It treats scout `code` strings as canonical when field-level values are missing or contradictory.

## Focus Areas

- Read `.dvw`, XML, and VSM-like exports with consistent entry points. -XML VSM currently missing-
- Extract match-level metadata (teams, set info, roster references, score context).
- Keep raw values available for later derivation instead of over-normalizing early.
- Preserve row order and index traceability for downstream QA and issue reporting.

## Expected Outputs

- A play/event list that can be validated or analyzed immediately.
- Match metadata packaged with enough context for augmentation steps.
- Structured parse issues when strict schema assumptions cannot be met.

## Primary Sources

- `docs/skills/sources.md` (DataVolley handbooks, OpenVolley parsing references).
