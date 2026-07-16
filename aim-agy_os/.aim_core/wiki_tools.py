import os
import glob
import sqlite3
import requests
import time
try:
    from .aim_core.reasoning_utils import generate_reasoning
except ImportError:
    from reasoning_utils import generate_reasoning

def get_base_dir():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "aim-agy_os", "setup.sh")): return os.path.join(current, "aim-agy_os")
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def search_wiki(query):
    """
    Performs a lightning-fast local search over the memory-wiki/ directory
    using an in-memory SQLite FTS5 database.
    """
    base_dir = get_base_dir()
    wiki_dir = os.path.join(base_dir, "memory-wiki")
    
    if not os.path.exists(wiki_dir):
        print("Error: memory-wiki/ directory not found. Please initialize the wiki first.")
        return

    # In-memory FTS5 search
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute('''CREATE VIRTUAL TABLE wiki_fts USING fts5(filepath, content)''')

    # Load markdown files
    md_files = glob.glob(os.path.join(wiki_dir, "**", "*.md"), recursive=True)
    for file_path in md_files:
        if os.path.basename(file_path) == "GEMINI.md": continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                c.execute("INSERT INTO wiki_fts (filepath, content) VALUES (?, ?)", (os.path.basename(file_path), content))
        except Exception as e:
            import sys; print(f"[WARN] Failed to read {file_path}: {e}", file=sys.stderr)
    
    # Query
    try:
        c.execute("SELECT filepath, snippet(wiki_fts, 1, '>>', '<<', '...', 64) FROM wiki_fts WHERE wiki_fts MATCH ? ORDER BY rank LIMIT 5", (query,))
        results = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback to basic LIKE if query is invalid FTS syntax
        c.execute("SELECT filepath, substr(content, 1, 200) FROM wiki_fts WHERE content LIKE ? LIMIT 5", (f"%{query}%",))
        results = c.fetchall()
        
    conn.close()

    if not results:
        print(f"No results found in Wiki for '{query}'.")
        return

    print(f"\\n--- 🔍 WIKI SEARCH RESULTS: '{query}' ---")
    for filepath, snippet in results:
        print(f"\\n📄 {filepath}:\\n{snippet}\\n")
    print("-----------------------------------")



def process_wiki_agent():
    """Legacy: hand off ingest to a tmux wiki agent (agy). Prefer deterministic."""
    import subprocess
    base_dir = get_base_dir()
    ingest_dir = os.path.join(base_dir, "memory-wiki/_ingest")
    if not os.path.exists(ingest_dir):
        print("Error: memory-wiki/_ingest/ directory not found.")
        return
    files = [
        f for f in glob.glob(os.path.join(ingest_dir, "*.*"))
        if os.path.basename(f) not in (".gitkeep", ".keep")
    ]
    if not files:
        print("No files found in memory-wiki/_ingest/ to process.")
        return
    from session_naming import build_agent_session_name
    session_name = build_agent_session_name("wiki", base_dir)
    wiki_dir = os.path.join(base_dir, "memory-wiki")
    check_cmd = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    if check_cmd.returncode == 0:
        print(f"[{session_name}] is already active and processing the queue. Skipping new spawn.")
        return
    print(f"Starting fresh '{session_name}' tmux session (agy)...")
    try:
        from agy_workspace_trust import prepare_agy_spawn, dismiss_trust_prompt_tmux

        wiki_dir = prepare_agy_spawn(wiki_dir)
    except Exception as te:
        print(f"[TRUST] WARN: {te}")
        dismiss_trust_prompt_tmux = None  # type: ignore

    subprocess.run([
        "tmux", "new-session", "-d", "-s", session_name, "-c", wiki_dir,
        "bash", "-c", f"cd {wiki_dir} && source ~/.bashrc 2>/dev/null; agy --dangerously-skip-permissions",
    ])
    print(f"Handing off {len(files)} file(s) to {session_name} for processing...")
    # Thin pointer — full rules live in memory-wiki/AGENTS.md (schema)
    prompt = (
        "Read AGENTS.md (schema) and index.md first. "
        "Process exactly ONE file in `_ingest/` per the schema: integrate into "
        "index.md, log.md, and pages/; delete that file; stop. "
        f"When `_ingest/` is empty: `tmux kill-session -t {session_name}`."
    )
    try:
        if dismiss_trust_prompt_tmux:
            dismiss_trust_prompt_tmux(session_name)
        injected = False
        for _ in range(30):
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", session_name],
                capture_output=True, text=True,
            )
            out = result.stdout or ""
            if "trust" in out.lower():
                # List UI: Enter on pre-selected Yes — never send "y"
                subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
                time.sleep(0.5)
                continue
            if "Antigravity" in out or "Enter your" in out or "❯" in out:
                subprocess.run(["tmux", "set-buffer", prompt], check=True)
                subprocess.run(["tmux", "paste-buffer", "-p", "-t", session_name], check=True)
                time.sleep(1)
                subprocess.run(["tmux", "send-keys", "-t", session_name, "Escape"], check=True)
                time.sleep(0.3)
                subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
                injected = True
                break
            time.sleep(0.5)
        if not injected:
            print("[WARNING] Wiki agent readiness unclear; injecting blindly.")
            subprocess.run(["tmux", "set-buffer", prompt], check=True)
            subprocess.run(["tmux", "paste-buffer", "-p", "-t", session_name], check=True)
            time.sleep(1)
            subprocess.run(["tmux", "send-keys", "-t", session_name, "Escape"], check=True)
            time.sleep(0.3)
            subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
        print(f"[SUCCESS] Directives dispatched to {session_name}.")
    except Exception as e:
        print(f"[ERROR] Failed to hand off to {session_name}: {e}")


def process_wiki_deterministic():
    """Compile _ingest/ (and optional raw logs) without a second agent."""
    print("--- WIKI PROCESS (deterministic) ---")
    try:
        from wiki_compiler import (
            process_raw_logs_to_ingest,
            process_ingest,
            ensure_wiki_scaffold,
            wiki_paths,
        )
    except ImportError:
        print("[ERROR] wiki_compiler.py missing — cannot run deterministic wiki.")
        return []
    ensure_wiki_scaffold(wiki_paths())
    for line in process_raw_logs_to_ingest():
        print(" ", line)
    results = process_ingest()
    for line in results:
        print(" ", line)
    return results


def process_wiki():
    """
    Default: deterministic compiler (fleet-safe, no second agent).
    Set AIM_WIKI_MODE=agent for tmux + agy maintainer.
    """
    mode = os.environ.get("AIM_WIKI_MODE", "deterministic").lower()
    if mode in ("agent", "agy", "llm"):
        return process_wiki_agent()
    return process_wiki_deterministic()
