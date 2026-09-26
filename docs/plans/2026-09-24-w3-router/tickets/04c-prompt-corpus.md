# 04c — prompt_corpus.py (reusable prompt corpus tool)

**Blocked by:** 04b (extraction logic validated)
**Date:** 2026-09-25

## Goal

Promote the 04b extraction logic into a reusable corpus tool. Used by: W4 replay, T2 skill evals, and the router precision/recall gate. Replaces the one-off `tools/precision_report.py` (redirect it to this tool).

## Output location

`~/.claude/sir-albert-corpus/corpus.jsonl` — **outside the repo** (raw private prompts).  
Only aggregate stats go in the repo.

## Commands

```
python3 plugins/sir-albert/tools/prompt_corpus.py extract
    Reads ~/.claude/projects/**/*.jsonl (skip /subagents/).
    Applies same organic-filter exclusions as 04b.
    For each organic prompt, writes one JSON line to corpus.jsonl:
      {
        "session_id": str,
        "timestamp": str,
        "cwd": str,
        "project": str,        # last path component of project dir
        "text": str,           # full prompt text
        "preceding_turns": [   # up to 2 turns before this prompt, each truncated to 500 chars
          {"role": "assistant"|"user", "text": str}
        ],
        "label": str | null    # skill slug that fired in the next assistant turn, or null
      }
    Writes to ~/.claude/sir-albert-corpus/corpus.jsonl (appends, deduplicates by session_id+text hash).
    Prints: total written, total skipped (already present), total excluded.

python3 plugins/sir-albert/tools/prompt_corpus.py stats
    Reads corpus.jsonl, prints counts per label (sorted desc).

python3 plugins/sir-albert/tools/prompt_corpus.py sample --label X -n 5
    Prints 5 random prompts for label X, redacted to ≤80 chars each.

python3 plugins/sir-albert/tools/prompt_corpus.py router-eval
    Replaces tools/precision_report.py.
    Reads corpus.jsonl for labeled examples (recall set).
    Also reads ~/.claude/projects/**/*.jsonl for organic prompts (precision set).
    Runs prompt_router.py patterns, reports precision + recall table.
    Writes report to docs/plans/2026-09-24-w3-router/router-eval-report-YYYY-MM-DD.txt.
```

## Label detection

For each organic user prompt, scan forward in the same transcript for the next `assistant` message that contains a `Skill` tool_use. Extract the `skill` input value. If found within 2 assistant turns → label = skill slug. Else → label = null.

## Organic filter (same as 04b)

Exclude if any of:
- Starts with "Base directory for this skill", `<task-notification`, `<command-`, `<local-command-`
- Contains "This session is being continued from a previous conversation"
- `isinstance(content, list)` and only has `tool_result`/`tool_use` blocks
- Length > 2000 chars
- Starts with `<` and contains `>` in first 50 chars

## Tests

`plugins/sir-albert/tests/test_prompt_corpus.py`:
- Fixture: small JSONL with 3 user prompts (1 organic, 1 injected "Base directory for this skill...", 1 task-notification), 1 assistant Skill turn
- `extract` → 1 line written, label = the skill slug
- `stats` → shows label count
- `sample` → returns redacted snippet
- Injected messages excluded from corpus

## Definition of Done

- [ ] `plugins/sir-albert/tools/prompt_corpus.py` exists, all 4 commands work
- [ ] `~/.claude/sir-albert-corpus/` created on first `extract` run
- [ ] `tools/precision_report.py` redirects to `router-eval` (or is removed)
- [ ] pytest for extraction passes (fixture covers injected exclusion + label detection)
- [ ] `router-eval` produces same fire rate as 04b report (within ±1%)
