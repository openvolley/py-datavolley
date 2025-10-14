"""
Example: Create heatmaps for attack start and end locations.

Shows where attacks are set from and where they land.
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

import datavolley as dv

data = dv.read_dv(dv.example_file())

attacks = [p for p in data if p.get("skill") == "Attack"]
x5_attacks = [p for p in attacks if p.get("attack_code") == "X5"]

start_coords = [
    (p["start_coordinate_x"], p["start_coordinate_y"])
    for p in x5_attacks
    if p.get("start_coordinate_x") is not None
]

end_coords = [
    (p["end_coordinate_x"], p["end_coordinate_y"])
    for p in x5_attacks
    if p.get("end_coordinate_x") is not None
]

fig, axes = plt.subplots(1, 2, figsize=(10, 7))

dv.dv_heatmap(
    start_coords,
    zones=True,
    color_low="white",
    color_mid="lightcoral",
    color_high="darkred",
    threshold_mid=3,
    threshold_high=8,
    ax=axes[0],
)
axes[0].set_title(f"X5 \n(n={len(start_coords)})")

dv.dv_heatmap(
    end_coords,
    zones=True,
    color_low="white",
    color_mid="lightblue",
    color_high="darkblue",
    threshold_mid=3,
    threshold_high=8,
    ax=axes[1],
)
axes[1].set_title(f"X5 Landing Zones\n(n={len(end_coords)})")

plt.tight_layout()
plt.savefig("x5_heatmaps.png", dpi=150, bbox_inches="tight")
print("Saved x5_heatmaps.png")
print("Open x5_heatmaps.png to view the plot")
