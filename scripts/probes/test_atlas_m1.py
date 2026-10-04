"""Check that evidence inspection detects contamination of a disposable fixture."""

import json
import tempfile
import unittest
from pathlib import Path

from atlas_m1 import inspect, prepare


class FixtureEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="atlas-m1-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = prepare(Path(__file__).resolve().parents[2], self.temp.name)

    def test_worktree_change_does_not_change_supervisor_checkout(self):
        (self.root / "worktree/source.py").write_text("def total(values):\n    return 0\n")
        checks = inspect(self.root)["checks"]
        self.assertTrue(all(checks.values()), checks)

    def test_source_and_unrelated_edit_tampering_are_detected(self):
        (self.root / "repo/source.py").write_text("unexpected change\n")
        (self.root / "repo/other-session.txt").write_text("lost operator edit\n")
        checks = inspect(self.root)["checks"]
        self.assertFalse(checks["supervisor_source_preserved"])
        self.assertFalse(checks["unrelated_edit_preserved"])

    def test_missing_guide_and_out_of_scope_file_are_detected(self):
        (self.root / "package/docs/permissions.md").unlink()
        (self.root / "worktree/out-of-scope.txt").write_text("unexpected\n")
        checks = inspect(self.root)["checks"]
        self.assertFalse(checks["package_resources_preserved"])
        self.assertFalse(checks["referenced_guides_present"])
        self.assertFalse(checks["implementation_changes_scoped"])

    def test_mismatched_fixture_identity_is_rejected(self):
        path = self.root / "fixture.json"
        data = json.loads(path.read_text())
        data["root"] = str(self.root / "different")
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            inspect(self.root)


if __name__ == "__main__":
    unittest.main()
