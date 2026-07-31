# RESOLVER — the sir_albert_os map (read me first)

**"I'm about to do X → which skill/rule/pack applies, and where does the output go?"** One screen. If it isn't here, it isn't load-bearing.

## Boot
Every sir-albert skill boots from [`os/PREAMBLE.md`](PREAMBLE.md): it loads identity + active rules + settled decisions + the **anti-slop / use-the-skill** contract. Identity is authored once in `os/identity/{USER,SOUL,HEARTBEAT}.md` — Claude Code `@`-imports it; other runtimes (NanoClaw) read the same files raw.

## The 3 modes → entry point → gates → output
| I'm about to… | Start here | Gated by | Output lands in |
|---|---|---|---|
| Make a **GTM** change (tag/var/trigger) | `packs/gtm` — plan → apply → publish | `rules/gtm-naming.md` + `rules/consent-map.md` (validated *before* apply) | dry-run first; live publish only after **ASK**; then `/handoff` |
| Build a **dashboard / analysis** | `packs/data` — `/prototype` → query (Kremer/z2h) → viz | `data-review` + attested metric specs | z2h **look** + OKF mirror; Slack draft in voice |
| Build a **skill / agent / wiki / MCP** | `packs/build` — discover → spec → prototype → build → **attest** → ship | OS-vs-team-repo boundary | skill in this repo; durable knowledge → wiki |
| Fix an **n8n / integration** flow | `packs/automation` — `/n8n-triage` | HubSpot API-safety check | fix proposal; **ASK** before prod deploy |
| **Think first** (front-runs any mode) | Core `/discover` — pick a lens: explore · sharpen · attack · zoom-out | — | feeds the mode above |

## Core — loaded everywhere
- **Continuity:** `/handoff` (writes the doc **and** a paste-able restart prompt) · `/resume` (reload latest handoff, state plan back in ≤5 bullets) · `/sync` (post-merge git; safe `-d` cleanup only).
- **Memory:** `/decide` → `os/state/decisions.jsonl` — a settled question is **auto-applied, not re-asked**.
- **Safety:** `guard.sh` (blocks destructive cmds) · `/freeze [path]` (scope edits during investigation) · autonomy tiers → `rules/autonomy.md`.
- **Voice / anti-slop:** `slack-in-my-voice`, `linkedin-in-my-voice` (channels resolved from `USER.md`) · TLDR-first, bullets, tables for comparisons, no re-explaining what I know.

## Knowledge engine — inherit, don't fork
Query & capture via the **`llm-wiki-agent` plugin** (canonical): `wiki-query` / `learn-recall` / `learn-research`; commands `/wiki-init` `/wiki-compile` `/learn-capture`. Write side: `kw-compound` → `raw/` → canonicalize → `/wiki-compile`. **Legacy `kb-*` is retired — do not use.**

## Externals — WRAP, never fork
Called from here, kept intact and auto-updating: **superpowers** (process/skills spine) · **z2h** (dashboards) · **commit-commands** (git) · **pr-guardrails** (PR checks).

## Protected — NEVER disable (they ship critical payload)
**token-optimizer** (hooks) · **axcli** (gateway+hooks) · **slack** (MCP) · **code-review** / **code-simplifier** · **cf-external** (vibe MCP).

## Trust layer — why parallel delegation is safe
Durable knowledge is **OKF**: `sources` (cited) + `stale_after` (hard expiry) + `status` (draft/stable/deprecated). Metrics are **z2h looks** (declarative spec = attestable) mirrored to OKF; the attester fails on spec/SQL drift. **If a rule or metric is stale or uncited, treat it as unverified** — that's the line between "act on it" and "check it first."
