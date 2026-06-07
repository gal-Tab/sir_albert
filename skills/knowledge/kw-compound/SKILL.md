---
name: kw-compound
description: >
  Capture knowledge from the current session and file it back into the sir_albert knowledge base.
  Use when the user says "save this to the wiki", "file this knowledge", "add this to my KB",
  "remember this for future sessions", "compound this insight", "compound this session", or
  "save what we just learned". Also trigger when kb-query synthesizes a cross-reference not yet
  in the wiki and the user wants to preserve it. Writes structured markdown to raw/ for
  kb-compile to process into wiki/.
allowed-tools: Read, Write, Bash(git add *), Bash(git commit *)
---

# kw-compound

Capture session knowledge and write it to `raw/` as a structured markdown file, ready for `kb-compile` to ingest into `wiki/`.

**Announce at start:** "I'm using kw-compound to file this knowledge to `raw/` for the next wiki compilation."

## The Knowledge Loop

```
session insights
    ↓  kw-compound writes
raw/ (source drop zone)
    ↓  kb-compile processes
wiki/ (structured pages)
    ↑  kb-query reads
```

This skill is the **write** side of the loop. `kb-query` reads from `wiki/`; `kw-compound` feeds `raw/` so the next `kb-compile` pass makes session insights permanent wiki knowledge.

## When to Use

- User explicitly asks to save, file, or remember something for the wiki
- `kb-query` produced a synthesis (comparison, concept connection) not yet in the wiki, and the user wants to preserve it
- After a deep conversation that produced domain knowledge worth persisting
- End-of-session capture: "compound this session"

## When NOT to Use

- The insight is trivial or already in the wiki — run `kb-query` to check first
- Content is a session preference or tool config (that belongs in `MEMORY.md`)
- User wants to update an existing wiki page in place — use `Write` directly + commit
- The insight is operational/task-specific and won't be useful across sessions

---

## Workflow

### Step 1: Identify and classify

Extract 1–3 compoundable items from the session. More than 3 means you're not filtering enough.

For each candidate, determine the page type per `wiki-schema.md`:

| Type | When to use |
|---|---|
| **concept** | New domain idea, framework, named principle — only if domain-specific or novel |
| **entity** | Specific person, org, tool, project, product worth tracking |
| **comparison** | Two entities or approaches contrasted with clear dimensions |
| **source** | External document, paper, article discussed in session |

Draft each learning in one sentence: "What we now know and why it matters."

Present to the user: "Found N items worth filing to the wiki — approve?"

**Never auto-save. Approval required for each item.**

### Step 2: Read the schema

```
Read: wiki-schema.md
```

Check:
- Correct frontmatter fields for the page type
- Slug derivation rules
- Confidence label requirements (STATED / INFERRED / UNCERTAIN)
- Create threshold — don't file concepts a practitioner would already know

### Step 3: Check for conflicts

```
Read: wiki/index.md
```

If a related page already exists:
- Show the existing page path and ask: "Update existing or save as new entry?"
- If updating: note the page path and flag the new content as an addendum to add at the bottom

### Step 4: Write to raw/

Create `raw/<slug>.md` where `<slug>` follows `wiki-schema.md` slug rules.

**File structure:**

```markdown
---
title: "<Human-readable title>"
type: source|entity|concept|comparison
kw_capture: true
kw_date: YYYY-MM-DD
tags: [relevant, keywords]
source_refs: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <Title>

<Content structured per the page type's sections in wiki-schema.md>

## See Also
- (links to related wiki pages with confidence labels per wiki-schema.md)

## Source / Origin
Captured from session on YYYY-MM-DD. <One sentence: context where this knowledge emerged.>
```

Use `STATED / INFERRED / UNCERTAIN` confidence labels for any cross-references to existing wiki pages.

### Step 5: Update raw/.manifest.json

```
Read: raw/.manifest.json
```

If the new slug is not in the manifest, add it. The manifest tells `kb-compile` which files are new.

### Step 6: Commit

```bash
git add raw/<slug>.md raw/.manifest.json
git commit -m "[kw-compound] Filed: <title>"
```

### Step 7: Confirm

Report back:
- **Filed:** `raw/<slug>.md` (type: concept / entity / comparison / source)
- **Next:** "Run `/kb-compile` to ingest this into `wiki/`, or it will be picked up next session."

---

## Guardrails

- **Write to `raw/` only** — never directly to `wiki/`. Always let `kb-compile` do the compilation.
- **Read `wiki-schema.md` before writing** — it governs structure, slug rules, and confidence labels.
- **Approval required** — never auto-save. Present and confirm before writing.
- **1–3 items max per session** — quality over quantity.
- **Concept create threshold** — only concepts that are domain-specific or coined/defined with novel treatment. Skip general practitioner knowledge.
- **Confidence labels are mandatory** for any cross-references in frontmatter `source_refs` or `## See Also` sections.
- **When in doubt: wiki vs MEMORY.md** — wiki is for durable domain knowledge; MEMORY.md is for preferences, behaviors, and project context.
