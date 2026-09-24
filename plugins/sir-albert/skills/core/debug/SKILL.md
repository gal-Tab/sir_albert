---
name: debug
description: Use when something is broken, failing, throwing errors, or behaving wrong. Triggers on "debug this", "diagnose", "something is broken", "this is failing", "figure out why X", "diagnose this bug", "it's throwing an error", "something's off", "this isn't working".
---

# debug

Boot from `os/PREAMBLE.md`.

Adapted from Pocock `skills/engineering/diagnosing-bugs` (MIT); see `THIRD_PARTY_NOTICES.md`.

**Phase 1 is non-negotiable.** Do not read code looking for a theory before Phase 1 is complete. The moment you think "I can see the bug from here" is the moment this skill is most needed.

---

## Redact

Show commands, outputs, and captured artifacts only after redacting secrets. Write `<REDACTED>` in place of any credential, token, API key, or auth header. Build loops against env vars so credentials stay in the environment. If the redacted output is not enough to diagnose the bug, say so and ask the user.

---

## Phase 1 — Build a feedback loop (cannot skip)

This is the skill. A tight, red-capable loop beats any amount of code reading.

### Feedback loop construction methods (in order of preference)

1. **Failing test** at the seam that reaches the bug: unit, integration, or e2e.
2. **Curl / HTTP script** against a running dev server; assert on the exact symptom.
3. **CLI invocation** with a fixture input; diff stdout against a known-good snapshot.
4. **Headless browser script** (Playwright, Puppeteer) — only if the environment has it.
5. **Replay a captured trace.** Save a real network request, payload, or event log to disk; replay through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run 100+ random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states, automate "check at state X" — only if version history is available and accessible.
9. **Differential loop.** Run the same input through two configs or versions; diff outputs.
10. **Structured human-in-the-loop.** Last resort. If a human must click, write a step-by-step capture script so the output feeds back in a structured way.

### Tighten the loop

Once a loop exists, treat it as a product:
- Can it be faster? (Cache setup, skip unrelated init, narrow scope)
- Can the signal be sharper? (Assert on the specific symptom, not "didn't crash")
- Can it be made deterministic? (Pin time, seed RNG, isolate filesystem, freeze network)

A 2-second deterministic loop is a debugging superpower. A 30-second flaky loop is barely useful.

### Non-deterministic bugs

Goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, add stress, narrow timing windows. A 50%-flake bug is debuggable; 1% is not. Raise the rate until it is ≥50% before proceeding.

### When a loop cannot be built

Stop. Say so explicitly. List what was tried. Ask the user for:
- (a) Access to the environment that reproduces it
- (b) A redacted captured artifact (HAR file, log dump, core dump, screen recording)
- (c) Permission to add temporary instrumentation

Do not proceed to Phase 2 without a loop.

### Phase 1 completion criterion

Phase 1 is done only when:
- [ ] **Red-capable:** the loop drives the actual bug code path and asserts the user's exact symptom
- [ ] **Deterministic:** same verdict every run (or: flaky bug at ≥50% repro rate)
- [ ] **Fast:** seconds, not minutes
- [ ] **Agent-runnable:** runs unattended

Show the invocation and its actual output (redacted) before proceeding.

---

## Phase 2 — Hypothesize

Generate 3–5 ranked hypotheses before testing any. Each must be falsifiable:

> "If X is the cause, then changing Y will make the bug disappear / changing Z will make it worse."

If the prediction cannot be stated, the hypothesis is a vibe. Discard or sharpen it.

Show the ranked list before testing. The user may re-rank instantly based on domain knowledge.

---

## Phase 3 — Fix

Change one variable at a time. Each probe maps to a specific prediction from Phase 2.

Prefer debugger / REPL inspection over logs. If logs are needed, tag every debug log with a unique prefix (e.g., `[DEBUG-a4f2]`) — cleanup becomes a single grep.

For performance bugs: measure first (timing harness, profiler, query plan), then fix. Logs are wrong for perf bugs.

---

## Phase 4 — Verify

1. Turn the minimized repro into a regression test at the correct seam (if one exists).
2. Run the Phase 1 loop against the original scenario — confirm it goes green.
3. Confirm the regression test passes.
4. If no correct seam exists, document why.

---

## Phase 5 — Close

Before done:
- [ ] Original repro no longer reproduces (re-run Phase 1 loop)
- [ ] All `[DEBUG-...]` logs removed (grep the prefix)
- [ ] Throwaway prototypes deleted
- [ ] The correct hypothesis stated in the commit/PR message
