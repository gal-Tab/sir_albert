#!/usr/bin/env zsh
# cron-wiki.sh — weekly knowledge consolidation via launchd (com.sir-albert.wiki).
# v1 = SAFE report: runs /sir-albert:learnings canonicalization and prints the plan +
# promotion candidates + a stale_after sweep. Does NOT write wiki pages, does NOT touch git.
# HARD SAFETY: --disallowedTools "Write" "Edit" blocks the mutation path (report only).
# Invoked by launchd as: /bin/zsh -lc <this script>. Non-fatal; logs everything.
# (v2 upgrade: real wiki-compile in an isolated git worktree.)
set -u
LOGDIR="$HOME/.claude/sir-albert-cron"; mkdir -p "$LOGDIR" 2>/dev/null || true
LOG="$LOGDIR/wiki-$(date +%Y%m%d-%H%M).log"
cd "$HOME/Development/sir_albert" 2>/dev/null || exit 0

PROMPT="Run /sir-albert:learnings now (weekly consolidation). Canonicalize the .compound drafts: dedup near-duplicate slugs, apply the page-creation threshold. PRINT a REPORT of (a) what would be merged, (b) which entries are ready to promote via /wiki-compile, (c) a stale_after sweep of os/rules + os/knowledge (flag anything past its date). READ + PRINT ONLY. HARD RULES: do NOT create or modify any file, do NOT run wiki-compile writes, do NOT invoke kw-compound, do NOT git add/commit/push. You have no Write/Edit tools — output text only."

{
  echo "=== wiki/dream run $(date) ==="
  claude -p "$PROMPT" --permission-mode bypassPermissions --disallowedTools "Write" "Edit"
  echo "=== claude exit $? ==="
} >> "$LOG" 2>&1
exit 0
