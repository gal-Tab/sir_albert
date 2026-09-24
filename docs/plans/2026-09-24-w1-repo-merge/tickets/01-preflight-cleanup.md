# 01 — Pre-flight clean-up

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w1-repo-merge-design.md` §1
**Repo:** `/Users/galta/Development/sir_albert`

## Context
Current branch `discovery-lens-voice-agents` is 2 commits ahead of `origin/main` (voice agents + gal-va journal spec). Local `main` is stale. Uncommitted: `os/PREAMBLE.md`, `os/identity/HEARTBEAT.md`. Untracked: `.memory-bank/HANDOFF-2026-09-22.md`, `.memory-bank/HANDOFF-2026-09-24.md`, `.memory-bank/recon-inventory.md`, `docs/plans/2026-05-13-demo-dark-mode-toggle.html`, `docs/superpowers/{plans,specs}/*`, `docs/specs/2026-09-24-w1-repo-merge-design.md`, `docs/plans/2026-09-24-w1-repo-merge*`, `hooks/hooks.json`, `hooks/validate-skill.py`, `skills/packs/gtm/ga4-regex.zip`.

## Steps
1. `git stash push -m w1-os-edits -- os/PREAMBLE.md os/identity/HEARTBEAT.md`
2. `git push` the current branch (plain push, no force). **CHECKPOINT — ask the coordinator before pushing.**
3. `gh pr create --base main --head discovery-lens-voice-agents` with a short why/what body ending with the 🤖 attribution line. **CHECKPOINT — ask before merging.** Once approved: `gh pr merge --merge`.
4. `git checkout main && git pull --ff-only`.
5. `git checkout -b os/preamble-heartbeat && git stash pop && git commit -am "os: PREAMBLE + HEARTBEAT edits (2026-09-24)"`. Do not push. Then `git checkout main`.
6. `git checkout -b w1/repo-merge`.
7. Untracked triage on `w1/repo-merge`:
   - `git mv` is not possible for untracked files: plain `mv docs/superpowers/specs/* docs/specs/` and `mv docs/superpowers/plans/* docs/plans/`, then remove the empty `docs/superpowers/` dirs (`rmdir`).
   - `unzip -l skills/packs/gtm/ga4-regex.zip` and compare with `skills/packs/gtm/ga4-regex/`. If the contents match, `rm` the zip. If not, stop and ask.
   - Leave `hooks/hooks.json` and `hooks/validate-skill.py` untracked (W3).
8. `git add .memory-bank docs && git commit -m "chore: track handoffs, move superpowers docs into docs/specs|plans, add W1 spec + plan"`.

## DOD
- [ ] PR merged; local `main` equals `origin/main`
- [ ] `os/preamble-heartbeat` exists locally with the 2 edits
- [ ] On `w1/repo-merge`, `git status --short` shows only `hooks/hooks.json` and `hooks/validate-skill.py`
- [ ] `docs/superpowers/` no longer exists
