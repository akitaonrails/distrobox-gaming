import importlib.util
import io
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "github_game_updates", Path(__file__).resolve().parents[1] / "check-github-game-updates.py"
)
GAME_UPDATES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GAME_UPDATES)


class GithubGameUpdatesTests(unittest.TestCase):
    def test_catalog_includes_games_but_not_emulators(self):
        games = dict(GAME_UPDATES.catalog_games())
        self.assertEqual(games["gaming-opensc2k"], "nicholas-ochoa/OpenSC2K")
        self.assertNotIn("gaming-rpcs3", games)

    def test_templated_pin_resolves_from_group_vars(self):
        self.assertEqual(
            GAME_UPDATES.pinned_tag("gaming-banjotooie-recomp", {}),
            "v0.1.0-alpha.4.5",
        )

    def test_stable_pin_ignores_nightly_and_unrelated_release_streams(self):
        releases = [
            {"tag_name": "geometrywars3-v2", "published_at": "2026-10-12T00:00:00Z"},
            {"tag_name": "midnightclubla-nightly", "published_at": "2026-10-11T00:00:00Z"},
            {"tag_name": "midnightclubla-v2", "published_at": "2026-10-10T00:00:00Z"},
        ]
        with patch.object(GAME_UPDATES.shutil, "which", return_value=None), patch.object(GAME_UPDATES, "urlopen", return_value=io.BytesIO(json.dumps(releases).encode())):
            release = GAME_UPDATES.latest_release(
                "CrownParkComputing/Xbox360-Native-Ports",
                "gaming-midnightclubla",
                "midnightclubla-v1",
                None,
            )
        self.assertEqual(release["tag_name"], "midnightclubla-v2")

    def test_stable_pin_ignores_release_candidates(self):
        releases = [
            {"tag_name": "v1.3.0-rc3", "published_at": "2026-10-23T00:00:00Z", "prerelease": True},
            {"tag_name": "v1.2.3", "published_at": "2026-10-22T00:00:00Z", "prerelease": False},
        ]
        with patch.object(GAME_UPDATES.shutil, "which", return_value=None), patch.object(GAME_UPDATES, "urlopen", return_value=io.BytesIO(json.dumps(releases).encode())):
            release = GAME_UPDATES.latest_release("moesuito/gt4-staticrecomp", "gaming-gt4-recomp", "1.2.3", None)
        self.assertEqual(release["tag_name"], "v1.2.3")

    def test_gh_shim_output_is_not_used_as_token(self):
        fake = subprocess.CompletedProcess(
            ["gh", "auth", "token"], 0, "mise setup text\ngho_example123\n", ""
        )
        with patch.dict(GAME_UPDATES.os.environ, {}, clear=True), patch.object(
            GAME_UPDATES.shutil, "which", return_value="/usr/bin/gh"
        ), patch.object(GAME_UPDATES.subprocess, "run", return_value=fake):
            self.assertEqual(GAME_UPDATES.github_token(), "gho_example123")

    def test_gh_api_handles_mise_shim_preamble(self):
        fake = subprocess.CompletedProcess(
            ["gh", "api"], 0,
            'mise setup text\n[{"tag_name":"v1.2.3","published_at":"2026-10-23T00:00:00Z"}]\n',
            "",
        )
        with patch.object(GAME_UPDATES.shutil, "which", return_value="/usr/bin/gh"), patch.object(
            GAME_UPDATES.subprocess, "run", return_value=fake
        ):
            release = GAME_UPDATES.latest_release("example/game", "gaming-gt4-recomp", "1.2.3", None)
        self.assertEqual(release["tag_name"], "v1.2.3")

    def test_request_errors_do_not_print_authorization_headers(self):
        output = io.StringIO()
        with patch.object(GAME_UPDATES, "catalog_games", return_value=[("gaming-dude", "Inkub0/dude")]), patch.object(
            GAME_UPDATES, "github_token", return_value="gho_example123"
        ), patch.object(GAME_UPDATES, "latest_release", side_effect=ValueError("Bearer gho_example123")), redirect_stdout(output):
            self.assertEqual(GAME_UPDATES.main(), 1)
        self.assertIn("ERROR", output.getvalue())
        self.assertNotIn("gho_example123", output.getvalue())


if __name__ == "__main__":
    unittest.main()
