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

# Skills Knowledge Base

This directory is the canonical home for skills documentation in this repository.
Each file defines one analyst workflow area with scope, focus, and references.
Use this index first, then go deeper into the individual skill documents.

## Skill Index

- `01-data-ingest.md`: Parse raw DataVolley-style sources into stable event structures.
- `02-file-validation.md`: Validate and normalize mixed-type records with lenient and strict modes.
- `03-data-augmentation.md`: Add rally context, phases, and derived fields for analysis.
- `04-feature-engineering.md`: Build deterministic feature columns from sequence and lineup state.
- `05-filtering-and-analysis-recipes.md`: Reusable analyst filters for common tactical questions.
- `06-indicators-and-kpis.md`: KPI formulas with explicit denominators and assumptions.
- `07-modeling-patterns.md`: xK-style modeling workflows with leakage-safe evaluation.
- `08-court-location-and-visuals.md`: Court-space conventions for zones, coordinates, and plots.

## Supporting Docs

- `sources.md`: Curated source links that informed the skills.
- `backlog.md`: Prioritized implementation backlog for growing the skills harness.
