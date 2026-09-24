# W2 — Core skills consolidation

**Status:** draft for review · **Date:** 2026-09-24 · **Owner:** Gal

## Context

- W1 merged: one repo, two plugins (`sir-albert` + `kb`), clean install from `plugins/`, no symlinks.
- W2 (this spec): consolidate ~12 scattered skills into 9 canonical core skills; create 2 new skills (execute, debug); establish the docs-layout rule; achieve zero `superpowers:` refs in `plugins/`.
- W3 follows: `SessionStart` + `UserPromptSubmit` router hooks, thin versioned CLAUDE.md, `/sir-albert:init`. W3 expects skills to be stable and correctly named so the router can reference them by slug.
- W4: side-by-side eval vs superpowers → uninstall if new setup wins or ties.

## Goal

Produce 9 lean, independently-loadable core skills that together replace the `superpowers` plugin, with no skill depending on `superpowers:*` and all output artifacts landing in a consistent docs layout.

## Non-goals

- W3 work: `SessionStart`/`UserPromptSubmit` hooks, CLAUDE.md versioning, `/sir-albert:init`.
- W4 work: superpowers eval, uninstall.
- Moving repo to dapulse org.
- Changing KB engine behavior.
- Editing any `packs/` skill beyond gtm-gate + param-audit merge.

---

## Target skill tree

| Target skill | Current path(s) | New path | Source skills absorbed | Δ |
|---|---|---|---|---|
| brainstorm | `core/discover`, `biz/discovery-lens`, `biz/board-of-advisors`, `biz/devils-advocate`, `biz/zoom-out`, `dev/grilling`, `dev/grill-with-docs` | `core/brainstorm` | 7 → 1 | −6 |
| plan | `docs/html-plans` | `core/plan` (rename + move) | superpowers writing-plans gates (inline) | 0 |
| execute | _(new)_ | `core/execute` | Pocock implement-spec port | +1 |
| debug | _(new)_ | `core/debug` | Pocock diagnosing-bugs port | +1 |
| build | `packs/build/build-discipline` | `core/build` | superpowers finishing-a-branch, tdd, verification (3-line absorbs) | 0 |
| handoff | `core/handoff` | `core/handoff` | no change | 0 |
| resume | `core/resume` | `core/resume` | no change | 0 |
| create-skill | `dev/create-skill` | `dev/create-skill` | inline superpowers:writing-skills SDO material | 0 |
| slack-in-my-voice | `biz/slack-in-my-voice` | `biz/slack-in-my-voice` | no structural change; just stays | 0 |
| gtm-gate | `packs/gtm/gtm-gate` | `packs/gtm/gtm-gate` | absorbs param-audit | −1 |

**Before (skills in scope):** 12 (7 brainstorm sources + html-plans + build-discipline + create-skill + gtm-gate + param-audit)
**After (W2 net result for in-scope skills):** 9 core + 1 pack = 10 invokable skills from 12 — net −2 (plus 2 new = net 0 on total count, but 7→1 consolidation is the structural win)

---

## Per-skill design

### brainstorm

**Path:** `plugins/sir-albert/skills/core/brainstorm/`
**Absorbed:** core/discover, biz/discovery-lens (+ agents/), biz/board-of-advisors, biz/devils-advocate, biz/zoom-out, dev/grilling, dev/grill-with-docs

#### Mode table

| Mode | What it does | Runner | Trigger phrase examples |
|---|---|---|---|
| `explore` | 2–3 blind parallel voice agents explore angles; coordinator synthesizes | parallel subagents (from `agents/`) | "brainstorm this", "let's explore", "help me think through X", "WDYT", "fresh perspective" |
| `sharpen` | same council, sharpen mode prompt — distill to strongest core | parallel subagents | "sharpen this", "what's the core of this", "cut the noise" |
| `attack` | same council, attack mode prompt — find fatal flaws ruthlessly | parallel subagents | "attack this", "play devil's advocate", "stress test this", "challenge my idea", "find holes" |
| `panel` | named-persona panel from `agents/` (advisors); 4 distinct viewpoints | parallel subagents | "board of advisors", "4 perspectives", "multiple viewpoints", "panel on this" |
| `grill` | 1-question-at-a-time relentless interview in main conversation | main conversation | "grill me", "interview me about this", "stress-test my thinking" |
| `zoom-out` | single turn: map modules/callers/big-picture context | main conversation | "zoom out", "bigger picture", "how does this fit", "I don't know this area" |
| `design` | Spike / Bounded / Architectural classify → gates → 2–3 approaches + recommendation → spec to `docs/specs/` → self-review → hand off to `plan` | main conversation | "let's design this", "design X", "I want to build X", "plan this out", "architect this" |

