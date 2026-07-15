#!/usr/bin/env bash
# Install host-level agy wrapper so EVERY agy launch pre-trusts cwd.
# Safe to re-run.
set -euo pipefail

BIN_DIR="${HOME}/.local/bin"
REAL="${BIN_DIR}/agy.real"
WRAP_SRC="$(cd "$(dirname "$0")" && pwd)/agy_wrapper.sh"
TRUST_SRC="$(cd "$(dirname "$0")" && pwd)/../.aim_core/agy_workspace_trust.py"
SHARE="${HOME}/.local/share/aim-agy"

mkdir -p "${BIN_DIR}" "${SHARE}"

if [[ ! -f "${WRAP_SRC}" ]]; then
  echo "Missing ${WRAP_SRC}" >&2
  exit 1
fi

# If agy is currently the fat ELF binary, move it to agy.real
if [[ -e "${BIN_DIR}/agy" ]]; then
  if file "${BIN_DIR}/agy" | grep -qi 'ELF'; then
    if [[ -e "${REAL}" ]]; then
      # backup existing real then replace
      mv -f "${REAL}" "${REAL}.bak.$(date +%s)" 2>/dev/null || true
    fi
    mv -f "${BIN_DIR}/agy" "${REAL}"
    echo "[install] moved ELF agy → ${REAL}"
  elif [[ -L "${BIN_DIR}/agy" ]] || head -1 "${BIN_DIR}/agy" 2>/dev/null | grep -q bash; then
    echo "[install] ${BIN_DIR}/agy already looks like a wrapper; refreshing it"
  else
    echo "[install] WARN: ${BIN_DIR}/agy is not ELF; leaving as-is, writing agy.real if missing"
  fi
fi

if [[ ! -x "${REAL}" ]]; then
  # try common install locations
  for cand in \
    "${HOME}/.gemini/antigravity-cli/bin/agy" \
    "${HOME}/.local/share/antigravity/bin/agy"
  do
    if [[ -x "$cand" ]] && file "$cand" | grep -qi ELF; then
      cp -a "$cand" "${REAL}"
      echo "[install] copied real binary from $cand"
      break
    fi
  done
fi

if [[ ! -x "${REAL}" ]]; then
  echo "[install] ERROR: could not find real agy binary to place at ${REAL}" >&2
  echo "  Reinstall Antigravity CLI, then re-run this script." >&2
  exit 1
fi

# Copy trust helper for wrapper lookup
if [[ -f "${TRUST_SRC}" ]]; then
  cp -a "${TRUST_SRC}" "${SHARE}/agy_workspace_trust.py"
fi

# Install wrapper
cp -a "${WRAP_SRC}" "${BIN_DIR}/agy"
chmod +x "${BIN_DIR}/agy"
# ensure wrapper finds trust py
if ! grep -q 'AIM_AGY_TRUST_PY' "${BIN_DIR}/agy" 2>/dev/null; then
  :
fi

# Point wrapper default TRUST via env in a small env file optional
echo "export AGY_REAL_BIN=${REAL}" > "${SHARE}/agy_wrapper.env"
echo "export AIM_AGY_TRUST_PY=${SHARE}/agy_workspace_trust.py" >> "${SHARE}/agy_wrapper.env"

# Patch wrapper shebang block to export defaults if env file exists
# (wrapper already has defaults for REAL and TRUST_PY paths)

echo "[SUCCESS] agy trust wrapper installed"
echo "  wrapper: ${BIN_DIR}/agy"
echo "  real:    ${REAL}"
echo "  trust:   ${SHARE}/agy_workspace_trust.py"
echo
echo "Verify:"
echo "  file \$(which agy)   # should say shell script / ASCII"
echo "  which agy.real"
echo "  NEW=/tmp/agy_wrap_\$\$; mkdir -p \$NEW; cd \$NEW; agy --help | head -3"
