# 08 — CLAUDE.global.md (versioned canonical)

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 5

## Goal

Create `plugins/sir-albert/os/CLAUDE.global.md` — the ~20-line canonical text that will replace the content of `~/.claude/CLAUDE.md`. This is the repo-versioned source of truth.

## Steps

1. Read `~/.claude/CLAUDE.md` in full to capture every non-duplicated rule.
2. Identify what can be removed because it's already in `os/rules/` or the router injection:
   - guard.sh full list of blocked commands → keep only a one-liner (the full list is in the script itself)
   - `superpowers:brainstorming` reference → replace with `/sir-albert:brainstorm`
   - Identity `@`-imports → keep
3. Write `plugins/sir-albert/os/CLAUDE.global.md` per the draft in spec §Component 5.
   Confirm it is ≤ 25 lines.
4. Verify the file imports identity correctly: the two `@`-import lines must point to absolute paths that exist on this machine (`ls` both paths).
5. **Do NOT edit `~/.claude/CLAUDE.md` yet** — that is ticket 09 (the CHECKPOINT).

## Definition of Done

- [ ] `plugins/sir-albert/os/CLAUDE.global.md` exists
- [ ] ≤ 25 lines
- [ ] Contains `@`-imports for USER.md and SOUL.md
- [ ] References `/sir-albert:brainstorm` (not superpowers)
- [ ] References `os/RESOLVER.md`
- [ ] References guard.sh with one-liner only
- [ ] `wc -l plugins/sir-albert/os/CLAUDE.global.md` ≤ 25
