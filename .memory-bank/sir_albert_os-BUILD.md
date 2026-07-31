# sir_albert_os — BUILD ledger

- **Plan (spec):** `/Users/galta/Development/docs/plans/2026-07-30-personal-claude-os.html`
- **Handoff:** `/Users/galta/Development/docs/plans/2026-07-31-sir_albert_os-BUILD-HANDOFF.md`
- **Branch:** `os/foundation` — **local-only**; no push/PR to `gal-Tab` remote without explicit OK (gal-Tab ≠ dapulse/mondaycom org per security policy; dapulse mirror deferred to the 80x distribution tier).
- **Started:** 2026-07-31

## Protocol (per task)
IMPLEMENT (subagent) → SELF-CHECK (run DOD) → adversarial VERIFY subagent → loop max 3 (else STOP+flag) → small per-task commit → update this ledger. No task advances until verify passes.
Reversible-first: `claude plugin enable/disable`, `git mv` on branch; deletes only after the replacement is verified live. guard.sh + ask-before-live stay ON.

## Guardrails
- No `git push` / PR to `gal-Tab` remote without explicit user OK.
- ask-before-live: live-GTM publish, n8n prod deploy, external comms, deletes, **token rotation** → ASK / hand to user.
- `~/.claude/skills/sir-albert` symlinks to this repo → repo edits are **LIVE** in every session. Never break `plugin.json`.

## Status legend: ⬜ todo · 🔄 wip · ✅ done · ⛔ blocked

## M0 · Foundation
- ✅ 0.1 Branch `os/foundation` created; home confirmed (local-only build)
- ✅ 0.2 Reshape repo → Core/Context/Packs (verify PASS: valid JSON, 10 dirs exist, 20 skills intact, no live-load break). Commit b44d8b0.
- 🔄 0.3 RESOLVER.md — one-screen map (writing)

## M5.1 · Security (do early)
- ✅ 5.1a settings.local.json allowlist JWTs → single generic `Bash(claude mcp add:*)` (verify PASS: 0 secrets, valid JSON, minimal diff, backup `settings.local.json.bak-20260731` intact). Bonus: also caught an n8n `N8N_API_KEY` the recon missed.
- ⛔ 5.1b mcp.json `authorization` header + token ROTATION — LIVE AUTH; blocked on user OK (ask-before-live). Env-var swap feasible (`${BIGBRAIN_MCP_TOKEN}`), but needs env set before Claude launch + restart → can't verify in-session. Runbook to be presented at M0/M5-early status.

## M5.0 / M5.2 · Consolidation (greenlit)
- ⬜ 5.0 Plugin portfolio: 3 disabled (prior), wrap-list routed from RESOLVER, protected untouched
- ⬜ 5.2 Fold loose monday skills into sir_albert; rename brainstorm-council→discovery-lens; delete byte-identical dup; reconcile monday-mops-triage

## M1 · Session continuity
- ⬜ 1.1 Install/study session-insights; decide wrap vs reimplement
- ⬜ 1.2 /handoff — doc + paste-able restart prompt (generalize gtm-handoff)
- ⬜ 1.3 /resume + SessionStart nudge (cooperate with token-optimizer)
- ⬜ 1.4 /sync — post-merge git reconciliation (safe `-d` only)

## M2 · Personal-context (OKF format)
- ⬜ 2.1 identity USER/SOUL/HEARTBEAT + CLAUDE.md @imports; voice skills read USER.md
- ⬜ 2.2 rules/gtm-naming.md + pre-apply gate
- ⬜ 2.3 rules/consent-map.md (OKF frontmatter: sources/stale_after/status)
- ⬜ 2.4 rules/output-style.md + PREAMBLE.md (anti-slop + use-the-skill contract)

## M3 · Domain packs
- ⬜ 3.1 GTM pack + /param-audit (maintain-mode)
- ⬜ 3.2 Building pack — named sub-loops + data-review + OS-vs-team boundary doc
- ⬜ 3.3 Automation pack + /n8n-triage + HubSpot API-safety check
- ⬜ 3.4 Attested metrics — z2h looks + OKF mirrors + attester (drift fails)

## M4 · Core machinery
- ⬜ 4.1 /decide + decisions.jsonl (auto-apply settled decisions)
- ⬜ 4.2 learnings loop auto-load + OKF canonicalization barrier
- ⬜ 4.3 /freeze on top of guard.sh
- ⬜ 4.4 Discover front door (discovery-lens + advisors + grilling + zoom-out…)
- ⬜ 4.5 retro loop + SessionEnd hook + historical backfill PR
- ⬜ 4.6 dream cycle (NanoClaw; HEARTBEAT-driven; proposes via PR)
- ⬜ 4.7 autonomy.md — ask-vs-act tiers + parallelism/cost cap

## M5 · remaining
- ⬜ 5.3 Inherit llm-wiki from agent_knowledgebase main; delete kb-query; align consumers (open_claw, Investment-agent)
- ⬜ 5.4 Repo clutter (dedup cookbook, archive _old, empty dirs) + usage-insights monthly

## M6 · Verify end-to-end
- ⬜ 6.1 Three-mode + continuity + memory smoke test (all 5 pass; DoD checkable)

## Log (append-only, newest last)
- 2026-07-31 · M0.1 ✅ — branch `os/foundation` created from `main` (was clean). Home = gal-Tab/sir_albert, local-only build confirmed. Verify: self (trivial — `git branch --show-current` = os/foundation). Recon subagent dispatched → `.memory-bank/recon-inventory.md`.
- 2026-07-31 · M5.1a ✅ — removed 3 token-bearing `claude mcp add` allowlist entries → 1 generic pattern in `Development/.claude/settings.local.json`. Independent adversarial verify PASS (0 `eyJ`/0 `authorization:`, minimal 4-line diff, backup reversible). Commit: settings.local.json is outside the repo (not committed); backup is the revert path.
- 2026-07-31 · M0.2 committed (b44d8b0) — os/ + skills/core + skills/packs scaffold, plugin.json +5 dirs, .gitignore noise. Verify dispatched (pending).
