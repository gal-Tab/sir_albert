# 06 — debug skill (new)

**Blocked by:** 08
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §debug

## Goal

Create `core/debug/SKILL.md` via `/sir-albert:create-skill`, porting Pocock `diagnosing-bugs` with redaction and non-deterministic bug handling.

## Steps

1. Fetch source for reference:
   ```bash
   gh api repos/mattpocock/skills/contents/skills/engineering/diagnosing-bugs/SKILL.md --jq '.content' | base64 -d
   ```
2. Run `/sir-albert:create-skill` to scaffold `core/debug/SKILL.md`.
   - Type: discipline (T1 smoke tier — Phase 1 is a non-negotiable rule, discipline not technique)
   - Name: `debug`
   - Trigger: "debug this", "diagnose", "something is broken", "this is failing", "figure out why X", "diagnose this bug", "it's throwing an error"
3. SKILL.md content (from Pocock source, preserve key discipline):
   - **Phase 1 — feedback loop** is non-negotiable; cannot skip or abbreviate. Show the feedback loop invocation and output before any hypothesis work.
   - **Redact** all secrets before showing any command output (`<REDACTED>`); build loops against env vars.
   - Tighten-the-loop section: faster / sharper signal / more deterministic (from source).
   - Non-deterministic bugs: raise repro rate to ≥50% before proceeding to hypothesis.
   - If loop cannot be built: stop, list what was tried, ask for access/artifact/instrumentation.
   - Phases structure: feedback-loop → hypothesis → fix → verify → close.
   - Keep Pocock's 10 feedback-loop construction methods (adapted to not assume git bisect/Playwright are always available).
4. Validate SKILL.md.
5. Commit: `feat(core): add debug skill (Pocock diagnosing-bugs port)`.

## Definition of Done

- [ ] `core/debug/SKILL.md` exists, validates cleanly
- [ ] Phase 1 feedback loop is a hard gate (explicit "cannot skip" language)
- [ ] Redaction rule in the skill body
- [ ] Non-deterministic bug handling present
- [ ] No `superpowers:` references

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
