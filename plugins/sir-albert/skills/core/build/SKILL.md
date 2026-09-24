---
name: build
description: Use when starting a new build, kicking off a dashboard, wiki, MCP, or agent, or when build loop guidance is needed. Triggers on "build discipline", "how to build X", "start a new dashboard", "start a new wiki", "start a new MCP", "start a new agent", "build loop", "which sub-loop", "finishing a branch", "verify before done", "write tests first".
---

Boot from `os/PREAMBLE.md`.

# Build Discipline

The universal Building loop for all Gal-owned work. Pick the right sub-loop, follow it, don't shortcut.

## The Loop

```
discover → spec (to-prd) → prototype → build → attest → ship
```

Every build — no matter how small — touches all six stages. Size decides depth, not whether you do them.

| Stage | What happens | Key skill |
|---|---|---|
| **discover** | Clarify the question, identify the right sub-loop, check what already exists | `kb:wiki-query`, `github-repo-analyzer` |
| **spec** | Formalise intent as a testable PRD or one-pager | `to-prd` |
| **prototype** | Answer one design question with throwaway code/query | `prototype` |
| **build** | Implement against the spec | sub-loop specific (see below) |
| **attest** | Verify the output matches the spec; run the relevant review | `data-review` (data), `git-guardrails` (code) |
| **ship** | Publish / deploy / commit with context pointer | `commit-push-pr`, `deploy-mf`, n8n deploy |

---

## Named Sub-Loops

### data / monitoring

**Entry:** You have a question that needs a number. Start at `prototype` (write a scratch query first).

```
prototype → query → viz → deliver
```

| Step | Tool / Skill |
|---|---|
| query | Kremer MCP (`kremer-mcp`), z2h (`z2h-explore`), Snowflake direct |
| viz | `monday-data-viz-vibe` |
| deliver | `to-prd` (for spec), `monday-presentation-v2` or `slack-in-my-voice` (for comms) |
| pre-ship gate | **Run `data-review` before sharing anything externally.** |

---

### knowledge

**Entry:** You need to add, query, or compile governed knowledge. The engine is the `kb` plugin.

```
ingest → compile → query / recall / research
```

| Command | Purpose |
|---|---|
| `/wiki-init` | Bootstrap a new wiki in a repo |
| `/wiki-compile` | Re-build the wiki index from sources |
| `/learn-capture` | Add a document or URL as a source |
| `wiki-query` / `learn-recall` | Answer questions from the compiled wiki |
| `learn-research` | Deep research that files back into the wiki |
| `/add-tool <doc>` | doc → `doc-to-skill` → commit (adds an executable skill from a reference doc) |

---

### MCP / agent

**Entry:** You need a new autonomous capability — either an agent or an MCP server.

```
design → validate → build → register → test → ship
```

| Step | What |
|---|---|
| design | open_claw agent design (roles, tools, guard rails) |
| validate | `nanoclaw-validate` (structure check before writing code) |
| MCP build | GTM Gateway pattern; read `skills/packs/gtm/` for conventions |
| test | Dry-run in staging before prod deploy |
| ship | Register in `os/AGENTS.md`; commit with context pointer |

---

## OS-vs-Team-Repo Boundary

This matters. Duplication here wastes hours.

| Layer | What lives here | Examples |
|---|---|---|
| **OS** (`sir_albert`) | Gal's *reusable* skills — logic Gal owns and reuses across contexts | `to-prd`, `data-review`, `build` |
| **Team repos** | *Shared / governed* knowledge and team-specific workflows | `marketing-cookbook` (GTM playbooks), `mopa_brain` (MOPA logic), `data-cookbook` (data definitions) |

**Rule:** If it's a reusable capability → OS. If it's governed team knowledge → team repo. When in doubt, ask: "Would another team member need to maintain this?" If yes → team repo.

---

## Guardrails

- Never skip `attest`. A shipped thing that wasn't attested is a liability.
- `data-review` is mandatory before any dashboard or analysis goes external.
- The loop applies to one-liners too — it's just faster, not absent.

---

## § Finishing a branch

Before merging or calling anything done:

- **Confirm DOD.** Every task in the ticket has a checked DOD. If any are unchecked, the branch is not done.
- **Tests pass.** Run the full relevant test suite — not just the new tests. Zero regressions.
- **No leftover artifacts.** Grep for TODO, FIXME, debug prints, commented-out code added during this branch. Remove or ticket them.
- **PR description explains the why.** Not just "adds X" — why X, what was tried, what was learned.
- **Evidence inline.** The PR or final commit message includes the test run or smoke result. No self-certification.

---

## § TDD

From Pocock `skills/engineering/tdd` (MIT, adapted):

- **Confirm seams with the user before writing any test.** Write down the seams (public interfaces to test at) and get agreement. No test is written at an unconfirmed seam.
- **Red before green.** Write the failing test first. Run it — verify it fails for the right reason. Then write only enough code to pass it.
- **No tautological assertions.** Expected values must come from an independent source (known-good literal, worked example, the spec) — never recomputed the same way the code does.
- **One vertical slice at a time.** One test → one implementation → repeat. Don't write all tests first ("horizontal slicing") — you test imagined behavior, not real behavior.
- **Tests verify behavior through public interfaces.** Code can change entirely; tests shouldn't. "User can log in with valid credentials" survives refactors; "PasswordService.hash() returns 60-char string" does not.

---

## § Verification before completion

- **Evidence precedes "done."** Show the test run, curl output, or smoke result inline before claiming the task is complete.
- **No self-certification.** The implementing agent cannot be the sole verifier. At minimum: run the actual command and paste the actual output.
- **If verification fails, it's not done.** Do not claim done with a caveat. Fix it first.
- **Verification step is explicit in every ticket.** The last step of any task is always a runnable check: `pytest …`, `curl …`, `claude --plugin-dir … -p "…"`, or equivalent.
- **For code branches:** run `git diff` and confirm no debug artifacts remain before writing "done."
