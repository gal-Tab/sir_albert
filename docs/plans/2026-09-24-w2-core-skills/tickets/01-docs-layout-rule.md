# 01 — docs-layout rule

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §docs-layout rule

## Goal

Create `plugins/sir-albert/os/rules/docs-layout.md` so all skills and the router know where output artifacts land.

## Steps

1. Read existing `os/rules/` files to match the OKF style (status, date, stale_after, content).
2. Write `plugins/sir-albert/os/rules/docs-layout.md` directly (this is an os/rule, not a skill — not routed through create-skill).
   Content: `docs/specs/` naming, `docs/plans/` HTML + tickets/, `.memory-bank/HANDOFF-` pattern, naming conventions (lowercase-hyphenated slugs, YYYY-MM-DD prefix).
3. Add a `@`-import reference to the new rule in `os/PREAMBLE.md` so it boots with every skill.
4. Verify: `grep -n "docs-layout" plugins/sir-albert/os/PREAMBLE.md` returns a hit.
5. Commit: `chore: add docs-layout rule to os/rules/`.

## Definition of Done

- [ ] `os/rules/docs-layout.md` exists with OKF frontmatter (status/date/stale_after)
- [ ] PREAMBLE.md `@`-imports it
- [ ] No other rules file defines conflicting paths
