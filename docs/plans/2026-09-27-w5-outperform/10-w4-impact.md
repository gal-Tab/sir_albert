# Ticket 10 — W4 impact

**Finding:** 1 of 60 W4 artifacts (30 pairs) was misjudged due to the first-result bug.

## Affected artifact

| Artifact | result_index stored | chars after first result |
|---|---|---|
| `b-600120ad468a3201-rep2.json` | 0 | 5,373 |

The harness captured `result_event` from `result_index=0` (a background-agent status line). The real synthesis — 5,373 chars — followed in assistant turns after that first result, but the judge scored only the status line.

## W4 verdict impact

The W4 overall verdict does **not change**. Arm B failed the skill gate regardless: the judge saw the full `assistant_text` (which includes all text blocks, emitted correctly), but the brainstorm skill quality gate requires the response to demonstrate structured synthesis. The misjudged pair `b-600120ad468a3201-rep2` went to A; reverting it would still leave B below the gate threshold.

## W4 files modified

None. W4 artifacts are gitignored and read-only; this note records the impact without touching them.
