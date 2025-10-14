"""
Example script demonstrating the plotting capabilities of py-datavolley.

This shows how to:
1. Draw a basic volleyball court
2. Create heatmaps from match data
3. Plot specific plays on the court
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

import datavolley as dv

data = dv.read_dv(dv.example_file())

fig, axes = plt.subplots(2, 3, figsize=(12, 14))

ax1 = axes[0, 0]
dv.dv_court(ax=ax1)
ax1.set_title("Basic Full Court")

ax2 = axes[0, 1]
dv.dv_court(half=True, ax=ax2)
ax2.set_title("Half Court")

ax3 = axes[0, 2]
dv.dv_court(zones=True, zone_labels=True, ax=ax3)
ax3.set_title("Court with Zone Labels")

serves = [p for p in data if p.get("skill") == "Serve"]
serve_coords = [
    (p.get("end_coordinate_x"), p.get("end_coordinate_y"))
    for p in serves
    if p.get("end_coordinate_x") is not None
]

if serve_coords:
    ax4 = axes[1, 0]
    dv.dv_heatmap(serve_coords, zones=True, ax=ax4)
    ax4.set_title(f"Serve Landing Zones ({len(serve_coords)} serves)")

attacks = [p for p in data if p.get("skill") == "Attack"]
attack_coords = [
    (p.get("end_coordinate_x"), p.get("end_coordinate_y"))
    for p in attacks
    if p.get("end_coordinate_x") is not None
]

if attack_coords:
    ax5 = axes[1, 1]
    dv.dv_heatmap(attack_coords, zones=True, ax=ax5)
    ax5.set_title(f"Attack Landing Zones ({len(attack_coords)} attacks)")

if attack_coords:
    ax6 = axes[1, 2]
    dv.dv_heatmap(
        attack_coords, subzones=True, threshold_mid=5, threshold_high=15, ax=ax6
    )
    ax6.set_title("Attack Subzones (Detailed)")

plt.tight_layout()
plt.savefig("court_examples.png", dpi=150, bbox_inches="tight")
print("Saved court_examples.png")
print("Open court_examples.png to view the plot")
