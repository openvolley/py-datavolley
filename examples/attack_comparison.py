"""
Example: Compare different attack codes side-by-side.

Shows attack patterns for multiple attack codes on separate subplots.
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

import datavolley as dv

data = dv.read_dv(dv.example_file())

attack_codes = ["X5", "X6", "V5", "V6"]

fig, axes = plt.subplots(2, 2, figsize=(12, 14))
axes = axes.flatten()

attacks = [p for p in data if p.get("skill") == "Attack"]

for idx, attack_code in enumerate(attack_codes):
    ax = axes[idx]

    code_attacks = [p for p in attacks if p.get("attack_code") == attack_code]

    coords = []
    for attack in code_attacks:
        if all(
            [
                attack.get("start_coordinate_x") is not None,
                attack.get("start_coordinate_y") is not None,
                attack.get("end_coordinate_x") is not None,
                attack.get("end_coordinate_y") is not None,
            ]
        ):
            coords.append(
                {
                    "start_x": attack["start_coordinate_x"],
                    "start_y": attack["start_coordinate_y"],
                    "end_x": attack["end_coordinate_x"],
                    "end_y": attack["end_coordinate_y"],
                }
            )

    dv.dv_court(zones=True, ax=ax)

    for coord in coords:
        ax.scatter(
            coord["start_x"], coord["start_y"], color="red", s=30, alpha=0.5, zorder=5
        )
        ax.scatter(
            coord["end_x"], coord["end_y"], color="blue", s=30, alpha=0.5, zorder=5
        )
        ax.plot(
            [coord["start_x"], coord["end_x"]],
            [coord["start_y"], coord["end_y"]],
            color="gray",
            linestyle="--",
            linewidth=0.8,
            alpha=0.4,
            zorder=4,
        )

    description = dv.dv_attack_code2desc([attack_code])[attack_code]
    ax.set_title(f"{attack_code}: {description}\n(n={len(coords)})")

plt.tight_layout()
plt.savefig("attack_comparison.png", dpi=150, bbox_inches="tight")
print("Saved attack_comparison.png")
print("Open attack_comparison.png to view the plot")
