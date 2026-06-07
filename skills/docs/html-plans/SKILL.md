---
name: html-plans
description: Generate implementation plans as rich, interactive HTML files styled with monday.com's dark theme. Use this skill whenever the user asks to write a plan, create an implementation plan, plan a feature, write a technical spec for implementation, or break down a task into steps. Replaces markdown plans with visually rich HTML that includes collapsible sections, Mermaid diagrams, styled code blocks, and progress tracking. Also triggers on "plan this", "break this down", "write a plan for", "implementation steps", or any multi-step coding task that needs a plan before execution.
---

# html-plans

Generate implementation plans as single-file, self-contained HTML documents styled with monday.com's dark theme. Plans are visually rich, easy to skim, and executable by both humans and coding agents.

**Announce at start:** "I'm using the html-plans skill to create an HTML implementation plan."

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.html`

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

After saving the plan, offer:

**"Plan saved to `docs/plans/<filename>.html`. Open it in your browser to review.**

**Ready to execute? Two options:**
1. **This session** — I'll implement task by task, you review between milestones
2. **New session** — Open a fresh session and pass in this plan file for implementation"

---

## Remember

- Exact file paths, always
- Complete code in plan (not "add validation here")
- Exact commands with expected output
- DOD per task includes regression check
- Final task is always end-to-end verification
- Risks inline with relevant tasks, not in a separate section
- DRY, YAGNI, TDD, frequent commits
