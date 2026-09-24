# W1 — Repo merge: sir_albert + agent_knowledgebase → one repo, two plugins

**Status:** draft for review · **Date:** 2026-09-24 · **Owner:** Gal

## Context

Part of a 4-workstream restructure to make the setup simpler, portable and consistent, and to replace the `superpowers` plugin:

| # | Workstream | Depends on |
|---|---|---|
| **W1** | **Repo merge** (this spec) | — |
| W2 | Core skills: `brainstorm` (modes), `plan`, `execute`, `debug`, `build`, lean `create-skill`; archive unused | W1 |
| W3 | Router hooks (`SessionStart` + `UserPromptSubmit`), thin versioned CLAUDE.md, `/sir-albert:init` | W2 |
| W4 | Side-by-side eval vs superpowers → uninstall only if new setup wins or ties | W3 |

Decisions already made: one repo / two plugins · KB plugin renamed `kb` · repos stay on `gal-Tab` for now (dapulse migration later) · copy 3 Pocock skills in W2 · every skill created or edited goes through `/sir-albert:create-skill` · builds run in a Sonnet 5 subagent · docs layout (defined in W2 as `os/rules/docs-layout.md`): `docs/specs/YYYY-MM-DD-<topic>.md`, `docs/plans/YYYY-MM-DD-<topic>.html` + `docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md`.

## Goal

One repo (`sir_albert`), one marketplace, two plugins: `sir-albert` and `kb`. One place to edit, and the live install is the repo itself: no symlinks, no second marketplace, no local-vs-remote drift.

## Non-goals

- Skill consolidation, new skills, router hooks, CLAUDE.md rewrite (W2–W3).
- Moving to the dapulse org.
- Changing KB engine behavior.

## Target layout

```
sir_albert/
  .claude-plugin/marketplace.json   # lists plugins/sir-albert + plugins/kb
  plugins/
    sir-albert/                     # name unchanged → sir-albert:* refs keep working
      .claude-plugin/plugin.json
      skills/  hooks/  os/  tools/  shared/
    kb/                             # ex agent_knowledgebase, history preserved
      .claude-plugin/plugin.json    # name: "kb"
      commands/ skills/ hooks/ lib/ tools/ templates/ tests/
  raw/  wiki/  wiki-schema.md       # KB *data* for this repo — not plugin code
  docs/  .memory-bank/  README.md  REGISTRY.md
```

## Steps

### 1. Pre-flight clean-up
- Open a PR for the 2 commits on `discovery-lens-voice-agents` (voice agents + gal-va journal spec) → merge to `main`. Update local `main`.
- Move the uncommitted `os/PREAMBLE.md` + `os/identity/HEARTBEAT.md` edits to a new branch `os/preamble-heartbeat` off `main`.
- Untracked files: commit `.memory-bank/HANDOFF-*`, `recon-inventory.md` and `docs/superpowers/*` (moved to `docs/specs|plans/`). Delete `skills/packs/gtm/ga4-regex.zip` after confirming the live dir has the same content. Leave `hooks/hooks.json` and `hooks/validate-skill.py` untracked for W3.
- Work on branch `w1/repo-merge` off the updated `main`.

### 2. Bring in the KB with its history
- `git -C agent_knowledgebase pull --ff-only` (currently 5 behind, clean tree).
- In sir_albert: `git subtree add --prefix=plugins/kb <agent_knowledgebase> main`.

### 3. Move sir-albert into `plugins/sir-albert/`
- `git mv` `.claude-plugin/plugin.json`, `skills/`, `hooks/`, `os/`, `tools/`, `shared/` → `plugins/sir-albert/`.
- Fix relative paths in `plugin.json`; drop the dead `./skills/knowledge` entry.
- Root `.claude-plugin/marketplace.json` lists both plugins.
- Update absolute-path references (`os/` paths in `~/.claude/CLAUDE.md` `@`-imports, launchd `.plist` files, cron scripts, PREAMBLE boot lines) — found by grep, fixed in the same commit.

### 4. Rename the KB plugin to `kb`
- `plugins/kb/.claude-plugin/plugin.json` name → `kb`; skills become `kb:wiki-query`, `kb:learn-capture`, etc.
- Update every `llm-wiki-agent` reference (grep across repo, `~/.claude/CLAUDE.md`, `~/.claude/settings.json`).

### 5. KB fixes
- `kw-compound` → `plugins/kb/skills/`; replace `kb-query`/`kb-compile` with `wiki-query`/`wiki-compile`.
- Fold `learnings` into `kb:learn-recall` (keep any unique behavior as a section); remove the old skill.

### 6. Install switch (this machine)
Done in one go, with the old state captured first so it can be restored:
1. Back up `~/.claude/settings.json` and note the symlink target.
2. Remove the `~/.claude/skills/sir-albert` symlink.
3. `claude plugin marketplace add /Users/galta/Development/sir_albert`; install `sir-albert` and `kb`.
4. Uninstall `llm-wiki-agent` and remove the `gal-Tab/agent_knowledgebase` marketplace.
5. Update the hook paths in `settings.json` that point into `sir_albert/hooks/` → `plugins/sir-albert/hooks/`.

### 7. Verify (all must pass before the old repo is touched)
- `pytest` passes in `plugins/kb` (181 tests).
- A fresh session lists the `sir-albert:*` and `kb:*` skills, and no `llm-wiki-agent:*`.
- Hooks fire: guard, freeze-guard, session-record, kb `wiki-status` / `learn-surface` / `learn-capture`.
- `grep -rn 'llm-wiki-agent\|kb-query\|kb-compile'` in the repo and `~/.claude` returns nothing (except history docs).
- `/kb:wiki-query` answers from `wiki/`.

### 8. Retire the old repo
- Push a "moved to sir_albert/plugins/kb" README to `gal-Tab/agent_knowledgebase`. **Ask first** (it's public).
- Archiving it on GitHub is a separate step that needs approval.

## Rollback

Until step 6 everything is local git: drop the `w1/repo-merge` branch. After step 6, restore `settings.json` from the backup, recreate the symlink, and reinstall `llm-wiki-agent` from its marketplace.

## Risks

| Risk | Mitigation |
|---|---|
| Absolute paths to `sir_albert/os|hooks` break silently (launchd, CLAUDE.md imports) | Grep before the move; the verify step checks every hook fires |
| Prefix change `llm-wiki-agent:` → `kb:` misses a reference | Grep gate in step 7 |
| Hooks declared both in the plugin and in `settings.json` fire twice | Step 6 removes the `settings.json` duplicates for the KB hooks; sir-albert hooks move into plugin `hooks.json` in W3 |
| Local-path marketplace behaves differently from GitHub-sourced | Acceptable for now; switch the source to GitHub when moving to dapulse |
