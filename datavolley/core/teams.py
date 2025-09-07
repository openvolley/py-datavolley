# datavolley/core/teams.py

import re
from typing import Dict, Optional


def extract_teams(raw_content: str) -> Dict:
    """
    Extract team data from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        Dictionary with team information
    """
    # Find the [3TEAMS] section
    teams_pattern = r"\[3TEAMS\](.*?)(?=\[3|\n\n|$)"
    match = re.search(teams_pattern, raw_content, re.DOTALL)

    if not match:
        return {}

    teams_section = match.group(1).strip()
    lines = [line.strip() for line in teams_section.split("\n") if line.strip()]

    teams_data = {}

    # Parse each team line
    for i, line in enumerate(lines):
        if line:
            team_data = parse_team_line(line)
            if team_data:
                # First team is typically home team (team_1)
                # Second team is typically visiting team (team_2)
                if i == 0:
                    teams_data["team_1_id"] = team_data["team_id"]
                    teams_data["team_1"] = team_data["team_name"]
                elif i == 1:
                    teams_data["team_2_id"] = team_data["team_id"]
                    teams_data["team_2"] = team_data["team_name"]

    return teams_data


def parse_team_line(line: str) -> Optional[Dict]:
    """
    Parse a single team line split by semicolons.

    Args:
        line: Single team data line

    Returns:
        Dictionary with team information or None if invalid
    """
    # Split by semicolon
    parts = line.split(";")

    # Need at least team ID and name
    if len(parts) < 2:
        return None

    try:
        team_data = {
            "team_id": int(parts[0]) if parts[0].isdigit() else None,
            "team_name": parts[1] if len(parts) > 1 and parts[1] else None,
            "score": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None,
            "raw_data": parts,
        }

        return team_data

    except (ValueError, IndexError) as e:
        print(f"Error parsing team line: {line}")
        print(f"Error: {e}")
        return None


def get_team_by_id(teams_data: Dict, team_id: int) -> Optional[str]:
    """
    Get team name by team ID.

    Args:
        teams_data: Dictionary from extract_teams()
        team_id: Team ID to look up

    Returns:
        Team name or None if not found
    """
    if teams_data.get("team_1_id") == team_id:
        return teams_data.get("team_1")
    elif teams_data.get("team_2_id") == team_id:
        return teams_data.get("team_2")
    return None


def get_team_info(teams_data: Dict) -> Dict:
    """
    Get formatted team information.

    Args:
        teams_data: Dictionary from extract_teams()

    Returns:
        Dictionary with formatted team info
    """
    return {
        "home_team": {
            "id": teams_data.get("team_1_id"),
            "name": teams_data.get("team_1"),
        },
        "visiting_team": {
            "id": teams_data.get("team_2_id"),
            "name": teams_data.get("team_2"),
        },
    }
