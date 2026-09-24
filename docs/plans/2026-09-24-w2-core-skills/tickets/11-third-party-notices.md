# 11 — update THIRD_PARTY_NOTICES.md with Pocock attribution

**Blocked by:** 05, 06, 07
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §Pocock provenance

## Goal

Update `plugins/sir-albert/skills/dev/THIRD_PARTY_NOTICES.md` to credit the three Pocock skills ported in W2: implement-spec (→execute), diagnosing-bugs (→debug), tdd (absorbed into build).

## Steps

1. Read current `THIRD_PARTY_NOTICES.md` to see format.
2. Add three entries under the existing MIT license block:
   ```
   - `core/execute` — ported from `mattpocock/skills` `skills/in-progress/implement-spec/SKILL.md`; adapted: optional worktrees, hard CHECKPOINT gates, Sonnet subagents.
   - `core/debug` — ported from `mattpocock/skills` `skills/engineering/diagnosing-bugs/SKILL.md`; adapted: redaction rule, non-deterministic bug handling.
   - `core/build` (TDD section) — ported from `mattpocock/skills` `skills/engineering/tdd/SKILL.md`; adapted: seam-confirmation step, inline absorption into build-discipline loop.
   ```
3. Verify the existing entries (grill-with-docs, prototype, grilling, domain-modeling, claude-handoff) are still accurate — these skills are being archived, but notices should remain as provenance.
4. Commit: `chore: update THIRD_PARTY_NOTICES for W2 Pocock ports`.

## Definition of Done

- [ ] Three new entries added for execute, debug, and build (TDD section)
- [ ] All MIT attribution lines present
- [ ] Existing entries for archived Pocock skills retained for provenance