**Explicit arg syntax:**
- `/sir-albert:brainstorm` — auto-detect from phrase table
- `/sir-albert:brainstorm <mode>` — force mode
- `/sir-albert:brainstorm panel --voices graham,verna <idea>` — panel with named voices
- `/sir-albert:brainstorm attack <idea>` — attack mode

#### Behavioral rules
- State the mode picked and why before running (one line). Explicit arg overrides.
- Parallel modes (`explore`, `sharpen`, `attack`, `panel`) dispatch blind subagents from `agents/`; coordinator labels each voice's output.
- `design` mode: classify Spike / Bounded / Architectural out loud first. Hard gate: no implementation before approval of the required artifact for the path. Run `kb:learn-research` first to pull past learnings. Write spec to `docs/specs/YYYY-MM-DD-<topic>.md`. Hand off to `plan` explicitly.
- `grill` mode: one question at a time; absorb grill-with-docs behavior (can be run against provided docs).
- `zoom-out` mode: go up a layer of abstraction; use domain glossary vocabulary.
- Discovery-lens `voices.md` and existing `agents/*.md` files (boris.md, collison.md, karpathy.md, etc.) move into `core/brainstorm/agents/`.
- `board-of-advisors` personas become additional `agents/` files for `panel` mode.
- `devils-advocate` content becomes the `attack` mode prompt fill-in.

#### What changes
- 7 skills → 1; all former skill dirs become archived (see archive section) after `brainstorm` is verified.
- REGISTRY.md core table: `discover` row → `brainstorm` row.
- RESOLVER.md line 15: `Core /discover` → `Core /brainstorm`.
- `skills/core/README.md`: discover entry → brainstorm.
- `skills/packs/README.md`: last line references `core/discover` → `core/brainstorm`.

---

### plan

**Path:** `plugins/sir-albert/skills/core/plan/` (renamed from `docs/html-plans`)
**Decision:** rename `html-plans` → `plan` and move from `skills/docs/` to `skills/core/`. The command was `/sir-albert:html-plans`; it becomes `/sir-albert:plan`.

#### Absorbed
- Superpowers `writing-plans` gates: exact files + 2–5 min steps, test steps, tracer-bullet vertical slices with blocking edges.
- Produces `docs/plans/YYYY-MM-DD-<topic>.html` (human view) **and** `docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md` (agent source of truth).

#### Behavioral rules
- Classify request depth (one-file task / feature / subsystem) before generating.
- Ticket format: **Goal**, **Blocked by**, **Steps** (2–5 min), **DOD**, **CHECKPOINT** markers.
- HTML output retains interactive monday dark-theme; ticket .md files are the agent-executable truth.
- Shared design tokens / mermaid-patterns refs (`../../../shared/references/`) path stays valid once moved to `core/plan/` because `shared/` is at the same level.
- Approve the breakdown before generating ticket files (tracer-bullet slice: user approves once).

#### What changes
- `git mv plugins/sir-albert/skills/docs/html-plans plugins/sir-albert/skills/core/plan`.
- `plugin.json`: `./skills/docs` continues to load everything in that dir; also needs `./skills/core` — already listed. But `html-plans` SKILL.md name field must change to `plan`.
- REGISTRY.md: docs table `html-plans` row → core table `plan` row.
- `to-prd/SKILL.md` line 147: `../html-plans/sample-plan.html` → `../../../core/plan/sample-plan.html` (or keep cross-ref).
- `shared/references/design-tokens.md` line 1 title: "Design Tokens — html-plans" → "Design Tokens — plan".

---

### execute

**Path:** `plugins/sir-albert/skills/core/execute/` _(new)_
**Source:** Pocock `skills/in-progress/implement-spec/SKILL.md` (MIT License, port with attribution)

