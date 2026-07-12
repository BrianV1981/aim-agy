"""Vessel-scoped tmux session names for reincarnation."""
from __future__ import annotations

import os
import re
import time


def vessel_cli_id(env: dict | None = None) -> str:
    """Return sanitized vessel id used as the reincarnation session prefix.

    aim-agy default is ``agy``. Override with ``AIM_VESSEL_CLI`` (e.g. grok, opencode).
    """
    source = env if env is not None else os.environ
    raw = (source.get("AIM_VESSEL_CLI") or "agy").strip().lower()
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    return cleaned or "agy"


def reincarnation_session_name(
    env: dict | None = None,
    *,
    timestamp: int | None = None,
) -> str:
    """Build ``{vessel}_reincarnation_{unix_ts}`` for a new tmux vessel session."""
    vessel = vessel_cli_id(env)
    ts = int(time.time()) if timestamp is None else int(timestamp)
    return f"{vessel}_reincarnation_{ts}"


def is_reincarnation_session(name: str, env: dict | None = None) -> bool:
    """True if *name* matches this vessel's reincarnation session pattern."""
    prefix = f"{vessel_cli_id(env)}_reincarnation_"
    if not name.startswith(prefix):
        return False
    suffix = name[len(prefix) :]
    return bool(re.fullmatch(r"[0-9]+", suffix))
