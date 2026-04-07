# Skill 08: Court Location and Visuals

This skill defines how location data is represented and plotted consistently.
It aligns zones, subzones, cones, and coordinates to one court reference frame.
It ensures spatial visuals remain faithful to scouting intent.

## Location Systems

- Zones/subzones: categorical locations used across all skills.
- Cones: attack-direction coding used as directional sectors instead of end zones.
- Coordinates: fine-grained point locations (`start`, `mid`, `end`) stored per event.

## Canonical Plotting Conventions

- Convert all locations to a shared x/y court frame before plotting.
- Keep team direction explicit, then normalize orientation only when analysis requires it.
- Preserve whether a file was cone-coded or zone-coded for attacks.

## Direction Normalization

- Mixed-direction files are common, especially in merged datasets.
- Normalize by flipping actions that start on the opposite court half.
- Apply the same flip operation to start, mid, and end coordinates together.

## Plot Types and When to Use Them

- Zone/subzone heat tiles: coarse tactical distribution and tendency views.
- Line segments/arrows: serve and attack trajectories.
- Cone polygons or arrows: directional attack profiling.
- KDE heatmaps: smoothed density for high-volume coordinate datasets.

## Mid-Coordinate Handling

- Use mid-coordinates when available to avoid misleading straight-line paths.
- Draw two segments (`start -> mid`, `mid -> end`) for deflections or block touches.
- Fall back to `start -> end` only when mid-coordinates are missing.

## QA Checklist

- Confirm coordinate null rates before plotting.
- Spot-check coordinate conversion against known zone locations.
- State orientation choice in chart subtitles or metadata.

## Primary Sources

- `docs/skills/sources.md` (OpenVolley court plotting guidance and examples).
