#!/bin/bash
# A.I.M. Sovereign Co-Agent Installer
# curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim-agy/main/aim-agy_os/install-agent.sh | bash -s python-developer

set -e
echo "--- A.I.M. SOVEREIGN CO-AGENT INSTALLER ---"

PERSONA="${1:-generic-node}"
echo "[*] Target Persona Blueprint: $PERSONA"

CURRENT_DIR=$(pwd)
CLI_NAME=$(basename "$CURRENT_DIR")

echo "[*] Step 1: Provisioning Local Operating System..."

# Clone the engine directly into a temporary hidden folder to avoid empty directory conflicts
git clone --depth 1 https://github.com/BrianV1981/aim-agy.git .aim_temp_clone
cd .aim_temp_clone

echo "    [*] Building Engine Virtual Environment..."
./aim-agy_os/setup.sh

# Move everything out of the temp folder into the current directory
echo "[*] Step 2: Scaffolding Sovereign Environment..."
shopt -s dotglob
mv * ../
cd ..
rm -rf .aim_temp_clone
shopt -u dotglob

# Clean Sweep (Severing identity and cleaning out developer artifacts)
rm -rf .git/
rm -rf aim-agy_os/tests/
rm -rf aim-agy_os/benchmarks/
rm -rf aim-agy_os/docs/
rm -rf aim-agy_os/scripts/
rm -rf aim-agy_os/skills/
git init

# Base OS Provisioning (Moving the pre-baked DB to the active layer)
mkdir -p aim-agy_os/memory_lance
cp -r aim-agy_os/assets/default_lance/* aim-agy_os/memory_lance/

echo "    [*] Initializing Headless OS..."
./aim-agy_os/venv/bin/python3 ./aim-agy_os/.aim_core/aim_cli.py init --headless --persona "$PERSONA"

echo ""
echo "--- CO-AGENT DEPLOYMENT COMPLETE ---"
echo "Your Sovereign Node ($PERSONA) is installed."
