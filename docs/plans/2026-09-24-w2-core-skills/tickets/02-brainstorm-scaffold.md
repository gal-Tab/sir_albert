# 02 — brainstorm scaffold

**Blocked by:** 01
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §brainstorm

## Goal

Create `plugins/sir-albert/skills/core/brainstorm/` directory structure with `agents/` files moved from `biz/discovery-lens/agents/` and new persona files for `panel` mode.

## Steps

1. `git mv plugins/sir-albert/skills/biz/discovery-lens/agents/ plugins/sir-albert/skills/core/brainstorm/agents/` — moves the 8 existing voice files (boris.md, collison.md, karpathy.md, kohavi.md, seibel.md, shreyas.md, verna.md, yc.md).
2. Copy `biz/discovery-lens/references/voices.md` to `core/brainstorm/references/voices.md`.
3. Create `core/brainstorm/references/modes.md` describing the 7 modes, runner types, and phrase examples (drawn from spec §brainstorm mode table).
4. Write `core/brainstorm/agents/devils-advocate.md` — adapted from `biz/devils-advocate/SKILL.md` protocol as a panel-agent persona file (character only, no orchestration logic, ends with `{{placeholder}}`).
5. Write `core/brainstorm/agents/board-advisor-*.md` files (the 4 archetypes from board-of-advisors: tech-lead.md, boris-product.md, operator.md, metrics.md) following the same persona format.
6. Verify structure: `ls plugins/sir-albert/skills/core/brainstorm/agents/` shows at least 12 agent files.
7. Do NOT create SKILL.md yet — that is ticket 03.

## Definition of Done

- [ ] `core/brainstorm/agents/` directory exists with ≥12 agent files
- [ ] `core/brainstorm/references/voices.md` and `references/modes.md` exist
- [ ] `biz/discovery-lens/agents/` no longer exists (moved, not copied)
- [ ] No SKILL.md yet (blocked on 03)

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
