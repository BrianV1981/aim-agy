#!/usr/bin/env python3
"""AGY-native operator reincarnation → memory-wiki E2E."""
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

VESSEL = Path(os.environ.get("AIM_VESSEL", os.getcwd())).resolve()
AIM = VESSEL / "aim-agy_os"
if not (AIM / ".aim_core").is_dir():
    AIM = VESSEL  # flat layout fallback
PY3 = sys.executable
if (AIM / "venv" / "bin" / "python3").is_file():
    PY3 = str(AIM / "venv" / "bin" / "python3")
BRAIN = Path.home() / ".gemini/antigravity-cli/brain"
WIKI = AIM / "memory-wiki"
REPORT = AIM / "planning-artifacts" / "OPERATOR_E2E_REINCARNATE_WIKI_AGY_LATEST.md"

MARKER = os.environ.get("MARKER", f"OP_WIKI_AGY_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
DIRECTIVES = [
    f"OPERATOR_DIRECTIVE_1: Codename IRON_WILLOW for AGY vessel. Marker={MARKER}",
    f"OPERATOR_DIRECTIVE_2: Prefer brain UUID exclusive pulse. Marker={MARKER}",
    f"OPERATOR_DIRECTIVE_3: Never claim AGY wiki works without grepping {MARKER}.",
]

def log(m): print(m, flush=True)

def write_agy_transcript(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    step = 0
    def add(typ, content, source=None):
        nonlocal step
        if source is None:
            source = "USER_EXPLICIT" if typ == "USER_INPUT" else "MODEL"
        rows.append({
            "step_index": step,
            "source": source,
            "type": typ,
            "status": "DONE",
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "content": content,
        })
        step += 1
    add("USER_INPUT", "<USER_REQUEST>\nWake up. AGY reincarnation memory test.\n</USER_REQUEST>")
    add("PLANNER_RESPONSE", "Ready for operator directives.")
    for d in DIRECTIVES:
        add("USER_INPUT", f"<USER_REQUEST>\n{d}\n</USER_REQUEST>")
        add("PLANNER_RESPONSE", f"Acknowledged: {d[:100]}")
    add("USER_INPUT", "<USER_REQUEST>\nok, reincarnate so memory-wiki keeps these directives.\n</USER_REQUEST>")
    add("PLANNER_RESPONSE", "Initiating handoff with three directives locked.")
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r)+"\n")

def main():
    sid = "e2eagy01-" + hashlib.sha1(MARKER.encode()).hexdigest()[:8] + "-4e2e-8e2e-" + hashlib.sha1((MARKER+"x").encode()).hexdigest()[:12]
    # valid-looking uuid-ish
    sid = "e2eagy01-op01-4e2e-8e2e-" + hashlib.sha1(MARKER.encode()).hexdigest()[:12]
    tpath = BRAIN / sid / ".system_generated" / "logs" / "transcript.jsonl"
    if tpath.parent.exists():
        shutil.rmtree(tpath.parents[2])
    write_agy_transcript(tpath)
    log(f"=== AGY E2E marker={MARKER} session={sid} ===")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(AIM / ".aim_core") + os.pathsep + env.get("PYTHONPATH","")
    env["AIM_WIKI_SKIP_LANCE"] = "1"
    daemon = WIKI / "daemon.log"
    daemon.parent.mkdir(parents=True, exist_ok=True)
    off = daemon.stat().st_size if daemon.exists() else 0
    cmd = [PY3, str(AIM/".aim_core"/"handoff_pulse_generator.py"), "--session-id", sid]
    p = subprocess.run(cmd, cwd=str(VESSEL), env=env, capture_output=True, text=True, timeout=120)
    log(p.stdout or ""); log(p.stderr or ""); log(f"pulse exit={p.returncode}")
    daemon_new = ""
    deadline = time.time()+45
    while time.time()<deadline:
        if daemon.exists():
            daemon_new = daemon.read_bytes()[off:].decode("utf-8","replace")
            if "[SUCCESS] Deterministic" in daemon_new or "[FATAL] Archive" in daemon_new:
                time.sleep(0.5); break
        time.sleep(0.4)
    log("--- daemon ---\n" + (daemon_new[-2000:] if daemon_new else "(empty)"))
    archives = list((AIM/"archive"/"history").glob(f"*_{sid}.md"))
    arch_ok = any(MARKER in a.read_text(errors="replace") for a in archives)
    pages = []
    for pg in (WIKI/"pages").glob("*.md") if (WIKI/"pages").is_dir() else []:
        if MARKER in pg.read_text(errors="replace"):
            pages.append(str(pg))
    fr = AIM/".aim_core"/"temp"/"LAST_SESSION_FLIGHT_RECORDER.md"
    fr_ok = fr.exists() and MARKER in fr.read_text(errors="replace")
    gates = {
        "pulse_exit_0": p.returncode==0,
        "exclusive_in_stdout": sid in (p.stdout or ""),
        "archive_marker": arch_ok,
        "flight_marker": fr_ok,
        "daemon_success": "[SUCCESS] Deterministic wiki reincarnation sequence complete." in daemon_new,
        "wiki_pages_marker": len(pages)>0,
    }
    hard = all(gates.values())
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        f"# AGY Operator E2E\n\n**VERDICT: {'PASS' if hard else 'FAIL'}**\n\n"
        f"marker={MARKER}\nsession={sid}\n\n"
        + "\n".join(f"- {k}: {v}" for k,v in gates.items())
        + f"\n\npages:\n" + "\n".join(pages) + f"\n\nstdout:\n{(p.stdout or '')[-1500:]}\n",
        encoding="utf-8",
    )
    log(f"=== VERDICT {'PASS' if hard else 'FAIL'} {gates} ===")
    # cleanup fixture brain session
    try:
        shutil.rmtree(BRAIN / sid)
    except Exception:
        pass
    return 0 if hard else 2

if __name__ == "__main__":
    sys.exit(main())
