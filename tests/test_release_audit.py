# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import importlib.util
from pathlib import Path
import unittest


class ReleaseAuditTest(unittest.TestCase):
    def test_source_tree_passes_release_audit(self):
        script = Path(__file__).resolve().parents[1] / "scripts/verify_release.py"
        spec = importlib.util.spec_from_file_location("verify_release", script)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertEqual([], module.audit())


if __name__ == "__main__":
    unittest.main()
