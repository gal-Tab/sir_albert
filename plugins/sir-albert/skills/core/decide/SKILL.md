---
name: decide
description: >
  Decision memory: record a call once, auto-apply it every time the same
  question recurs — never re-decide what's already settled.
  Use when the user says "/decide", "record this decision", "we decided",
  "did we decide X before", "log this call", or "is this already decided".
argument-hint: "question_id slug + the decision to record (or just a question to look up)"
---

# Decide

Boot from `os/PREAMBLE.md`.

**Purpose:** stop re-deciding recurring calls. Every settled question gets one authoritative record in `os/state/decisions.jsonl`. When the same question surfaces again, the prior decision is stated and applied automatically — no re-ask.

---

## 0. Check before asking — always

Before prompting the user about anything that looks like a policy, threshold, or recurring call, scan `os/state/decisions.jsonl` for a matching `question_id`:

```bash
grep '"question_id"' os/state/decisions.jsonl
```

Or for a specific slug:

```bash
grep 'suppress-existing-customers' os/state/decisions.jsonl
```

If a match exists and the `scope` / `project` still applies, **do not ask — auto-apply** (see §2).

---

## 1. Store — recording a new decision

Append exactly one JSON object (no newline inside the object, blank line between entries is fine) to `os/state/decisions.jsonl`:

```json
{"ts":"2026-07-31","question_id":"suppress-existing-customers","choice":"yes","rationale":"Re-engaging existing customers from acquisition campaigns inflates CAC and confuses attribution.","project":"*","scope":"gtm"}
```

Field rules:

| Field | Format | Notes |
|---|---|---|
| `ts` | `YYYY-MM-DD` | Date the decision was made |
| `question_id` | `kebab-case-slug` | Stable identifier — never change once written |
| `choice` | short string | The answer: `"yes"`, `"no"`, `"last-touch"`, `"≥1000"`, etc. |
| `rationale` | 1–2 sentences | The *why* — future-you needs this, not just the what |
| `project` | string or `"*"` | Specific project slug or `"*"` for org-wide |
| `scope` | string | Domain label: `"gtm"`, `"data"`, `"ab-testing"`, `"consent"`, etc. |

Append command (never overwrite, never delete):

```bash
echo '{"ts":"YYYY-MM-DD","question_id":"<slug>","choice":"<choice>","rationale":"<why>","project":"<project-or-*>","scope":"<scope>"}' >> os/state/decisions.jsonl
```

Confirm the append by reading back the last line:

```bash
tail -1 os/state/decisions.jsonl
```

---

## 2. Auto-apply — when a prior decision matches

When a question arises that maps to an existing `question_id` (and `project` is `"*"` or matches the current project, and `scope` is relevant):

1. Do **not** ask the user to re-decide.
2. State the prior decision inline, in this format:

   > **Prior decision (2026-06-01):** suppress existing customers = yes, because re-engaging them inflates CAC and confuses attribution — **auto-applied**.

3. Proceed with the choice already applied.

If the user wants to **override**, they say so explicitly — then record a new entry with the updated choice and `ts`. The old entry stays (append-only log).

---

## 3. Recurring examples

These question_ids cover the most common recurring calls. Check for them before asking.

| question_id | Typical choice | Scope |
|---|---|---|
| `suppress-existing-customers` | `yes` | gtm |
| `ab-test-min-audience-size` | `≥1000` per variant | ab-testing |
| `attribution-model-paid-social` | `last-touch` | data |
| `consent-container-owner` | `monday-marketing` | consent |

---

## 4. Lookup mode (/decide without a new decision)

If the user asks "did we decide X?" or "is this already decided?", run the grep from §0, then:

- **Found:** surface the full JSON object, formatted as a human-readable summary (ts, choice, rationale), and note whether it auto-applies to the current context.
- **Not found:** say "No recorded decision for this question. Want me to record one now?" — then follow §1 if yes.

---

## Completion report

After any store or lookup, confirm:

```
Decision logged: <question_id> → <choice>  (os/state/decisions.jsonl, appended)
```

or

```
Decision found: <question_id> → <choice> (recorded <ts>) — auto-applied.
```

Do NOT commit `decisions.jsonl` unless the user explicitly asks.
