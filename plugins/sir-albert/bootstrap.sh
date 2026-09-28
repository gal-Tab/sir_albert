#!/usr/bin/env bash
# bootstrap.sh — machine-level setup for sir_albert. Run once per machine.
# Each step is idempotent. See spec: docs/specs/2026-09-24-w3-router-design.md §Component 0
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")" && pwd)"
PLUGINS_DIR="$(dirname "$PLUGIN_ROOT")"

echo "[bootstrap] sir_albert machine setup"
echo "[bootstrap] PLUGIN_ROOT = $PLUGIN_ROOT"
echo "[bootstrap] PLUGINS_DIR = $PLUGINS_DIR"
echo ""

# ── CHECKPOINT 1: alias in ~/.zshrc ──────────────────────────────────────────
ALIAS_LINE="alias claude='claude --plugin-dir ${PLUGINS_DIR}'"
if grep -qF "sir_albert/plugins" ~/.zshrc 2>/dev/null; then
  echo "[bootstrap] CHECKPOINT 1: alias already present in ~/.zshrc — skipping"
else
  [ -f ~/.zshrc ] && cp ~/.zshrc ~/.zshrc.backup-w3
  printf '\n# sir_albert — added by bootstrap.sh\n%s\n' "$ALIAS_LINE" >> ~/.zshrc
  echo "[bootstrap] CHECKPOINT 1: added alias to ~/.zshrc (backup: ~/.zshrc.backup-w3)"
fi

# ── CHECKPOINT 2: ~/.claude/CLAUDE.md → one-line @import ────────────────────
GLOBAL_MD="${PLUGIN_ROOT}/os/CLAUDE.global.md"
IMPORT_LINE="@${GLOBAL_MD}"
CLAUDE_MD=~/.claude/CLAUDE.md

if [ -f "$CLAUDE_MD" ] && grep -qF "$IMPORT_LINE" "$CLAUDE_MD"; then
  echo "[bootstrap] CHECKPOINT 2: CLAUDE.md already contains the @import — skipping"
else
  # Ask first: this replaces ~/.claude/CLAUDE.md. SIR_ALBERT_CLAUDE_MD=yes|no answers non-interactively.
  ANSWER="${SIR_ALBERT_CLAUDE_MD:-}"
  if [ -z "$ANSWER" ] && [ -t 0 ]; then
    [ -f "$CLAUDE_MD" ] && echo "[bootstrap] ~/.claude/CLAUDE.md exists; it will be backed up and replaced."
    read -r -p "[bootstrap] Use Sir Albert's CLAUDE.md (one-line @import of os/CLAUDE.global.md)? [y/N] " ANSWER
  fi
  case "$ANSWER" in
    y|Y|yes|YES)
      mkdir -p ~/.claude
      [ -f "$CLAUDE_MD" ] && cp "$CLAUDE_MD" ~/.claude/CLAUDE.md.backup-w3 && echo "[bootstrap] backed up existing CLAUDE.md → ~/.claude/CLAUDE.md.backup-w3"
      printf '%s\n' "$IMPORT_LINE" > "$CLAUDE_MD"
      echo "[bootstrap] CHECKPOINT 2: wrote ~/.claude/CLAUDE.md with @import"
      ;;
    *)
      echo "[bootstrap] CHECKPOINT 2: skipped — CLAUDE.md left unchanged (to use it later, add this line: $IMPORT_LINE)"
      ;;
  esac
fi

# ── CHECKPOINT 3: guard.sh symlink ──────────────────────────────────────────
GUARD_SRC="${PLUGIN_ROOT}/hooks/guard.sh"
GUARD_DST=~/.claude/hooks/guard.sh

if [ -L "$GUARD_DST" ] && [ "$(readlink "$GUARD_DST")" = "$GUARD_SRC" ]; then
  echo "[bootstrap] CHECKPOINT 3: guard.sh symlink already correct — skipping"
else
  mkdir -p ~/.claude/hooks
  if [ -e "$GUARD_DST" ]; then
    mv "$GUARD_DST" "${GUARD_DST}.backup-w3"
    echo "[bootstrap] backed up existing guard.sh → ${GUARD_DST}.backup-w3"
  fi
  ln -s "$GUARD_SRC" "$GUARD_DST"
  echo "[bootstrap] CHECKPOINT 3: symlinked guard.sh"
fi

# ── CHECKPOINT 4: register guard.sh as a PreToolUse hook ────────────────────
# The symlink alone does nothing; Claude Code only runs hooks listed in settings.json.
SETTINGS=~/.claude/settings.json
GUARD_CMD="bash ${GUARD_DST}"

if [ -f "$SETTINGS" ] && grep -qF "hooks/guard.sh" "$SETTINGS"; then
  echo "[bootstrap] CHECKPOINT 4: guard.sh hook already registered — skipping"
else
  [ -f "$SETTINGS" ] && cp "$SETTINGS" "${SETTINGS}.backup-w3" && echo "[bootstrap] backed up settings.json → ${SETTINGS}.backup-w3"
  python3 - "$SETTINGS" "$GUARD_CMD" <<'PY'
import json, os, sys
path, cmd = sys.argv[1], sys.argv[2]
s = json.load(open(path)) if os.path.exists(path) else {}
s.setdefault("hooks", {}).setdefault("PreToolUse", []).append(
    {"matcher": "Bash", "hooks": [{"type": "command", "command": cmd}]})
json.dump(s, open(path, "w"), indent=2)
PY
  echo "[bootstrap] CHECKPOINT 4: registered guard.sh PreToolUse hook in settings.json"
fi

echo ""
echo "[bootstrap] Done."
echo ""
echo "Verify:"
echo "  grep 'sir_albert' ~/.zshrc"
echo "  cat ~/.claude/CLAUDE.md"
echo "  ls -la ~/.claude/hooks/guard.sh"
echo "  grep guard.sh ~/.claude/settings.json"
