# Skill 02: File Validation

This skill defines how parsed records are checked and normalized without surprising users.
It supports lenient defaults for analyst workflows and strict mode for production gates.
It prioritizes typed outputs plus explicit issue collection over silent coercion.

## Focus Areas

- Validate heterogeneous input (`str`, `int`, `float`, `None`) into predictable types.
- Preserve nullable behavior for incomplete players, teams, and coordinate fields.
- Derive missing zone information from `code` when explicit zone fields are absent.
- Return per-row, per-field issues for quality tracking and debugging.

## Validation Modes

- `lenient`: continue processing and collect validation issues.
- `strict`: raise on invalid records to enforce schema guarantees.

## Expected Outputs

- Normalized plays suitable for aggregation and model pipelines.
- Issue artifacts that can be inspected without rerunning parsing logic.

## Primary Sources

- `docs/skills/sources.md` (OpenVolley snippets on file validation, package docs).
