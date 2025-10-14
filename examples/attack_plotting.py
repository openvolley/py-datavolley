"""
Example: Plotting attack trajectories on the volleyball court.

This shows how to:
1. Filter attacks by attack code
2. Plot start and end coordinates
3. Draw trajectory lines between points
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

import datavolley as dv

data = dv.read_dv(dv.example_file())

attacks = [p for p in data if p.get("skill") == "Attack"]
x5_attacks = [p for p in attacks if p.get("attack_code") == "X5"]

print(f"Total attacks: {len(attacks)}")
print(f"X5 attacks: {len(x5_attacks)}")

coords = []
for attack in x5_attacks:
    if all([
        attack.get("start_coordinate_x") is not None,
        attack.get("start_coordinate_y") is not None,
        attack.get("end_coordinate_x") is not None,
        attack.get("end_coordinate_y") is not None,
    ]):
        coords.append({
            "start_x": attack["start_coordinate_x"],
            "start_y": attack["start_coordinate_y"],
            "end_x": attack["end_coordinate_x"],
            "end_y": attack["end_coordinate_y"],
            "evaluation": attack.get("evaluation_code"),
        })

print(f"X5 attacks with complete coordinates: {len(coords)}")

fig, ax = plt.subplots(figsize=(6, 10))

dv.dv_court(zones=True, ax=ax)

for coord in coords:
    ax.scatter(
        coord["start_x"], coord["start_y"], color="red", s=50, alpha=0.6, zorder=5
    )
    ax.scatter(coord["end_x"], coord["end_y"], color="blue", s=50, alpha=0.6, zorder=5)
    ax.plot(
        [coord["start_x"], coord["end_x"]],
        [coord["start_y"], coord["end_y"]],
        color="gray",
        linestyle="--",
        linewidth=1,
        alpha=0.5,
        zorder=4,
    )

ax.scatter([], [], color="red", s=50)
ax.scatter([], [], color="blue", s=50)
ax.legend(loc="upper right")

ax.set_title(f"X5 Attack Trajectories (n={len(coords)})")

plt.tight_layout()
plt.savefig("x5_attacks.png", dpi=150, bbox_inches="tight")
print("Saved x5_attacks.png")
print("Open x5_attacks.png to view the plot")
