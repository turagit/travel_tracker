import os
import plistlib
import tempfile
import unittest
from src.shortcut_generator.generator import generate_shortcuts


class TestGenerator(unittest.TestCase):
    def test_generates_three_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = generate_shortcuts(output_dir=tmpdir)
            self.assertEqual(len(files), 3)
            for f in files:
                self.assertTrue(os.path.exists(f))
                self.assertTrue(f.endswith(".shortcut"))

    def test_file_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = generate_shortcuts(output_dir=tmpdir)
            basenames = sorted(os.path.basename(f) for f in files)
            self.assertEqual(basenames, ["Travel Tracker Setup.shortcut", "Trip End.shortcut", "Trip Start.shortcut"])

    def test_files_are_valid_plists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = generate_shortcuts(output_dir=tmpdir)
            for f in files:
                with open(f, "rb") as fh:
                    data = plistlib.load(fh)
                self.assertIn("WFWorkflowActions", data)
                self.assertGreater(len(data["WFWorkflowActions"]), 0)


if __name__ == "__main__":
    unittest.main()
