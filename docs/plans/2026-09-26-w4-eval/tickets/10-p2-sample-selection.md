# 10 — p2-sample-selection

**Blocked by:** 03
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Sample`

## Goal
Add a `sample-p2` subcommand to `prompt_corpus.py` that selects N=15 from the labelled set — 5 where B routes and the label agrees, 5 where label says route but B is silent, 5 `none`/`ambiguous` — excluding prompts with file/path references, and writes `docs/plans/2026-09-26-w4-eval/sample.jsonl`.

## Steps

1. Write failing test `plugins/sir-albert/tests/eval/test_p2_sample.py`:
   - Fixture: 30-row labelled JSONL with known slices and labels (10 router_match with label==predicted, 10 task_initiating with non-null label, 10 none/ambiguous)
   - Assert `sample-p2` selects exactly 15 rows: 5 router_match correct, 5 task_initiating mismatch (B silent), 5 none/ambiguous
   - Assert no selected row contains a file path reference (regex `r'[/\\][a-zA-Z0-9_.-]+\.[a-zA-Z]{2,5}'`)
   - Assert `sample.jsonl` has `slice` and `label` fields preserved plus a `p2_slice` field: `"happy_path"`, `"b_silent"`, or `"control"`

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_p2_sample.py -q` — Expected: FAIL

2. Add `cmd_sample_p2(args)` to `plugins/sir-albert/tools/prompt_corpus.py` and wire as `sample-p2`:
   - Load `--file` (default `EVAL_DIR / "labeled-set.jsonl"`)
   - Define path-exclusion filter: `re.search(r'[/\\][a-zA-Z0-9_.-]+\.[a-zA-Z]{2,5}', text)` → exclude

3. Implement happy-path slice (5 rows) in `cmd_sample_p2`:
   - Filter: `slice == "router_match"` AND `label == predicted_route` AND not path-containing
   - `random.seed(7)` then `random.sample(pool, min(5, len(pool)))`
   - Tag: `"p2_slice": "happy_path"`

4. Implement B-silent slice (5 rows) in `cmd_sample_p2`:
   - `patterns = _compile_patterns()`
   - Filter: `slice == "task_initiating"` AND `label not in ("none","ambiguous",None)` AND `_route(text, patterns) is None` AND not path-containing
   - (These are prompts Gal labelled as needing a route but the router fires nothing — B's known weakness)
   - `random.seed(8)` then `random.sample(pool, min(5, len(pool)))`
   - Tag: `"p2_slice": "b_silent"`

5. Implement control slice (5 rows) in `cmd_sample_p2`:
   - Filter: `label in ("none","ambiguous")` AND not path-containing
   - `random.seed(9)` then `random.sample(pool, min(5, len(pool)))`
   - Tag: `"p2_slice": "control"`

6. Write `docs/plans/2026-09-26-w4-eval/sample.jsonl` (15 rows total).
   - Print summary: `sample: happy_path=5 b_silent=5 control=5 path_excluded=N`
   - Guard: if any slice has fewer than 5 candidates, print `WARN: happy_path slice only N candidates` and proceed with what's available (do not fail — Gal decides whether to relabel)

7. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_p2_sample.py -q` — Expected: PASS

8. Smoke run: `/usr/local/bin/python3.13 plugins/sir-albert/tools/prompt_corpus.py sample-p2` — Expected: `sample.jsonl` created with ≤15 rows, summary printed

## Definition of Done
- [ ] `sample-p2` subcommand writes `docs/plans/2026-09-26-w4-eval/sample.jsonl` with ≤15 rows
- [ ] Each row has `p2_slice` field: `"happy_path"` | `"b_silent"` | `"control"`
- [ ] Path-exclusion filter applied; exclusion count reported
- [ ] Random seeds fixed (7, 8, 9) for reproducibility
- [ ] Warns but does not fail if a slice has fewer than 5 candidates
- [ ] Tests pass: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_p2_sample.py -q`
