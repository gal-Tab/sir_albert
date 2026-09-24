---
name: plan
description: Use when asked to write a plan, break down a task, create implementation steps, or turn a spec into agent-executable tickets. Triggers on "write a plan", "plan this", "break this down", "break this down into tickets", "implementation steps", "vertical slices", "write a plan for", "plan a feature".
---

# plan

Generates two artifacts from a single planning session: an interactive HTML document for human navigation and agent-executable ticket `.md` files as the source of truth for build work.

**Announce at start:** "I'm using the plan skill."

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.html`

## Approval gate

Before generating any files:
1. **Classify request depth:** one-file task / feature / subsystem (governs milestone count and granularity).
2. Present the breakdown (milestones + ticket slugs) for user approval.
3. Wait for explicit approval — "yes", "looks good", thumbs-up, etc.
4. Generate HTML + ticket `.md` files only after approval. This is a tracer-bullet: approve once, then generate all files.

Do not generate files before approval. Do not auto-approve.

---

## Ticket output

For each milestone/task in the plan, also write a ticket `.md` file:

**Path:** `docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md`

**Format:**
```markdown
# NN — <slug>

**Blocked by:** <ticket numbers or —>
**Spec:** `docs/specs/YYYY-MM-DD-<topic>.md §<section>` (if applicable)

## Goal
One sentence: what does "done" look like?

## Steps
1. <exact file path + action, 2–5 min each>
2. ...

## Definition of Done
- [ ] criterion

## CHECKPOINT (if any irreversible action)
Stop and ask before: pushing to remote, deploying, external sends, deletes.
```

**Granularity rules (writing-plans gates):**
- Each step touches a specific file at a specific path — no vague steps ("update the config").
- Steps are 2–5 minutes each. A 30-minute step is actually 6–10 steps.
- Test steps are included explicitly: "Run: `pytest tests/…` — Expected: PASS."
- Blocking edges are explicit: `**Blocked by:** 03, 07` not just prose.
- One vertical slice (the smallest possible thing that works end-to-end) is always the first ticket.

---

## Why HTML over Markdown

HTML plans are easier to read, navigate, and share. They support collapsible task details, syntax-highlighted code, Mermaid diagrams for data flow, and visual progress indicators. A 200-line markdown plan becomes an interactive document you actually want to read. The trade-off is slower generation and noisier diffs — worth it for plans that will be read more than once or shared with others.

---

## Plan Structure

Every plan has these sections in this order. The structure is mandatory; the visual treatment within each section is up to you.

### 1. Header

Top of the document. Orients the reader in 10 seconds.

- **Goal**: One sentence — what does "done" look like?
- **Architecture**: 2-3 sentences on the approach and key decisions
- **Tech stack**: Specific tools, frameworks, versions (not just "React, Node" — say "Next.js 14 App Router, Prisma 5, tRPC v11")
- **Effort estimate**: T-shirt size or time range
- **Feature flag**: If applicable, the flag name
- **Scope boundary**: 1-2 sentences on what is explicitly NOT included

### 2. Definition of Done (Project-Level)

3-5 bullet criteria that define when the entire plan is complete. These are the acceptance criteria for the plan itself, not individual tasks.

Example:
- All new endpoints return correct responses for happy path and error cases
- Existing test suite passes with zero regressions
- Feature is behind `comments_v1` flag and tested in staging
- PR reviewed and approved

### 3. Architecture / Data Flow Diagram

When the plan involves multiple components, services, or data transformations, include a Mermaid diagram. Read `../../../shared/references/mermaid-patterns.md` for monday-themed Mermaid config and common patterns.

Use diagrams when they clarify — not on every plan. A plan that touches one file doesn't need a flowchart.

### 4. Milestones

Group tasks into logical milestones (2-5 milestones for a typical plan). Each milestone should be independently shippable or at least independently reviewable.

Show milestones as a visual timeline or card layout. Include:
- Milestone name and time estimate
- Which tasks belong to it
- What's true when this milestone is complete

### 5. Tasks

The core of the plan. Each task follows the structure below.

### 6. Verification Task

The final task is always an end-to-end verification. Same format as other tasks. It runs the full flow described in the Goal and confirms the Definition of Done is met.

---

## Task Structure

Each task is a collapsible section. When collapsed, show: task number, name, files touched. When expanded, show everything.

```
### Task N: [Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Steps:**

Step 1: Write the failing test
  [code snippet]

Step 2: Run test to verify it fails
  Run: `pytest tests/path/test.py::test_name -v`
  Expected: FAIL with "function not defined"

