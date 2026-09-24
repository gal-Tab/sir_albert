# 05 — execute skill (new)

**Blocked by:** 08
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §execute

## Goal

Create `core/execute/SKILL.md` via `/sir-albert:create-skill`, porting Pocock `implement-spec` with Gal-specific adaptations (optional worktrees, hard checkpoints, Sonnet builders).

## Steps

1. Fetch source for reference (do not copy verbatim — adapt):
   ```bash
   gh api repos/mattpocock/skills/contents/skills/in-progress/implement-spec/SKILL.md --jq '.content' | base64 -d
   ```
2. Run `/sir-albert:create-skill` to scaffold `core/execute/SKILL.md`.
   - Type: technique (T1 smoke tier)
   - Name: `execute`
   - Trigger: "implement this spec", "execute the plan", "work the tickets", "implement ticket NN", "run the execute skill"
3. SKILL.md adaptations from Pocock source:
   - Worktrees + draft PR: **optional** — skip unless user requests; most of Gal's work is not a code PR.
   - Implementer subagents: run in background, Sonnet model, sparse context pointers to spec/tickets/commits.
   - **Hard CHECKPOINT gates** before: push, PR create, PR merge, live config apply, any deploy. Stop and ask; do not proceed autonomously.
   - Coordinator stays in main context, answers subagent questions.
   - Code review at end only if output is a code branch; else a verification step matching spec's DOD.
   - Announce: "I'm using the execute skill. Reading the spec and building the task graph."
4. Create `core/execute/references/` with a brief guide on building the task graph (blocking edges, frontier concept).
5. Validate SKILL.md.
6. Commit: `feat(core): add execute skill (Pocock implement-spec port, Gal-adapted)`.

## Definition of Done

- [ ] `core/execute/SKILL.md` exists, validates cleanly
- [ ] CHECKPOINT markers present for push/PR/merge/deploy actions
- [ ] Worktrees marked optional
- [ ] Subagent model explicitly Sonnet
- [ ] No `superpowers:` references

## CHECKPOINT

Smoke-testing execute with a real spec would spawn background subagents and potentially push branches. Do NOT smoke-test with live repos without explicit approval. Verify by code-reading the skill only (T1 tier is acceptable here given the risk profile).

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
