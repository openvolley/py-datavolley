# datavolley\utils\metadata.py

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datavolley.types import MatchData


def extract_date(raw_content: str) -> datetime | None:
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
            return datetime.strptime(datetime_str, "%m/%d/%Y %H:%M:%S")  # noqa: DTZ007 - DVW match times carry no timezone
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
    for key in set_scores:
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


def _is_serve_play(play: dict) -> bool:
    """A play is a serve if its skill says so, or its scout code marks it."""
    if play.get("skill") == "Serve":
        return True

    code = play.get("code") or ""
    return code[3:4] == "S"


def _is_point_play(play: dict) -> bool:
    """A play assigns a point if its skill or scout code marks it."""
    if play.get("skill") == "Point":
        return True

    code = play.get("code") or ""
    return code[1:2] == "p"


def _is_timeout_play(play: dict) -> bool:
    """A play is a timeout if its skill or scout code marks it."""
    if play.get("skill") in {"Timeout", "Technical timeout"}:
        return True

    code = play.get("code") or ""
    return code[1:2] == "T"


def _assign_point_ids(plays: list[dict]) -> None:
    """Assign zero-based, match-wide point identifiers in place."""
    point_id = 0

    for index, play in enumerate(plays):
        if index > 0 and (
            _is_point_play(plays[index - 1])
            or _is_timeout_play(play)
            or _is_timeout_play(plays[index - 1])
        ):
            point_id += 1

        play["point_id"] = point_id


def _is_attack_play(play: dict) -> bool:
    """A play is an attack if its skill says so, or its scout code marks it."""
    if play.get("skill") == "Attack":
        return True

    code = play.get("code") or ""
    return code[3:4] == "A"


def _team_touch_team(play: dict) -> str | None:
    """Return a stable team marker for team-touch boundary comparisons."""
    code = play.get("code") or ""
    if code.startswith("**"):
        return None
    if code[:1] in {"*", "a"}:
        return code[:1]
    return play.get("team")


def _assign_team_touch_ids(plays: list[dict]) -> None:
    """Assign zero-based, match-wide team-touch identifiers in place."""
    if not plays:
        return

    team_touch_id = 0
    previous = plays[0]
    previous["team_touch_id"] = team_touch_id
    previous_was_attack = _is_attack_play(previous)

    for play in plays[1:]:
        if (
            _team_touch_team(play) != _team_touch_team(previous)
            or play.get("point_id") != previous.get("point_id")
            or (_is_attack_play(play) and previous_was_attack)
        ):
            team_touch_id += 1

        play["team_touch_id"] = team_touch_id
        previous = play
        previous_was_attack = _is_attack_play(play)


def _assign_point_metadata(
    plays: list[dict],
    home_team: str,
    visiting_team: str,
    players: dict[str, list[dict]] | None = None,
) -> None:
    point_groups: dict[int | None, list[dict]] = {}
    for play in plays:
        point_groups.setdefault(play.get("point_id"), []).append(play)

    current_set = None
    current_home_score = 0
    current_visiting_score = 0
    for point_plays in point_groups.values():
        set_number = point_plays[0].get("set_number")
        if set_number != current_set:
            current_set = set_number
            current_home_score = 0
            current_visiting_score = 0

        home_scores = [
            int(play["home_team_score"])
            for play in point_plays
            if play.get("home_team_score") is not None
        ]
        visiting_scores = [
            int(play["visiting_team_score"])
            for play in point_plays
            if play.get("visiting_team_score") is not None
        ]
        end_home_score = max(home_scores, default=current_home_score)
        end_visiting_score = max(visiting_scores, default=current_visiting_score)

        serving_team = next(
            (play.get("team") for play in point_plays if _is_serve_play(play)), None
        )
        receiving_team = (
            visiting_team
            if serving_team == home_team
            else home_team
            if serving_team == visiting_team
            else None
        )
        point_won_by = next(
            (play.get("team") for play in point_plays if play.get("point")), None
        )

        for play in point_plays:
            play["home_score_start_of_point"] = current_home_score
            play["visiting_score_start_of_point"] = current_visiting_score
            play["home_team_score"] = end_home_score
            play["visiting_team_score"] = end_visiting_score
            play["serving_team"] = serving_team
            play["receiving_team"] = receiving_team
            play["point_won_by"] = point_won_by

        current_home_score = end_home_score
        current_visiting_score = end_visiting_score

    player_maps: dict[str, dict[str, object]] = {"home": {}, "visiting": {}}
    if players:
        for side in player_maps:
            player_maps[side] = {
                str(player.get("player_number")): player.get("player_id")
                for player in players.get(side, [])
                if player.get("player_number") is not None
            }

    for play in plays:
        for side in ("home", "visiting"):
            for position in range(1, 7):
                number = play.get(f"{side}_p{position}")
                play[f"{side}_player_id{position}"] = (
                    player_maps[side].get(str(number)) if number is not None else None
                )

    reception_touch_ids = {
        play.get("team_touch_id") for play in plays if play.get("skill") == "Reception"
    }
    ball_skills = {"Serve", "Reception", "Set", "Attack", "Block", "Dig", "Freeball"}
    for index, play in enumerate(plays):
        skill = play.get("skill")
        phase = "Transition" if skill in ball_skills else None
        if skill == "Serve":
            phase = "Serve"
        if play.get("team_touch_id") in reception_touch_ids and skill in ball_skills:
            phase = "Reception"
        if (
            skill == "Block"
            and index > 0
            and plays[index - 1].get("skill") == "Attack"
            and plays[index - 1].get("phase") == "Reception"
        ):
            phase = "Reception"
        play["phase"] = phase

        if skill == "Attack" and index + 1 < len(plays):
            next_play = plays[index + 1]
            if (
                next_play.get("skill") in {"Dig", "Block"}
                and next_play.get("evaluation") == "Error"
            ):
                play["winning_attack"] = True


# Alternative simpler version if you just need to process a list of plays directly
def assign_rally_numbers_to_plays(
    plays: list,
    home_team: str | None = None,
    visiting_team: str | None = None,
    players: dict[str, list[dict]] | None = None,
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

    _assign_point_ids(plays)
    _assign_team_touch_ids(plays)

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
    current_rally = 1
    serve_seen_in_set = False

    for play in plays:
        play_set = play.get("set_number")

        # Convert set_number to int if it's a string
        if isinstance(play_set, str) and play_set.isdigit():
            play_set = int(play_set)

        # Reset rally counter when moving to a new set
        if play_set != current_set:
            current_set = play_set
            current_rally = 1
            serve_seen_in_set = False

        # Increment rally number on every serve except the first of the set
        if _is_serve_play(play):
            if serve_seen_in_set:
                current_rally += 1
            else:
                serve_seen_in_set = True

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
            if _is_serve_play(play):
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
        for play in rally_plays:
            # Basic rally fields
            play["serving_team"] = serving_team
            play["receiving_team"] = receiving_team
            play["point_won_by"] = point_won_by

            current_team = play.get("team")

            # Calculate possession_number - start at 0 for serve
            if _is_serve_play(play):
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

    _assign_point_metadata(plays, home_team, visiting_team, players)
    return plays


def get_rally_number(result_content: MatchData) -> MatchData:
    """Assign rally and point metadata to plays in a match-data dictionary."""
    if "plays" not in result_content:
        raise ValueError("result_content must contain a 'plays' key with list of plays")

    teams = result_content.get("teams", {})
    result_content["plays"] = assign_rally_numbers_to_plays(
        result_content["plays"],
        teams.get("team_1"),
        teams.get("team_2"),
        result_content.get("players"),
    )
    return result_content