#### Behavioral rules
- Reads spec + tickets, builds a task graph with a frontier of unblocked tickets.
- **Optional worktrees + draft PR** — most of Gal's work isn't a code PR; omit unless explicitly requested.
- Implementer subagents run in the background (Sonnet model); coordinator answers their questions in main context.
- Outward-facing actions (push, PR, merge, live config apply) are **hard CHECKPOINT** gates: stop and ask before proceeding. These are irreversible.
- Sparse context pointers to spec/tickets/commits — no duplication.
- Code review at end if output is a code branch; otherwise a verification step matching the spec's DOD.
- Starts with: "I'm using the execute skill. Reading the spec and building the task graph."

#### What changes
- New skill; requires THIRD_PARTY_NOTICES.md update (Pocock/implement-spec).

---

### debug

**Path:** `plugins/sir-albert/skills/core/debug/` _(new)_
**Source:** Pocock `skills/engineering/diagnosing-bugs/SKILL.md` (MIT License, port with attribution)

#### Behavioral rules
- Phase 1 is non-negotiable: build a tight pass/fail feedback loop before any hypothesis work. Cannot skip.
- Redact secrets before showing any command output or captured artifact.
- Tighten the loop: faster → sharper signal → more deterministic.
- Non-deterministic bugs: raise repro rate to ≥50% before proceeding.
- If a tight loop cannot be constructed, stop and say so explicitly; ask for access/artifact/instrumentation permission.
- Phases: feedback-loop → hypothesis → fix → verify → close.

#### What changes
- New skill; requires THIRD_PARTY_NOTICES.md update.

---

### build

**Path:** `plugins/sir-albert/skills/core/build/` (moved from `packs/build/build-discipline/`)
**Decision:** move to `core/` — it's mode-agnostic OS-level discipline, not domain-specific.

#### Absorbed (3-line each)
- **finishing-a-branch** (superpowers): before merging, confirm DOD, run tests, verify no leftover TODOs, no debug artifacts.
- **tdd** (Pocock): red-green-refactor at agreed seams; confirm seams with user before writing tests; no tautological assertions.
- **verification-before-completion** (superpowers): evidence before "done"; show the test run / curl / smoke result inline.

#### Stale ref fix
- `build-discipline/SKILL.md` references `kb-query` and `kb-compile` — replace with `kb:wiki-query` and `kb:wiki-compile`.
- References `github-repo-analyzer` and `git-guardrails` in sub-loop tables — keep these refs (skills exist and are functional; archive table covers their future).

#### What changes
- `git mv plugins/sir-albert/skills/packs/build/build-discipline plugins/sir-albert/skills/core/build`.
- `plugin.json`: `./skills/packs/build` entry can be removed; `./skills/core` already covers it.
- REGISTRY.md: packs table `build-discipline` row → core table `build` row.
- RESOLVER.md line 13: `packs/build` path reference → `core/build`.

---

### create-skill

**Path:** `plugins/sir-albert/skills/dev/create-skill/` (unchanged)

#### Independence work
- `SKILL.md` lines 8–9: "**REQUIRED BACKGROUND:** Load `superpowers:writing-skills`…" → replace with inline content from `references/methodology.md` section on SDO thinking and anti-narrative patterns. About 150 words of inline rules.
- `references/methodology.md` lines 3–16: currently says "read `superpowers:writing-skills` directly" — replace with a self-contained inline SDO summary in `references/methodology.md` (already has the comparison table; extend it with the key rules: match-the-form-to-the-failure, anti-narrative, rationalization tables).
- `references/angles.md` line 31: `superpowers:writing-skills` ref → inline text.
- `scripts/validate-skill.py` line 6: `superpowers:writing-skills SDO` comment → update to refer to `references/methodology.md`.
- After: zero `superpowers:` occurrences in `skills/dev/create-skill/`.

#### Lean path
- SKILL.md length: currently ~170 lines. Reduce to ~400 words (the common path: classify → elicit → scaffold → validate → tier gate). Deep eval path stays in `references/`.
- The T2 workflow opt-in, agents/, scripts/score.py, evals/ machinery: kept as-is in references/; SKILL.md just points to them.

#### Behavioral rules (unchanged)
- Every SKILL.md create or edit in W2 goes through this skill.
- Validate before advancing (`validate-skill.py`).
- Choose the lowest tier that matches skill value.

