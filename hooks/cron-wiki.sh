#!/usr/bin/env zsh
# cron-wiki.sh — weekly knowledge consolidation via launchd (com.sir-albert.wiki).
# v1 = SAFE report: runs /sir-albert:learnings canonicalization and prints the plan +
# promotion candidates. Does NOT write wiki pages, does NOT run wiki-compile writes, does
# NOT touch git on the live working tree. (v2 upgrade: real compile in an isolated worktree.)
# Invoked by launchd as: /bin/zsh -lc <this script>. Non-fatal; logs everything.
set -u
LOGDIR="$HOME/.claude/sir-albert-cron"; mkdir -p "$LOGDIR" 2>/dev/null || true
LOG="$LOGDIR/wiki-$(date +%Y%m%d-%H%M).log"
cd "$HOME/Development/sir_albert" 2>/dev/null || exit 0

PROMPT="Run /sir-albert:learnings now (weekly consolidation). Canonicalize the .compound drafts: dedup near-duplicate slugs and apply the page-creation threshold. Produce a REPORT of (a) what would be merged, (b) which entries are ready to promote via /wiki-compile, and a stale_after sweep of os/rules + os/knowledge (flag anything past its date). DRAFT / REPORT ONLY: do NOT write wiki pages, do NOT run wiki-compile's writes, do NOT git add/commit/push. Print the canonicalization plan + promotion candidates + stale flags for review."

{
  echo "=== wiki/dream run $(date) ==="
  claude -p "$PROMPT" --permission-mode bypassPermissions
  echo "=== claude exit $? ==="
} >> "$LOG" 2>&1
exit 0
