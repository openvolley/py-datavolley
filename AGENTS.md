Execute Python development through systematic phases:

1. Codebase Analysis
   Understand project structure and establish development patterns.

Analysis framework:

Project layout and package structure
Dependency analysis with uv
Code style configuration review

Code quality evaluation:
Code smell detection with ruff
Performance baseline establishment

2. Implementation Phase
   Develop Python solutions with modern best practices.

Implementation priorities:

Apply Pythonic idioms and patterns
Ensure complete type coverage
Optimize for performance and memory

3. Fianl out
   Should be a dictionary the user can easily parse into a padnas dataframe. But we don't want to use pandas in this project.
   The user should be able to use read_dv('path') in order to create the datavolley/io/plays.py object.

4. Data, function
   match_id = generate_match_id
   video_time = parse_play_line
   code = parse_play_line
   team = parse_play_code
   player_number = parse_play_code
   player_name = parse_play_code
   player_id = parse_play_code
   skill = parse_play_code
   evaluation_code = parse_play_code
   setter_position =
   attack_code = parse_play_code
   set_code = parse_play_code
   set_type =
   start_zone = parse_play_code
   end_zone = parse_play_code
   end_subzone = parse_play_code
   num_players_numeric = parse_play_code
   home_team_score = extract_plays
   visiting_team_score = extract_plays
   home_setter_position = parse_play_line
   visiting_setter_position = parse_play_line
   custom_code =
   home_p1 = parse_play_line
   home_p2 = parse_play_line
   home_p3 = parse_play_line
   home_p4 = parse_play_line
   home_p5 = parse_play_line
   home_p6 = parse_play_line
   visiting_p1 = parse_play_line
   visiting_p2 = parse_play_line
   visiting_p3 = parse_play_line
   visiting_p4 = parse_play_line
   visiting_p5 = parse_play_line
   visiting_p6 = parse_play_line
   start_coordinate = parse_play_line
   mid_coordinate = parse_play_line
   end_coordinate = parse_play_line
   point_phase =
   attack_phase =
   start_coordinate_x = play_dict["start_coordinate_x"], play_dict["start_coordinate_x"] = (coords)
   start_coordinate_y = play_dict["start_coordinate_y"], play_dict["start_coordinate_y"] = (coords)
   mid_coordinate_x = play_dict["mid_coordinate_x"], play_dict["mid_coordinate_x"] = (coords)
   mid_coordinate_y = play_dict["mid_coordinate_y"], play_dict["mid_coordinate_y"] = (coords)
   end_coordinate_x = play_dict["end_coordinate_x"], play_dict["end_coordinate_x"] = (coords)
   end_coordinate_y = play_dict["end_coordinate_y"], play_dict["end_coordinate_y"] = (coords)
   set_number = parse_play_line
   home_team = play_dict["home_team"] = teams.get("team_1")
   visiting_team = play_dict["visiting_team"] = teams.get("team_2")
   home_team_id = play_dict["home_team_id"] = teams.get("team_1_id")
   visiting_team_id = play_dict["visiting_team_id"] = teams.get("team_2_id")
   point_won_by =
   serving_team =
   receiving_team =
   rally_number =
   possesion_number =
