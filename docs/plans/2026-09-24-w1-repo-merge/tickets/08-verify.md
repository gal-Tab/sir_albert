# 08 — End-to-end verification

**Blocked by:** 07
**Spec:** §7

Run each check and paste its output into `docs/plans/2026-09-24-w1-repo-merge/verify-08-result.md`. Show evidence; don't just say it passed.

## Checks
1. **KB tests:** `cd plugins/kb && python3 -m pytest -q`: all pass.
2. **Skills load:** `claude -p "List every available skill whose name starts with sir-albert: or kb: or llm-wiki-agent:. One per line, names only."` → sir-albert:* (37 expected after removing `learnings` and moving `kw-compound`), kb:* (wiki-query, learn-recall, learn-research, kw-compound, plus the commands wiki-init, wiki-compile, learn-capture), **zero** llm-wiki-agent:*.
3. **Identity imports:** `claude -p "What are Gal's pronouns and role? Answer from context only."` → he/him, marketing-ops/GTM/data at monday.com.
4. **Hooks fire:**
   - guard: `claude -p "run: git reset --hard HEAD"` in a throwaway repo under `/tmp` → blocked by guard.sh
   - kb hooks: start a session in `/Users/galta/Development/sir_albert` → `wiki-status` output appears
   - session-record: after a `claude -p` run, a new entry appears where `session-record.sh` writes (check the script for the path)
   - freeze-guard and validate-skill: run the script directly with sample stdin JSON (see the scripts) and expect exit 0 for allowed input
5. **Stale names gate:** `grep -rn 'llm-wiki-agent\|kb-query\|kb-compile' --exclude-dir=.git --exclude-dir=.memory-bank --exclude-dir=docs /Users/galta/Development/sir_albert ~/.claude/settings.json ~/.claude/CLAUDE.md` → empty.
6. **Query works:** `claude -p "/kb:wiki-query what does the wiki say about anomaly detection failure shapes?"` from the sir_albert root → an answer citing `wiki/` pages.
7. **Launchd:** `launchctl print gui/$(id -u)/com.sir-albert.retro | grep -E 'state|path'` shows the new path.
8. **Edit loop:** make a trivial edit to a skill description, apply the loop from spike 02, and confirm the change is visible in a new session. Then revert the edit.

## DOD
- [ ] All 8 checks pass with evidence in the result file
- [ ] Commit the result file on `w1/repo-merge`; then **ask the coordinator** before pushing or opening the PR
