# datavolley/core/setter_calls.py

import re
from typing import Dict, List, Optional


def extract_setter_calls(raw_content: str) -> List[Dict]:
    """
    Extract setter call data from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        List of setter call dictionaries
    """
    # Find the [3SETTERCALL] section that ends at the next [3 section
    setter_pattern = r"\[3SETTERCALL\](.*?)(?=\[3|\n\n|$)"
    match = re.search(setter_pattern, raw_content, re.DOTALL)

    if not match:
        return []

    setter_section = match.group(1).strip()
    lines = [line.strip() for line in setter_section.split("\n") if line.strip()]

    setter_calls = []

    # Parse each setter call line
    for line in lines:
        if line:
            call_data = parse_setter_call_line(line)
            if call_data:
                setter_calls.append(call_data)

    return setter_calls


def parse_setter_call_line(line: str) -> Optional[Dict]:
    """
    Parse a single setter call line split by semicolons.

    Args:
        line: Single setter call data line

    Returns:
        Dictionary with setter call information or None if invalid
    """
    # Split by semicolon
    parts = line.split(";")

    # Need at least the basic fields
    if len(parts) < 3:
        return None

    try:
        call_data = {
            "code": parts[0] if parts[0] else None,  # K1, KM, etc.
            "field_1": parts[1] if len(parts) > 1 else None,  # Usually empty
            "description": parts[2] if parts[2] else None,  # Quick ahead, Push, etc.
            "field_3": parts[3] if len(parts) > 3 else None,  # Usually empty
            "color_code": int(parts[4])
            if len(parts) > 4 and parts[4].isdigit()
            else None,  # Color coding
            "position_1": int(parts[5])
            if len(parts) > 5 and parts[5].isdigit()
            else None,  # Position info
            "position_2": int(parts[6])
            if len(parts) > 6 and parts[6].isdigit()
            else None,  # Position info
            "position_3": int(parts[7])
            if len(parts) > 7 and parts[7].isdigit()
            else None,  # Position info
            "additional_codes": parts[8]
            if len(parts) > 8 and parts[8]
            else None,  # Additional codes (comma-separated)
            "field_9": int(parts[9])
            if len(parts) > 9 and parts[9].isdigit()
            else None,  # Additional field
            "raw_data": parts,
        }

        # Parse additional codes if present (comma-separated values)
        if call_data["additional_codes"]:
            call_data["additional_codes_list"] = [
                code.strip()
                for code in call_data["additional_codes"].split(",")
                if code.strip()
            ]
        else:
            call_data["additional_codes_list"] = []

        return call_data

    except (ValueError, IndexError) as e:
        print(f"Error parsing setter call line: {line}")
        print(f"Error: {e}")
        return None


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


# Example usage function
def demo_setter_calls_extraction():
    """Demo function showing how to use the setter calls extraction."""

    # This would normally be loaded from your DVW file
    with open("example_match.dvw", "r") as f:
        content = f.read()

    # Extract setter calls
    setter_calls = extract_setter_calls(content)

    print("SETTER CALLS:")
    print("-" * 80)
    print(f"Total setter calls found: {len(setter_calls)}")
    print()

    # Show all setter calls
    for i, call in enumerate(setter_calls):
        code = call.get("code", "N/A")
        description = call.get("description", "N/A")
        additional_codes = call.get("additional_codes", "")
        color_code = call.get("color_code", "N/A")

        print(
            f"{i + 1:2}. {code:3} | {description:15} | Color: {color_code:8} | Additional: {additional_codes}"
        )

        # Show position info if available
        pos1 = call.get("position_1")
        pos2 = call.get("position_2")
        pos3 = call.get("position_3")
        if any([pos1, pos2, pos3]):
            positions = [str(p) for p in [pos1, pos2, pos3] if p is not None]
            print(f"     Positions: {', '.join(positions)}")

        # Show parsed additional codes
        if call.get("additional_codes_list"):
            print(f"     Additional codes: {call['additional_codes_list']}")

        print()

    # Show summary
    summary = get_setter_call_summary(setter_calls)
    print("SUMMARY:")
    print("-" * 40)
    print(f"Total setter calls: {summary.get('total_setter_calls', 0)}")
    print(
        f"Calls with additional codes: {summary.get('calls_with_additional_codes', 0)}"
    )

    print("\nAll codes:")
    for code in summary.get("all_codes", []):
        print(f"  {code}")

    print("\nAll descriptions:")
    for desc in summary.get("all_descriptions", []):
        print(f"  {desc}")

    # Test specific lookups
    print("\nSPECIFIC LOOKUPS:")
    print("-" * 40)

    # Look up a specific call
    k1_call = get_call_by_code(setter_calls, "K1")
    if k1_call:
        print(f"K1 Call: {k1_call['description']}")
        if k1_call.get("additional_codes_list"):
            print(f"  Additional codes: {k1_call['additional_codes_list']}")

    # Get calls with additional codes
    calls_with_codes = get_calls_with_additional_codes(setter_calls)
    print(f"\nCalls with additional codes: {len(calls_with_codes)}")
    for call in calls_with_codes:
        print(
            f"  {call['code']}: {call['description']} -> {call['additional_codes_list']}"
        )


if __name__ == "__main__":
    demo_setter_calls_extraction()
