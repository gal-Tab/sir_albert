# 13 — end-to-end verification

**Blocked by:** 10, 11, 12
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md`

## Goal

Confirm every W2 core skill loads cleanly, mode selection fires correctly, zero stale refs remain, and zero `superpowers:` references exist in `plugins/`.

## Steps

1. **Plugin load test** — each skill must appear in the listing:
   ```bash
   claude --plugin-dir /Users/galta/Development/sir_albert/plugins -p "list all sir-albert skills"
   ```
   Expected: brainstorm, plan, execute, debug, build, handoff, resume, create-skill, slack-in-my-voice, gtm-gate (plus packs and other unchanged skills).

2. **Mode selection smoke** — one example prompt per mode:
   | Prompt | Expected mode | Pass condition |
   |---|---|---|
   | "grill me about this idea: X" | grill | Asks one question; does not dispatch subagents |
   | "attack this plan: Y" | attack | States "attack mode" and dispatches parallel subagent voices |
   | "zoom out on this codebase" | zoom-out | Gives abstraction map; no subagents |
   | "let's design a new feature Z" | design | Classifies Spike/Bounded/Arch; asks clarifying question |
   | "brainstorm this idea: W" | explore (default) | States "explore mode"; dispatches voices |

3. **Stale ref grep** — must return zero hits:
   ```bash
   grep -rn "discover\|html-plans\|build-discipline\|kb-query\|kb-compile\|superpowers:" \
     plugins/sir-albert/ \
     --include="*.md" --include="*.json" --include="*.py" --include="*.sh" \
     | grep -v "_archive\|THIRD_PARTY_NOTICES\|methodology.md"
   ```
   `methodology.md` is excluded because it keeps the Pocock comparison table (historical, not a live dependency).

4. **superpowers: ref sweep** across the entire plugins/ dir:
   ```bash
   grep -rn "superpowers:" plugins/ --include="*.md" --include="*.json"
   ```
   Must return zero hits outside `_archive/` and `THIRD_PARTY_NOTICES.md`.

5. **docs-layout rule** — confirm PREAMBLE loads it:
   ```bash
   grep "docs-layout" plugins/sir-albert/os/PREAMBLE.md
   ```

6. **plan skill ticket output** — `/sir-albert:plan "add login button"` → produces both `.html` and `/tickets/` .md files in `docs/plans/`.

7. **create-skill independence** — confirmed by stale ref grep returning zero; also:
   ```bash
   grep -n "superpowers" plugins/sir-albert/skills/dev/create-skill/SKILL.md
   ```
   Must return empty.

8. If any check fails: do not merge the branch. Fix the failing ticket and re-run only the affected checks.

9. Commit: `chore: W2 verification passed — all skills load, no stale refs`.

## Definition of Done

- [ ] All 9+ core skills appear in plugin listing
- [ ] All 5 mode-selection smokes pass
- [ ] Stale ref grep returns zero (step 3)
- [ ] superpowers: grep returns zero (step 4)
- [ ] PREAMBLE imports docs-layout rule
- [ ] plan skill produces both HTML and .md ticket files
- [ ] create-skill SKILL.md has zero superpowers: refs

## CHECKPOINT

Mode-selection smokes that use `attack` and `explore` modes will spawn parallel subagents. Confirm with Gal before running those two smokes (cost/token). The other 3 modes (grill, zoom-out, design) run in main conversation and are free to test.
