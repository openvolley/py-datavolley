import re
from datetime import datetime


def _parse_event_time(
    match_date: str | None, event_time: str | None
) -> datetime | None:
    if not match_date or not event_time:
        return None

    try:
        return datetime.strptime(  # noqa: DTZ007 - DVW event clocks have no timezone
            f"{match_date} {event_time}", "%m/%d/%Y %H.%M.%S"
        )
    except ValueError:
        return None


def extract_score_from_code(code: str | None) -> dict | None:
    """
    Extract score information from play codes like *p23:18, ap24:18, etc.
    """
    if not code:
        return None

    # Pattern to match score codes: (*|a)p(digits):(digits)
    score_pattern = r"^[*a]p(\d+):(\d+)$"
    match = re.match(score_pattern, code)

    if match:
        home_score = match.group(1)
        visiting_score = match.group(2)

        return {"home_score": home_score, "visiting_score": visiting_score}

    return None


def parse_play_line(line: str, line_number: int) -> dict | None:
    """
    Parse a single play line split by semicolons.

    Args:
        line: Single play data line
        line_number: Line number for reference

    Returns:
        Dictionary with play information or None if invalid
    """
    # Split by semicolon
    parts = line.split(";")

    try:
        code = parts[0] if parts[0] else None
        home_setter_position = parts[9] if len(parts) > 9 else None
        visiting_setter_position = parts[10] if len(parts) > 10 else None

        custom_code = None
        if code and len(code) > 14:
            last_tilde_idx = code.rfind("~")
            if last_tilde_idx != -1 and last_tilde_idx < len(code) - 1:
                potential_custom = code[last_tilde_idx + 1 :]
                if potential_custom and potential_custom != "":
                    custom_code = potential_custom

        play_data = {
            "line_number": line_number,
            "code": code,
            "time": parts[7] if len(parts) > 7 and parts[7] else None,
            "point_phase": {"p": "Breakpoint", "s": "Sideout"}.get(
                parts[1], parts[1] or None
            )
            if len(parts) > 1
            else None,
            "attack_phase": {
                "r": "Reception",
                "p": "Transition breakpoint",
                "s": "Transition sideout",
            }.get(parts[2], parts[2] or None)
            if len(parts) > 2
            else None,
            "point": extract_score_from_code(code) is not None,
            "end_of_set": bool(re.match(r"^\*\*\d+set", code or "", re.IGNORECASE)),
            "timeout": (code or "")[:2] in {"*T", "aT"},
            "substitution": bool(re.match(r"^[*a][Pc]", code or ""))
            and ">lup" not in (code or "").lower(),
            "winning_attack": (code or "")[3:4] == "A" and (code or "")[5:6] == "#",
            "custom_code": custom_code,
            "start_coordinate": parts[4] if len(parts) > 4 else None,
            "mid_coordinate": parts[5] if len(parts) > 5 else None,
            "end_coordinate": parts[6] if len(parts) > 6 and parts[6] else None,
            "set_number": parts[8] if len(parts) > 8 and parts[8] else None,
            "home_setter_position": home_setter_position,
            "visiting_setter_position": visiting_setter_position,
            "setter_position": visiting_setter_position
            if code and code.startswith("a")
            else (home_setter_position if code and code.startswith("*") else None),
            "video_time": int(parts[12])
            if len(parts) > 12 and parts[12].isdigit()
            else None,
        }

        # Add home team rotation data [14:20] -> home_p1, home_p2, ..., home_p6
        home_positions = parts[14:20] if len(parts) > 14 else []
        for i, position in enumerate(home_positions):
            if i < 6:  # Only take first 6 positions
                play_data[f"home_p{i + 1}"] = position if position else None

        # Add visiting team rotation data [20:26] -> visiting_p1, visiting_p2, ..., visiting_p6
        visiting_positions = parts[20:26] if len(parts) > 20 else []
        for i, position in enumerate(visiting_positions):
            if i < 6:  # Only take first 6 positions
                play_data[f"visiting_p{i + 1}"] = position if position else None

        return play_data

    except (ValueError, IndexError) as e:
        print(f"Error parsing play line {line_number}: {line}")
        print(f"Error: {e}")
        return None


def extract_plays(raw_content: str) -> list[dict]:
    """
    Extract plays data from DVW file content with score tracking.

    Args:
        raw_content: Raw DVW file content

    Returns:
        List of play dictionaries with scores propagated to all plays
    """
    # Find the [3SCOUT] section that continues to the end of file
    scout_pattern = r"\[3SCOUT\](.*?)(?=$)"
    match = re.search(scout_pattern, raw_content, re.DOTALL)

    if not match:
        return []

    scout_header_line = raw_content[: match.start()].count("\n") + 1
    match_date_match = re.search(r"\[3MATCH\]\s+(\d{2}/\d{2}/\d{4})", raw_content)
    match_date = match_date_match.group(1) if match_date_match else None
    lines = []
    for line_offset, line in enumerate(match.group(1).split("\n")):
        stripped_line = line.strip()
        if stripped_line and stripped_line.strip("\x00"):
            lines.append((scout_header_line + line_offset, stripped_line))

    plays = []
    current_set = None
    current_home_score = "0"
    current_visiting_score = "0"

    # Parse each play line
    for line_num, (file_line_number, line) in enumerate(lines):
        if line:
            play_data = parse_play_line(line, line_num + 1)
            if play_data:
                play_data["file_line_number"] = file_line_number
                play_data["time"] = _parse_event_time(match_date, play_data.get("time"))
                # Reset running score when the set changes
                play_set = play_data.get("set_number")
                if play_set is not None and play_set != current_set:
                    current_set = play_set
                    current_home_score = "0"
                    current_visiting_score = "0"

                # Check if this play has score information
                score_info = extract_score_from_code(play_data["code"])
                if score_info:
                    # Update current scores
                    current_home_score = score_info["home_score"]
                    current_visiting_score = score_info["visiting_score"]

                # Add current scores to all plays
                play_data["home_score"] = current_home_score
                play_data["visiting_score"] = current_visiting_score

                plays.append(play_data)

    return plays
