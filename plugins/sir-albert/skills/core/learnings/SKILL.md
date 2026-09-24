---
name: learnings
description: >
  Close the compound-learning loop: surface past corrections/patterns/playbooks
  from the project's .compound/ directory, then canonicalize accumulated drafts
  before they reach wiki-compile. Use when the user says "learnings",
  "load past corrections", "what did we learn", "canonicalize compound",
  "before wiki-compile", or "close the learnings loop". Also run before any
  invocation of /wiki-compile to prevent the wiki from fragmenting into
  near-duplicate micro-pages.
---

# Learnings

Boot from `os/PREAMBLE.md`.

Purpose: close the compound-learning loop. This skill adapts `kw-compound` +
`.compound/` to do two things that neither tool does alone — surface prior
knowledge at the start of a session and canonicalize accumulated drafts before
they graduate to the wiki.

**Announce at start:** "Running /sir-albert:learnings to surface and canonicalize compound knowledge."

---

## 1. Surface past learnings

Locate `.compound/` in the **current project directory** (the directory Claude
Code is opened on, not the sir_albert OS repo).

```
.compound/
  index.md           ← master table of all entries
  corrections/       ← confirmed bugs, misbeliefs corrected
  patterns/          ← recurring technical/domain patterns
  playbooks/         ← step-by-step repeatable procedures
```

Steps:

1. Read `.compound/index.md`. If it does not exist, report "No .compound/ found
   in this project — nothing to surface." and stop.
2. Identify entries relevant to the current task or conversation (match on `type`,
   `scope`, topic keywords in the headline). If the user gave no specific topic,
   surface all `scope: project` entries — those are always relevant.
3. For each matched entry, read the corresponding file (path =
   `.compound/<type-dir>/<id>.md`, where type-dir is `corrections`, `patterns`,
   or `playbooks`).
4. Present a compact TLDR surface: one bullet per entry in the format
   `[type] <headline> (created: YYYY-MM-DD)`, followed by a one-sentence
   implication. Do not paste the full file contents unless the user asks.

Example surface output:

```
Past learnings for this project:

- [correction] Monday.com board items in Canvas mode are invisible to Chrome
  accessibility tree (2026-06-10)
  → For board-item interactions, use the Monday.com API/MCP; Chrome automation
    fails on item rows.

- [playbook] sGTM vendor tag creation — ticket to production in 7 steps
  (2026-06-11)
  → Follow .compound/playbooks/sgtm-vendor-tag-creation.md before starting any
    new vendor tag.
```

> NOTE: auto-surface at session start = a SessionStart hook, deferred to the
> hooks step. Until that hook exists, invoke this skill manually at the start of
> a session or before resuming complex work.

---

## 2. Canonicalization barrier (run BEFORE /wiki-compile)

Before passing `.compound/` drafts to `/wiki-compile`, consolidate near-duplicates
and enforce the page-creation threshold. This prevents wiki fragmentation.

### 2a. Read all drafts

Read every `.md` file under `.compound/corrections/`, `.compound/patterns/`, and
`.compound/playbooks/`. Also re-read `index.md` for the full slug list.

### 2b. Merge near-duplicate slugs

Group slugs that cover the same concept. A group qualifies for merging when:
- Two or more slugs share the same topic noun (e.g., `mql`, `mql-definition`,
  `mql-threshold`) **and** the content overlaps by >50%, OR
- One entry's headline is a subset of another's ("sGTM tag" vs.
  "sGTM vendor tag creation").

For each merge group:
1. Designate the most complete file as the **canonical** slug.
2. Fold unique content from the others into the canonical file's body
   (add a `## Also captured` section if needed).
3. Delete the superseded files and remove their rows from `index.md`.
4. Present the merge plan to the user and get approval before writing.

### 2c. Apply the page-creation threshold

A concept seen **once** does NOT get its own wiki page — it folds into a parent
page. Apply this rule:

| Condition | Action |
|---|---|
| Slug has appeared in `index.md` across **1 session** only | Tag it `promote: fold` — it attaches to the closest parent page at compile time |
| Slug appears across **2+ sessions** OR the user explicitly marks it as canonical | Tag it `promote: page` — it becomes its own wiki page |
| Slug is a playbook or correction | Always `promote: page` regardless of session count — operational knowledge earns its own page |

Add a `promote: fold|page` line to the frontmatter of each `.compound/` draft.
Do not write it if it's already present.

### 2d. Confirm before writing

Present the full canonicalization plan (merges + promote tags) as a table. Wait
for user approval. Write changes only after approval.

---

## 3. Promote to wiki

After canonicalization, promote `promote: page` entries by running:

```
/wiki-compile
```

(provided by `llm-wiki-agent`). This is the standard pipeline — `kw-compound`
writes to `raw/`, `wiki-compile` processes `raw/` into `wiki/`. The
canonicalization step in Section 2 ensures `raw/` is clean before compile runs.

Promote on either of these triggers:
- The user explicitly says "promote" or "wiki-compile" or "close the loop".
- There are 3+ `promote: page` entries that have not yet been promoted (a
  backlog signal).

Do not promote automatically otherwise — promotion is a deliberate act.

---

## Guardrails

- **Never auto-write.** Surface and canonicalize plans require user approval
  before any file is modified.
- **Never read the entire wiki into context.** Read `wiki/index.md` to check for
  conflicts; read individual pages only if a specific overlap is suspected.
- **Corrections and playbooks always earn a page.** The threshold only gates
  concept pages.
- **This skill does not create `.compound/` entries.** Use `kw-compound` for
  that. This skill reads and curates; `kw-compound` writes.
