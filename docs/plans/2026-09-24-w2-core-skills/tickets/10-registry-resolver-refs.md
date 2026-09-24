# 10 — update REGISTRY.md, RESOLVER.md, plugin.json, READMEs

**Blocked by:** 03, 04, 07, 09
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §References to update

## Goal

Update all cross-references for the renamed/moved skills atomically: discover→brainstorm, html-plans→plan, build-discipline→build, param-audit removal.

## Steps

1. Run the full grep to catch any refs missed in the spec:
   ```bash
   grep -rn "discover\|html-plans\|build-discipline\|param-audit" \
     plugins/sir-albert/os/ plugins/sir-albert/skills/ REGISTRY.md \
     --include="*.md" --include="*.json" | grep -v "_archive\|THIRD_PARTY\|docs/specs\|docs/plans"
   ```
2. **REGISTRY.md** — make all changes in one edit:
   - core table: `discover` row → `brainstorm` row (path, trigger phrases covering all 7 modes).
   - docs table: `html-plans` row → move to core table as `plan` row.
   - core table: remove `discover` row entirely (absorbed into brainstorm).
   - packs table: `build-discipline` row → move to core table as `build` row; update path.
   - packs table: `param-audit` row → remove; update gtm-gate trigger phrases row.
   - shared assets table lines 132–133: `html-plans` → `plan`.
   - Update the "Adding a New Skill" section category list to include `core/` explicitly.
3. **RESOLVER.md**:
   - Line 13: `packs/build` reference → `core/build`.
   - Line 15: `Core /discover — pick a lens: explore · sharpen · attack · zoom-out` → `Core /brainstorm — modes: explore · sharpen · attack · panel · grill · zoom-out · design`.
4. **skills/core/README.md**: replace `discover` entry with `brainstorm` entry.
5. **skills/packs/README.md**: replace last-line ref to `core/discover` → `core/brainstorm`; remove build pack entry (skill now in core).
6. **plugin.json** (`plugins/sir-albert/.claude-plugin/plugin.json`): if `./skills/packs/build` is listed, remove it. Confirm `./skills/core` is listed.
7. Re-run grep from step 1 — must return zero hits (excluding archive/ and docs/ history files).
8. Commit: `chore: update REGISTRY, RESOLVER, READMEs, plugin.json for W2 skill renames`.

## Definition of Done

- [ ] Zero hits from step-1 grep (excluding _archive/, docs/ history)
- [ ] REGISTRY.md: brainstorm in core table; plan in core table; build in core table; no param-audit row
- [ ] RESOLVER.md: both line 13 and line 15 updated
- [ ] plugin.json: `./skills/packs/build` removed if it existed
- [ ] core/README.md and packs/README.md updated
