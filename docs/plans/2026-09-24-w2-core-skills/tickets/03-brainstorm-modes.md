# 03 — brainstorm SKILL.md

**Blocked by:** 02, 08 (create-skill must be independent before use)
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §brainstorm

## Goal

Write `core/brainstorm/SKILL.md` via `/sir-albert:create-skill`, covering all 7 modes with phrase→mode routing and explicit arg syntax.

## Steps

1. Run `/sir-albert:create-skill` to scaffold `core/brainstorm/SKILL.md`.
   - Type: technique/discipline hybrid (T1 smoke tier)
   - Trigger phrases: full phrase→mode table from spec §brainstorm mode table
   - Name: `brainstorm`
2. SKILL.md content requirements:
   - Frontmatter: `name: brainstorm`, description leading with all 7 mode trigger phrases.
   - Boot from `os/PREAMBLE.md` + load `os/rules/docs-layout.md` (for `design` mode).
   - Mode-selection section: the phrase→mode routing table (verbatim from spec).
   - Per-mode execution section: each mode's runner type and behavior (≤5 bullets each).
   - `design` mode section: classify Spike/Bounded/Architectural out loud; hard gate block; run `kb:learn-research` first; write spec to `docs/specs/`; hand off to `plan`.
   - `grill` mode: one question at a time; can run against provided docs.
   - Explicit arg syntax block (4 examples from spec).
3. Validate: `python3 scripts/validate-skill.py` passes with no 🔴.
4. T1 smoke: invoke brainstorm with one prompt per mode, confirm correct mode fires.
5. Commit: `feat(core): add brainstorm skill (7 modes, replaces discover + 6 biz/dev skills)`.

## Definition of Done

- [ ] `core/brainstorm/SKILL.md` exists, validates cleanly
- [ ] All 7 modes documented with trigger phrases
- [ ] `design` mode has hard gate and `kb:learn-research` first-step
- [ ] Smoke: `/sir-albert:brainstorm grill me about X` fires grill mode (1 question)
- [ ] `/sir-albert:brainstorm attack <idea>` fires attack mode with subagents

## CHECKPOINT

Before running smoke tests that dispatch subagents: confirm with Gal that spawning parallel subagents is acceptable in current context (cost/token consideration).

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
