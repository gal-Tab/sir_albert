# Ticket 10 — W4 impact

**Finding:** 1 of 60 W4 artifacts (30 pairs) was misjudged due to the first-result bug.

## Affected artifact

| Artifact | result_index stored | chars after first result |
|---|---|---|
| `b-600120ad468a3201-rep2.json` | 0 | 5,373 |

The harness captured `result_event` from `result_index=0` (a background-agent status line). The real synthesis — 5,373 chars — followed in assistant turns after that first result, but the judge scored only the status line.

## W4 verdict impact

The W4 verdict (FAIL) does **not change**, because its failing gate is the skill-invocation gate: B invoked the labelled skill on 2/5 happy-path prompts, against a bar of ≥4. That gate reads `skills_called` and is independent of the judge. What the bug did distort is the **quality** comparison. The judge's input comes from `result_event.result`, so it saw only B's status line for this pair and resolved it `A_wins`. With B's actual synthesis, that pair could flip, which would raise B's 56.7% win-rate. It wasn't re-judged. (Coordinator correction, 2026-09-27: an earlier draft of this note said the judge saw the full `assistant_text`, which is wrong.)

## W4 files modified

None. W4 artifacts are gitignored and read-only; this note records the impact without touching them.