---

### docs-layout rule

**Path:** `plugins/sir-albert/os/rules/docs-layout.md` _(new)_

#### Content (OKF style)
- `docs/specs/YYYY-MM-DD-<topic>.md` — design specs; `status:` frontmatter (draft / approved / superseded).
- `docs/plans/YYYY-MM-DD-<topic>.html` — human-readable interactive plan (generated by `plan` skill).
- `docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md` — agent-executable tickets; each with Goal / Blocked by / Steps / DOD / CHECKPOINTs.
- `.memory-bank/HANDOFF-YYYY-MM-DD.md` — session handoff docs (written by `handoff` skill).
- **Never** write plan tickets inline in the spec; the spec is the design, tickets are the execution units.
- **Naming:** slugs are lowercase-hyphenated, no spaces. Date prefix is `YYYY-MM-DD`.

---

### gtm-gate (+ param-audit merge)

**Path:** `plugins/sir-albert/skills/packs/gtm/gtm-gate/` (unchanged)
**Absorbed:** `packs/gtm/param-audit/` content (sGTM FB/LinkedIn tag parameter audit)

#### Behavioral rules
- Param-audit content becomes a **§ Parameter audit** section in gtm-gate's SKILL.md.
- Trigger phrases from param-audit (`/param-audit`, "audit sGTM params", etc.) added to gtm-gate's description.
- param-audit skill dir → `git mv` to `_archive/` after gtm-gate update is verified.
- REGISTRY.md packs table: remove param-audit row; update gtm-gate trigger phrases.

---

## References to update

| File | Current value | New value |
|---|---|---|
| `REGISTRY.md` line 103 | `discover \| core/discover/ \| "help me think through X"…` | `brainstorm \| core/brainstorm/ \| "brainstorm this", "grill me", "design this"…` |
| `REGISTRY.md` line 44 | `html-plans \| docs/html-plans/ \| "write a plan"…` | `plan \| core/plan/ \| "write a plan", "plan this", "break this down"…` |
| `REGISTRY.md` line 121 | `build-discipline \| packs/build/build-discipline/ \| …` | `build \| core/build/ \| …` |
| `REGISTRY.md` line 119 | `param-audit \| packs/gtm/param-audit/ \| …` | _(row removed; gtm-gate row gains trigger phrases)_ |
| `REGISTRY.md` lines 132–133 | `html-plans, to-prd` in shared assets table | `plan, to-prd` |
| `RESOLVER.md` line 13 | `packs/build — discover → spec…` | `core/build — brainstorm → spec…` |
| `RESOLVER.md` line 15 | `Core /discover — pick a lens: explore · sharpen · attack · zoom-out` | `Core /brainstorm — modes: explore · sharpen · attack · panel · grill · zoom-out · design` |
| `skills/core/README.md` | `discover` entry | `brainstorm` entry |
| `skills/packs/README.md` last line | `core/discover` | `core/brainstorm` |
| `plugin.json` skills list | `./skills/packs/build` | remove (covered by `./skills/core`); confirm `./skills/core` is listed |
| `skills/docs/to-prd/SKILL.md` line 147 | `../html-plans/sample-plan.html` | `../../../core/plan/sample-plan.html` |
| `shared/references/design-tokens.md` line 1 | `# Design Tokens — html-plans` | `# Design Tokens — plan` |
| `create-skill/SKILL.md` lines 8–9 | `Load superpowers:writing-skills before proceeding…` | inline SDO/anti-narrative rules (~150 words) |
| `create-skill/references/methodology.md` lines 3–16 | `read superpowers:writing-skills directly` | inline SDO summary |
| `create-skill/references/angles.md` line 31 | `superpowers:writing-skills` | `references/methodology.md §SDO` |
| `create-skill/scripts/validate-skill.py` line 6 | `superpowers:writing-skills SDO` comment | `references/methodology.md` |
| `packs/build/build-discipline/SKILL.md` | `kb-query` / `kb-compile` refs | `kb:wiki-query` / `kb:wiki-compile` |

---

## Archive candidates

Skills with 0 recorded runs that are candidates for `git mv` to `plugins/sir-albert/skills/_archive/`. Gal decides — this table is the input.

