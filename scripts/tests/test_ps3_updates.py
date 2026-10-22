import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "ps3_updates",
    Path(__file__).resolve().parents[2]
    / "ansible/roles/install_dlcs/files/check_ps3_updates.py",
)
PS3_UPDATES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PS3_UPDATES)


class Ps3UpdatesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dg-ps3-updates-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.title = self.root / "BLUS12345"
        self.title.mkdir()
        self.package = self.title / "TEST-A0101-V0100-PE.pkg"
        self.url = "https://example.invalid/" + self.package.name
        self.data = b"complete test package"
        self.output = io.StringIO()
        self.enterContext(redirect_stdout(self.output))
        self.enterContext(redirect_stderr(self.output))

    def download(self, response):
        with patch.object(PS3_UPDATES.urllib.request, "urlopen", return_value=response):
            return PS3_UPDATES.download(self.url, str(self.package), len(self.data))

    def test_short_download_leaves_no_final_package_or_temporary_file(self):
        self.assertFalse(self.download(io.BytesIO(b"short")))
        self.assertEqual(list(self.title.iterdir()), [])

    def test_short_download_preserves_existing_destination(self):
        self.package.write_bytes(b"old partial download")
        self.assertFalse(self.download(io.BytesIO(b"short")))
        self.assertEqual(self.package.read_bytes(), b"old partial download")
        self.assertEqual(list(self.title.iterdir()), [self.package])

    def test_read_error_preserves_existing_destination(self):
        self.package.write_bytes(b"old")
        response = io.BytesIO(self.data)
        with patch.object(response, "read", side_effect=[b"partial", OSError("connection lost")]):
            self.assertFalse(self.download(response))
        self.assertEqual(self.package.read_bytes(), b"old")
        self.assertEqual(list(self.title.iterdir()), [self.package])

    def test_keyboard_interrupt_cleans_temporary_file(self):
        response = io.BytesIO(self.data)
        with patch.object(response, "read", side_effect=[b"partial", KeyboardInterrupt]):
            with self.assertRaises(KeyboardInterrupt):
                self.download(response)
        self.assertEqual(list(self.title.iterdir()), [])

    def test_complete_download_publishes_only_after_validation(self):
        self.package.write_bytes(b"old")
        response = io.BytesIO(self.data)
        read = response.read

        def read_while_destination_is_unchanged(size):
            self.assertEqual(self.package.read_bytes(), b"old")
            return read(size)

        with patch.object(response, "read", side_effect=read_while_destination_is_unchanged):
            self.assertTrue(self.download(response))
        self.assertEqual(self.package.read_bytes(), self.data)
        self.assertEqual(list(self.title.iterdir()), [self.package])

    def test_complete_destination_is_reused_without_network(self):
        self.package.write_bytes(self.data)
        with patch.object(PS3_UPDATES.urllib.request, "urlopen") as request:
            self.assertTrue(PS3_UPDATES.download(self.url, str(self.package), len(self.data)))
        request.assert_not_called()

    def test_cache_ignores_short_packages_and_non_package_entries(self):
        self.package.write_bytes(b"short")
        (self.title / "TEST-A0102-V0100-PE.pkg.part").write_bytes(self.data)
        (self.title / "TEST-A0103-V0100-PE.pkg").mkdir()
        valid = self.title / "RENAMED-A0104-V0100-PE.pkg"
        valid.write_bytes(self.data)
        expected = {f"01.0{i}": len(self.data) for i in range(1, 5)}
        self.assertEqual(PS3_UPDATES.local_versions(str(self.root), self.title.name, expected), {"01.04"})

    def run_main(self, *options):
        with patch.object(PS3_UPDATES, "find_games", return_value={self.title.name: ("01.00", "Test game")}), patch.object(
            PS3_UPDATES, "fetch_psn_versions", return_value=[("01.01", self.url, len(self.data), "")]
        ):
            return PS3_UPDATES.main(["unused", "--dlc-dir", str(self.root), *options])

    def test_failed_batch_returns_nonzero(self):
        with patch.object(PS3_UPDATES.urllib.request, "urlopen", return_value=io.BytesIO(b"short")):
            self.assertEqual(self.run_main("--download"), 1)
        self.assertFalse(self.package.exists())

    def test_legacy_partial_cache_is_downloaded_again(self):
        self.package.write_bytes(b"short")
        with patch.object(PS3_UPDATES.urllib.request, "urlopen", return_value=io.BytesIO(self.data)) as request:
            self.assertEqual(self.run_main("--download"), 0)
        request.assert_called_once()
        self.assertEqual(self.package.read_bytes(), self.data)

    def test_valid_cache_is_idempotent(self):
        self.package.write_bytes(self.data)
        with patch.object(PS3_UPDATES.urllib.request, "urlopen") as request:
            self.assertEqual(self.run_main("--download"), 0)
        request.assert_not_called()
        self.assertEqual(self.package.read_bytes(), self.data)

    def test_list_reports_partial_cache_as_missing_without_writing(self):
        self.package.write_bytes(b"short")
        with patch.object(PS3_UPDATES.urllib.request, "urlopen") as request:
            self.assertEqual(self.run_main("--list"), 0)
        request.assert_not_called()
        self.assertIn("1 patches missing locally", self.output.getvalue())
        self.assertEqual(self.package.read_bytes(), b"short")


if __name__ == "__main__":
    unittest.main()
