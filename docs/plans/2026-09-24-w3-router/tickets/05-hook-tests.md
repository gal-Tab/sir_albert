# 05 — hook tests (pytest)

**Blocked by:** 03, 04
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 3

## Goal

Write pytest tests for both hooks. Mirror the `plugins/kb/tests/` structure. Tests call the hook scripts as subprocesses (same pattern as `test_learn_capture_hook_bash.py` in kb).

## Steps

1. Create directory structure:
   ```
   plugins/sir-albert/tests/
     __init__.py
     conftest.py
     fixtures/
       project_gtm/         (touch apply-deploy.ts)
       project_n8n/         (touch workflow.json)
       project_kb/          (mkdir raw wiki)
       project_plain/       (empty — no signals)
   ```
2. Write `conftest.py`: fixtures that return tmp dirs seeded from `fixtures/`.
3. Write `test_session_start.py`:
   - For each project fixture: run `bash session-start.sh` with `CLAUDE_PLUGIN_ROOT` set and `CWD` set to the fixture dir
   - Assert: JSON parses, `additionalContext` present, correct pack(s) appear in output, char count ≤ 800
   - `project_plain`: assert `(none detected)` in output
4. Write `test_prompt_router.py`:
   - For each row in `router-data.json keyword_patterns`: feed a representative prompt, assert the nudge appears
   - 5 no-match cases: `"what time is it"`, `"show me the diff"`, `"מה שלומך"`, `"list files"`, `"git status"` — assert empty stdout
5. Run: `cd plugins/sir-albert && python3 -m pytest tests/ -v`

## Definition of Done

- [ ] All test files present (`__init__.py`, `conftest.py`, `test_session_start.py`, `test_prompt_router.py`)
- [ ] All 4 project fixtures exist
- [ ] `pytest tests/ -v` passes with 0 failures
- [ ] At least 1 no-match test case per each of the 5 no-match prompts
- [ ] Hebrew prompt test case passes (UTF-8)
