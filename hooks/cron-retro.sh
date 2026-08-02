#!/usr/bin/env zsh
# cron-retro.sh — daily retro via launchd (com.sir-albert.retro).
# Runs /sir-albert:retro headless, DRAFT-ONLY, appends output to ~/.claude/sir-albert-cron/.
# Invoked by launchd as: /bin/zsh -lc <this script>  (login shell → PATH + auth loaded).
# Non-fatal: never blocks; logs everything.
set -u
LOGDIR="$HOME/.claude/sir-albert-cron"; mkdir -p "$LOGDIR" 2>/dev/null || true
LOG="$LOGDIR/retro-$(date +%Y%m%d-%H%M).log"
cd "$HOME/Development/sir_albert" 2>/dev/null || exit 0

PROMPT="Run /sir-albert:retro now. DRAFT ONLY: analyze recent sessions (axcli analytics.duckdb + relevant transcripts) and PRINT the recommended skill/trigger fixes as recommendation blocks. Do NOT edit any SKILL.md or settings.json. Do NOT git add/commit/push. Do NOT publish or apply anything. Output the recommendations only."

{
  echo "=== retro run $(date) ==="
  claude -p "$PROMPT" --permission-mode bypassPermissions
  echo "=== claude exit $? ==="
} >> "$LOG" 2>&1
exit 0
