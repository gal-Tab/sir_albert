# 02 — label-capture

**Blocked by:** 01
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P1 — Router scorecard / Labeled set`

## Goal
Define the `labeled-set.jsonl` row schema, add a `validate-labels` subcommand to `prompt_corpus.py` that rejects malformed or incomplete label files, and implement `--merge` on the `label-set` subcommand so a partially-labelled file can be topped up without losing work.

## Steps

1. Write failing test `plugins/sir-albert/tests/eval/test_label_capture.py`:
   - Fixture A: fully-labelled JSONL (all rows have `label` in `VALID_LABELS`, `labeled_by` non-null, `labeled_at` non-null) → validator exits 0, prints `ok: 15/15 labelled`
   - Fixture B: JSONL where 3 rows still have `"label": null` → validator exits 1, prints `remaining=3 / total=15`
   - Fixture C: malformed row (missing `_hash`) → validator exits 1, prints `malformed row at index 2: missing _hash`
   - Fixture D: invalid label value `"label": "grill"` → validator exits 1, prints `invalid label 'grill' at hash=...`

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_label_capture.py -q` — Expected: FAIL

2. Add `VALID_LABELS` constant to `plugins/sir-albert/tools/prompt_corpus.py` (after `EVAL_DIR`):
   ```python
   VALID_LABELS = {
       "brainstorm", "debug", "plan", "execute", "build",
       "handoff", "resume", "slack", "linkedin-hebrew",
       "none", "ambiguous"
   }
   ```

3. Add `cmd_validate_labels(args)` to `plugins/sir-albert/tools/prompt_corpus.py` and wire as `validate-labels`:
   - Load `--file` arg (default: `str(EVAL_DIR / "labeled-set.jsonl")`)
   - For each row: verify `_hash` present; verify `text` present; verify `label` is in `VALID_LABELS` or is `None`/absent
   - Count null labels; track malformed rows (missing required keys or invalid label value)
   - If any malformed: print `malformed row at index N: <reason>` and `sys.exit(1)`
   - If null labels remain: print `remaining=N / total=T` and `sys.exit(1)`
   - If all labelled: print `ok: T/T labelled` and `sys.exit(0)`

4. Add `--merge` flag to the existing `label-set` subcommand parser in `main()`:
   - In `cmd_label_set`: if `--merge` and `EVAL_DIR / "labeled-set.jsonl"` exists, load existing rows into a dict keyed by `_hash`; for any existing row with a non-null `label`, preserve `label`, `labeled_by`, `labeled_at` in the new output
   - Checklist skips already-labelled rows (prints count: `already labelled=K, remaining=N`)

5. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_label_capture.py -q` — Expected: PASS

6. Integration check: Run `validate-labels` on the stub from ticket 01:
   `/usr/local/bin/python3.13 plugins/sir-albert/tools/prompt_corpus.py validate-labels` — Expected: exits 1 with `remaining=N / total=T` (all null, as expected pre-labelling)

## Definition of Done
- [ ] `VALID_LABELS` set defined in `prompt_corpus.py` with all 11 valid values
- [ ] `validate-labels` subcommand exits 0 on complete file, 1 on incomplete or malformed
- [ ] Prints `remaining=N / total=T` on partial file; `malformed row at index N` on bad schema
- [ ] `--merge` flag on `label-set` preserves existing non-null labels on re-run
- [ ] Tests pass: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_label_capture.py -q`

## Review corrections (binding, supersede the steps above where they conflict)

1. **`VALID_LABELS` is derived, not hardcoded:** `{intent for intent, _, _ in _compile_patterns()} | {"none", "ambiguous"}`. The hardcoded set was missing `attack`, `grill`, `zoom-out`, `design` and `slack-hebrew`. Fixture D's "grill is invalid" is wrong: use `"label": "not-a-route"` instead.
2. **Add an `import-labels` subcommand.** Without it, Gal would have to hand-edit JSONL for 142 rows. It parses `labeled-set-checklist.md` (`### [n] hash=… slice=…` headers plus `**Label:** …` lines) and writes the labels into `labeled-set.jsonl`:
   - Shorthand `y` → `predicted_route` for `router_match`, and → `none` for `negative_control`. `y` on a `task_initiating` row is rejected, since there is nothing to agree with.
   - Blank or `___` → stays null, which keeps the import resumable. Re-importing never clears an existing label.
   - Sets `labeled_by="gal"` and `labeled_at=<UTC ISO>` on rows it fills.
   - Unknown label → exit 1 and list the offending hashes. The file is written only if every filled label is valid (no partial writes).
   - Tests: shorthand mapping per slice, resumability (import twice keeps labels), invalid label blocks the write.
3. The label-set `--merge` behaviour is kept, but `import-labels` is the primary path Gal uses.
