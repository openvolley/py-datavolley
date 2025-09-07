# datavolley\utils\metadata.py

import re
import uuid
from datetime import datetime
from typing import Optional


def extract_date(raw_content: str) -> Optional[datetime]:
    """
    Extract match date from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        datetime object of the match date, or None if not found
    """
    # Look for the [3MATCH] section with date pattern: MM/DD/YYYY;HH.MM.SS
    match_pattern = r"\[3MATCH\]\s+(\d{2}/\d{2}/\d{4});(\d{2}\.\d{2}\.\d{2})"
    match = re.search(match_pattern, raw_content)

    if match:
        date_str = match.group(1)  # MM/DD/YYYY
        time_str = match.group(2)  # HH.MM.SS

        try:
            # Convert to standard datetime format
            datetime_str = f"{date_str} {time_str.replace('.', ':')}"
            return datetime.strptime(datetime_str, "%m/%d/%Y %H:%M:%S")
        except ValueError:
            return None

    return None


def generate_match_id(raw_content: str) -> str:
    """
    Extract VM Match ID or generate a unique match ID for the DVW file.

    Args:
        raw_content: Raw DVW file content

    Returns:
        Match ID string
    """
    # Look for the [3MATCH] section and parse the semicolon-separated values
    match_pattern = r"\[3MATCH\]\s*([^;]+;[^;]+;[^;]*;[^;]*;[^;]*;[^;]*;[^;]*;([^;]+))"
    match = re.search(match_pattern, raw_content)

    if match:
        # The VM Match ID should be in the 8th position (index 7) after splitting by semicolons
        full_match_line = match.group(1)
        parts = full_match_line.split(";")

        if len(parts) >= 8 and parts[7].strip():
            match_id = parts[7].strip()
            if match_id.isdigit():
                return match_id
            else:
                return f"{match_id}"

    fallback_pattern = r"\[3MATCH\].*?(\d{5,})"
    fallback_match = re.search(fallback_pattern, raw_content)

    if fallback_match:
        return fallback_match.group(1)

    # If no existing ID found, generate a UUID
    return f"{uuid.uuid4().hex[:8]}"


def extract_set_scores(raw_content: str) -> dict:
    """
    Extract set scores from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        Dictionary with set scores organized by set and team
    """
    # Find the [3SET] section
    set_pattern = r"\[3SET\](.*?)(?=\[3|$)"
    match = re.search(set_pattern, raw_content, re.DOTALL)

    if not match:
        return {}

    set_section = match.group(1).strip()

    # Parse set lines
    lines = [line.strip() for line in set_section.split("\n") if line.strip()]

    set_scores = {}

    for set_num, line in enumerate(lines, 1):
        parts = line.split(";")

        if len(parts) >= 6:
            final_score = parts[4].strip()
            final_team_score = parts[5].strip() if len(parts) > 5 else ""

            # Check for incomplete data
            all_scores_empty = all(not part.strip() for part in parts[1:5])

            if all_scores_empty and final_team_score.isdigit():
                if set_num >= 4:
                    continue
                else:
                    continue

            # Parse final score
            if "-" in final_score:
                try:
                    team1_score, team2_score = final_score.split("-")
                    team1_score = int(team1_score.strip())
                    team2_score = int(team2_score.strip())

                    set_scores[f"team_1_set_{set_num}"] = team1_score
                    set_scores[f"team_2_set_{set_num}"] = team2_score

                except (ValueError, IndexError):
                    continue

            # Fail check if we have two separate score fields
            elif final_team_score.isdigit() and any("-" in part for part in parts[1:5]):
                for part in parts[1:5]:
                    if "-" in part:
                        try:
                            team1_score, team2_score = part.split("-")
                            team1_score = int(team1_score.strip())
                            team2_score = int(team2_score.strip())

                            set_scores[f"team_1_set_{set_num}"] = team1_score
                            set_scores[f"team_2_set_{set_num}"] = team2_score
                            break

                        except (ValueError, IndexError):
                            continue

    return set_scores


def get_match_result(set_scores: dict) -> dict:
    """
    Calculate match result from set scores.

    Args:
        set_scores: Dictionary from extract_set_scores

    Returns:
        Dictionary with match summary
    """
    if not set_scores:
        return {}

    # Count sets won by each team
    team_1_sets_won = 0
    team_2_sets_won = 0
    total_sets = 0

    # Find the maximum set number
    set_numbers = []
    for key in set_scores.keys():
        if key.startswith("team_1_set_"):
            set_num = int(key.split("_")[-1])
            set_numbers.append(set_num)

    for set_num in set_numbers:
        team_1_key = f"team_1_set_{set_num}"
        team_2_key = f"team_2_set_{set_num}"

        if team_1_key in set_scores and team_2_key in set_scores:
            team_1_score = set_scores[team_1_key]
            team_2_score = set_scores[team_2_key]

            if team_1_score > team_2_score:
                team_1_sets_won += 1
            elif team_2_score > team_1_score:
                team_2_sets_won += 1

            total_sets += 1

    return {
        "team_1_sets_won": team_1_sets_won,
        "team_2_sets_won": team_2_sets_won,
        "total_sets_played": total_sets,
        "match_winner": "team_1"
        if team_1_sets_won > team_2_sets_won
        else "team_2"
        if team_2_sets_won > team_1_sets_won
        else "tie",
    }
