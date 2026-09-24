# 09 — thin ~/.claude/CLAUDE.md (CHECKPOINT)

**Blocked by:** 08
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 5

## Goal

Replace `~/.claude/CLAUDE.md` with a single `@`-import pointing to `CLAUDE.global.md`.

## ⚠ CHECKPOINT — live config change

This edits `~/.claude/CLAUDE.md`, which affects every Claude Code session on this machine. A wrong path in the `@import` silently loads nothing.

**Rollback:** before editing, run:
```bash
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup-w3
```
To restore: `cp ~/.claude/CLAUDE.md.backup-w3 ~/.claude/CLAUDE.md`

## Steps

1. **Back up**: `cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup-w3`
2. Open `~/.claude/CLAUDE.md` and replace entire contents with:
   ```
   @/Users/galta/Development/sir_albert/plugins/sir-albert/os/CLAUDE.global.md
   ```
3. Start a new `claude -p "what are your non-negotiables"` session — confirm it correctly reflects the rules from `CLAUDE.global.md` (plan first, ask before live, skill edits via create-skill).
4. Confirm identity loads: the session should reference USER.md / SOUL.md content.

## Definition of Done

- [ ] Backup at `~/.claude/CLAUDE.md.backup-w3`
- [ ] `~/.claude/CLAUDE.md` is exactly one line (the `@`-import)
- [ ] New session responds to "what are your non-negotiables" with content from CLAUDE.global.md
- [ ] Identity (USER.md, SOUL.md) still loads in session
