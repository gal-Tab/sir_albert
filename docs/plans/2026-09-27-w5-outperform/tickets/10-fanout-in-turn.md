# 10 — fanout-in-turn

**Blocked by:** 04

## Goal
When brainstorm's explore/panel modes dispatch voice agents, the skill waits for them and synthesizes in the same turn. It never ends a turn with "I'll synthesize once they're back".

## Why
In W4 the only happy-path pair A lost on merit (`600120ad468a3201` rep 2) was B invoking brainstorm, dispatching 3 voices, and ending with no answer. Using the skill made the answer worse.

## Steps
1. Read `docs/plans/2026-09-27-w5-outperform/04-probe-results.md` and take the verdict and wording from it:
   - `returns`: no skill change is needed. Close this ticket with a note and skip to step 5.
   - `returns-only-when-told-to-wait`: use ticket 04's exact wait wording.
   - `never-returns`: in headless runs, voices run sequentially inline (the coordinator writes each voice itself, clearly labelled), and the answer notes the loss of blindness.
2. Invoke `/sir-albert:create-skill` in edit mode on `plugins/sir-albert/skills/core/brainstorm/SKILL.md` (mandatory). Change the dispatch bullets at lines ~35 and ~42 and `references/modes.md:17` per step 1. Add: "Never end the turn before the synthesis is delivered."
3. Complete create-skill's scoring loop and evals, including an eval where panel mode must deliver its synthesis in one turn.
4. Live check (~$0.20, AUTO). Re-run W4 prompt `600120ad468a3201` on arm B with context (ticket 01 mechanism) into `runs-dev/`. Expected: the final text contains a synthesis, not just a status line.
5. Suite green. Commit: `git commit -m "fix(w5): brainstorm panel synthesizes in-turn"`

## Definition of Done
- [ ] Behavior matches the ticket 04 verdict; edited via create-skill
- [ ] Live re-run delivers a synthesis in-turn
