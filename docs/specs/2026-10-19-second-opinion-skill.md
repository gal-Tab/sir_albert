---
status: approved
date: 2026-10-19
owner: Gal
sources:
  - "`codex --version` / `codex login status` 2026-10-19: codex-cli 0.159.2, 'Logged in using ChatGPT'"
  - "`codex doctor` 2026-10-19: wrapper ~/.axcli/bin/codex -> axcli spawn-codex, default provider axcli, auth via AXCLI_CODEX_KEY; real binary /opt/homebrew/bin/codex (brew cask)"
  - "smoke tests 2026-10-19: wrapper run shows 'provider: axcli'; direct /opt/homebrew/bin/codex run uses ChatGPT login (enterprise-managed requirements warning)"
  - os/rules/autonomy.md (AUTO vs ASK tiers)
---

# second-opinion skill — ask another model (Codex/GPT) to look at something

## Problem (needs approval)
Gal wants a cheap, repeatable way to get a second model's view on a plan, a diff, or an open question, using his ChatGPT subscription. Today nothing in sir_albert routes to a non-Claude model, so "ask GPT to look at this" is ad-hoc.

## Setup status (no install needed)
| Item | State |
|---|---|
| Codex CLI | Installed (brew cask, 0.159.2), `/opt/homebrew/bin/codex` |
| Login | ChatGPT login stored in `~/.codex/auth.json`, global, persists across sessions |
| Two paths | **Wrapper** `~/.axcli/bin/codex` (first on PATH) routes via axcli gateway provider, billed against axcli/company budget. **Direct** `/opt/homebrew/bin/codex` uses the ChatGPT login. |
| Decision | Skill calls the **direct** binary by absolute path so it uses Gal's ChatGPT subscription, not the axcli gateway. (Overrides the "keep wrapper" pick, made before the billing difference was known.) |
| Known noise | `codex doctor` flags CrowdStrike exclusions (unverified) and update 0.163.0 available. Neither blocks. |

## Skill: `core/second-opinion`
**Triggers:** "second opinion", "ask codex", "ask GPT", "have another model look at this", "review this plan with codex", "sanity check with another model".

**Modes**
| Mode | Command shape |
|---|---|
| plan / spec / doc review | `/opt/homebrew/bin/codex exec -s read-only --ephemeral -C <dir> -o <out> -` (prompt on stdin: files named by Gal + a "find holes, rank by severity" frame) |
| diff / code review | `/opt/homebrew/bin/codex exec review --uncommitted` or `--base <branch>` / `--commit <sha>` |
| open question | same as plan review with free-form prompt |

**Rules**
- Always `read-only` sandbox + `--ephemeral`. Codex never edits files. This keeps it AUTO under `autonomy.md`.
- Send only the files or text Gal names. State up front what leaves the machine. ASK first when content could hold secrets, customer or HubSpot data.
- Output is labeled "Codex/GPT says", followed by Claude's own agree/disagree per point. Never a raw pass-through.
- Prompt goes on stdin (long prompts, per `reference_claude-headless-cli-gotchas`). Capture the final message with `-o`.
- Fails loudly if `codex login status` is not "Logged in using ChatGPT" and tells Gal to run `! /opt/homebrew/bin/codex login`.

## Model router
Source of truth is a small table in the skill (`references/models.md`), keyed by role, not by model name:

| Role | Model | Effort | Used for |
|---|---|---|---|
| consult (default) | `gpt-6.1-sol` | `high` | plan review, second opinion, open questions |
| deep | `gpt-6.1-sol` | `xhigh` | Gal says "deep" / architectural review |
| quick | `gpt-6-luna` | `medium` | cheap sanity check, "quick look" |

Invoked as `-m <model> -c model_reasoning_effort="<effort>"`.

**Keeping up with models (no manual tracking)**
- Codex ships its own live catalog: `codex debug models` (JSON: slug, visibility, supported efforts). Seen 2026-10-19: 6.1-sol, 6-sol, 6-astra, 6-luna, 5.6-sol/terra/luna.
- Pre-flight in the skill: check the router's slug exists with `visibility: list` and the effort is in `supported_reasoning_levels`. If not, say so, fall back to the newest `*-sol` in the catalog, and tell Gal which model actually ran.
- Drift check: compare the catalog slugs to the table. Any new slug = one-line note "new model X available, router unchanged".
- Update the table only when Gal says so. Changing the table counts as a skill edit, so it goes through `create-skill`.
- Codex CLI itself is behind (0.159.2, 0.163.0 available). Catalog is served by the account, so models appear regardless. Update only if a model needs a newer client.

## Build
Only via `/sir-albert:create-skill` (scoring loop + evals), in a Sonnet subagent per memory. Branch off main, no commit/push without Gal's explicit yes.

## Out of scope
Auto-editing from Codex output, multi-round Claude-vs-Codex debate, API-key OpenAI usage, updating Codex to 0.163.0.

## Open
- Eval: what proves the skill works? Proposal: 3 evals (plan review returns ranked holes; diff review runs read-only; missing login path gives the fix command).