Step 3: Write minimal implementation
  [code snippet]

Step 4: Run test to verify it passes
  Run: `pytest tests/path/test.py::test_name -v`
  Expected: PASS

Step 5: Commit
  `git add ... && git commit -m "feat: ..."`

**DOD:**
- [ ] New test passes
- [ ] `npm test` / full suite still green
- [ ] [task-specific acceptance criteria]

**⚠️ Risk** (only if there's a real one):
Brief risk + mitigation, inline. No risk? Don't include this.
```

### Task Granularity

Each step is one action (2-5 minutes):
- "Write the failing test" — one step
- "Run it to confirm it fails" — one step
- "Implement minimal code to pass" — one step
- "Run tests to confirm green" — one step
- "Commit" — one step

Keep this granularity. It makes plans mechanically executable by coding agents.

### Open Questions

If there are unresolved decisions that could affect implementation, list them at the end of the relevant task (not in a separate section). Include who should decide and when.

---

## HTML Output Requirements

### Single File, Zero Dependencies (except Mermaid CDN)

The output is one `.html` file. All CSS is inline in `<style>`. All JS is inline in `<script>`. The only external dependency allowed is the Mermaid CDN for diagram rendering.

### Design System

Read `../../../shared/references/design-tokens.md` for the full CSS variable set. Key tokens:

**Colors (dark theme):**
- Background: `#000000`
- Surface (cards, panels): `#232427`
- Surface alt (nested): `#2D3035`
- Text primary: `#ffffff`
- Text secondary: `#c3ced8`
- Text muted: `#a0a0a0`
- Purple (brand/accent): `#6164ff`
- Green (success): `#00c875`
- Yellow (warning/highlight): `#ffcb00`
- Red (risk/urgent): `#ff3d57`

**Typography:**
- Font: Poppins (400, 600 weights only)
- Load from Google Fonts CDN
- Use `vmin` units for responsive sizing

**Spacing:**
- Use CSS variables: `--space-1` (0.5vmin) through `--space-10` (10vmin)
- Never hardcode `px` for spacing

### HTML Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Feature Name] — Implementation Plan</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <style>
    /* Design tokens — read ../../../shared/references/design-tokens.md */
    /* Layout, components, collapsibles, code blocks */
  </style>
</head>
<body>
  <!-- Plan content -->
  <script>
    // Mermaid init with monday theme
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#6164ff',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#6164ff',
        lineColor: '#c3ced8',
        secondaryColor: '#232427',
        tertiaryColor: '#2D3035',
        fontFamily: 'Poppins, sans-serif'
      }
    });
    // Collapsible toggle logic
  </script>
</body>
</html>
```

### Interactive Elements

**Collapsible tasks:** Each task section collapses/expands on click. Default: first task expanded, rest collapsed. Use a chevron indicator and smooth transition.

**Code blocks:** Use `<pre><code>` with syntax highlighting via CSS classes. Dark surface background, monospace font (SF Mono, Fira Code, Consolas fallback).

**DOD checkboxes:** Render as real `<input type="checkbox">` elements. They don't persist state — they're for visual tracking during a session.

**Risk callouts:** Styled inline with a left border in `--color-yellow` or `--color-red` depending on severity.

**Progress indicator:** A simple bar or fraction at the top showing "N of M tasks" — updated by checkbox state if you want, or static.

### Visual Freedom

The structure above is the content contract. Within it, you have freedom to:
- Choose layout (single column, sidebar TOC, cards)
- Add a table of contents with anchor links
- Use tabs to group milestones
- Add visual emphasis where it helps readability
- Include mockups or wireframes as inline HTML when the plan has UI implications
- Use Mermaid diagrams for data flow, dependency graphs, sequence diagrams

Don't force visuals. A plan for a one-file refactor doesn't need diagrams and tabs. Match the visual complexity to the plan complexity.

---

## Diagrams

When a plan involves data flow, component interaction, or task dependencies, use Mermaid diagrams rendered client-side. Read `../../../shared/references/mermaid-patterns.md` for the full reference including monday-themed configuration.

Common diagram types for plans:
- **Flowchart**: Data flow, request lifecycle, decision trees
- **Sequence**: API call chains, auth flows, multi-service interactions
- **Graph**: Task dependency visualization

Embed diagrams inline:
```html
<pre class="mermaid">
flowchart LR
  A[Client] -->|POST /api| B[Server]
  B --> C[(Database)]
  C -->|rows| B
  B -->|JSON| A
</pre>
```

---

## Execution Handoff

After saving the plan, **automatically open it in the user's default browser** (do not wait for them to ask):