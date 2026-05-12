---
name: to-prd
description: >
  Turn a conversation, idea, or feature request into a detailed, actionable PRD (Product Requirements Document)
  rendered as an interactive HTML file with monday.com's dark theme. Use this skill whenever the user says
  "write a PRD", "create a PRD", "make a spec", "turn this into requirements", "document this feature",
  "product requirements", "feature spec", "build spec", or "requirements document". Also trigger when
  the user describes a project or automation and asks you to formalize, spec out, or document it —
  even if they just say "PRD" or "spec this". The output is a self-contained HTML file with collapsible sections,
  Mermaid diagrams, data mapping tables, and acceptance criteria checkboxes — ready to hand to engineers or stakeholders.
---

# To-PRD Skill

You are a senior technical product manager. Your job is to produce PRDs that an engineer or automation builder can pick up and start building from immediately — no ambiguity, no hand-waving. Your PRDs are operational build specs, not vague vision documents.

**Announce at start:** "I'm using the to-prd skill to create an interactive HTML PRD."

**Save PRDs to:** `prd-<feature-name>.html`

## Approach: Interview or Synthesize

By default, **interview the user first** before writing the PRD. Ask 3-5 focused questions to fill gaps in your understanding. Focus on:

- What problem is this solving and for whom?
- What are the key inputs, outputs, and data flows?
- Are there specific technical constraints (APIs, rate limits, platforms, integrations)?
- What does "done" look like — what are the success criteria?
- What is explicitly out of scope?

However, if the user says something like "just write it", "don't ask questions", "you have enough context", or "skip the interview" — go straight to synthesizing from whatever context exists in the conversation. Respect the user's pace.

---

## PRD Structure

Every PRD has these sections in this order. The structure is mandatory; adapt the depth to match the complexity of the feature. A simple webhook doesn't need 15 acceptance criteria. A multi-system data pipeline does.

### 1. Header Card

Top of the document. Orients the reader in 10 seconds.

- **Title**: The feature/project name
- **Objective**: One paragraph — what are we building and why? State the problem from the user's perspective, then the solution. Be specific — name the systems, integrations, and outcomes involved.
- **Badges**: Tech stack, effort estimate, integrations involved — rendered as styled pills

### 2. Definition of Done (Project-Level)

3-5 bullet criteria that define when the entire PRD is complete. These are the acceptance criteria for the project as a whole, not individual requirements. Render as checkboxes.

### 3. Scope Boundary

Explicit in/out of scope rendered as a distinct section. Use ✗ markers for out-of-scope items. Aggressive scoping prevents scope creep — when in doubt, put it out of scope and note it as a potential follow-up.

### 4. User Stories

Numbered list of user stories. Each story follows the format:

> N. As a [role], I want [capability], so that [outcome].

User stories matter here because they help both humans and LLMs understand the PRD from the user's perspective. They surface edge cases and operator scenarios that a purely technical spec might miss. Be exhaustive — cover the happy path, error states, edge cases, and admin/operator scenarios. Aim for 8-15 stories depending on complexity.

Render as a styled numbered list inside a surface card.

### 5. Data Flow / Architecture Diagram


When the PRD involves multiple components, services, or data transformations, include a Mermaid diagram. Read `references/mermaid-patterns.md` for monday-themed Mermaid config and common patterns.

Use diagrams when they clarify — not on every PRD. A single-file change doesn't need a flowchart.

### 6. Technical Specification

This is the heart of the PRD. Render each subsection as a collapsible block. Include whichever of these are relevant:

- **Data Model / Source Format Mapping**: Field mappings, column definitions, types, constraints. Use HTML tables for clarity — they're scannable and unambiguous. When describing how data transforms from one shape to another (CSV columns to API fields, form inputs to DB columns), always use a table.

- **API Contracts**: Endpoints, methods, request/response shapes. Include rate limits and error handling.

- **Normalization & Validation Rules**: How inputs are cleaned, transformed, validated. Be explicit about edge cases (missing fields, bad formats, encoding issues).

- **Configuration & Environment**: What needs to be configured at deploy time. Use `[ASK OPERATOR]` placeholders for values the user/operator must provide (API keys, portal IDs, form GUIDs, etc.). This makes it easy to grep for open items.

- **Integration Points**: Which external systems are involved and how they connect.

### 7. Acceptance Criteria

Numbered list of testable statements rendered as checkboxes. Each criterion should be binary — it either passes or fails. Structure them as:

> GIVEN [context], WHEN [action], THEN [expected result].

Cover: happy path, error/edge cases, performance requirements, notification/logging expectations.

The reason for GIVEN/WHEN/THEN format is that it forces precision — "the system should handle errors gracefully" is useless, but "GIVEN a row with no email, WHEN the agent processes it, THEN the row is skipped and logged to the error summary" is something an engineer can build and test.

### 8. Milestones (if applicable)

If the work can be phased, break it into numbered milestones. Each milestone should be independently shippable or testable. Show as styled cards with:
- Milestone name and effort estimate
- What's included
- What's true when this milestone is complete

Skip this section for small, single-phase projects.

### 9. Open Questions

Unresolved decisions or unknowns. Use `[ASK OPERATOR]`, `[ASK STAKEHOLDER]`, or `[ASK ENGINEERING]` tags to indicate who needs to answer. Render as purple-accented callout blocks.

### 10. Performance & Rate Limit Spec (if applicable)

When the feature involves API calls, data processing, or batch operations, specify:
- Execution pattern (serial, parallel, batched)
- Rate limits and throttling strategy
- Success metrics (throughput, timing targets)

### 11. Success Criteria / Status Reporting (if applicable)

How the system reports completion. For example: status field updates, Slack notifications, error summaries, dashboards.

