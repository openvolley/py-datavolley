#!/usr/bin/env python3
"""
Example usage of the datavolley package to extract and parse volleyball match data.

This script demonstrates:
1. Loading a DVW file
2. Extracting plays
3. Parsing play codes
4. Displaying the data in JSON format
"""

import json
import sys
from pathlib import Path
from typing import Dict

# Import the datavolley package
try:
    import datavolley as dv
except ImportError:
    print("Error: datavolley package not found. Make sure it's installed.")
    print("You can install it using: pip install -e .")
    sys.exit(1)


def format_play_data(play: Dict, raw_content: str) -> Dict:
    """
    Format a play dictionary with parsed code information.

    Args:
        play: Play dictionary from extract_plays()
        raw_content: Raw DVW file content for code parsing

    Returns:
        Formatted play dictionary with parsed code
    """
    formatted_play = {
        "line_number": play.get("line_number"),
        "code": play.get("code"),
        "set_number": play.get("set_number"),
        "video_time": play.get("video_time"),
        "home_score": play.get("home_score"),
        "visiting_score": play.get("visiting_score"),
    }

    # Parse the play code if available
    if play.get("code"):
        parsed_code = dv.parse_play_code(raw_content, play["code"])
        if parsed_code:
            formatted_play["parsed_code"] = {
                "team": parsed_code.get("team"),
                "player_number": parsed_code.get("player_number"),
                "player_name": parsed_code.get("player_name"),
                "skill": parsed_code.get("skill"),
                "evaluation_code": parsed_code.get("evaluation_code"),
                "attack_code": parsed_code.get("attack_code"),
                "set_code": parsed_code.get("set_code"),
                "start_zone": parsed_code.get("start_zone"),
                "end_zone": parsed_code.get("end_zone"),
                "skill_subtype": parsed_code.get("skill_subtype"),
            }

    # Add rotation data if available
    rotation_data = {}

    # Home team positions
    home_positions = []
    for i in range(1, 7):
        pos_key = f"home_p{i}"
        if pos_key in play and play[pos_key]:
            home_positions.append(play[pos_key])
    if home_positions:
        rotation_data["home_rotation"] = home_positions

    # Visiting team positions
    visiting_positions = []
    for i in range(1, 7):
        pos_key = f"visiting_p{i}"
        if pos_key in play and play[pos_key]:
            visiting_positions.append(play[pos_key])
    if visiting_positions:
        rotation_data["visiting_rotation"] = visiting_positions

    if rotation_data:
        formatted_play["rotations"] = rotation_data

    return formatted_play


def main():
    """Main function to demonstrate datavolley package usage."""

    print("=" * 60)
    print("DataVolley Package Demo - Play Extraction and Parsing")
    print("=" * 60)
    print()

    # Try to use the example file if available, otherwise look for a DVW file
    dvw_file = None

    # Option 1: Try to use the package's example file
    try:
        dvw_file = dv.example_file()
        if not Path(dvw_file).exists():
            dvw_file = None
    except Exception:
        pass

    # Option 2: Look for example_match.dvw in the current directory
    if not dvw_file:
        current_dir = Path.cwd()
        dvw_file = current_dir / "example_match.dvw"

    # Option 3: Look for any .dvw file in the current directory
    if not dvw_file:
        dvw_files = list(current_dir.glob("*.dvw"))
        if dvw_files:
            dvw_file = str(dvw_files[0])

    if not dvw_file:
        print("Error: No DVW file found.")
        print("Please provide a DVW file in the current directory.")
        sys.exit(1)

    print(f"Loading DVW file: {Path(dvw_file).name}")
    print("-" * 40)

    try:
        # Load the DVW file
        match_data = dv.load_dvw(dvw_file)

        # Get match summary
        summary = dv.get_match_summary(match_data)

        print(f"Match: {summary['teams']['home']} vs {summary['teams']['visiting']}")
        print(f"Date: {summary['date']}")
        print(
            f"Final Score: {summary['final_score']['home_sets']}-{summary['final_score']['visiting_sets']}"
        )
        print(f"Winner: {summary['winner']}")
        print(f"Total Plays: {summary['total_plays']}")
        print()

        # Extract plays
        plays = match_data.get("plays", [])

        if not plays:
            print("No plays found in the DVW file.")
            return

        # Filter plays with actual play codes (exclude score-only entries)
        play_codes = [
            p
            for p in plays
            if p.get("code")
            and not p["code"].startswith(("*p", "ap", "ac", "*c", "**"))
        ]

        if not play_codes:
            print("No play codes found in the DVW file.")
            return

        print(f"Found {len(play_codes)} plays with codes")
        print()

        # Read the raw content for parsing
        with open(dvw_file, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Select first 5 plays with codes (or fewer if not available)
        sample_plays = play_codes[:5]

        print(f"Displaying first {len(sample_plays)} plays with parsed codes:")
        print("=" * 60)
        print()

        # Format and display each play
        formatted_plays = []
        for i, play in enumerate(sample_plays, 1):
            print(f"Play #{i}")
            print("-" * 40)

            formatted_play = format_play_data(play, raw_content)
            formatted_plays.append(formatted_play)

            # Pretty print the JSON
            print(json.dumps(formatted_play, indent=2, default=str))
            print()

        # Save to a JSON file
        output_file = "sample_plays.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "match_info": {
                        "teams": summary["teams"],
                        "date": str(summary["date"]),
                        "final_score": summary["final_score"],
                        "winner": summary["winner"],
                    },
                    "sample_plays": formatted_plays,
                },
                f,
                indent=2,
                default=str,
            )

        print("=" * 60)
        print(f"Sample plays saved to: {output_file}")
        print()

        # Show some statistics
        print("Play Statistics:")
        print("-" * 40)

        # Count skills
        skill_counts = {}
        for play in play_codes:
            parsed = dv.parse_play_code(raw_content, play["code"])
            if parsed and parsed.get("skill"):
                skill = parsed["skill"]
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        print("Skills distribution:")
        for skill, count in sorted(
            skill_counts.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {skill}: {count}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing DVW file: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
