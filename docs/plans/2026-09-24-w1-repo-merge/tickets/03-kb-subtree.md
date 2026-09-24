# 03 — Bring agent_knowledgebase into plugins/kb with its history

**Blocked by:** 01
**Spec:** §2

## Steps
1. `git -C /Users/galta/Development/agent_knowledgebase status --short` must be empty. Then `git -C … checkout main && git -C … pull --ff-only`. It was 5 commits behind; confirm `git log -1` is `9ffda12 chore(naming): align commands into wiki-* / learn-* families (#11)` or newer.
2. In sir_albert on `w1/repo-merge`: `git subtree add --prefix=plugins/kb /Users/galta/Development/agent_knowledgebase main` (no `--squash`, so history is kept).
3. `git log --oneline -- plugins/kb | head` shows the KB commits.
4. Tests: `cd plugins/kb && python3 -m pytest -q`. Expect about 181+ tests passing (the count may have grown). If anything fails, compare with the same run in the original repo before touching it; failures that already exist there are not caused by W1, so report them to the coordinator.
5. Ensure `plugins/kb/.pytest_cache` and `__pycache__` are git-ignored (append to the root `.gitignore` if needed) and commit.

## DOD
- [ ] `plugins/kb/` exists with commands, skills, hooks, lib, tools, templates, tests
- [ ] KB history visible under `plugins/kb`
- [ ] pytest in `plugins/kb` passes, or failures match the original repo exactly
