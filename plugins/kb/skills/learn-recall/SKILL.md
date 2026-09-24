---
name: learn-recall
description: Use when the user asks what was learned before, references past mistakes/lessons/playbooks ("have we hit this before", "what did we learn about X", "lessons learned", "did I already solve this"), or when you want to consult the agent's own compound learnings before acting. Reads the compound-learnings store (project .compound/ + the global store), index-first.
allowed-tools: Read, Glob, Grep
---

# Compound Learnings — Recall

Consult the agent's own accumulated **work-lessons** (corrections, playbooks,
insights, patterns) to answer "have we learned this before?" and to inform how
you approach the current task. These are the agent's lessons — **not** source
wiki pages (`wiki-query` handles those) and **not** user preferences (those live
in MEMORY).

This skill is **index-first and token-frugal**: read the compact index, then
fetch at most a handful of bodies, and only the ones that actually sharpen the
answer. Never load the store wholesale.

## When to Use This Skill

- User asks what was learned/decided before, or references past mistakes,
  corrections, playbooks, or "lessons learned."
- User asks "have we hit this before?", "did I already solve this?", "what's our
  approach to X?"
- You are about to start a task and want to check for a relevant past correction
  or blessed playbook before acting.

## When NOT to Use This Skill

- Domain questions about ingested sources → use `wiki-query` (the wiki).
- User *preferences/behaviors* → those are MEMORY, not learnings.
- Capturing a new lesson → use `/learn-capture`. This skill is read-only.
- General coding questions with no relevant captured learning.

## The Two Stores

Retrieval merges both tiers; the **project store shadows global** on id collision.

| Scope | Root | Notes |
|-------|------|-------|
| project | `<repo>/.compound/` | primary, committed, team-shared |
| global | `$COMPOUND_KNOWLEDGE_HOME` or `~/.claude/compound-knowledge/` | opt-in, curated, cross-project |

Each store: a compact `index.md` plus per-type bodies under
`insights/ playbooks/ corrections/ patterns/`. The index line schema is:

```
- [CODE] {id} | {tags} | {headline} | {confidence} | {date}
```

Type codes → body directory: `C` → `corrections/`, `P` → `playbooks/`,
`I` → `insights/`, `Pa` → `patterns/`. The body file is `<root>/<dir>/<id>.md`.

## Recall Procedure

1. **Locate the indexes.** Read `<repo>/.compound/index.md` and the global
   `index.md` (under `$COMPOUND_KNOWLEDGE_HOME` or `~/.claude/compound-knowledge/`).
   If neither exists, say no learnings have been captured yet and stop — there is
   nothing to recall.

2. **Scan the index lines** (cheap — they are headline-only). Match the user's
   question against the **tags** column and headlines. If a store is large, use
   `grep -i "<term>" <root>/index.md` to find candidate lines rather than reading
   the whole file. **Corrections rank first** (mistakes not to repeat), then
   playbooks, then insights/patterns.

3. **Merge tiers**, project over global on duplicate id. Keep the most relevant
   candidates (typically ≤5).

4. **Fetch bodies on demand — at most 5, only when needed.** For a candidate that
   directly answers the question, read its body at `<root>/<type-dir>/<id>.md`
   (or `Glob` for `**/<id>.md` if unsure of the type). Skip bodies whose headline
   already answers the question — many recalls need no body read at all.

5. **Synthesize and cite ids and scope.** Lead with corrections. For each lesson
   used, cite its id and scope, e.g.:
   - "A past correction (`kw-2026-06-08-retry-jitter`, project) says: add jitter…"
   - "Per the blessed playbook `kw-…-deploy` (global): …"
   Distinguish a captured learning from general reasoning when you add your own.

## Canonicalization (run BEFORE `/kb:wiki-compile`)

Before passing `.compound/` drafts to `/kb:wiki-compile`, consolidate near-duplicates
and enforce the page-creation threshold. This prevents wiki fragmentation.
Run when the user says "canonicalize compound", "before wiki-compile", or "close the
learnings loop", or when 3+ `promote: page` entries are pending promotion.

### Steps

1. **Read all drafts.** Read every `.md` under `.compound/corrections/`, `.compound/patterns/`,
   and `.compound/playbooks/`. Also re-read `index.md` for the full slug list.

2. **Merge near-duplicate slugs.** Group slugs that cover the same concept. A group qualifies
   when two or more slugs share the same topic noun **and** content overlaps >50%, or one
   headline is a strict subset of another. For each group: designate the most complete file as
   canonical, fold unique content from others in, delete superseded files, remove their rows
   from `index.md`. Present the merge plan and get approval before writing.

3. **Apply the page-creation threshold.**

   | Condition | Action |
   |---|---|
   | Slug appeared in only **1 session** | Tag `promote: fold` — attaches to closest parent page at compile time |
   | Slug appears in **2+ sessions** OR user marks it canonical | Tag `promote: page` — becomes its own wiki page |
   | Slug is a playbook or correction | Always `promote: page` — operational knowledge earns its own page |

   Add `promote: fold|page` to the frontmatter of each `.compound/` draft (skip if already present).

4. **Confirm before writing.** Present the full plan (merges + promote tags) as a table. Wait
   for approval. Write changes only after approval.

5. **Promote.** After canonicalization, run `/kb:wiki-compile` to promote `promote: page`
   entries into `wiki/`. Only on explicit user trigger ("promote", "wiki-compile", "close the
   loop") or when 3+ `promote: page` entries are backlogged.

## Guardrails

- **Index-first, never load the store wholesale.** Read indexes, then bodies on
  demand.
- **At most 5 bodies per recall** unless the user explicitly asks for a full
  review.
- **Read-only for recall.** This skill never writes except in the canonicalization
  section above, which always requires user approval. To capture a new lesson,
  route to `/learn-capture`.
- **Cite ids + scope** for every lesson you rely on.
- **Corrections first** — surface contradicting/cautionary lessons before
  reinforcing ones.
- **Never auto-write.** All canonicalization changes require user approval before
  any file is modified.
