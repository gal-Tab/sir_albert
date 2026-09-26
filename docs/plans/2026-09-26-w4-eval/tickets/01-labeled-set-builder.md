# 01 — labeled-set-builder

**Blocked by:** —
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P1 — Router scorecard / Labeled set`

## Goal
Add a `label-set` subcommand to `plugins/sir-albert/tools/prompt_corpus.py` that emits a human-labelable checklist and a machine-readable stub covering all router matches (count computed at runtime — measured at 102 on 2026-09-26), 30 random task-initiating prompts, and 10 negative controls — reusing `is_organic`, `_compile_patterns`, and `_route` without reimplementing routing.

## Steps

1. Write failing test `plugins/sir-albert/tests/eval/__init__.py` (empty) and `plugins/sir-albert/tests/eval/test_label_set.py`:
   - Build a 20-row in-memory fixture JSONL: 5 rows that route (brainstorm/plan/handoff), 5 task-initiating rows with `preceding_turns=[]`, 5 ack-style rows with non-empty `preceding_turns` and text < 40 chars, 5 long-prompt rows
   - Patch `CORPUS_FILE` to the fixture path via monkeypatch
   - Assert subcommand exits 0 and creates `labeled-set.jsonl` and `labeled-set-checklist.md` in the eval dir
   - Assert every row in `labeled-set.jsonl` is valid JSON with keys `_hash`, `text`, `predicted_route`, `slice`, `label` (null), `labeled_by` (null), `labeled_at` (null)
   - Assert sections `## Router matches`, `## Task-initiating`, `## Negative controls` appear in the checklist

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_label_set.py -q` — Expected: FAIL (ImportError or AttributeError — `label-set` not yet implemented)

2. Add `EVAL_DIR` constant to `plugins/sir-albert/tools/prompt_corpus.py` after the existing `REPORT_DIR` line:
   ```python
   EVAL_DIR = REPO_ROOT / "docs" / "plans" / "2026-09-26-w4-eval"
   ```

3. Add stub `cmd_label_set(args)` function to `plugins/sir-albert/tools/prompt_corpus.py` after `cmd_router_eval`, then wire it into `sub.add_parser("label-set")` and `main()`.

4. Implement router-match slice in `cmd_label_set`:
   - Load all rows from `CORPUS_FILE` via `load_jsonl(CORPUS_FILE)`
   - `patterns = _compile_patterns()`
   - For each row where `is_organic(row["text"])` is True, call `route = _route(row["text"], patterns)`; collect rows where `route is not None`, deduplicated by `_hash`

5. Implement task-initiating slice in `cmd_label_set`:
   - Filter corpus rows where `row.get("preceding_turns", []) == []` and `len(row["text"]) > 40` and `_hash` not already in router-match set
   - Filter out rows where `row["text"]` contains a path reference: `re.search(r'[/\\][a-zA-Z0-9_.-]+\.[a-zA-Z]{2,5}', row["text"])`
   - `random.seed(42)` then `random.sample(pool, min(30, len(pool)))`

6. Implement negative-control slice in `cmd_label_set`:
   - Filter corpus rows where `len(row.get("preceding_turns", [])) > 0` and `len(row["text"].strip()) < 50`
   - **Explicitly include known false-fire traps:** after random sampling, ensure at least one row matching `re.search(r'^(continue|resume|yes|ok|go|1|done)\b', text, re.IGNORECASE)` is present, and at least one matching `re.search(r'yes open pr|open pr|merge', text, re.IGNORECASE)` if available — these are the exact patterns the `build`/`resume` dead-route diagnosis identified as ambiguous. If not enough organic samples exist, supplement with synthetic controls noted as `synthetic: true` in the stub.
   - `random.seed(99)` then `random.sample(pool, min(10, len(pool)))`

7. Write human-labelable checklist to `docs/plans/2026-09-26-w4-eval/labeled-set-checklist.md`:
   - Section `## Router matches (binary: yes this should route / no + correct route if wrong)`
   - Section `## Task-initiating (label: one of 10 route names | none | ambiguous)`
   - Section `## Negative controls (binary: should NOT fire)`
   - Each entry: `### [n] hash={hash} slice={slice}\n> {text[:200]}\n**Label:** ___  **Notes:** ___`
   - Print count summary: `router_match=N task_initiating=M negative_control=10`

8. Write machine-readable stub to `docs/plans/2026-09-26-w4-eval/labeled-set.jsonl` (overwrites if exists):
   - One JSON line per row: `{"_hash":"...","text":"...","predicted_route":"...|null","slice":"router_match|task_initiating|negative_control","label":null,"labeled_by":null,"labeled_at":null}`

9. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_label_set.py -q` — Expected: PASS

10. Smoke run: `/usr/local/bin/python3.13 plugins/sir-albert/tools/prompt_corpus.py label-set` — Expected: prints `router_match=102 task_initiating=30 negative_control=10` (counts may vary), files created at `docs/plans/2026-09-26-w4-eval/`

## Definition of Done
- [ ] `label-set` subcommand added to `prompt_corpus.py` and wired into CLI
- [ ] `docs/plans/2026-09-26-w4-eval/labeled-set.jsonl` emitted with all `label: null`; all router-match rows have `predicted_route` set (not null)
- [ ] `docs/plans/2026-09-26-w4-eval/labeled-set-checklist.md` emitted with three labelled sections
- [ ] Path-reference exclusion filter applied to task-initiating slice
- [ ] Random seeds fixed (42 and 99) so output is reproducible
- [ ] Test passes: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_label_set.py -q`

⚠️ Risk: editing `plugins/sir-albert/tools/prompt_corpus.py` is immediately live in every new session via the `--plugin-dir` alias. Add the new subcommand after existing code; do not modify existing functions.

## Review corrections (binding, supersede the steps above where they conflict)

1. **Never destroy labels.** Step 8's "overwrites if exists" is wrong. If `labeled-set.jsonl` exists and any row has a non-null `label`, `label-set` must refuse with exit 1: `refusing to overwrite N existing labels; use --merge`. Test: create a stub with one label, re-run and assert the label survives and the exit code is 1.
2. **Checklist entries show up to 400 chars** (not 200), with `…` when truncated. Router-match entries also show `predicted: <route>` so the binary call is one glance.
3. **Checklist label line uses shorthands** that ticket 02's importer understands:
   - Router matches: `**Label:** y` means the predicted route is right. Otherwise write the correct route name, `none`, or `ambiguous`.
   - Task-initiating: a route name, `none`, or `ambiguous`.
   - Negative controls: `**Label:** y` means it should not route (`none`). Otherwise write the route it *should* take.
   - Put the shorthand legend at the top of the checklist.
4. **Measured pool sizes (2026-09-26):** task-initiating pool = 59 (≥30 ✅), negative-control pool = 582, router matches = 102, duplicate `_hash` = 0. Put these in the smoke-run expected output.
