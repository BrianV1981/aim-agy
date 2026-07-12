"""TDD coverage for vessel-prefixed reincarnation tmux session names (#93)."""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1] / ".aim_core"
sys.path.insert(0, str(CORE))

from reincarnation.session_naming import (  # noqa: E402
    is_reincarnation_session,
    reincarnation_session_name,
    vessel_cli_id,
)


def test_default_vessel_is_agy():
    assert vessel_cli_id({}) == "agy"
    assert vessel_cli_id({"AIM_VESSEL_CLI": ""}) == "agy"
    assert vessel_cli_id({"AIM_VESSEL_CLI": "   "}) == "agy"


def test_vessel_cli_from_env():
    assert vessel_cli_id({"AIM_VESSEL_CLI": "grok"}) == "grok"
    assert vessel_cli_id({"AIM_VESSEL_CLI": "OpenCode"}) == "opencode"
    assert vessel_cli_id({"AIM_VESSEL_CLI": "aim-agy!"}) == "aim-agy_"


def test_session_name_default_prefix_and_timestamp():
    name = reincarnation_session_name({}, timestamp=1783840823)
    assert name == "agy_reincarnation_1783840823"


def test_session_name_respects_aim_vessel_cli():
    name = reincarnation_session_name(
        {"AIM_VESSEL_CLI": "opencode"}, timestamp=99
    )
    assert name == "opencode_reincarnation_99"


def test_session_name_live_timestamp_is_numeric_suffix():
    before = int(time.time())
    name = reincarnation_session_name({"AIM_VESSEL_CLI": "agy"})
    after = int(time.time())
    assert name.startswith("agy_reincarnation_")
    ts = int(name.rsplit("_", 1)[-1])
    assert before <= ts <= after


def test_is_reincarnation_session_matcher():
    env = {"AIM_VESSEL_CLI": "agy"}
    assert is_reincarnation_session("agy_reincarnation_123", env)
    assert not is_reincarnation_session("aim_reincarnation_123", env)
    assert not is_reincarnation_session("grok_reincarnation_123", env)
    assert not is_reincarnation_session("agy_reincarnation_", env)
    assert not is_reincarnation_session("agy_reincarnation_abc", env)


def test_legacy_aim_prefix_is_not_used_by_builder():
    name = reincarnation_session_name({}, timestamp=1)
    assert not name.startswith("aim_reincarnation_")
    assert name.startswith("agy_reincarnation_")


@pytest.mark.skipif(
    subprocess.run(["which", "tmux"], capture_output=True).returncode != 0,
    reason="tmux not installed",
)
def test_tmux_e2e_session_visible_under_vessel_prefix():
    """Integration: create a real tmux session with the vessel name."""
    name = reincarnation_session_name({"AIM_VESSEL_CLI": "agy"}, timestamp=int(time.time()))
    assert re.fullmatch(r"agy_reincarnation_[0-9]+", name)
    subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
    try:
        r = subprocess.run(
            ["tmux", "new-session", "-d", "-s", name, "sleep", "30"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert r.returncode == 0, r.stderr
        listed = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout
        prefix = "agy_reincarnation"
        matches = [ln for ln in listed.splitlines() if ln.startswith(prefix)]
        assert name in matches
        assert is_reincarnation_session(name, {"AIM_VESSEL_CLI": "agy"})
    finally:
        subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
