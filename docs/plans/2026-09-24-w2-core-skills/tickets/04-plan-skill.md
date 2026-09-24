# 04 — plan skill (rename html-plans → plan, move to core/)

**Blocked by:** 01, 08
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §plan

## Goal

Rename `skills/docs/html-plans` → `skills/core/plan`, update SKILL.md name + absorb superpowers writing-plans granularity (exact files, 2–5 min steps, tracer-bullet slices with blocking edges), and produce both HTML + ticket .md output.

## Steps

1. `git mv plugins/sir-albert/skills/docs/html-plans plugins/sir-albert/skills/core/plan`.
2. Open `core/plan/SKILL.md` via `/sir-albert:create-skill` (edit mode, not from scratch).
   Changes to make:
   - Frontmatter `name: html-plans` → `name: plan`.
   - Description: add trigger phrases "plan this", "break this down into tickets", "vertical slices".
   - New section **Ticket output** (after existing HTML section): for each milestone/task, also write `docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md` with the ticket format (Goal / Blocked by / Steps / DOD / CHECKPOINT).
   - New section **Approval gate**: present breakdown for user approval before generating ticket files (tracer-bullet: approve once, then generate).
   - Superpowers writing-plans gates (inline, ~5 bullets): exact file paths, 2–5 min step granularity, test steps included, blocking edges explicit.
3. Validate SKILL.md.
4. Fix cross-refs:
   - `skills/docs/to-prd/SKILL.md` line 147: update path to `../../../core/plan/sample-plan.html`.
   - `shared/references/design-tokens.md` line 1: update title to `Design Tokens — plan`.
5. Confirm `plugin.json`: `./skills/core` is listed (it is); `./skills/docs` still loads to-prd and other docs skills. No change needed to json.
6. Smoke: `/sir-albert:plan "add login endpoint"` → produces HTML plan at `docs/plans/` AND ticket .md files.
7. Commit: `feat(core): rename html-plans → plan, move to core/, add ticket output`.

## Definition of Done

- [ ] `core/plan/` exists; `docs/html-plans/` no longer exists
- [ ] SKILL.md name is `plan`; validates cleanly
- [ ] Ticket .md output format matches `docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md`
- [ ] to-prd cross-ref updated; design-tokens title updated
- [ ] Smoke: both HTML and ticket .md files generated for a test plan

## CHECKPOINT

Smoke run generates files in `docs/plans/`. This is a write to the repo — confirm before running if working in a context where docs writes are sensitive.

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
