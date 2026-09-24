# 12 — archive decisions

**Blocked by:** 03 (brainstorm verified), 10
**Spec:** `docs/specs/2026-09-24-w2-core-skills-design.md` §Archive candidates

## Goal

Present the archive table to Gal for decisions, then `git mv` approved skills to `_archive/`.

## Steps

1. **Present archive table** (do not proceed until Gal approves each item):

   | Skill | Recommendation | Reason |
   |---|---|---|
   | `core/sync` | Archive | No live deps; git handled by commit-commands |
   | `agentic/self-reflection` | Archive | No recorded use; retro covers the loop |
   | `dev/claude-handoff` | Archive | Replaced by execute skill |
   | `biz/discovery-lens` | Archive after brainstorm verified | Absorbed into brainstorm |
   | `biz/board-of-advisors` | Archive after brainstorm verified | Panel mode in brainstorm |
   | `biz/devils-advocate` | Archive after brainstorm verified | Attack mode in brainstorm |
   | `biz/zoom-out` | Archive after brainstorm verified | zoom-out mode in brainstorm |
   | `dev/grilling` | Archive after brainstorm verified | grill mode in brainstorm |
   | `dev/grill-with-docs` | Archive after brainstorm verified | grill mode in brainstorm; dep on domain-modeling removed |
   | `dev/domain-modeling` | Archive after brainstorm verified | Only dep was grill-with-docs (also archived) |
   | `packs/gtm/param-audit` | Archive | Absorbed into gtm-gate |
   | `core/decide` | Keep | Live state store (decisions.jsonl) |
   | `core/freeze` | Keep | Live hook (freeze-guard.sh) |
   | `core/retro` | Keep | Live cron (launchd) |
   | `docs/to-prd` | Keep | Used in build sub-loop |
   | `dev/prototype` | Keep | Referenced by build skill |
   | `dev/git-guardrails` | Keep | Referenced by build skill |
   | `dev/github-repo-analyzer` | Keep | Referenced by build skill |

   **CHECKPOINT — WAIT FOR EXPLICIT GAL APPROVAL before step 2. Do not archive anything until each item is confirmed.**

2. For each Gal-approved archive, run:
   ```bash
   mkdir -p plugins/sir-albert/skills/_archive
   git mv plugins/sir-albert/skills/<current-path> plugins/sir-albert/skills/_archive/<skill-name>
   ```
3. Verify: `claude --plugin-dir /Users/galta/Development/sir_albert/plugins -p "list skills"` still shows brainstorm, plan, execute, debug, build, gtm-gate, handoff, resume, create-skill, slack-in-my-voice. Does NOT show archived skills.
4. Confirm plugin.json skill paths: `_archive/` is not included in any `./skills/*` entry.
5. Commit: `chore: archive approved skills (W2 consolidation)`.

## Definition of Done

- [ ] Gal has explicitly approved each archive decision
- [ ] `_archive/` directory contains only approved skills
- [ ] Plugin skill listing excludes all archived skills
- [ ] plugin.json has no path pointing into `_archive/`

## CHECKPOINT

`git mv` is reversible but changes the plugin's invokable skill set immediately. Run the plugin load test (step 3) before committing.
