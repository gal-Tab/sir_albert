# 07 — build skill (move packs/build/build-discipline → core/build)

**Blocked by:** 08
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §build

## Goal

Move `packs/build/build-discipline` to `core/build`, fix stale `kb-query`/`kb-compile` refs, and absorb superpowers finishing-a-branch + Pocock tdd + superpowers verification-before-completion (~3 lines each).

## Steps

1. `git mv plugins/sir-albert/skills/packs/build/build-discipline plugins/sir-albert/skills/core/build`.
2. Open `core/build/SKILL.md` via `/sir-albert:create-skill` (edit mode):
   - `name:` field: `build-discipline` → `build`
   - Fix stale refs: replace `kb-query` → `kb:wiki-query` and `kb-compile` → `kb:wiki-compile` everywhere in the file.
   - Add **§ Finishing a branch** (3–5 bullets from superpowers finishing-a-branch): before merging, confirm DOD met, tests pass, no leftover TODO/debug artifacts, PR description explains the why.
   - Add **§ TDD** (3–5 bullets from Pocock tdd): confirm seams with user before writing tests; red-before-green; no tautological assertions (expected values from independent source); one slice at a time.
   - Add **§ Verification before completion** (3–5 bullets from superpowers): show evidence inline (test run, curl output, smoke result) before claiming done; evidence precedes "done".
   - Fetch Pocock tdd source for TDD bullets:
     ```bash
     gh api repos/mattpocock/skills/contents/skills/engineering/tdd/SKILL.md --jq '.content' | base64 -d
     ```
3. Validate SKILL.md.
4. Confirm `plugin.json`: check if `./skills/packs/build` is a separate entry. If so, remove it (core/ covers the skill now). If `./skills/core` is listed, no action needed.
5. Smoke: `/sir-albert:build` loads cleanly and shows the build loop.
6. Commit: `feat(core): move build-discipline → core/build, fix stale kb refs, absorb finishing/tdd/verify`.

## Definition of Done

- [ ] `core/build/SKILL.md` exists at new path, name is `build`, validates cleanly
- [ ] `packs/build/build-discipline/` no longer exists
- [ ] Zero occurrences of `kb-query` or `kb-compile` in the skill file
- [ ] Finishing-a-branch, TDD, and verification sections present (3–5 bullets each)
- [ ] plugin.json updated if `./skills/packs/build` was a separate entry

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md created or edited in this ticket runs the **full** `/sir-albert:create-skill` loop: author → score → converge, with the resulting `evals/` dir **committed** next to the skill. No "lightest path" or tier-skip. Don't paste source content verbatim; only true hard constraints are pinned. The coordinator verifies from your transcript (Skill calls + `evals/` dirs) before this ticket counts as done.
- [ ] Full create-skill loop run; `evals/` committed for each skill touched
