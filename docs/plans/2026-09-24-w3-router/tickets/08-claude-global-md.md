# 08 — CLAUDE.global.md (versioned canonical)

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 5

## Goal

Create `plugins/sir-albert/os/CLAUDE.global.md` — the ~20-line canonical text. Uses **relative** `@identity/USER.md` / `@identity/SOUL.md` imports (relative to the file at `os/`). The absolute path to this file is only written by `bootstrap.sh` into `~/.claude/CLAUDE.md`.

## Steps

1. Read `~/.claude/CLAUDE.md` in full to confirm what the current text contains (do not copy verbatim — extract only the non-duplicated rules).
2. Identify what to drop: the full guard.sh blocked-commands list (lives in the script); `superpowers:brainstorming` ref; verbose operating contract (covered by `os/rules/`).
3. Write `plugins/sir-albert/os/CLAUDE.global.md` per the draft in spec §Component 5:
   - Use `@identity/USER.md` and `@identity/SOUL.md` (relative paths — no absolute paths in this file)
   - 8 non-negotiable bullets including the restored "Use the skill" rule and separate "Evidence before done" bullet
   - One-liner on guard.sh (no full list)
   - Pointer to RESOLVER.md
4. Verify relative imports exist: `ls plugins/sir-albert/os/identity/USER.md plugins/sir-albert/os/identity/SOUL.md`
5. Count lines: `wc -l plugins/sir-albert/os/CLAUDE.global.md` — must be ≤ 25.
6. **Do NOT edit `~/.claude/CLAUDE.md` yet** — that is ticket 09 (via bootstrap.sh).

## Definition of Done

- [ ] `plugins/sir-albert/os/CLAUDE.global.md` exists, ≤25 lines
- [ ] Uses relative `@identity/` imports (not absolute paths)
- [ ] Contains "Use the skill" bullet
- [ ] Contains separate "Evidence before done" bullet
- [ ] References `/sir-albert:brainstorm` (not superpowers)
- [ ] References `os/RESOLVER.md`
- [ ] No absolute paths inside this file
