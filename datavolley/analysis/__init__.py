# datavolley/analysis/__init__.py

from typing import Dict, List, Optional


# Attacks
def get_combos_by_type(attack_combinations: List[Dict], attack_type: str) -> List[Dict]:
    """
    Get all attack combinations of a specific type.

    Args:
        attack_combinations: List from extract_attack_combinations()
        attack_type: Type to filter by (H, Q, M, etc.)

    Returns:
        List of matching attack combinations
    """
    return [combo for combo in attack_combinations if combo.get("type") == attack_type]


def get_combos_by_zone(attack_combinations: List[Dict], zone: int) -> List[Dict]:
    """
    Get all attack combinations for a specific zone.

    Args:
        attack_combinations: List from extract_attack_combinations()
        zone: Zone number to filter by

    Returns:
        List of matching attack combinations
    """
    return [combo for combo in attack_combinations if combo.get("zone") == zone]


def get_combo_by_code(attack_combinations: List[Dict], code: str) -> Optional[Dict]:
    """
    Get a specific attack combination by its code.

    Args:
        attack_combinations: List from extract_attack_combinations()
        code: Attack combination code (V5, X9, etc.)

    Returns:
        Attack combination dictionary or None if not found
    """
    for combo in attack_combinations:
        if combo.get("code") == code:
            return combo
    return None


def get_combo_summary(attack_combinations: List[Dict]) -> Dict:
    """
    Get summary statistics of attack combinations.

    Args:
        attack_combinations: List from extract_attack_combinations()

    Returns:
        Dictionary with summary information
    """
    if not attack_combinations:
        return {}

    # Count by type
    type_counts = {}
    zone_counts = {}
    direction_counts = {}

    for combo in attack_combinations:
        # Count types
        combo_type = combo.get("type")
        if combo_type:
            type_counts[combo_type] = type_counts.get(combo_type, 0) + 1

        # Count zones
        zone = combo.get("zone")
        if zone is not None:
            zone_counts[zone] = zone_counts.get(zone, 0) + 1

        # Count directions
        direction = combo.get("direction")
        if direction:
            direction_counts[direction] = direction_counts.get(direction, 0) + 1

    return {
        "total_combinations": len(attack_combinations),
        "by_type": type_counts,
        "by_zone": zone_counts,
        "by_direction": direction_counts,
        "all_codes": [
            combo.get("code") for combo in attack_combinations if combo.get("code")
        ],
    }


# Code
def get_skill_description(skill_code: str) -> Optional[str]:
    """
    Get human-readable description for skill codes.

    Args:
        skill_code: Single character skill code (S, R, E, A, D, B, F, p)

    Returns:
        Human-readable skill description or None if unknown
    """
    skill_descriptions = {
        "S": "Serve",
        "R": "Reception",
        "E": "Set",
        "A": "Attack",
        "D": "Dig",
        "B": "Block",
        "F": "Freeball",
        "p": "Point",
    }

    return skill_descriptions.get(skill_code)


# Players
def get_player_by_number(
    players_data: Dict[str, List[Dict]], team: str, number: int
) -> Optional[Dict]:
    """
    Get a player by their jersey number.

    Args:
        players_data: Dictionary from extract_players()
        team: 'home' or 'visiting'
        number: Player jersey number

    Returns:
        Player dictionary or None if not found
    """
    if team not in players_data:
        return None

    for player in players_data[team]:
        try:
            if int(player["player_number"]) == number:
                return player
        except (ValueError, TypeError):
            continue

    return None


def get_starting_lineup(players_data: Dict[str, List[Dict]], team: str) -> List[Dict]:
    """
    Get the starting lineup for a team (typically first 6 players with valid numbers).

    Args:
        players_data: Dictionary from extract_players()
        team: 'home' or 'visiting'

    Returns:
        List of starting player dictionaries
    """
    if team not in players_data:
        return []

    # Filter players with valid numbers and sort by number
    valid_players = []
    for player in players_data[team]:
        try:
            player_num = int(player["player_number"])
            if player_num > 0:  # Valid jersey number
                valid_players.append((player_num, player))
        except (ValueError, TypeError):
            continue

    # Sort by jersey number and return first 6
    valid_players.sort(key=lambda x: x[0])
    return [player[1] for player in valid_players[:6]]


def get_players_by_team(
    players_data: Dict[str, List[Dict]], team_name: str
) -> List[Dict]:
    """
    Get all players for a specific team by team name.

    Args:
        players_data: Dictionary from extract_players()
        team_name: Name of the team to filter by

    Returns:
        List of player dictionaries
    """
    all_players = []
    for team_players in players_data.values():
        for player in team_players:
            if player.get("team") == team_name:
                all_players.append(player)
    return all_players


# Sets
def get_setter_call_summary(setter_calls: List[Dict]) -> Dict:
    """
    Get summary statistics of setter calls.

    Args:
        setter_calls: List from extract_setter_calls()

    Returns:
        Dictionary with summary information
    """
    if not setter_calls:
        return {}

    # Count calls with additional codes
    calls_with_codes = len(get_calls_with_additional_codes(setter_calls))

    # Collect all descriptions
    descriptions = [
        call.get("description") for call in setter_calls if call.get("description")
    ]

    # Collect all codes
    all_codes = [call.get("code") for call in setter_calls if call.get("code")]

    return {
        "total_setter_calls": len(setter_calls),
        "calls_with_additional_codes": calls_with_codes,
        "all_codes": all_codes,
        "all_descriptions": descriptions,
    }


def get_calls_with_additional_codes(setter_calls: List[Dict]) -> List[Dict]:
    """
    Get setter calls that have additional codes defined.

    Args:
        setter_calls: List from extract_setter_calls()

    Returns:
        List of setter calls with additional codes
    """
    return [
        call
        for call in setter_calls
        if call.get("additional_codes_list") and len(call["additional_codes_list"]) > 0
    ]


def get_call_by_code(setter_calls: List[Dict], code: str) -> Optional[Dict]:
    """
    Get a specific setter call by its code.

    Args:
        setter_calls: List from extract_setter_calls()
        code: Setter call code (K1, KM, etc.)

    Returns:
        Setter call dictionary or None if not found
    """
    for call in setter_calls:
        if call.get("code") == code:
            return call
    return None


# Teams
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
