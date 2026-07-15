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

## The fix (aim-agy) — systemic, not one code path

### Layer A — Host wrapper (covers *all* launches)

```bash
bash aim-agy_os/scripts/install_agy_trust_wrapper.sh
```

- Moves real ELF to `~/.local/bin/agy.real`
- Installs `~/.local/bin/agy` shell wrapper that **pre-trusts `pwd` (+ `--add-dir`)** before `exec` real binary  
- Covers: manual `cd newdir && agy`, tmux scribes, swarm, reincarnate, install-agent scaffolds, Claude/opus panes — **anything that calls `agy` from PATH**

Re-run after `agy update` if the update overwrites the wrapper (reinstall script is idempotent).

### Layer B — Library (Python spawn sites)

Module: `aim-agy_os/.aim_core/agy_workspace_trust.py`

- `ensure_workspace_trusted(cwd)` — register **exact** absolute path  
- `prepare_agy_spawn(cwd)` — call before every programmatic spawn  
- `dismiss_trust_prompt_tmux(session)` — Enter-only fallback (not `y`)  

Wired into:

- `reincarnation/teleport_engine.py` (reincarnate)  
- `wiki_tools.py` (wiki agent)  
- `aim_init.py` (onboarding)  
- `aim_swarm.py` (`./aim swarm spawn`)  
- `link_cli_alias.sh` / `install-agent.sh` (register project root + install wrapper)  

### Scenarios that used to break (all of these)

| Scenario | Why it broke | Mitigation |
|----------|--------------|------------|
| `./aim fix` worktree / new folder | New exact path | Wrapper trusts pwd; spawn sites call prepare |
| Wiki / scribe agent | cwd = memory-wiki or worktree leaf | Same |
| Reincarnate vessel | New session cwd | teleport_engine + wrapper |
| `aim swarm spawn` | project_dir may be new | aim_swarm + wrapper |
| Manual `cd … && agy` | Human path | **Wrapper only** |
| install-agent persona node | Fresh project root | link_cli_alias + install-agent |

## Operator / agent rule

1. **Install the host wrapper once per machine** (and after agy upgrades).  
2. Any Python that spawns tmux+agy must still call `prepare_agy_spawn(cwd)` (belt + suspenders).  

```python
from agy_workspace_trust import prepare_agy_spawn
cwd = prepare_agy_spawn(workspace_path)
```

```bash
PYTHONPATH=aim-agy_os/.aim_core python3 aim-agy_os/.aim_core/agy_workspace_trust.py /path/to/cwd
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
