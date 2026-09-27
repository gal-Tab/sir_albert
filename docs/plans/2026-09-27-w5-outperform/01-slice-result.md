# 01 — Slice result: replay-with-context

**Date:** 2026-09-27  
**Arm:** B  
**Hash:** `aef6880dbd5903c4`  
**Rep:** 1

## Outcome

| Field | Value |
|---|---|
| `context_turns` | 2 |
| Contains "nothing has been shared" | No |
| Contains "no doc" | No |
| `assistant_text` length | 1858 chars |
| `result_subtype` | success |

## Interpretation

With `preceding_turns` injected via `--append-system-prompt`, the model engaged
substantively with the earlier conversation context (sgtm stabilization, per-stream
exclusion windows, Kohavi/Boris framing) rather than answering as if the thread had
just started. The W4 "nothing has been shared yet" failure mode does not appear.

## Known limitation

`preceding_turns` holds at most the turns captured in the corpus (here: 2, truncated
to 500 chars each). Context is lossy but identical across arms — a controlled
confound, not a bias.
