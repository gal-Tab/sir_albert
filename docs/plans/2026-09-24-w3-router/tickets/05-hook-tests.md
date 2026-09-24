# 05 — hook tests (pytest)

**Blocked by:** 03, 04
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 3

## Goal

Write pytest tests for both Python hooks. Mirror `plugins/kb/tests/` structure. Use `subprocess.run` to invoke scripts (same pattern as `test_learn_capture_hook_bash.py` in kb).

## Steps

1. Create directory structure:
   ```
   plugins/sir-albert/tests/
     __init__.py
     conftest.py               ← fixtures returning tmp dirs seeded from fixtures/
     fixtures/
       project_gtm/            (touch apply-deploy.ts)
       project_n8n/            (touch workflow.json)
       project_kb/             (mkdir raw wiki)
       project_plain/          (empty)
   test_session_start.py
   test_prompt_router.py
   ```

2. `test_session_start.py` — for each project fixture:
   - Run `session_start.py` with `CLAUDE_PLUGIN_ROOT` set, `CWD` set to fixture copy
   - Assert: JSON parses, `additionalContext` present
   - Assert: correct pack(s) in output (`gtm`, `n8n`, `kb`, or `(none detected)`)
   - Assert: `len(additionalContext) <= 800`

3. `test_prompt_router.py` — two classes:
   - `TestMatches`: one test per intent row in `router_data.json`; use a representative phrase per intent; assert nudge appears in output
   - `TestNoMatch`: required false-positive phrases → assert empty stdout:
     - `"execute this SQL"`
     - `"publish the GTM container"`
     - `"challenge accepted"`
     - `"I'm feeling broken today"`
     - `"architect of the building"`
     - `"what time is it"`
     - `"show me the diff"`
     - `"git status"`

4. Run: `cd plugins/sir-albert && python3 -m pytest tests/ -v`

## Definition of Done

- [ ] All test files and fixtures present
- [ ] `pytest tests/ -v` — 0 failures
- [ ] All 8 false-positive test cases present and passing
- [ ] Hebrew match test case present (at least 1, after ticket 04a)
- [ ] Char-count assertion present in `test_session_start.py`
