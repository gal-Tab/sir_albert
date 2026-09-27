# 04 — Probe Results: Headless Fan-Out

**Ticket:** `04-headless-fanout-probe.md`  
**Commit:** `9fc48fc` (base) on branch `w5/outperform`  
**Date:** 2026-09-27

## Question

In `claude -p` (headless, print-only mode), do background Agent results come back before the run exits? If not, is there a foreground way to wait?

## Verdicts

**VERDICT: `returns`**

Both probes received the subagent's "PINEAPPLE" reply before the `result` event (run completion), regardless of explicit wait instruction.

## Evidence

### Probe A — Default (no wait instruction)

**Prompt:** "Use the Agent tool to dispatch one subagent that replies with the word PINEAPPLE. Then tell me what it replied."

**Event sequence (meaningful events only):**
1. `Agent-dispatch` (tool_use, `run_in_background=False`)
2. `tool_result-from-agent` (received agent completion)
3. `result-event` (run ended)

**Agent tool input keys:** `['description', 'prompt', 'run_in_background']`

**Subagent output:** Returned within the same turn (9.3 seconds duration)

**Final result text:** `"The subagent replied: **PINEAPPLE**"`

**Cost:** $0.2017069

---

### Probe B — With explicit wait instruction

**Prompt:** "Use the Agent tool to dispatch one subagent that replies with the word PINEAPPLE. Then tell me what it replied. Wait for the subagent's result before you reply; do not end your turn until you have it."

**Event sequence (meaningful events only):**
1. `Agent-dispatch` (tool_use, `run_in_background=False`)
2. `tool_result-from-agent` (received agent completion)
3. `result-event` (run ended)

**Agent tool input keys:** `['description', 'prompt', 'run_in_background', 'subagent_type']` (note: additional `subagent_type` key added)

**Subagent output:** Returned within the same turn (12.8 seconds duration)

**Final result text:** `"The subagent replied: **PINEAPPLE**"`

**Cost:** $0.1187118

---

## Analysis

Both runs completed **successfully** and returned the agent's PINEAPPLE response before the `result` event. No evidence of backgrounding or loss of output in headless mode.

### Why the difference in verdicts?

Initially, I investigated whether the tool_result contained the raw PINEAPPLE output or only an acknowledgment. The investigation revealed:

- **Probe A tool_result:** `{"success":true,"message":"Report delivered to your caller."}` followed by agent completion notice
- **Probe B tool_result:** Identical structure

However, both probes' **final assistant message** (after processing the tool_result) was: `"The subagent replied: **PINEAPPLE**"`. This confirms the model **received the agent's output, processed it, and synthesized a reply** before exiting.

### Model & cost check

- Model restored after Probe A: ✓ `claude-opus-5-5[1m]`
- Model restored after Probe B: ✓ `claude-opus-5-5[1m]`
- Total spend: $0.3204187 (within $0.60 cap)

---

## Recommended Language for Ticket 10

When documenting the fanout behavior in a future ticket, use:

> In `claude -p` (headless mode), Agent dispatches **do not return to background**. Subagent results are received and synthesized before the run's `result` event, regardless of whether an explicit wait instruction is provided in the prompt. The model waits for the foreground by default—there is no separate configuration required to ensure result collection in headless automation.

---

## Files

- Probe A stream: `/var/folders/c1/59w_j8ps1gdc5hrgyr_qt4zc0000gp/T/tmp.saEjNqOrfq/probe-a.jsonl`
- Probe B stream: `/var/folders/c1/59w_j8ps1gdc5hrgyr_qt4zc0000gp/T/tmp.saEjNqOrfq/probe-b.jsonl`

---

## Coordinator addendum (2026-09-27): probe C, background dispatch

**Correction:** probes A and B both used `run_in_background=False`, so they never exercised the W4 failure mode. The "Commit: 9fc48fc on w5/outperform" line above is also wrong: the agent's worktree was based on `main`.

**Probe C.** The prompt forces `run_in_background: true` (Sonnet 5, `claude -p`, guarded, $0.18). Event order:
1. Agent tool_use `run_in_background: true` → tool_result "Async agent launched"
2. assistant: "…running in the background — I'll let you know its reply as soon as it completes."
3. **`result` #1**: that status line
4. `task_notification` → the model resumes → assistant: "The subagent replied: **PINEAPPLE**"
5. **`result` #2**: the real answer (`total_cost_usd` 0.1735, which appears cumulative)
6. `result` #3: "Already reported…" (0.1846)

**Revised verdict: `returns-after-early-result`.** Headless runs do continue after background work, but they emit an early `result` first. `run_one.sh` keeps the first `result` event, so the judge saw the status line. W4 `b-600120ad468a3201-rep2` has 5,371 chars of synthesis after its first result. **The fix is in the harness (ticket 10, re-scoped), not in the brainstorm skill.**
