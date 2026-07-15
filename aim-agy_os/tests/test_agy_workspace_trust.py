#!/usr/bin/env python3
"""Tests for AGY folder-trust helper (exact path registration)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".aim_core"))

import agy_workspace_trust as awt  # noqa: E402


class AgyWorkspaceTrustTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = Path(self.tmp.name) / "settings.json"
        self.settings.write_text(json.dumps({"trustedWorkspaces": []}) + "\n")
        self.cwd = Path(self.tmp.name) / "project"
        self.cwd.mkdir()
        self._patch = mock.patch.object(awt, "SETTINGS_PATH", self.settings)
        self._patch.start()
        self._legacy = mock.patch.object(
            awt, "LEGACY_TRUSTED", Path(self.tmp.name) / "trustedFolders.json"
        )
        self._legacy.start()

    def tearDown(self):
        self._patch.stop()
        self._legacy.stop()
        self.tmp.cleanup()

    def test_exact_path_required(self):
        parent = str(self.cwd)
        child = self.cwd / "nested"
        child.mkdir()
        awt.ensure_workspace_trusted(parent, quiet=True)
        self.assertTrue(awt.is_workspace_trusted(parent))
        # Parent trust must NOT imply child (AGY exact-match semantics)
        self.assertFalse(awt.is_workspace_trusted(str(child)))
        awt.ensure_workspace_trusted(str(child), quiet=True)
        self.assertTrue(awt.is_workspace_trusted(str(child)))

    def test_prepare_registers(self):
        path = awt.prepare_agy_spawn(str(self.cwd), quiet=True)
        self.assertEqual(path, str(self.cwd.resolve()))
        self.assertTrue(awt.is_workspace_trusted(path))

    def test_pane_markers(self):
        self.assertTrue(
            awt.pane_shows_trust_prompt("Do you trust the contents of this project")
        )
        self.assertFalse(awt.pane_shows_trust_prompt("Antigravity CLI 1.1.2"))


if __name__ == "__main__":
    unittest.main()
