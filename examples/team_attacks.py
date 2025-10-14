"""
Example: Filter and plot attacks by team.

Compare attack patterns between two teams.
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

import datavolley as dv

data = dv.read_dv(dv.example_file())

attacks = [p for p in data if p.get("skill") == "Attack"]

if attacks:
    team1 = attacks[0].get("home_team", "Team 1")
    team2 = attacks[0].get("visiting_team", "Team 2")
else:
    team1, team2 = "Team 1", "Team 2"

team1_attacks = [p for p in attacks if p.get("team") == team1]
team2_attacks = [p for p in attacks if p.get("team") == team2]

team1_coords = [
    (p["end_coordinate_x"], p["end_coordinate_y"])
    for p in team1_attacks
    if p.get("end_coordinate_x") is not None
]

team2_coords = [
    (p["end_coordinate_x"], p["end_coordinate_y"])
    for p in team2_attacks
    if p.get("end_coordinate_x") is not None
]

print(f"{team1}: {len(team1_attacks)} attacks")
print(f"{team2}: {len(team2_attacks)} attacks")

fig, axes = plt.subplots(1, 2, figsize=(10, 7))

if team1_coords:
    dv.dv_heatmap(
        team1_coords,
        zones=True,
        threshold_mid=5,
        threshold_high=15,
        ax=axes[0],
    )
    axes[0].set_title(f"{team1}\nAttack Landing Zones\n(n={len(team1_coords)})")
else:
    dv.dv_court(zones=True, ax=axes[0])
    axes[0].set_title(f"{team1}\nNo attack data")

if team2_coords:
    dv.dv_heatmap(
        team2_coords,
        zones=True,
        threshold_mid=5,
        threshold_high=15,
        ax=axes[1],
    )
    axes[1].set_title(f"{team2}\nAttack Landing Zones\n(n={len(team2_coords)})")
else:
    dv.dv_court(zones=True, ax=axes[1])
    axes[1].set_title(f"{team2}\nNo attack data")

plt.tight_layout()
plt.savefig("team_attacks.png", dpi=150, bbox_inches="tight")
print("Saved team_attacks.png")
print("Open team_attacks.png to view the plot")
