#!/usr/bin/env bash
# agy_wrapper.sh — systemic fix for Antigravity "Do you trust this folder?"
#
# Install as ~/.local/bin/agy with the real binary at ~/.local/bin/agy.real
# (see install_agy_trust_wrapper.sh).
#
# Why: --dangerously-skip-permissions does NOT skip folder trust.
# trustedWorkspaces is exact-path only; every new cwd must be registered
# before the binary starts or pipelines hang forever on Yes/No.
set -euo pipefail

REAL_AGY="${AGY_REAL_BIN:-${HOME}/.local/bin/agy.real}"
TRUST_PY="${AIM_AGY_TRUST_PY:-}"

# Locate trust helper (prefer repo checkout, then next to wrapper)
if [[ -z "${TRUST_PY}" ]]; then
  for cand in \
    "${HOME}/aim-agy/aim-agy_os/.aim_core/agy_workspace_trust.py" \
    "${HOME}/.local/share/aim-agy/agy_workspace_trust.py" \
    "$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")/../.aim_core/agy_workspace_trust.py"
  do
    if [[ -f "$cand" ]]; then
      TRUST_PY="$cand"
      break
    fi
  done
fi

# Collect dirs to trust: cwd + any --add-dir values
dirs_to_trust=("$(pwd -P 2>/dev/null || pwd)")
args=("$@")
i=0
while [[ $i -lt ${#args[@]} ]]; do
  a="${args[$i]}"
  if [[ "$a" == "--add-dir" && $((i+1)) -lt ${#args[@]} ]]; then
    dirs_to_trust+=("${args[$((i+1))]}")
    i=$((i+2))
    continue
  fi
  # --add-dir=/path form
  if [[ "$a" == --add-dir=* ]]; then
    dirs_to_trust+=("${a#--add-dir=}")
  fi
  i=$((i+1))
done

if [[ -n "${TRUST_PY}" && -f "${TRUST_PY}" ]]; then
  # Quiet pre-trust; never block launch if trust helper fails
  python3 "${TRUST_PY}" "${dirs_to_trust[@]}" >/dev/null 2>&1 || true
else
  # Minimal fallback: patch settings.json without full helper
  python3 - "${dirs_to_trust[@]}" <<'PY' >/dev/null 2>&1 || true
import json, os, sys
from pathlib import Path
settings = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
settings.parent.mkdir(parents=True, exist_ok=True)
data = {}
if settings.is_file():
    try:
        data = json.loads(settings.read_text() or "{}")
    except Exception:
        data = {}
tw = list(data.get("trustedWorkspaces") or [])
s = set(str(x) for x in tw)
changed = False
for raw in sys.argv[1:]:
    try:
        p = str(Path(raw).expanduser().resolve())
    except Exception:
        continue
    if p not in s:
        tw.append(p)
        s.add(p)
        changed = True
if changed:
    data["trustedWorkspaces"] = tw
    tmp = settings.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, settings)
PY
fi

if [[ ! -x "${REAL_AGY}" ]]; then
  echo "[agy-wrapper] ERROR: real binary not found at ${REAL_AGY}" >&2
  echo "  Set AGY_REAL_BIN or run: bash aim-agy_os/scripts/install_agy_trust_wrapper.sh" >&2
  exit 127
fi

exec "${REAL_AGY}" "$@"