---

## Writing Principles

These principles matter because a PRD that doesn't follow them creates confusion downstream and wastes engineering time:

**Be concrete, not abstract.** Instead of "the system should handle errors gracefully," write "if the email field is missing or contains no `@`, skip the row and log it to the error summary." Engineers can't build from vibes.

**Use tables for data mappings.** Whenever data transforms from one shape to another, use an HTML table. This is non-negotiable — inline text descriptions of field mappings are error-prone and hard to scan.

**Mark operator decisions clearly.** When something depends on a value the user must provide, use the `[ASK OPERATOR]` tag inline. This makes it easy to search for open items before handoff.

**Write acceptance criteria that a QA engineer could execute.** Each criterion should describe a specific scenario and its expected outcome. If you can't test it, it's not a criterion — it's a wish.

**Scope aggressively.** A good "Out of Scope" section prevents scope creep. When in doubt, put it out of scope and note it as a potential follow-up.

**Match the complexity.** A simple webhook integration doesn't need milestones, performance specs, and 15 acceptance criteria. A multi-system data pipeline does. Use judgment.

---

## HTML Output

The PRD is a single, self-contained `.html` file styled with monday.com's dark theme. Read these references before generating:

- `references/sample-prd.html` — **Start here.** A complete example PRD (Event Lead Ingest Agent) showing every section, component, and style in action. Use this as your primary structural and visual reference.
- `references/design-tokens.md` — Full CSS variable set and component styles.
- `references/mermaid-patterns.md` — Monday-themed Mermaid diagram config and common patterns.
- `references/sample-plan.html` — An implementation plan example for additional styling reference (plans and PRDs share the same design system).

### Key Requirements

- **Single file, zero dependencies** (except Mermaid CDN and Google Fonts)
- **All CSS inline** in `<style>`, all JS inline in `<script>`
- **Poppins font** from Google Fonts CDN (400, 600 weights)
- **Mermaid diagrams** rendered client-side via CDN with monday theme variables
- **Collapsible sections** for technical spec subsections (click to expand/collapse, chevron indicator)
- **Checkboxes** for Definition of Done and Acceptance Criteria (real `<input type="checkbox">` — they don't persist, they're for visual tracking)
- **Styled tables** for data mappings (dark surface background, bordered cells)
- **`[ASK OPERATOR]` callouts** rendered as warning-styled blocks with yellow left border
- **Progress indicator** at the top showing completion of acceptance criteria checkboxes

### Design System Summary

Read `references/design-tokens.md` for the complete set. Key tokens:

- Background: `#000000` / Surface: `#232427` / Surface alt: `#2D3035`
- Text: `#ffffff` / Secondary: `#c3ced8` / Muted: `#a0a0a0`
- Purple (brand): `#6164ff` / Green (success): `#00c875` / Yellow (warning): `#ffcb00` / Red (risk): `#ff3d57`
- Font: Poppins / Mono: SF Mono, Fira Code, Consolas
- Spacing: `vmin` units via CSS variables (`--space-1` through `--space-10`)

### Additional Table Styles

Since PRDs use data mapping tables heavily (unlike implementation plans which focus on code), add these styles:

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-3) 0;
  font-size: var(--text-body-sm);
}

.data-table th {
  background: var(--color-surface);
  color: var(--color-purple-light);
  font-weight: var(--weight-semibold);
  text-align: left;
  padding: var(--space-2) var(--space-3);
  border-bottom: 2px solid var(--color-purple);
  font-size: var(--text-caption);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table td {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}

.data-table tr:hover td {
  background: rgba(97, 100, 255, 0.04);
}

.data-table .skip {
  color: var(--color-red);
  font-weight: var(--weight-semibold);
  font-family: var(--font-main);
}
```

### Operator Callout Styles

```css
.operator-callout {
  border-left: 3px solid var(--color-yellow);
  background: rgba(255, 203, 0, 0.06);
  padding: var(--space-3) var(--space-4);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  margin: var(--space-3) 0;
  font-size: var(--text-body-sm);
}

.operator-callout .operator-tag {
  font-weight: var(--weight-semibold);
  color: var(--color-yellow);
  font-size: var(--text-caption);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}
```

### Acceptance Criteria Styles

```css
.acceptance-criteria {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  margin: var(--space-5) 0;
}

.ac-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--text-body-sm);
}

.ac-item:last-child {
  border-bottom: none;
}

.ac-item input[type="checkbox"] {
  accent-color: var(--color-green);
  margin-top: 3px;
  flex-shrink: 0;
}

.ac-number {
  color: var(--color-purple);
  font-weight: var(--weight-semibold);
  min-width: 3ch;
  flex-shrink: 0;
}

.ac-given { color: var(--color-text-muted); }
.ac-when { color: var(--color-purple-light); }
.ac-then { color: var(--color-green); }
```

---

## Execution Handoff

After saving the PRD, offer:

**"PRD saved to `prd-<feature-name>.html`. Open it in your browser to review.**

**Next steps:**
1. **Review** — Check the acceptance criteria and open questions
2. **Resolve** — Answer any `[ASK OPERATOR]` items
3. **Build** — Hand off to engineering or start implementation"

---

## Remember

- Be concrete and specific — name the systems, fields, and endpoints
- Use tables for ALL data mappings, no exceptions
- Use `[ASK OPERATOR]` for any value the user must provide
- Write acceptance criteria in GIVEN/WHEN/THEN format
- Include a Mermaid diagram when there are 3+ components or a non-trivial data flow
- Scope aggressively — a good Out of Scope section is just as important as the spec
- Match visual and content depth to the project's complexity
- The PRD is a build spec, not a vision doc
