# datavolley/core/players.py

import random
import re
import string
from typing import Dict, List, Optional


def extract_teams(raw_content: str) -> Dict:
    """
    Extract team data from DVW file content.

    This is a lightweight version to avoid circular imports.
    For full team functionality, use teams.extract_teams()

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
            parts = line.split(";")
            if len(parts) >= 2:
                if i == 0:
                    teams_data["team_1"] = parts[1] if parts[1] else None
                elif i == 1:
                    teams_data["team_2"] = parts[1] if parts[1] else None

    return teams_data


def extract_players(raw_content: str) -> Dict[str, List[Dict]]:
    """
    Extract player data from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        Dictionary with 'home' and 'visiting' team players
    """
    teams = extract_teams(raw_content)
    players = {"home": [], "visiting": []}

    # Extract home team players [3PLAYERS-H]
    home_pattern = r"\[3PLAYERS-H\](.*?)(?=\[3PLAYERS-V\]|\[3|\n\n|$)"
    home_match = re.search(home_pattern, raw_content, re.DOTALL)

    if home_match:
        home_section = home_match.group(1).strip()
        players["home"] = parse_player_lines(home_section, teams.get("team_1", "Home"))

    # Extract visiting team players [3PLAYERS-V]
    visiting_pattern = r"\[3PLAYERS-V\](.*?)(?=\[3|\n\n|$)"
    visiting_match = re.search(visiting_pattern, raw_content, re.DOTALL)

    if visiting_match:
        visiting_section = visiting_match.group(1).strip()
        players["visiting"] = parse_player_lines(
            visiting_section, teams.get("team_2", "Visiting")
        )

    return players


def parse_player_lines(section_content: str, team: str) -> List[Dict]:
    """
    Parse individual player lines from a team section.

    Args:
        section_content: Raw text content of player section
        team: Team name

    Returns:
        List of player dictionaries
    """
    players = []
    lines = [line.strip() for line in section_content.split("\n") if line.strip()]

    for line in lines:
        player_data = parse_single_player(line, team)
        if player_data:
            players.append(player_data)

    return players


def parse_single_player(line: str, team: str) -> Optional[Dict]:
    """
    Parse a single player line split by semicolons.

    Args:
        line: Single player data line
        team: Team name

    Returns:
        Dictionary with player information or None if invalid
    """
    # Split by semicolon
    parts = line.split(";")

    # DVW player lines typically have around 18-20 fields
    if len(parts) < 10:
        return None

    try:
        # Extract player number safely
        player_number = parts[1] if len(parts) > 1 and parts[1] else "0"

        # Extract player ID safely
        player_id = parts[8] if len(parts) > 8 and parts[8] else None
        if not player_id:
            player_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=6)
            )

        # Extract names safely
        last_name = parts[9] if len(parts) > 9 and parts[9] else None
        first_name = parts[10] if len(parts) > 10 and parts[10] else None

        # Create full name
        name_parts = [first_name, last_name]
        full_name = " ".join(str(filter(None, name_parts))) or None

        player = {
            "team": team,
            "player_number": player_number,
            "player_id": player_id,
            "last_name": last_name,
            "first_name": first_name,
            "role": parts[12] if len(parts) > 12 and parts[12] else None,
            "full_name": full_name,
        }

        return player

    except (ValueError, IndexError) as e:
        print(f"Error parsing player line: {line}")
        print(f"Error: {e}")
        return None
