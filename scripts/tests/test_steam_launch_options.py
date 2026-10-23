import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "set-steam-launch-options.py"
SPEC = importlib.util.spec_from_file_location("steam_launch_options", SCRIPT)
STEAM_OPTIONS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STEAM_OPTIONS)


def block(key, contents, depth=0):
    indent = "\t" * depth
    return f'{indent}"{key}"\n{indent}{{\n{contents}{indent}}}\n'


def localconfig(apps="", siblings=""):
    contents = block("apps", apps, 4)
    contents = block("Steam", contents, 3)
    contents = block("Valve", contents, 2)
    return block("UserLocalConfigStore", siblings + block("Software", contents, 1))


class SteamLaunchOptionsTests(unittest.TestCase):
    def test_empty_apps_block_accepts_first_launch_option(self):
        lines = localconfig().splitlines(keepends=True)
        self.assertTrue(STEAM_OPTIONS.set_launch_option(lines, "1018010", "DXVK_FRAME_RATE=60 %command%"))
        self.assertIn('"1018010"', "".join(lines))
        self.assertIn('"LaunchOptions"\t\t"DXVK_FRAME_RATE=60 %command%"', "".join(lines))
        self.assertFalse(STEAM_OPTIONS.set_launch_option(lines, "1018010", "DXVK_FRAME_RATE=60 %command%"))

    def test_never_played_app_needs_no_last_played_field(self):
        app = block("1018010", '\t' * 6 + '"ViewedLaunchEula"\t\t"1"\n', 5)
        lines = localconfig(app).splitlines(keepends=True)
        self.assertTrue(STEAM_OPTIONS.set_launch_option(lines, "1018010", "%command%"))
        self.assertIn('"ViewedLaunchEula"\t\t"1"', "".join(lines))
        self.assertEqual("".join(lines).count('"1018010"'), 1)

    def test_unrelated_apps_block_with_launch_options_is_preserved(self):
        decoy_app = block("1018010", '\t' * 6 + '"LaunchOptions"\t\t"keep me"\n', 5)
        decoy = block("Other", block("Valve", block("Steam", block("apps", decoy_app, 4), 3), 2), 1)
        lines = localconfig(siblings=decoy).splitlines(keepends=True)
        self.assertTrue(STEAM_OPTIONS.set_launch_option(lines, "1018010", "new option"))
        self.assertIn(decoy, "".join(lines))
        start, end = STEAM_OPTIONS.find_steam_apps_block(lines)
        self.assertIn('"new option"', "".join(lines[start:end]))
        self.assertNotIn('"keep me"', "".join(lines[start:end]))

    def test_missing_canonical_path_does_not_modify_unrelated_apps(self):
        decoy = block("Other", block("Valve", block("Steam", block("apps", "", 4), 3), 2), 1)
        original = block("UserLocalConfigStore", decoy)
        lines = original.splitlines(keepends=True)
        with self.assertRaisesRegex(ValueError, "could not find"):
            STEAM_OPTIONS.set_launch_option(lines, "1018010", "%command%")
        self.assertEqual("".join(lines), original)

    def test_key_casing_and_spaces_are_accepted(self):
        original = localconfig().replace('"Software"', '"software"').replace("\t", "    ")
        lines = original.splitlines(keepends=True)
        self.assertTrue(STEAM_OPTIONS.set_launch_option(lines, "1018010", "%command%"))
        self.assertFalse(STEAM_OPTIONS.set_launch_option(lines, "1018010", "%command%"))

    def test_existing_options_are_updated_without_changing_other_apps(self):
        first = block("1018010", '\t' * 6 + '"LaunchOptions"\t\t"old"\n', 5)
        other = block("123", '\t' * 6 + '"LastPlayed"\t\t"12345"\n', 5)
        original = localconfig(first + other)
        lines = original.splitlines(keepends=True)
        self.assertTrue(STEAM_OPTIONS.set_launch_option(lines, "1018010", "new"))
        self.assertEqual("".join(lines), original.replace('"old"', '"new"'))

    def test_cli_creates_backup_escapes_options_and_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="dg-steam-options-test-") as temporary:
            config = Path(temporary) / "localconfig.vdf"
            original = localconfig()
            config.write_text(original)
            option = 'WINEDLLOVERRIDES="sensapi=n,b" %command%'
            command = [sys.executable, str(SCRIPT), "--localconfig", str(config), "--set", "1018000", option]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("changed: true", first.stdout)
            self.assertIn('WINEDLLOVERRIDES=\\"sensapi=n,b\\" %command%', config.read_text())
            backup = config.with_suffix(".vdf.bak-dg-metal-gear")
            self.assertEqual(backup.read_text(), original)
            written = config.read_bytes()
            modified = config.stat().st_mtime_ns
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("changed: false", second.stdout)
            self.assertEqual(config.read_bytes(), written)
            self.assertEqual(config.stat().st_mtime_ns, modified)
            self.assertEqual(backup.read_text(), original)


if __name__ == "__main__":
    unittest.main()
