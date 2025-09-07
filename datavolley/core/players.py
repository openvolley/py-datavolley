# datavolley/core/players.py

import re
from typing import Dict, List, Optional


def extract_players(raw_content: str) -> Dict[str, List[Dict]]:
    """
    Extract player data from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        Dictionary with 'home' and 'visiting' team players
    """
    players = {"home": [], "visiting": []}

    # Extract home team players [3PLAYERS-H]
    home_pattern = r"\[3PLAYERS-H\](.*?)(?=\[3PLAYERS-V\]|\[3|\n\n|$)"
    home_match = re.search(home_pattern, raw_content, re.DOTALL)

    if home_match:
        home_section = home_match.group(1).strip()
        players["home"] = parse_player_lines(home_section, team="home")

    # Extract visiting team players [3PLAYERS-V]
    visiting_pattern = r"\[3PLAYERS-V\](.*?)(?=\[3|\n\n|$)"
    visiting_match = re.search(visiting_pattern, raw_content, re.DOTALL)

    if visiting_match:
        visiting_section = visiting_match.group(1).strip()
        players["visiting"] = parse_player_lines(visiting_section, team="visiting")

    return players


def parse_player_lines(section_content: str, team: str) -> List[Dict]:
    """
    Parse individual player lines from a team section.

    Args:
        section_content: Raw text content of player section
        team: 'home' or 'visiting'

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
        team: 'home' or 'visiting'

    Returns:
        Dictionary with player information or None if invalid
    """
    # Split by semicolon
    parts = line.split(";")

    # DVW player lines typically have around 18-20 fields
    if len(parts) < 10:
        return None

    try:
        player = {
            "team": team,
            "team_id": int(parts[0]) if parts[0].isdigit() else None,
            "shirt_number": int(parts[1]) if parts[1].isdigit() else None,
            "player_count_pos": int(parts[2]) if parts[2].isdigit() else None,
            # Starting positions for different sets (parts 3-7)
            "set1_position": parts[3] if parts[3] and parts[3] != "*" else None,
            "set2_position": parts[4] if parts[4] and parts[4] != "*" else None,
            "set3_position": parts[5] if parts[5] and parts[5] != "*" else None,
            "set4_position": parts[6] if parts[6] and parts[6] != "*" else None,
            "set5_position": parts[7] if parts[7] and parts[7] != "*" else None,
            # Player identification (typically around parts 8-12)
            "player_id": parts[8] if len(parts) > 8 else None,
            "last_name": parts[9] if len(parts) > 9 else None,
            "first_name": parts[10] if len(parts) > 10 else None,
            "nickname": parts[11] if len(parts) > 11 else None,
            # Additional fields that might be present
            "role": parts[12] if len(parts) > 12 and parts[12] else None,
            "captain": parts[13] if len(parts) > 13 and parts[13] else None,
            "libero": parts[14] == "True" if len(parts) > 14 else False,
            # Added data
            "full_name": " ".join(
                filter(
                    None,
                    [
                        parts[10] if len(parts) > 10 else None,
                        parts[9] if len(parts) > 9 else None,
                    ],
                )
            )
            or None,
            # Store all raw parts for debugging/future use
            "raw_data": parts,
        }

        return player

    except (ValueError, IndexError) as e:
        print(f"Error parsing player line: {line}")
        print(f"Error: {e}")
        return None


def get_starting_lineup(players: List[Dict], set_number: int = 1) -> List[Dict]:
    """
    Get the starting lineup for a specific set.

    Args:
        players: List of player dictionaries
        set_number: Set number (1-5)

    Returns:
        List of players in starting positions for that set
    """
    position_field = f"set{set_number}_position"

    starting_players = []
    for player in players:
        if player.get(position_field) is not None:
            starting_players.append({**player, "position": player[position_field]})

    # Sort by position
    starting_players.sort(
        key=lambda x: int(x["position"]) if x["position"].isdigit() else 999
    )

    return starting_players


def get_player_by_number(players: List[Dict], shirt_number: int) -> Optional[Dict]:
    """
    Find a player by their shirt number.

    Args:
        players: List of player dictionaries
        shirt_number: Player's shirt number

    Returns:
        Player dictionary or None if not found
    """
    for player in players:
        if player.get("shirt_number") == shirt_number:
            return player
    return None
