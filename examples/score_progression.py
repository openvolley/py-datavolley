"""Generate the README preview and interactive GitHub Pages demo.

Run from the repository root:
    uv run --extra viz python examples/score_progression.py
"""

from pathlib import Path

from lets_plot import (
    aes,
    facet_wrap,
    geom_step,
    ggplot,
    ggsize,
    labs,
    theme,
    theme_minimal,
)

import datavolley as dv


def main():
    points = [play for play in dv.read_plays(dv.example_file()) if play["point"]]
    rows = {"set": [], "rally": [], "team": [], "score": []}
    for play in points:
        set_label = f"Set {play['set_number']}"
        teams = [play["home_team"], play["visiting_team"]]
        if play["rally_number"] == 1:
            rows["set"] += [set_label] * 2
            rows["rally"] += [0, 0]
            rows["team"] += teams
            rows["score"] += [0, 0]
        rows["set"] += [set_label] * 2
        rows["rally"] += [play["rally_number"]] * 2
        rows["team"] += teams
        rows["score"] += [play["home_team_score"], play["visiting_team_score"]]

    fig = (
        ggplot(rows, aes("rally", "score", color="team"))
        + geom_step()
        + facet_wrap("set", ncol=3, scales="free_x")
        + labs(title="Score progression by set", x="Rally", y="Score", color="Team")
        + theme_minimal()
        + theme(legend_position="bottom")
        + ggsize(960, 400)
    )

    output_dir = Path(__file__).resolve().parents[1] / "docs"
    output_dir.mkdir(exist_ok=True)
    html_path = output_dir / "index.html"
    html = "\n".join(line.rstrip() for line in fig.to_html().splitlines()) + "\n"
    html_path.write_text(html, encoding="utf-8", newline="\n")
    print(html_path)
    print(fig.to_png(str(output_dir / "score-progression.png")))


if __name__ == "__main__":
    main()
