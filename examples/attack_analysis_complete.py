"""
Complete attack analysis example - similar to your original code.

This demonstrates:
1. Loading data
2. Filtering by skill and attack code
3. Extracting coordinates
4. Plotting trajectories on court
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

import datavolley as dv

print("Loading data...")
data = dv.read_dv(dv.example_file())
print(f"Loaded {len(data)} plays")

print("\nFiltering attacks with attack code 'X5'...")
atk_data = [
    p for p in data if p.get("skill") == "Attack" and p.get("attack_code") == "X5"
]
print(f"Found {len(atk_data)} X5 attacks")

coordinate_data = []
for play in atk_data:
    if all([
        play.get("start_coordinate_x") is not None,
        play.get("start_coordinate_y") is not None,
        play.get("end_coordinate_x") is not None,
        play.get("end_coordinate_y") is not None,
    ]):
        coordinate_data.append({
            "start_coordinate_x": play["start_coordinate_x"],
            "start_coordinate_y": play["start_coordinate_y"],
            "end_coordinate_x": play["end_coordinate_x"],
            "end_coordinate_y": play["end_coordinate_y"],
            "evaluation": play.get("evaluation_code"),
            "player": play.get("player_name"),
        })

print(f"X5 attacks with complete coordinates: {len(coordinate_data)}")


def plot_coordinates(coordinates):
    """
    Plot attack trajectories on a volleyball court.

    Args:
        coordinates: List of dicts with start/end coordinate keys
    """
    fig, ax = plt.subplots(figsize=(6, 10))

    dv.dv_court(zones=True, ax=ax)

    for coord in coordinates:
        ax.scatter(
            coord["start_coordinate_x"],
            coord["start_coordinate_y"],
            color="red",
            s=50,
            alpha=0.6,
            zorder=5,
        )
        ax.scatter(
            coord["end_coordinate_x"],
            coord["end_coordinate_y"],
            color="blue",
            s=50,
            alpha=0.6,
            zorder=5,
        )

        ax.plot(
            [coord["start_coordinate_x"], coord["end_coordinate_x"]],
            [coord["start_coordinate_y"], coord["end_coordinate_y"]],
            color="gray",
            linestyle="--",
            linewidth=1,
            alpha=0.5,
            zorder=4,
        )

    ax.scatter([], [], color="red", s=50)
    ax.scatter([], [], color="blue", s=50)
    ax.legend(loc="upper right")

    attack_desc = dv.dv_attack_code2desc("X5")
    ax.set_title(f"X5 Attack Trajectories\n{attack_desc}\n(n={len(coordinates)})")

    plt.tight_layout()
    return fig, ax


print("\nPlotting coordinates...")
fig, ax = plot_coordinates(coordinate_data)

plt.savefig("x5_attack_trajectories.png", dpi=150, bbox_inches="tight")
print("Saved x5_attack_trajectories.png")
print("Open x5_attack_trajectories.png to view the plot")
