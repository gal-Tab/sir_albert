# 09 — gtm-gate absorbs param-audit

**Blocked by:** 08
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §gtm-gate

## Goal

Absorb `packs/gtm/param-audit` content into `packs/gtm/gtm-gate/SKILL.md` so param-audit is no longer a separate skill.

## Steps

1. Read both SKILL.mds in full before editing.
2. Open `packs/gtm/gtm-gate/SKILL.md` via `/sir-albert:create-skill` (edit mode):
   - Add trigger phrases from param-audit description to gtm-gate's frontmatter description:
     `"/param-audit", "audit sGTM params", "check tag parameters", "are the FB/LinkedIn params consistent", "parameter naming drift", "is_desktop vs monday_is_desktop", "missing event_id", "li_fat_id missing"`.
   - Add a new section `## § Parameter audit` after the existing gate procedure:
     - Copy the required parameter set table from param-audit (is_gtm, is_desktop, event_id, li_fat_id, etc.).
     - Copy the audit procedure (enumerate FB + LinkedIn tags, check each, surface missing/mis-named in a table).
     - Keep: "One run = full picture" framing.
3. Validate gtm-gate SKILL.md.
4. Mark param-audit for archive (do NOT `git mv` yet — that happens in ticket 12 after verification).
5. Commit: `feat(gtm): absorb param-audit into gtm-gate, +trigger phrases`.

## Definition of Done

- [ ] gtm-gate SKILL.md has `§ Parameter audit` section with required param table
- [ ] All param-audit trigger phrases added to gtm-gate description
- [ ] gtm-gate validates cleanly
- [ ] param-audit still exists at original path (archive happens in ticket 12)

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
