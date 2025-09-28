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


def extract_comments(raw_content: str) -> str:
    """
    Extract comments from DVW file content.

    Args:
        raw_content: Raw DVW file content

    Returns:
        Comments string, or empty string if not found
    """
    # Find the [3COMMENTS] section
    comments_pattern = r"\[3COMMENTS\](.*?)(?=\[3|\n\n|$)"
    match = re.search(comments_pattern, raw_content, re.DOTALL)

    if match:
        comments_section = match.group(1).strip()
        # Remove empty lines and join remaining lines
        lines = [line.strip() for line in comments_section.split("\n") if line.strip()]
        return "\n".join(lines) if lines else ""

    return ""


# Updated functions for metadata.py to use team names and add new variables


def get_rally_number(result_content: dict) -> dict:
    """
    Assign rally numbers (possession numbers) per set, incrementing on serves.
    Also determines point winners, phases, and possession tracking for each rally.

    Args:
        result_content: Dictionary containing the processed match data with 'plays' and 'teams' keys

    Returns:
        Updated dictionary with rally_number, point_won_by, point_phase, attack_phase,
        serving_team, receiving_team, and possession_number fields added to each play
    """
    # Get the plays list from the result content
    if "plays" not in result_content:
        raise ValueError("result_content must contain a 'plays' key with list of plays")

    result = result_content["plays"]

    # Extract team names from the result_content
    teams = result_content.get("teams", {})
    home_team = teams.get("team_1", "home")  # fallback to "home" if not found
    visiting_team = teams.get(
        "team_2", "visiting"
    )  # fallback to "visiting" if not found

    # First pass: Assign rally numbers
    current_set = None
    current_rally = 0

    for play_dict in result:
        play_set = play_dict.get("set_number")

        # Convert set_number to int if it's a string
        if isinstance(play_set, str) and play_set.isdigit():
            play_set = int(play_set)

        # Reset rally counter when moving to a new set
        if play_set != current_set:
            current_set = play_set
            current_rally = 1  # Start at 1 for the first rally

        # Increment rally number on serves after the first one
        if play_dict.get("skill") == "Serve":
            if current_set is not None and current_rally > 1:
                current_rally += 1
            elif current_set is not None and current_rally == 0:
                current_rally = 1

        play_dict["rally_number"] = current_rally

    # Group plays by set and rally for processing
    rallies = {}
    for play in result:
        set_num = play.get("set_number")
        rally_num = play.get("rally_number")

        # Convert to int if string
        if isinstance(set_num, str) and set_num.isdigit():
            set_num = int(set_num)

        key = (set_num, rally_num)
        if key not in rallies:
            rallies[key] = []
        rallies[key].append(play)

    # Process each rally to determine all the new fields
    current_home_score = 0
    current_visiting_score = 0
    current_set = None

    for (set_num, rally_num), plays_in_rally in sorted(rallies.items()):
        if set_num != current_set:
            current_set = set_num
            current_home_score = 0
            current_visiting_score = 0

        start_home = current_home_score
        start_visiting = current_visiting_score

        # Find the serving team for this rally
        serving_team = None
        receiving_team = None
        for play in plays_in_rally:
            if play.get("skill") == "Serve":
                serving_team = play.get("team")
                # Determine receiving team
                if serving_team == home_team:
                    receiving_team = visiting_team
                elif serving_team == visiting_team:
                    receiving_team = home_team
                else:
                    # Try to match by home_team or visiting_team fields
                    if play.get("home_team") == serving_team:
                        receiving_team = play.get("visiting_team")
                    elif play.get("visiting_team") == serving_team:
                        receiving_team = play.get("home_team")
                break

        # Determine point winner
        point_won_by = None
        if plays_in_rally:
            last_play = plays_in_rally[-1]
            home_score_str = last_play.get("home_team_score", "0")
            visiting_score_str = last_play.get("visiting_team_score", "0")

            try:
                end_home = int(home_score_str) if home_score_str else 0
                end_visiting = int(visiting_score_str) if visiting_score_str else 0
            except (ValueError, TypeError):
                end_home = start_home
                end_visiting = start_visiting

            if end_home > start_home:
                point_won_by = home_team
            elif end_visiting > start_visiting:
                point_won_by = visiting_team

            current_home_score = end_home
            current_visiting_score = end_visiting

        # Track possession changes for possession_number
        possession_number = 0
        last_team_in_possession = None
        possession_started = False

        # Apply all fields to plays in this rally
        for play in plays_in_rally:
            # Set serving and receiving teams
            play["serving_team"] = serving_team
            play["receiving_team"] = receiving_team
            play["point_won_by"] = point_won_by

            # Determine point_phase
            current_team = play.get("team")
            if current_team == serving_team:
                play["point_phase"] = "Serve"
            elif current_team == receiving_team:
                play["point_phase"] = "Reception"
            else:
                play["point_phase"] = None

            # Determine attack_phase (only for attacks)
            if play.get("skill") == "Attack":
                # Check if this is the first attack after serve/reception
                # Look at previous plays to determine context
                is_first_attack = True
                for prev_play in plays_in_rally:
                    if prev_play == play:
                        break
                    if (
                        prev_play.get("skill") == "Attack"
                        and prev_play.get("team") == current_team
                    ):
                        is_first_attack = False
                        break

                if is_first_attack and play["point_phase"] == "Reception":
                    play["attack_phase"] = "Reception"
                else:
                    play["attack_phase"] = "Transition"
            else:
                play["attack_phase"] = None

            # Calculate possession_number - start at 0 for serve
            if play.get("skill") == "Serve":
                possession_number = 0
                last_team_in_possession = current_team
                possession_started = True
            elif (
                possession_started
                and current_team != last_team_in_possession
                and current_team is not None
            ):
                possession_number += 1
                last_team_in_possession = current_team
            elif not possession_started and current_team is not None:
                # For plays before the serve (like substitutions), keep at 0
                possession_number = 0
                last_team_in_possession = current_team

            play["possession_number"] = possession_number

    return result_content


