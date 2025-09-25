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
