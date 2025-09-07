# datavolley/core/attack_combos.py

import re
from typing import Dict, List, Optional


def extract_attack_combinations(raw_content: str) -> List[Dict]:
    """
    Extract attack combination data from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        List of attack combination dictionaries
    """
    # Find the [3ATTACKCOMBINATION] section that ends at [3SETTERCALL]
    attack_pattern = r"\[3ATTACKCOMBINATION\](.*?)(?=\[3SETTERCALL\]|\[3|\n\n|$)"
    match = re.search(attack_pattern, raw_content, re.DOTALL)

    if not match:
        return []

    attack_section = match.group(1).strip()
    lines = [line.strip() for line in attack_section.split("\n") if line.strip()]

    attack_combinations = []

    # Parse each attack combination line
    for line in lines:
        if line:
            combo_data = parse_attack_combo_line(line)
            if combo_data:
                attack_combinations.append(combo_data)

    return attack_combinations


def parse_attack_combo_line(line: str) -> Optional[Dict]:
    """
    Parse a single attack combination line split by semicolons.

    Args:
        line: Single attack combination data line

    Returns:
        Dictionary with attack combination information or None if invalid
    """
    # Split by semicolon
    parts = line.split(";")

    # Need at least the basic fields
    if len(parts) < 5:
        return None

    try:
        combo_data = {
            "code": parts[0] if parts[0] else None,  # V5, X9, etc.
            "zone": int(parts[1]) if parts[1].isdigit() else None,  # Zone number
            "position": parts[2] if parts[2] else None,  # R, L, C (Right, Left, Center)
            "type": parts[3] if parts[3] else None,  # H, Q, M, etc. (attack type)
            "description": parts[4] if parts[4] else None,  # Human readable description
            "field_5": parts[5] if len(parts) > 5 else None,  # Usually empty
            "color_code": int(parts[6])
            if len(parts) > 6 and parts[6].isdigit()
            else None,  # Color coding
            "position_code": int(parts[7])
            if len(parts) > 7 and parts[7].isdigit()
            else None,  # Position info
            "set_direction": parts[8]
            if len(parts) > 8 and parts[8]
            else None,  # F, B, P, C, S (Front, Back, Pipe, Center, Setter)
            "backrow": parts[9] == "1"
            if len(parts) > 9 and parts[9]
            else False,  # if 1, True (backrow attack) else False
            "field_10": parts[10] if len(parts) > 10 else None,  # Additional field
            "raw_data": parts,
        }

        return combo_data

    except (ValueError, IndexError) as e:
        print(f"Error parsing attack combo line: {line}")
        print(f"Error: {e}")
        return None


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


# Example usage function
def demo_attack_combos_extraction():
    """Demo function showing how to use the attack combinations extraction."""

    # This would normally be loaded from your DVW file
    with open("example_match.dvw", "r") as f:
        content = f.read()

    # Extract attack combinations
    attack_combos = extract_attack_combinations(content)

    print("ATTACK COMBINATIONS:")
    print("-" * 80)
    print(f"Total combinations found: {len(attack_combos)}")
    print()

    # Show first few combinations
    for i, combo in enumerate(attack_combos[:10]):  # Show first 10
        code = combo.get("code", "N/A")
        zone = combo.get("zone", "N/A")
        direction = combo.get("direction", "N/A")
        combo_type = combo.get("type", "N/A")
        description = combo.get("description", "N/A")
        set_dir = combo.get("set_direction", "N/A")

        print(
            f"{i + 1:2}. {code:3} | Zone: {zone:2} | Dir: {direction} | Type: {combo_type} | Pos: {set_dir} | {description}"
        )

    if len(attack_combos) > 10:
        print(f"... and {len(attack_combos) - 10} more")

    # Show summary
    summary = get_combo_summary(attack_combos)
    print("SUMMARY:")
    print("-" * 40)
    print(f"Total combinations: {summary.get('total_combinations', 0)}")

    print("\nBy Type:")
    for combo_type, count in summary.get("by_type", {}).items():
        print(f"  {combo_type}: {count}")

    print("\nBy Direction:")
    for direction, count in summary.get("by_direction", {}).items():
        direction_name = {"R": "Right", "L": "Left", "C": "Center"}.get(
            direction, direction
        )
        print(f"  {direction_name}: {count}")

    print("\nBy Zone:")
    for zone, count in sorted(summary.get("by_zone", {}).items()):
        print(f"  Zone {zone}: {count}")

    # Test specific lookups
    print("\nSPECIFIC LOOKUPS:")
    print("-" * 40)

    # Look up a specific combo
    v5_combo = get_combo_by_code(attack_combos, "V5")
    if v5_combo:
        print(
            f"V5 Combo: {v5_combo['description']} (Zone {v5_combo['zone']}, {v5_combo['direction']})"
        )

    # Get all quick attacks
    quick_attacks = get_combos_by_type(attack_combos, "Q")
    print(f"Quick attacks (Q): {len(quick_attacks)} combinations")

    # Get all zone 2 attacks
    zone2_attacks = get_combos_by_zone(attack_combos, 2)
    print(f"Zone 2 attacks: {len(zone2_attacks)} combinations")


if __name__ == "__main__":
    demo_attack_combos_extraction()
