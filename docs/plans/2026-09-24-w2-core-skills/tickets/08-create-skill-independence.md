# 08 — create-skill independence from superpowers

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §create-skill

## Goal

Remove all `superpowers:` references from `skills/dev/create-skill/` by inlining the SDO/anti-narrative rules it currently delegates to `superpowers:writing-skills`.

## Steps

1. Grep to confirm all occurrences:
   ```bash
   grep -rn "superpowers" plugins/sir-albert/skills/dev/create-skill/
   ```
   Expected hits: SKILL.md (3), methodology.md (3+), angles.md (1), validate-skill.py (1).

2. **Edit `SKILL.md` directly** (bootstrap exception — this skill edits itself; cannot route through itself for this change):
   - Remove lines 8–9 (`REQUIRED BACKGROUND: Load superpowers:writing-skills…`).
   - Replace with inline SDO rules (~150 words):
     - Match the form to the failure: discipline skills exist because humans rationalize the rule away; make the check automatic, not advisory.
     - Rationalization table: for each rule, name the 3 most common rationalizations and why they fail.
     - Anti-narrative: description never narrates the workflow; it states when and (at most) what.
     - Red flags: "it's obvious", "everyone knows", "just once", "special case this time" → apply the rule harder.
   - Remove the "spec + superpowers" parenthetical in the description rule section.

3. **Edit `references/methodology.md`**:
   - Section "The superpowers challenge (§2)": keep the comparison table (it's useful attribution); replace the instruction "read `superpowers:writing-skills` directly" with "the SDO rules are inlined in SKILL.md §SDO".
   - Remove all other `superpowers:` occurrences.

4. **Edit `references/angles.md`** line 31: replace `superpowers:writing-skills` ref with `SKILL.md §SDO`.

5. **Edit `scripts/validate-skill.py`** line 6 comment: `superpowers:writing-skills SDO` → `see references/methodology.md`.

6. Verify zero `superpowers:` occurrences:
   ```bash
   grep -rn "superpowers" plugins/sir-albert/skills/dev/create-skill/
   ```
   Must return empty.

7. Commit: `fix(create-skill): inline SDO rules, remove superpowers dependency`.

## Definition of Done

- [ ] `grep -rn "superpowers" plugins/sir-albert/skills/dev/create-skill/` returns empty
- [ ] SKILL.md has inline SDO/anti-narrative block (~150 words)
- [ ] methodology.md comparison table kept; delegation removed
- [ ] validate-skill.py comment updated

**Note:** This ticket must be done BEFORE any other ticket that invokes `/sir-albert:create-skill`, to avoid the skill loading superpowers at runtime. Tickets 03, 04, 05, 06, 07, 09 all depend on this.

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