| Skill | Current path | Dependencies found | Recommend | Why |
|---|---|---|---|---|
| `freeze` | `core/freeze/` | `hooks/freeze-guard.sh` wired as `PreToolUse` hook in `~/.claude/settings.json` | **Keep** | Live hook dependency; archive only after W3 removes or re-wires the hook. |
| `retro` | `core/retro/` | `hooks/cron-retro.sh` + launchd cron (`com.sir-albert.retro`) | **Keep** | Live cron; archive only after the launchd plist is updated or removed. |
| `decide` | `core/decide/` | Writes to `os/state/decisions.jsonl`; RESOLVER.md §Memory references it | **Keep** | Active state store (`decisions.jsonl` is live data). Archive removes the write path. |
| `sync` | `core/sync/` | None found | **Archive** | Pure git helper; not in target 9; git is already handled by `commit-commands`. |
| `self-reflection` | `agentic/self-reflection/` | None found | **Archive** | No recorded use; `retro` covers the self-improvement loop. |
| `to-prd` | `docs/to-prd/` | Referenced by build-discipline and html-plans sample plan | **Keep** | Still used in build sub-loop spec step; `plan` skill (html-plans rename) references its sample; do not archive until build is fully updated. |
| `prototype` | `dev/prototype/` | Referenced by build-discipline sub-loops and discover routing table | **Keep for now** | `build` skill still references it. Revisit in W3. |
| `domain-modeling` | `dev/domain-modeling/` | `grill-with-docs` depends on it | **Archive after brainstorm** | Once brainstorm absorbs grill-with-docs, the only live dep is removed. Archive in ticket 12 _after_ brainstorm verification. |
| `git-guardrails` | `dev/git-guardrails/` | Referenced in build-discipline attest stage | **Keep** | `build` skill still references it. |
| `github-repo-analyzer` | `dev/github-repo-analyzer/` | Referenced in build-discipline discover stage | **Keep** | `build` skill still references it. |
| `claude-handoff` | `dev/claude-handoff/` | None in settings.json or hooks; REGISTRY.md dev table | **Archive** | Spawns background agents — this is now `execute` skill's job. REGISTRY.md note about it should move to a historical note. |
| `grill-with-docs` | `dev/grill-with-docs/` | Depends on `grilling` + `domain-modeling` (both absorbed into brainstorm) | **Archive after brainstorm** | Absorbed into brainstorm grill mode; no live deps once brainstorm ships. |
| `grilling` | `dev/grilling/` | `grill-with-docs` depends on it (also archived after brainstorm) | **Archive after brainstorm** | Absorbed into brainstorm grill mode. |

**Immediate archives (no live deps):** sync, self-reflection, claude-handoff
**Archive after brainstorm ships:** domain-modeling, grill-with-docs, grilling
**Keep (live deps):** freeze, retro, decide, to-prd, prototype, git-guardrails, github-repo-analyzer

---

## Risks

- **Broken cross-refs:** skills that reference `discover`, `html-plans`, or `build-discipline` by name (RESOLVER.md, REGISTRY.md, build SKILL.md) must all be updated atomically in ticket 10. A partial update leaves the resolver pointing at a deleted path.
- **plugin.json `./skills/docs` still loads `plan/`?** Moving html-plans from `docs/` to `core/` means `./skills/docs` no longer covers it. Verify `./skills/core` is in plugin.json (it is), and confirm no double-load after the move.
- **`create-skill` self-dependency:** ticket 08 edits create-skill's own SKILL.md — but the instruction says every SKILL.md edit must go through create-skill. This is a bootstrap: edit the SKILL.md directly (it's a structural/independence fix), then use the updated skill for all subsequent W2 SKILL.md work.
- **Superpowers still installed during W2:** create-skill currently `Load superpowers:writing-skills` at runtime. Until ticket 08 ships, any create-skill invocation still pulls superpowers in. Execute 08 early in the build.
- **Archive before verify:** archiving biz/discovery-lens, dev/grilling, etc. before confirming brainstorm works would leave a gap. Ticket 12 (archive) is blocked by ticket 13's partial verification run.

## Rollback

- All moves are `git mv` — reversible by dropping the `w2/core-skills` branch or cherry-picking the revert.
- If a skill fails post-move, restore with `git mv _archive/<skill> <original-path>` and reload plugin.
