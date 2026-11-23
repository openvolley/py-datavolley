import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

import datavolley as dv
from datavolley.core.coordinates import dv_index2xy, dv_xy2index
from datavolley.types import normalize_play


def lineup(home=None, away=None, home_setter=1, away_setter=1):
    return {
        "home": {
            "positions": home or {"1": 2, "2": 9, "3": 4, "4": 5, "5": 6, "6": 7},
            "setterAt": home_setter,
        },
        "away": {
            "positions": away or {"1": 3, "2": 4, "3": 5, "4": 6, "5": 7, "6": 8},
            "setterAt": away_setter,
        },
    }


def match_data():
    starting = lineup()
    return {
        "gameType": "indoor",
        "startDate": "2025-08-20T18:00:00Z",
        "createdAt": "2025-08-20T18:30:00Z",
        "comment": "Match notes",
        "team": {
            "home": {
                "code": "HOME",
                "name": "Hôme",
                "libero": [0],
                "players": [
                    {
                        "shirtNumber": "02",
                        "code": "home-02",
                        "firstName": " Home ",
                        "lastName": " Setter ",
                        "position": 4,
                    },
                    {"shirtNumber": 0, "code": "home-zero", "lastName": "Libero"},
                    {"shirtNumber": 8, "code": "home-08", "lastName": "Substitute"},
                ],
            },
            "away": {
                "code": "AWAY",
                "name": "Visitors",
                "players": [
                    {"shirtNumber": 3, "code": "003", "lastName": "Setter"},
                    {"shirtNumber": 4, "code": "away-04", "lastName": "Hitter"},
                ],
            },
        },
        "attackCombinations": [
            {
                "code": "X1",
                "name": "Quick",
                "hitType": "Q",
                "targetAttacker": "C",
                "start": {"zone": 3, "subZone": "B"},
            }
        ],
        "setterCalls": [{"code": "K1", "name": "Front quick"}],
        "scout": {
            "video": {"path": "match.mp4"},
            "sets": [
                {
                    "startingLineup": starting,
                    "events": [
                        {
                            "_id": "rally-1",
                            "lineup": starting,
                            "score": {"home": 0, "away": 1},
                            "exchange": {
                                "point": "a",
                                "plays": [
                                    {
                                        "_id": "serve",
                                        "team": "*",
                                        "player": "02",
                                        "skill": "S",
                                        "hitType": "H",
                                        "effect": "+",
                                        "startZone": 1,
                                        "endZone": 5,
                                        "endSubZone": "a",
                                        "time": 101,
                                        "originalTime": 201,
                                        "travelPath": [
                                            {"x": 800, "y": -100},
                                            {"x": 200, "y": 1400},
                                        ],
                                    },
                                    {
                                        "_id": "reception",
                                        "team": "a",
                                        "player": "03",
                                        "skill": "R",
                                        "hitType": "H",
                                        "effect": "#",
                                        "startZone": 5,
                                        "endZone": 3,
                                        "time": 110,
                                    },
                                    {
                                        "_id": "set",
                                        "team": "a",
                                        "player": "03",
                                        "skill": "E",
                                        "hitType": "H",
                                        "effect": "#",
                                        "combination": "K1",
                                        "skillType": "2",
                                        "startZone": 3,
                                        "startSubZone": "b",
                                        "targetAttacker": "C",
                                        "time": 120,
                                        "originalTime": 220,
                                    },
                                    {
                                        "_id": "attack",
                                        "team": "a",
                                        "player": "04",
                                        "skill": "A",
                                        "hitType": "Q",
                                        "effect": "+",
                                        "combination": "X1",
                                        "skillType": "T",
                                        "players": 2,
                                        "special": "C",
                                        "custom": "long-custom-code",
                                        "time": 130,
                                        "originalTime": 230,
                                    },
                                    {
                                        "_id": "dig",
                                        "team": "*",
                                        "player": "00",
                                        "skill": "D",
                                        "hitType": "Q",
                                        "effect": "=",
                                        "skillType": "T",
                                        "time": 140,
                                        "originalTime": 240,
                                    },
                                ],
                            },
                        },
                        {
                            "_id": "timeout",
                            "lineup": starting,
                            "score": {"home": 0, "away": 1},
                            "timeout": {"team": "*"},
                        },
                        {
                            "_id": "sub",
                            "lineup": lineup(
                                home={"1": 8, "2": 9, "3": 4, "4": 5, "5": 6, "6": 7}
                            ),
                            "score": {"home": 0, "away": 1},
                            "substitution": {
                                "team": "*",
                                "playerOut": 2,
                                "playerIn": 8,
                            },
                        },
                    ],
                    "score": {"home": 0, "away": 1},
                }
            ],
        },
    }


class VolleyStationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def write_match(self, data=None, name="match.vsm", *, pretty=False):
        path = self.directory / name
        path.write_text(
            json.dumps(
                match_data() if data is None else data, indent=2 if pretty else None
            ),
            encoding="utf-8-sig",
        )
        return path

    def test_automatic_reading_and_matching_schemas(self):
        path = self.write_match(name="match.VSM")
        match = dv.load_dv(path)
        plays = dv.read_dv(path)
        self.assertEqual(plays, match["plays"])
        self.assertEqual(set(match), set(dv.load_dvw(dv.example_file())))
        self.assertEqual(len(plays[0]), 88)
        for play in plays:
            self.assertEqual(tuple(play), tuple(normalize_play({})))
            for flag in (
                "point",
                "timeout",
                "substitution",
                "end_of_set",
                "winning_attack",
            ):
                self.assertIs(type(play[flag]), bool)
        self.assertEqual(dv.load_dv(dv.example_file()), dv.load_dvw(dv.example_file()))

    def test_metadata_and_string_identifiers(self):
        match = dv.load_dv(self.write_match())
        self.assertEqual(match["teams"]["team_1_id"], "HOME")
        self.assertEqual(match["teams"]["team_2_id"], "AWAY")
        self.assertEqual(match["comments"], "Match notes")
        self.assertEqual(match["match_date"], datetime(2025, 8, 20, 18, tzinfo=UTC))
        self.assertEqual(match["match_result"]["team_2_sets_won"], 1)
        self.assertEqual(match["players"]["home"][0]["full_name"], "Home Setter")
        self.assertEqual(match["players"]["home"][0]["role"], "setter")
        self.assertEqual(match["players"]["home"][1]["role"], "libero")
        serve = next(play for play in match["plays"] if play["skill"] == "Serve")
        self.assertEqual(serve["player_id"], "home-02")
        self.assertEqual(serve["home_player_id1"], "home-02")
        self.assertEqual(serve["visiting_player_id1"], "003")
        self.assertEqual(serve["team_id"], "HOME")
        self.assertEqual(serve["player_number"], 2)
        dig = next(play for play in match["plays"] if play["skill"] == "Dig")
        self.assertEqual((dig["player_number"], dig["player_id"]), (0, "home-zero"))

    def test_definition_schemas_and_coordinate_grid(self):
        match = dv.load_dv(self.write_match())
        reference = dv.load_dvw(dv.example_file())
        for field in ("attack_combinations", "setter_calls"):
            self.assertEqual(tuple(match[field][0]), tuple(reference[field][0]))
        attack = match["attack_combinations"][0]
        self.assertEqual(attack["position_code"], dv_xy2index(2.25, 3.25))
        self.assertEqual(attack["set_direction"], "C")
        for index in range(1, 10101):
            xy = dv_index2xy(index)
            assert xy is not None
            self.assertEqual(dv_xy2index(*xy), index)
        self.assertEqual(dv_xy2index(-100, -100), 1)
        self.assertEqual(dv_xy2index(100, 100), 10100)
        self.assertIsNone(dv_xy2index(None, 1))

    def test_skill_codes_coordinates_and_timing(self):
        match = dv.load_dv(self.write_match())
        by_skill = {play["skill"]: play for play in match["plays"] if play["skill"]}
        serve, reception = by_skill["Serve"], by_skill["Reception"]
        self.assertEqual(serve["code"][:6], "*02SH+")
        self.assertEqual(serve["video_time"], 10)
        self.assertEqual(
            serve["time"],
            datetime(2025, 8, 20, 18, 30, tzinfo=UTC) + timedelta(seconds=20.1),
        )
        self.assertIsNone(reception["time"])
        self.assertAlmostEqual(serve["start_coordinate_x"], 800 / 293.3333 + 0.447159)
        for key in (
            "start_zone",
            "end_zone",
            "end_subzone",
            "start_coordinate",
            "end_coordinate",
            "start_coordinate_x",
            "end_coordinate_y",
        ):
            self.assertEqual(reception[key], serve[key], key)
        setter = by_skill["Set"]
        self.assertEqual(
            (setter["start_zone"], setter["end_zone"], setter["end_subzone"]),
            (None, 3, "B"),
        )
        self.assertEqual(setter["set_description"], "Front quick")
        self.assertEqual(setter["skill_subtype"], "2 hands set")
        attack = by_skill["Attack"]
        self.assertEqual(attack["attack_description"], "Quick")
        self.assertEqual(attack["set_type"], "C")
        self.assertEqual(attack["num_players"], "2 player block")
        self.assertEqual(attack["special_code"], "Block control")
        self.assertEqual(attack["skill_subtype"], "Tip")
        self.assertEqual(attack["custom_code"], "long-custom-code")
        self.assertTrue(attack["winning_attack"])
        self.assertEqual(by_skill["Dig"]["skill_subtype"], "Tip")

    def test_controls_lineups_scores_and_phases(self):
        plays = dv.read_dv(self.write_match())
        timeout = next(play for play in plays if play["timeout"])
        substitution = next(play for play in plays if play["substitution"])
        self.assertEqual(timeout["code"], "*T")
        self.assertEqual(timeout["video_time"], 14)
        self.assertEqual(substitution["code"], "*c02:08")
        self.assertEqual(substitution["home_p1"], 8)
        self.assertEqual(substitution["home_player_id1"], "home-08")
        self.assertTrue(any(play["code"] == "*P08" for play in plays))
        self.assertEqual(sum(play["point"] for play in plays), 1)
        self.assertEqual(sum(play["end_of_set"] for play in plays), 1)
        self.assertEqual(sum(">LUp" in (play["code"] or "") for play in plays), 4)
        skill_rows = [
            play
            for play in plays
            if play["skill"] in {"Serve", "Reception", "Set", "Attack", "Dig"}
        ]
        for play in skill_rows:
            self.assertEqual(
                (play["home_team_score"], play["visiting_team_score"]), (0, 1)
            )
            self.assertEqual(
                (
                    play["home_score_start_of_point"],
                    play["visiting_score_start_of_point"],
                ),
                (0, 0),
            )
            self.assertEqual(play["serving_team"], "Hôme")
            self.assertEqual(play["point_won_by"], "Visitors")
        reception = next(play for play in skill_rows if play["skill"] == "Reception")
        attack = next(play for play in skill_rows if play["skill"] == "Attack")
        self.assertEqual(reception["phase"], "Reception")
        self.assertEqual(attack["attack_phase"], "Reception")
        self.assertIsNone(attack["point_phase"])
        dig = next(play for play in skill_rows if play["skill"] == "Dig")
        self.assertEqual(dig["point_phase"], "Sideout")
        self.assertEqual(attack["possession_number"], 1)
        self.assertEqual(reception["team_touch_id"], attack["team_touch_id"])

    def test_set_and_block_end_zone_values_are_not_erased(self):
        for code, skill in (("E", "Set"), ("B", "Block")):
            with self.subTest(skill=skill):
                data = match_data()
                source = data["scout"]["sets"][0]["events"][0]["exchange"]["plays"][2]
                source.update(
                    skill=code,
                    startZone=None,
                    startSubZone=None,
                    endZone=2,
                    endSubZone="c",
                )
                plays = dv.read_dv(self.write_match(data))
                row = next(play for play in plays if play["skill"] == skill)
                self.assertEqual(row["end_zone"], 2)
                self.assertEqual(row["end_subzone"], "C")
                self.assertIsNone(row["start_zone"])

    def test_score_corrections_do_not_restore_old_maximum(self):
        data = match_data()
        events = data["scout"]["sets"][0]["events"]
        events.extend(
            [
                {"_id": "correction", "score": {"home": 0, "away": 0}},
                {
                    "_id": "rally-2",
                    "score": {"home": 1, "away": 0},
                    "exchange": {
                        "point": "*",
                        "plays": [
                            {"team": "a", "player": "03", "skill": "S", "effect": "="}
                        ],
                    },
                },
            ]
        )
        data["scout"]["sets"][0]["score"] = {"home": 1, "away": 0}
        plays = dv.read_dv(self.write_match(data))
        serve = [play for play in plays if play["skill"] == "Serve"][-1]
        self.assertEqual(serve["visiting_score_start_of_point"], 0)
        self.assertEqual(serve["visiting_team_score"], 0)
        self.assertEqual(serve["rally_number"], 2)
        self.assertEqual(plays[-1]["visiting_team_score"], 0)

    def test_physical_line_numbers_and_stable_match_id(self):
        data = match_data()
        compact = dv.load_dv(self.write_match(data))
        pretty_path = self.write_match(data, "pretty.vsm", pretty=True)
        pretty = dv.load_dv(pretty_path)
        self.assertEqual(compact["match_id"], pretty["match_id"])
        source = pretty_path.read_text(encoding="utf-8-sig").splitlines()
        serve = next(play for play in pretty["plays"] if play["skill"] == "Serve")
        self.assertIn('"serve"', source[serve["file_line_number"] - 1])
        self.assertTrue(all(play["file_line_number"] == 1 for play in compact["plays"]))

    def test_empty_unfinished_and_missing_optional_fields(self):
        match = dv.load_dv(self.write_match({"gameType": "indoor"}))
        self.assertEqual(match["plays"], [])
        self.assertEqual(match["players"], {"home": [], "visiting": []})
        self.assertEqual(match["match_result"], {})
        self.assertIsNone(match["match_date"])
        data = match_data()
        del data["createdAt"]
        data["scout"]["sets"][0]["score"] = {"home": 0, "away": 0}
        plays = dv.read_dv(self.write_match(data))
        self.assertFalse(any(play["end_of_set"] for play in plays))
        self.assertTrue(all(play["time"] is None for play in plays))
        self.assertEqual(dv.load_dv(self.write_match(data))["set_scores"], {})

    def test_beach_invalid_json_and_missing_files(self):
        data = match_data()
        data["gameType"] = "beach"
        with self.assertRaisesRegex(ValueError, "beach"):
            dv.read_dv(self.write_match(data))
        bad = self.directory / "bad.vsm"
        bad.write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "bad.vsm"):
            dv.read_dv(bad)
        with self.assertRaisesRegex(FileNotFoundError, "missing.vsm"):
            dv.read_dv(self.directory / "missing.vsm")
        with self.assertRaisesRegex(ValueError, "object"):
            dv.read_dv(self.write_match([]))

    def test_three_point_paths_unknown_players_and_singleton_lists(self):
        data = match_data()
        event = data["scout"]["sets"][0]["events"][0]
        serve = event["exchange"]["plays"][0]
        serve["travelPath"].insert(1, {"x": 400, "y": 600})
        serve["player"] = "$$"
        data["team"]["home"]["players"] = [data["team"]["home"]["players"]]
        plays = dv.read_dv(self.write_match(data))
        first = next(play for play in plays if play["skill"] == "Serve")
        self.assertIsNone(first["player_number"])
        self.assertIsNone(first["player_id"])
        self.assertIsNotNone(first["mid_coordinate"])
        serve["travelPath"] = [{"x": 0, "y": 0}]
        with self.assertRaisesRegex(ValueError, "travelPath"):
            dv.read_dv(self.write_match(data))

    def test_missing_lineup_substitution_and_missing_game_type(self):
        data = match_data()
        del data["gameType"]
        del data["scout"]["sets"][0]["events"][-1]["lineup"]
        plays = dv.read_dv(self.write_match(data))
        substitution = next(play for play in plays if play["substitution"])
        self.assertEqual(substitution["home_p1"], 8)
        self.assertTrue(any(play["code"] == "*P08" for play in plays))

    def test_identical_team_names_do_not_mix_player_ids_or_phases(self):
        data = match_data()
        data["team"]["away"]["name"] = data["team"]["home"]["name"]
        plays = dv.read_dv(self.write_match(data))
        serve = next(play for play in plays if play["skill"] == "Serve")
        reception = next(play for play in plays if play["skill"] == "Reception")
        self.assertEqual(reception["player_id"], "003")
        self.assertEqual(reception["team_id"], "AWAY")
        dig = next(play for play in plays if play["skill"] == "Dig")
        self.assertEqual(dig["point_phase"], "Sideout")
        self.assertEqual(reception["start_zone"], serve["start_zone"])

    def test_point_phase_uses_scoring_team_not_error_team(self):
        cases = [
            ("S", "=", "*", "Sideout"),
            ("S", "#", "*", "Breakpoint"),
            ("A", "#", "a", "Sideout"),
            ("A", "#", "*", "Breakpoint"),
            ("A", "/", "a", "Breakpoint"),
            ("B", "/", "*", "Sideout"),
            ("D", "=", "a", "Breakpoint"),
        ]
        for skill, effect, team, phase in cases:
            with self.subTest(skill=skill, effect=effect, team=team):
                data = match_data()
                event = data["scout"]["sets"][0]["events"][0]
                winner = "*" if phase == "Breakpoint" else "a"
                event["score"] = {
                    "home": int(winner == "*"),
                    "away": int(winner == "a"),
                }
                event["exchange"]["point"] = winner
                data["scout"]["sets"][0]["events"] = [event]
                data["scout"]["sets"][0]["score"] = event["score"]
                serve = {"team": "*", "player": "02", "skill": "S", "effect": "+"}
                terminal = {
                    "team": team,
                    "player": "02",
                    "skill": skill,
                    "effect": effect,
                }
                event["exchange"]["plays"] = (
                    [terminal] if skill == "S" else [serve, terminal]
                )
                plays = dv.read_dv(self.write_match(data))
                row = [
                    play
                    for play in plays
                    if play["skill"]
                    == {
                        "S": "Serve",
                        "A": "Attack",
                        "B": "Block",
                        "D": "Dig",
                    }[skill]
                ][-1]
                self.assertEqual(row["point_phase"], phase)
                if skill == "A":
                    self.assertEqual(
                        row["attack_phase"],
                        "Transition breakpoint"
                        if team == "*"
                        else "Transition sideout",
                    )

    def test_missing_defaults_and_wrapped_liberos(self):
        data = match_data()
        data["team"]["home"]["libero"] = [[0]]
        attack = data["scout"]["sets"][0]["events"][0]["exchange"]["plays"][3]
        attack.update(hitType="~", skillType="~", effect="~")
        match = dv.load_dv(self.write_match(data))
        self.assertEqual(match["players"]["home"][1]["role"], "libero")
        attack = next(play for play in match["plays"] if play["skill"] == "Attack")
        self.assertEqual(attack["skill_type"], "High ball attack")
        self.assertEqual(attack["skill_subtype"], "Hard")
        self.assertEqual(attack["evaluation_code"], "+")

    def test_lineup_only_set_and_invalid_roster_numbers(self):
        data = match_data()
        data["scout"]["sets"][0]["events"] = []
        del data["scout"]["sets"][0]["score"]
        plays = dv.read_dv(self.write_match(data))
        self.assertEqual(len(plays), 4)
        self.assertTrue(all(">LUp" in play["code"] for play in plays))
        self.assertFalse(any(play["substitution"] for play in plays))
        data["team"]["home"]["players"].append(
            {"shirtNumber": "invalid", "code": "unmatched"}
        )
        data["scout"]["sets"][0]["startingLineup"]["home"]["positions"]["6"] = None
        plays = dv.read_dv(self.write_match(data))
        self.assertTrue(all(play["home_player_id6"] is None for play in plays))

    def test_minimal_actions_faults_and_duplicate_source_ids(self):
        data = match_data()
        data["scout"]["sets"][0]["score"] = {"home": 1, "away": 0}
        data["scout"]["sets"][0]["events"] = [
            {
                "_id": "duplicate",
                "exchange": {
                    "point": "*",
                    "plays": [
                        {"_id": "duplicate", "team": "*", "player": "$$", "skill": "S"},
                        {"_id": "fault", "invalid": ">>WRONG_SCORE"},
                    ],
                },
            }
        ]
        plays = dv.read_dv(self.write_match(data))
        serve = next(play for play in plays if play["skill"] == "Serve")
        self.assertEqual(serve["code"], "*00SH+")
        self.assertIsNone(serve["file_line_number"])
        self.assertIsNone(serve["player_number"])
        self.assertEqual(serve["home_team_score"], 1)
        fault = next(play for play in plays if play["code"] == ">WRONG_SCORE")
        self.assertIsNone(fault["skill"])
        self.assertIsNone(fault["player_number"])

    def test_local_fixture_when_available(self):
        path = Path(dv.__file__).parent / "data" / "2025-08-20 FORD-Fairfield.vsm"
        if not path.exists():
            self.skipTest("Local VSM fixture is intentionally gitignored")
        match = dv.load_dv(path)
        self.assertEqual(len(match["players"]["home"]), 17)
        self.assertEqual(len(match["players"]["visiting"]), 17)
        self.assertEqual(
            match["match_result"],
            {
                "team_1_sets_won": 1,
                "team_2_sets_won": 4,
                "total_sets_played": 5,
                "match_winner": "team_2",
            },
        )
        plays = match["plays"]
        self.assertEqual(sum(play["timeout"] for play in plays), 6)
        self.assertEqual(sum(play["substitution"] for play in plays), 40)
        self.assertEqual(sum(play["end_of_set"] for play in plays), 5)
        skills = {"Serve", "Reception", "Set", "Attack", "Block", "Dig", "Freeball"}
        self.assertEqual(sum(play["skill"] in skills for play in plays), 1072)
        self.assertTrue(all(len(play) == 88 for play in plays))
        source = json.loads(path.read_text(encoding="utf-8-sig"))
        for number, match_set in enumerate(source["scout"]["sets"], 1):
            groups = {}
            for play in plays:
                if play["set_number"] == number and not play["end_of_set"]:
                    groups.setdefault(play["point_id"], []).append(play)
            self.assertEqual(len(groups), len(match_set["events"]))
            for event, rows in zip(match_set["events"], groups.values(), strict=True):
                if "score" in event:
                    for row in rows:
                        self.assertEqual(
                            (row["home_team_score"], row["visiting_team_score"]),
                            (event["score"]["home"], event["score"]["away"]),
                        )
        source_skills = [
            play
            for match_set in source["scout"]["sets"]
            for event in match_set["events"]
            for play in (event.get("exchange") or {}).get("plays", [])
        ]
        for source_play, row in zip(
            source_skills,
            (play for play in plays if play["skill"] in skills),
            strict=True,
        ):
            if source_play["skill"] in {"E", "B"}:
                expected_zone = source_play.get("startZone")
                if expected_zone is None:
                    expected_zone = source_play.get("endZone")
                self.assertEqual(row["end_zone"], expected_zone)
        for number, home, away in [
            (1, 21, 25),
            (2, 15, 25),
            (3, 30, 32),
            (4, 20, 25),
            (5, 15, 12),
        ]:
            final = [play for play in plays if play["set_number"] == number][-1]
            self.assertEqual(
                (final["home_team_score"], final["visiting_team_score"]), (home, away)
            )


if __name__ == "__main__":
    unittest.main()
