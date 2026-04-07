# Skill 07: Modeling Patterns

This skill defines practical modeling workflows on top of engineered volleyball event data.
It favors transparent baselines before complex architectures.
It focuses on leakage-safe evaluation and interpretable outputs for analysts and coaches.

## Typical Use Cases

- Expected kill probability (xK-like) for attacks.
- Sideout outcome prediction by reception quality and set context.
- Breakpoint probability under serve pressure profiles.

## Feature Families

- Spatial: set and attack coordinates or zone/subzone representations.
- Sequence: previous skill context, touch order, and phase markers.
- Tactical: attack type, quick availability proxies, and block context.
- Lineup: attacker identity, setter identity, and on-court composition.

## Example xK-Style Pattern

- Label: `kill` vs `not_kill` based on attack evaluation.
- Core predictors: set location, attack type, rally phase, quick-availability indicator.
- Start with logistic regression and tree-based baselines before tuning.

## Split and Evaluation Guidance

- Split by match/date blocks to avoid same-rally leakage across train and test.
- Track ROC-AUC, log loss, calibration, and class-specific precision/recall.
- Keep a fixed baseline model for regression testing across code changes.

## Interpretation Guardrails

- Distinguish prediction quality from tactical causality.
- Report confidence intervals or bootstrap uncertainty when possible.
- Avoid over-reading small segments (single rotation, single opponent, short windows).

## QA Checklist

- Verify no future columns leak into feature generation.
- Confirm label creation logic against raw event examples.
- Store data version and feature schema with model artifacts.

## Primary Sources

- `docs/skills/sources.md` (expected-kills references and OpenVolley modeling examples).
