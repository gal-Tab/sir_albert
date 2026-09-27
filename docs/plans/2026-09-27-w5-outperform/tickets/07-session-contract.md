# 07 — session-contract

**Blocked by:** —

## Goal
The SessionStart injection carries a scoped "use the skill" rule: invoke the matching sir_albert skill before any response to task work. It rules out the usual excuses and says explicitly when not to fire, so it gets superpowers' invocation lift without superpowers' blanket "1% rule" false fires.

## Why
Superpowers injects 3.2k chars of "MUST invoke before ANY response" and gets A to fire skills even on prompts that lack context. It also produced A's control false fire (`create-skill` on `feb8b4a9e0a8e885`, both reps). sir_albert injects only a 623-char table.

## Steps
1. Write the failing tests in `plugins/sir-albert/tests/test_session_start.py`:
   - `test_contract_present`: the injection contains `Use-the-skill rule`, `before any other response`, and `Skip only`.
   - `test_contract_names_router`: it contains `router`. The router's instruction is referenced so the two reinforce each other.
   - Change `test_within_800_chars` / `test_plain_within_800_chars` to ≤ 1600, and change the cap in `hooks/session_start.py` from 800 to 1600 (the error message too).
2. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/test_session_start.py`. Expected: new FAIL.
3. Rewrite `plugins/sir-albert/hooks/HOOK_CONTEXT.md`. Keep the existing table and `{PACK_LIST}`/`{RESUME_HINT}`, and add above the table:
   ```
   **Use-the-skill rule:** for task work — exploring or designing an idea, planning, executing a plan, debugging, shipping a branch, handing off — invoke the matching skill below with the Skill tool *before any other response*, including clarifying questions (the skill asks them better). When the sir-albert router names a skill, invoke it.
   Not reasons to skip: "it's simple", "I need context first", "I know what the skill says".
   Skip only for chit-chat, one-line factual answers, or when no row fits — never invoke a skill just to have invoked one.
   ```
4. Run the step 2 command again. Expected: PASS. Measure: `echo | PWD=/tmp python3 plugins/sir-albert/hooks/session_start.py | /usr/local/bin/python3.13 -c "import json,sys;print(len(json.load(sys.stdin)['hookSpecificOutput']['additionalContext']))"`. Expected: ≤ 1600.
5. Full suite green.
6. Commit: `git commit -m "feat(w5): scoped use-the-skill contract in session start"`

## Definition of Done
- [ ] New tests fail on the old code and pass on the new code; the suite is green
- [ ] Injection ≤ 1600 chars, with explicit skip conditions (the control-slice guard)

⚠️ Risk: live immediately in every Gal session. The "Skip only…" line is the false-fire guard; G3 in P3 measures it.
