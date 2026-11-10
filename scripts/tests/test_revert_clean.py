import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "dg_revert_clean", Path(__file__).resolve().parents[1] / "dg-revert-clean.py"
)
REVERT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVERT)


class RevertCleanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dg-revert-clean-")
        self.root = Path(self.tmp.name)
        self.box = self.root / "box"
        self.install = self.box / "tools" / "game"
        self.saves = self.install / "data"
        self.saves.mkdir(parents=True)
        (self.install / "game.bin").write_bytes(b"program")
        (self.install / "data" / "config.ini").write_bytes(b"config")
        (self.saves / "slot1.sav").write_bytes(b"save")
        self.backups = self.root / "backups.yml"
        self.backups.write_text(
            "dg_save_sets:\n"
            "  - { name: game, src: [\"file:tools/game/data/slot1.sav\"] }\n"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_revert_keeps_registered_save_and_removes_program(self):
        saves = REVERT.load_saves(str(self.backups), str(self.box), "player")
        kept = REVERT.clean(str(self.install), saves)

        self.assertEqual(kept, [str(self.saves / "slot1.sav")])
        self.assertTrue((self.saves / "slot1.sav").exists())
        self.assertFalse((self.install / "game.bin").exists())
        self.assertFalse((self.install / "data" / "config.ini").exists())

    def test_revert_keeps_a_registered_save_directory_whole(self):
        (self.saves / "slot2.sav").write_bytes(b"save")
        saves = REVERT.load_saves(str(self.backups), str(self.box), "player")
        saves.append(str(self.saves))
        REVERT.clean(str(self.install), saves)

        self.assertTrue((self.saves / "slot1.sav").exists())
        self.assertTrue((self.saves / "slot2.sav").exists())
        self.assertFalse((self.install / "game.bin").exists())

    def test_revert_deletes_a_path_with_no_registered_saves(self):
        other = self.box / "tools" / "other"
        other.mkdir(parents=True)
        (other / "x").write_bytes(b"x")
        saves = REVERT.load_saves(str(self.backups), str(self.box), "player")
        REVERT.clean(str(other), saves)
        self.assertFalse(other.exists())

    def test_save_sources_resolve_file_prefix_and_user_placeholder(self):
        backups = self.root / "b2.yml"
        backups.write_text(
            "dg_save_sets:\n"
            "  - { name: a, src: \"file:tools/game/data/slot1.sav\" }\n"
            "  - { name: b, src: \".local/share/{{ ansible_facts.user_id }}/save\" }\n"
        )
        saves = REVERT.load_saves(str(backups), str(self.box), "player")
        self.assertIn(str(self.box / "tools/game/data/slot1.sav"), saves)
        self.assertIn(str(self.box / ".local/share/player/save"), saves)


if __name__ == "__main__":
    unittest.main()
