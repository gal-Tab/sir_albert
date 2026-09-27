# 04 — headless-fanout-probe

**Blocked by:** —

## Goal
A recorded answer to "in `claude -p`, do background Agent results come back before the run exits? If not, is there a foreground way to wait?", with raw evidence.

## Why
W4: brainstorm's panel (`600120ad` B rep2) and the GTM task (`0c4bbdadad6f78d8`, both arms) dispatched background agents and ended with "I'll synthesize once they're back". The judge scored those as losses. That penalizes using skills, and it's a real bug for any headless/automated use.

## Steps
1. Scratch: `T=$(mktemp -d)`; `git -C $T init -q && git -C $T commit -q --allow-empty -m s`.
2. Probe A, default (~$0.10). From `$T`, run through `guarded.sh`: `claude --print --model claude-sonnet-5 --max-turns 6 --max-budget-usd 0.25 --output-format stream-json --verbose --no-session-persistence` with the stdin prompt `Use the Agent tool to dispatch one subagent that replies with the word PINEAPPLE. Then tell me what it replied.` Save to `$T/probe-a.jsonl`.
3. Probe B, explicit wait (~$0.10). Same, but the prompt adds: `Wait for the subagent's result before you reply; do not end your turn until you have it.` Save to `$T/probe-b.jsonl`.
4. Inspect both: the Agent `tool_use` input keys (look for any `run_in_background`-style parameter), whether a `tool_result` containing `PINEAPPLE` appears before the `result` event, and the final `result` text. After each spawn: `grep '"model"' ~/.claude/settings.json`.
5. Write `docs/plans/2026-09-27-w5-outperform/04-probe-results.md`: the tool input schema observed, the ordering of events per probe, and a verdict (one of: `returns` / `returns-only-when-told-to-wait` / `never-returns`), plus the exact wording ticket 10 should use.
6. Commit: `git add docs/plans/2026-09-27-w5-outperform/04-probe-results.md && git commit -m "docs(w5): headless fan-out probe results"`

## Definition of Done
- [ ] Both probes ran live; the stream files were inspected, not assumed
- [ ] The results doc states one of the 3 verdicts, with event-order evidence
- [ ] Gal's default model is intact after the probes
