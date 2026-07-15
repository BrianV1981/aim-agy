# AGY workspace trust (folder permission gate)

## The bug (why “fixed” kept failing)

When Antigravity CLI starts in a **new directory**, it shows:

```text
Do you trust the contents of this project
> Yes, I trust this folder
  No, exit
```

Agents repeatedly claimed this was fixed. It was not. Root causes:

1. **`agy --dangerously-skip-permissions` only auto-approves tool permission requests.** It does **not** skip the folder trust gate.
2. Trust is stored as an **exact path list** in  
   `~/.gemini/antigravity-cli/settings.json` → `trustedWorkspaces[]`.  
   Trusting `/home/kingb/aim-agy` does **not** trust  
   `/home/kingb/aim-agy/workspace/issue-10/ai`.
3. Keystroke bypass often sent **`y` then Enter**. The UI is a **list** with `>` on Yes — only **Enter** is correct. Sending `y` can leave the agent stuck.

## The fix (aim-agy)

Module: `aim-agy_os/.aim_core/agy_workspace_trust.py`

- `ensure_workspace_trusted(cwd)` — register **exact** absolute path before spawn  
- `prepare_agy_spawn(cwd)` — call from every spawn site  
- `dismiss_trust_prompt_tmux(session)` — Enter-only fallback if UI still appears  

Wired into:

- `reincarnation/teleport_engine.py` (reincarnate vessels)  
- `wiki_tools.py` (wiki agent mode)  
- `aim_init.py` (onboarding spawn)  

## Operator / agent rule

**Before every `tmux … agy` with a new `-c` directory:**

```python
from agy_workspace_trust import prepare_agy_spawn
cwd = prepare_agy_spawn(workspace_path)
# then tmux new-session -c cwd agy --dangerously-skip-permissions ...
```

Or CLI:

```bash
PYTHONPATH=aim-agy_os/.aim_core python3 -m agy_workspace_trust /path/to/cwd
```

## Verify

```bash
# Should print NOT trusted for a fresh path, then trusted after ensure
NEW=/tmp/agy_trust_demo_$$
mkdir -p "$NEW"
PYTHONPATH=aim-agy_os/.aim_core python3 aim-agy_os/.aim_core/agy_workspace_trust.py --check "$NEW" || true
PYTHONPATH=aim-agy_os/.aim_core python3 aim-agy_os/.aim_core/agy_workspace_trust.py "$NEW"
# Spawn should reach ready prompt without hanging on Yes/No
tmux new-session -d -s agy_trust_demo -c "$NEW" "agy --dangerously-skip-permissions"
sleep 4
tmux capture-pane -t agy_trust_demo -p | tail -20
# expect Antigravity CLI ready, NOT "Do you trust"
tmux kill-session -t agy_trust_demo
```

## Related false fix history

- #58 / #65: keystroke bypass only — brittle  
- #3: `--yolo` → `--dangerously-skip-permissions` — different problem  

This document is the non-negotiable contract until Google ships parent-folder trust or a real noninteractive flag for folder trust.
