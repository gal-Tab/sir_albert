#!/usr/bin/env zsh
# cron-retro.sh — daily retro via launchd (com.sir-albert.retro).
# Runs /sir-albert:retro headless, DRAFT-ONLY, appends output to ~/.claude/sir-albert-cron/.
# Invoked by launchd as: /bin/zsh -lc <this script>  (login shell → PATH + auth loaded).
# HARD SAFETY: --disallowedTools "Write" "Edit" blocks the mutation path at the harness
# level (retro only prints recommendations; it never needs to write). guard.sh still active.
# Non-fatal: never blocks; logs everything.
set -u
LOGDIR="$HOME/.claude/sir-albert-cron"; mkdir -p "$LOGDIR" 2>/dev/null || true
LOG="$LOGDIR/retro-$(date +%Y%m%d-%H%M).log"
cd "$HOME/Development/sir_albert" 2>/dev/null || exit 0

PROMPT="Run /sir-albert:retro now. READ + PRINT ONLY. Analyze recent Claude Code session transcripts (~/.claude/projects/*/*.jsonl) and, if duckdb is installed, axcli analytics; PRINT the recommended skill/trigger fixes as recommendation blocks. HARD RULES: do NOT create or modify any file. Do NOT invoke kw-compound or any skill that writes. Do NOT git add/commit/push. Do NOT apply anything. You have no Write/Edit tools — output text only."

{
  echo "=== retro run $(date) ==="
  claude -p "$PROMPT" --permission-mode bypassPermissions --disallowedTools "Write" "Edit"
  echo "=== claude exit $? ==="
} >> "$LOG" 2>&1
exit 0
