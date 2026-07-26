"""Expanded E2E / chaos tests for Handoff vNext three pipelines."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

OS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OS))
sys.path.insert(0, str(OS / ".aim_core"))

from handoff.adapters.fixture import FixtureAdapter
from handoff.blackbox_cron import run_blackbox_cron
from handoff.handoff_core import run_handoff
from handoff.models import Turn
from handoff.packet import build_packet, validate_packet

FIX_SRC = OS / "tests" / "fixtures" / "handoff_vnext"
MARKER = "E2E_HANDOFF_VNEXT_MARKER_7f3a"
PY = OS / "venv" / "bin" / "python3"
if not PY.is_file():
    PY = Path(sys.executable)


def _write_session(root: Path, sid: str, turns: list, cwd: str) -> Path:
    d = root / sid
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(json.dumps({"cwd": cwd}) + "\n", encoding="utf-8")
    lines = []
    for role, text in turns:
        kind = "user_message_chunk" if role == "user" else "agent_message_chunk"
        lines.append(
            json.dumps(
                {
                    "timestamp": time.time(),
                    "method": "session/update",
                    "params": {
                        "sessionId": sid,
                        "update": {
                            "sessionUpdate": kind,
                            "content": {"type": "text", "text": text},
                        },
                    },
                }
            )
        )
    (d / "updates.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d


class VesselE2EBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hvnext_e2e_"))
        (self.tmp / "aim-agy_os" / ".aim_core").mkdir(parents=True)
        (self.tmp / "aim-agy_os" / "setup.sh").write_text("#!/bin/bash\n")
        self.fix = self.tmp / "fixtures"
        self.fix.mkdir()
        # seed alpha-like session
        _write_session(
            self.fix,
            "e2e-alpha",
            [
                ("user", f"Wake. {MARKER} MANDATE: pipeline A."),
                ("assistant", "Ack. TODO: run tests."),
                ("user", "[[KEEP]] no agent spin-up for handoff"),
                ("assistant", "Understood."),
            ],
            str(self.tmp),
        )
        self.adapter = FixtureAdapter(self.fix)
        os.environ["AIM_BLACKBOX_ALLOW_CRON"] = "1"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestHandoffE2E(VesselE2EBase):
    def test_happy_path_packet_and_result_json(self):
        res = run_handoff(
            adapter=self.adapter,
            session_id="e2e-alpha",
            cwd=self.tmp,
            root=self.tmp,
            vessel="e2e-vessel",
            marker=MARKER,
        )
        self.assertEqual(res.status, "ok", res.to_dict())
        self.assertEqual(res.code, "OK")
        for g in ("G0", "G1", "G2", "G3", "G4", "G5"):
            self.assertTrue(res.gates.get(g), f"gate {g} false: {res.gates}")
        cur = Path(res.paths["continuity"])
        body = cur.read_text(encoding="utf-8")
        self.assertIn(MARKER, body)
        self.assertIn("Schema-Version: 1", body)
        self.assertIn("## Do Not Forget", body)
        result = self.tmp / "continuity" / "handoff_result.json"
        self.assertTrue(result.is_file())
        data = json.loads(result.read_text())
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["session_id"], "e2e-alpha")

    def test_wrong_session_id_fails_loud(self):
        res = run_handoff(
            adapter=self.adapter,
            session_id="does-not-exist-uuid",
            cwd=self.tmp,
            root=self.tmp,
            marker=MARKER,
        )
        self.assertEqual(res.status, "error")
        self.assertEqual(res.code, "RESOLVE_FAIL")
        self.assertFalse(res.gates.get("G0"))

    def test_empty_session_no_false_success(self):
        _write_session(self.fix, "empty-sess", [], str(self.tmp))
        # empty updates file
        (self.fix / "empty-sess" / "updates.jsonl").write_text("{}\n")
        res = run_handoff(
            adapter=self.adapter,
            session_id="empty-sess",
            cwd=self.tmp,
            root=self.tmp,
            marker=MARKER,
        )
        self.assertIn(res.status, ("empty", "error"))
        self.assertNotEqual(res.code, "OK")
        # must not claim SUCCESS
        self.assertNotEqual(res.status, "ok")

    def test_double_handoff_updates_current_keeps_history(self):
        run_handoff(
            adapter=self.adapter,
            session_id="e2e-alpha",
            cwd=self.tmp,
            root=self.tmp,
            marker=MARKER,
        )
        # second user turn appended
        path = self.fix / "e2e-alpha" / "updates.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": time.time(),
                        "method": "session/update",
                        "params": {
                            "sessionId": "e2e-alpha",
                            "update": {
                                "sessionUpdate": "user_message_chunk",
                                "content": {
                                    "type": "text",
                                    "text": f"Second pass {MARKER} KEEP going",
                                },
                            },
                        },
                    }
                )
                + "\n"
            )
        res2 = run_handoff(
            adapter=self.adapter,
            session_id="e2e-alpha",
            cwd=self.tmp,
            root=self.tmp,
            marker=MARKER,
        )
        self.assertEqual(res2.status, "ok")
        cur = Path(res2.paths["continuity"]).read_text()
        self.assertIn("Second pass", cur)
        hist = self.tmp / "continuity" / "history" / "e2e-alpha.md"
        self.assertTrue(hist.is_file())

    def test_marker_must_appear_in_self_check(self):
        res = run_handoff(
            adapter=self.adapter,
            session_id="e2e-alpha",
            cwd=self.tmp,
            root=self.tmp,
            marker="CUSTOM_MARKER_XYZ",
        )
        self.assertEqual(res.status, "ok")
        body = Path(res.paths["continuity"]).read_text()
        self.assertIn("- marker: CUSTOM_MARKER_XYZ", body)



if __name__ == "__main__":
    unittest.main()