# Alternative simpler version if you just need to process a list of plays directly
def assign_rally_numbers_to_plays(
    plays: list, home_team: Optional[str] = None, visiting_team: Optional[str] = None
) -> list:
    """
    Simplified version that works directly with a list of plays.
    Adds rally numbers, point winners, phases, and possession tracking.

    Args:
        plays: List of play dictionaries
        home_team: Name of the home team (optional)
        visiting_team: Name of the visiting team (optional)

    Returns:
        List of plays with rally_number, point_won_by, point_phase, attack_phase,
        serving_team, receiving_team, and possession_number fields added
    """
    if not plays:
        return plays

    # Try to extract team names from the plays if not provided
    if home_team is None or visiting_team is None:
        for play in plays:
            if home_team is None and play.get("home_team"):
                home_team = play["home_team"]
            if visiting_team is None and play.get("visiting_team"):
                visiting_team = play["visiting_team"]
            if home_team and visiting_team:
                break

        # Fallback to generic names if still not found
        if home_team is None:
            home_team = "home"
        if visiting_team is None:
            visiting_team = "visiting"

    # First pass: Assign rally numbers
    current_set = None
    current_rally = 0

    for play in plays:
        play_set = play.get("set_number")

        # Convert set_number to int if it's a string
        if isinstance(play_set, str) and play_set.isdigit():
            play_set = int(play_set)

        # Reset rally counter when moving to a new set
        if play_set != current_set:
            current_set = play_set
            current_rally = 1

        # Increment rally number on serves after the first one
        if play.get("skill") == "Serve":
            if current_set is not None and current_rally > 1:
                current_rally += 1

        play["rally_number"] = current_rally

    # Group by set and rally
    rallies = {}
    for play in plays:
        set_num = play.get("set_number")
        rally_num = play.get("rally_number")

        if isinstance(set_num, str) and set_num.isdigit():
            set_num = int(set_num)

        key = (set_num, rally_num)
        if key not in rallies:
            rallies[key] = []
        rallies[key].append(play)

    # Process rallies to determine all fields
    current_set = None
    current_home_score = 0
    current_visiting_score = 0

    for (set_num, rally_num), rally_plays in sorted(rallies.items()):
        if set_num != current_set:
            current_set = set_num
            current_home_score = 0
            current_visiting_score = 0

        start_home = current_home_score
        start_visiting = current_visiting_score

        # Find the serving and receiving teams
        serving_team = None
        receiving_team = None
        for play in rally_plays:
            if play.get("skill") == "Serve":
                serving_team = play.get("team")
                # Determine receiving team based on serving team
                if serving_team == home_team:
                    receiving_team = visiting_team
                elif serving_team == visiting_team:
                    receiving_team = home_team
                else:
                    # Fallback logic if team names don't match
                    # Check if serving team matches home_team or visiting_team in play
                    if play.get("home_team") == serving_team:
                        receiving_team = play.get("visiting_team", visiting_team)
                    elif play.get("visiting_team") == serving_team:
                        receiving_team = play.get("home_team", home_team)
                    else:
                        receiving_team = (
                            visiting_team if serving_team == home_team else home_team
                        )
                break

        # Determine point winner
        point_won_by = None
        if rally_plays:
            last_play = rally_plays[-1]

            try:
                end_home = int(last_play.get("home_team_score", "0"))
                end_visiting = int(last_play.get("visiting_team_score", "0"))
            except (ValueError, TypeError):
                end_home = start_home
                end_visiting = start_visiting

            # Determine winner using actual team names
            if end_home > start_home:
                point_won_by = home_team
            elif end_visiting > start_visiting:
                point_won_by = visiting_team

            current_home_score = end_home
            current_visiting_score = end_visiting

        # Track possession changes
        possession_number = 0
        last_team_in_possession = None
        possession_started = False

        # Apply fields to all plays in rally
        for i, play in enumerate(rally_plays):
            # Basic rally fields
            play["serving_team"] = serving_team
            play["receiving_team"] = receiving_team
            play["point_won_by"] = point_won_by

            # Determine point_phase
            current_team = play.get("team")
            if current_team == serving_team:
                play["point_phase"] = "Serve"
            elif current_team == receiving_team:
                play["point_phase"] = "Reception"
            else:
                # If team is not serving or receiving team, might be None or different format
                play["point_phase"] = None

            # Determine attack_phase (only for attacks)
            if play.get("skill") == "Attack":
                # Look for previous attacks by same team in this rally
                is_first_attack = True
                for j in range(i):
                    if (
                        rally_plays[j].get("skill") == "Attack"
                        and rally_plays[j].get("team") == current_team
                    ):
                        is_first_attack = False
                        break

                # If first attack and team is receiving team, it's Reception attack
                if is_first_attack and current_team == receiving_team:
                    play["attack_phase"] = "Reception"
                else:
                    play["attack_phase"] = "Transition"
            else:
                play["attack_phase"] = None

            # Calculate possession_number - start at 0 for serve
            if play.get("skill") == "Serve":
                possession_number = 0
                last_team_in_possession = current_team
                possession_started = True
            elif (
                possession_started
                and current_team != last_team_in_possession
                and current_team is not None
            ):
                possession_number += 1
                last_team_in_possession = current_team
            elif not possession_started and current_team is not None:
                # For plays before the serve (like substitutions), keep at 0
                possession_number = 0
                last_team_in_possession = current_team

            play["possession_number"] = possession_number

    return plays
