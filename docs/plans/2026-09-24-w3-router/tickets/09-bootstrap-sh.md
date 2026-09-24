# 09 — bootstrap.sh (machine setup, CHECKPOINTs)

**Blocked by:** 08
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 0

## Goal

Write `plugins/sir-albert/bootstrap.sh` — idempotent machine setup. Covers the three live-config writes that `/sir-albert:init` must NOT do. Each write is a guarded CHECKPOINT step.

## ⚠ Three CHECKPOINTs — all are live machine config

Run each step separately. Review what will be written before confirming.

**Rollbacks:**
- `.zshrc`: restore from `~/.zshrc.backup-w3`
- `CLAUDE.md`: restore from `~/.claude/CLAUDE.md.backup-w3`
- guard.sh symlink: `rm ~/.claude/hooks/guard.sh && mv ~/.claude/hooks/guard.sh.backup-w3 ~/.claude/hooks/guard.sh` (if original existed)

## Steps

1. Write `plugins/sir-albert/bootstrap.sh`:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   PLUGIN_ROOT="$(cd "$(dirname "$0")" && pwd)"

   # CHECKPOINT 1: alias in ~/.zshrc
   if ! grep -q "sir_albert/plugins" ~/.zshrc; then
     cp ~/.zshrc ~/.zshrc.backup-w3
     echo "\nalias claude='claude --plugin-dir ${PLUGIN_ROOT}/..'" >> ~/.zshrc
     echo "[bootstrap] Added --plugin-dir alias to ~/.zshrc"
   else
     echo "[bootstrap] alias already present, skipping"
   fi

   # CHECKPOINT 2: ~/.claude/CLAUDE.md one-line @import
   GLOBAL_MD="${PLUGIN_ROOT}/os/CLAUDE.global.md"
   IMPORT_LINE="@${GLOBAL_MD}"
   if [ ! -f ~/.claude/CLAUDE.md ] || ! grep -qF "$IMPORT_LINE" ~/.claude/CLAUDE.md; then
     [ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup-w3
     echo "$IMPORT_LINE" > ~/.claude/CLAUDE.md
     echo "[bootstrap] Wrote ~/.claude/CLAUDE.md"
   else
     echo "[bootstrap] CLAUDE.md already correct, skipping"
   fi

   # CHECKPOINT 3: guard.sh symlink
   GUARD_SRC="${PLUGIN_ROOT}/hooks/guard.sh"
   GUARD_DST=~/.claude/hooks/guard.sh
   if [ -L "$GUARD_DST" ] && [ "$(readlink "$GUARD_DST")" = "$GUARD_SRC" ]; then
     echo "[bootstrap] guard.sh symlink already correct, skipping"
   else
     mkdir -p ~/.claude/hooks
     [ -e "$GUARD_DST" ] && mv "$GUARD_DST" "${GUARD_DST}.backup-w3"
     ln -s "$GUARD_SRC" "$GUARD_DST"
     echo "[bootstrap] Symlinked guard.sh"
   fi

   echo "[bootstrap] Done."
   ```
2. `chmod +x plugins/sir-albert/bootstrap.sh`
3. Run in dry-run mode first (review output without `-e` trap): `bash -n plugins/sir-albert/bootstrap.sh`
4. **Execute — run bootstrap.sh**. Review each "[bootstrap]" line. Confirm all 3 CHECKPOINTs applied or skipped correctly.
5. Verify:
   - `grep "sir_albert/plugins" ~/.zshrc` — alias present
   - `cat ~/.claude/CLAUDE.md` — exactly one line (the @import)
   - `ls -la ~/.claude/hooks/guard.sh` — symlink pointing to plugin
   - Start a new shell and run `which claude` or `alias claude` — confirms alias active after `source ~/.zshrc`

## Definition of Done

- [ ] `bootstrap.sh` exists, executable
- [ ] Idempotent: second run prints "skipping" for all three steps
- [ ] `~/.zshrc` has the alias (backed up if modified)
- [ ] `~/.claude/CLAUDE.md` is one line: the @import (backed up if modified)
- [ ] `~/.claude/hooks/guard.sh` is a symlink to `plugins/sir-albert/hooks/guard.sh`
- [ ] Backups created for any file that was modified
