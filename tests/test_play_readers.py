import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

import datavolley as dv
from datavolley.types import normalize_play

ANALYSIS_FIELDS = (
    "match_id",
    "home_team",
    "home_team_id",
    "visiting_team",
    "visiting_team_id",
    "point_id",
    "team_touch_id",
    "code",
    "team",
    "team_id",
    "player_number",
    "player_name",
    "player_id",
    "skill",
    "skill_type",
    "evaluation_code",
    "evaluation",
    "attack_code",
    "attack_description",
    "set_code",
    "set_description",
    "set_type",
    "start_zone",
    "end_zone",
    "end_subzone",
    "end_cone",
    "skill_subtype",
    "timeout",
    "end_of_set",
    "substitution",
    "point",
    "home_team_score",
    "visiting_team_score",
    "home_score_start_of_point",
    "visiting_score_start_of_point",
    "point_phase",
    "attack_phase",
    "set_number",
    "point_won_by",
    "winning_attack",
    "serving_team",
    "receiving_team",
    "phase",
    "home_setter_position",
    "visiting_setter_position",
    "file_line_number",
    "rally_number",
    "possession_number",
    "setter_position",
    "source_file",
)


def roster_line(number: str, player_id: str, name: str) -> str:
    return f"0;{number};;;;;;;{player_id};{name};"


def match_content(codes: list[str], *, cones: bool = False) -> str:
    header = [
        "10/16/2026",
        "12.00.00",
        "",
        "",
        "",
        "",
        "",
        "123456",
        "",
        "",
        "C" if cones else "Z",
    ]
    scout = []
    for code in codes:
        fields = [""] * 26
        fields[0] = code
        fields[1:3] = ["s", "r"]
        fields[4:7] = ["0431", "-1-1", "7642"]
        fields[7:11] = ["12.01.02", "1", "1", "6"]
        fields[12] = "495"
        fields[14:26] = ["02", "3", "4", "5", "6", "7"] * 2
        scout.append(";".join(fields))
    return "\n".join(
        [
            "[3MATCH]",
            ";".join(header),
            "[3TEAMS]",
            "17; Hôme ",
            "42; Visiting ",
            "[3PLAYERS-H]",
            roster_line("02", "-101", "First"),
            roster_line("2", "-102", "Duplicate"),
            roster_line("0", "-103", "Zero"),
            "[3PLAYERS-V]",
            roster_line("2", "non-numeric", "Opponent"),
            "[3SCOUT]",
            "",
            "\x00",
            *scout,
        ]
    )


class PlayReaderTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def assert_analysis_matches_full(self, path: str) -> list[dict]:
        with patch("datavolley.utils.metadata.uuid.uuid4", return_value=UUID(int=0)):
            full = dv.read_dv(path)
            analysis = dv.read_plays(path)
        self.assertEqual(len(analysis), len(full))
        for lean, complete in zip(analysis, full, strict=True):
            self.assertEqual(tuple(lean), ANALYSIS_FIELDS)
            expected = {field: complete[field] for field in ANALYSIS_FIELDS[:-1]}
            expected["source_file"] = path
            self.assertEqual(lean, expected)
            for field in ANALYSIS_FIELDS[:-1]:
                self.assertIs(type(lean[field]), type(complete[field]), field)
        return analysis

    def test_analysis_matches_full_reader_on_all_bundled_files(self):
        for path in dv.example_file_list():
            with self.subTest(path=path):
                self.assert_analysis_matches_full(path)

    def test_raw_reader_matches_scout_extraction(self):
        path = self.directory / "raw match.dvw"
        content = match_content(["*02SM+~~~78A~~~00", "ap00:01"])
        path.write_text(content, encoding="utf-8")
        raw = dv.read_raw_plays(str(path))
        expected = dv.extract_plays(content)
        for row in expected:
            row["source_file"] = str(path)
        self.assertEqual(raw, expected)
        self.assertEqual(tuple(raw[0]), tuple(expected[0]))
        self.assertEqual(raw[0]["home_p1"], "02")
        self.assertEqual(raw[1]["visiting_score"], "01")
        self.assertEqual(raw[0]["time"].isoformat(), "2026-10-16T12:01:02")
        self.assertNotIn("skill", raw[0])
        self.assertNotIn("rally_number", raw[0])

    def test_context_events_and_player_id_policy(self):
        codes = [
            "*02SM+~~~78A~~~00",
            "a02RM#~~~58AM~~00B",
            "a02EH#~~~~~~~~~~~",
            "a02AH#~~~48H~~~00",
            "*02B1=~~~48H~~~00",
            "ap00:01",
            "*T",
            "aP02:03",
            "*09SM+~~~78A~~~00",
            "*00SM+~~~78A~~~00",
            "*$$SM+~~~78A~~~00",
            "**1set",
        ]
        path = self.directory / "context.dvw"
        path.write_text(match_content(codes), encoding="utf-8")
        plays = self.assert_analysis_matches_full(str(path))
        self.assertEqual(len(plays), len(codes))
        self.assertEqual(
            (plays[0]["player_name"], plays[0]["player_id"]), ("First", -101)
        )
        self.assertEqual(plays[0]["home_team"], "Hôme")
        self.assertIsNone(plays[1]["player_id"])
        self.assertEqual(plays[1]["phase"], "Reception")
        self.assertTrue(plays[3]["winning_attack"])
        self.assertTrue(plays[5]["point"])
        self.assertTrue(plays[6]["timeout"])
        self.assertTrue(plays[7]["substitution"])
        self.assertEqual(plays[8]["player_name"], "Player 9")
        self.assertEqual(plays[9]["player_name"], "Player 0")
        self.assertIsNone(plays[10]["player_name"])
        self.assertTrue(plays[11]["end_of_set"])
        for play in plays:
            for field in (
                "point",
                "timeout",
                "substitution",
                "end_of_set",
                "winning_attack",
            ):
                self.assertIs(type(play[field]), bool)

    def test_cone_and_zone_modes(self):
        for cones in (False, True):
            with self.subTest(cones=cones):
                path = self.directory / "cones.dvw"
                path.write_text(
                    match_content(["*02AH#~~~48H~~~00"], cones=cones), encoding="utf-8"
                )
                play = self.assert_analysis_matches_full(str(path))[0]
                self.assertEqual(play["start_zone"], 4)
                self.assertEqual(play["end_cone"], 8 if cones else None)
                self.assertEqual(play["end_zone"], None if cones else 8)

    def test_latin1_crlf_and_source_line_numbers(self):
        path = self.directory / "café match.dvw"
        content = match_content(["*02SM+~~~78A~~~00"])
        path.write_bytes(content.replace("\n", "\r\n").encode("latin-1"))
        analysis = self.assert_analysis_matches_full(str(path))
        raw = dv.read_raw_plays(str(path))
        self.assertEqual(analysis[0]["home_team"], "Hôme")
        self.assertEqual(raw[0]["file_line_number"], len(content.split("\n")))
        self.assertEqual(raw[0]["line_number"], 1)
        self.assertEqual(analysis[0]["file_line_number"], raw[0]["file_line_number"])
        self.assertEqual(raw[0]["source_file"], str(path))

    def test_empty_and_missing_sections(self):
        for content in ("", "[3MATCH]\n10/16/2026", "[3SCOUT]\n\n\x00"):
            with self.subTest(content=content):
                path = self.directory / "empty.dvw"
                path.write_text(content, encoding="utf-8")
                self.assertEqual(dv.read_plays(str(path)), [])
                self.assertEqual(dv.read_raw_plays(str(path)), [])
        path = self.directory / "scout only.dvw"
        path.write_text("[3SCOUT]\n*02AH#~~~48H~~~00", encoding="utf-8")
        self.assertEqual(len(self.assert_analysis_matches_full(str(path))), 1)

    def test_missing_file_errors_include_path(self):
        path = str(self.directory / "missing.dvw")
        for reader in (dv.load_dvw, dv.read_dv, dv.read_plays, dv.read_raw_plays):
            with self.subTest(reader=reader.__name__):
                with self.assertRaises(FileNotFoundError) as raised:
                    reader(path)
                self.assertIn(path, str(raised.exception))

    def test_full_normalizer_preserves_extra_fields_and_input(self):
        original = {"code": "*02AH#~~~48H~~~00", "player_number": "02", "extra": [1]}
        snapshot = original.copy()
        normalized = normalize_play(original)
        self.assertEqual(original, snapshot)
        self.assertEqual(normalized["player_name"], "Player 2")
        self.assertEqual(normalized["end_zone"], 8)
        self.assertEqual(normalized["extra"], [1])
        self.assertEqual(list(normalized)[-1], "extra")
        self.assertEqual(len(normalized), 89)


if __name__ == "__main__":
    unittest.main()
