#!/bin/bash
# Install staggered crons for aim-agy handoff vNext

VESSEL_ROOT="/home/kingb/aim-agy"
LOG_DIR="$HOME/.aim/cron/logs/aim-agy"

mkdir -p "$LOG_DIR"

CRON_JOB_1="5 2 * * * cd $VESSEL_ROOT && python3 aim-agy_os/.aim_core/aim_cli.py handoff-vnext blackbox-cron --vessel-root $VESSEL_ROOT >> $LOG_DIR/blackbox.log 2>&1"

(crontab -l 2>/dev/null | grep -v "aim_cli.py handoff-vnext" ; echo "$CRON_JOB_1") | crontab -

echo "aim-agy staggered crons installed."
crontab -l | grep "aim-agy"
