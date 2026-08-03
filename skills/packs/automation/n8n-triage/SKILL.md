---
name: n8n-triage
description: >
  Triage a failed n8n workflow execution. Paste an n8n execution URL and this skill pulls
  the failed node, reads the error, and proposes a concrete fix. Uses the n8n-mcp server
  (n8n at n8n.bigbrain.me). Triggers: "/n8n-triage", "n8n execution failed",
  "debug this n8n run", paste of an n8n execution URL (e.g. n8n.bigbrain.me/workflow/.../executions/...),
  "why did my workflow fail".
---

Boot from `os/PREAMBLE.md`.

# n8n Triage

## Mission

Diagnose a failed n8n execution from a URL. Find the failing node, explain the error in plain
terms, and propose an actionable fix — without deploying anything to production unless Gal
explicitly confirms.

## MCP server

All n8n calls go through **n8n-mcp** (instance: `n8n.bigbrain.me`). Tools used in this skill:

| Tool | Purpose |
|---|---|
| `mcp__n8n-mcp__tools_documentation` | Orientation — call once if unsure which tool applies |
| `mcp__n8n-mcp__search_nodes` | Look up unfamiliar node types mentioned in the error |
| `mcp__n8n-mcp__get_node` | Fetch schema/docs for the failing node type |
| `mcp__n8n-mcp__validate_node` | Validate a proposed node config before suggesting it |
| `mcp__n8n-mcp__validate_workflow` | Validate the full workflow JSON if Gal pastes it |

> The n8n-mcp server does **not** expose a live execution-fetch tool in this environment.
> Gal must paste (or describe) the execution error. The URL is used for context/linking only.

## Workflow

### Step 1 — Parse the execution URL

Extract from the URL:
- **Workflow ID** — the segment after `/workflow/`
- **Execution ID** — the segment after `/executions/`

Example: `https://n8n.bigbrain.me/workflow/abc123/executions/456` → workflow `abc123`, execution `456`.

If no URL is supplied, ask for it or for the raw error text.

### Step 2 — Identify the failing node

Ask Gal to paste the error output from the execution (the "Error" panel in the n8n UI), or
read it from whatever context is provided. Key things to extract:

- **Node name** — shown in the error header
- **Node type** — e.g. `nodes-base.httpRequest`, `nodes-base.slack`
- **Error message** — the human-readable description
- **Error code / status** — HTTP status, n8n error code, or stack trace hint

If the node type is not obvious, use `mcp__n8n-mcp__search_nodes` with keywords from the
node name to identify it.

### Step 3 — Fetch node docs

Call `mcp__n8n-mcp__get_node` with `detail: "standard"` for the identified node type.
Focus on:

- Required fields that may be misconfigured
- Auth/credential requirements
- Known incompatibilities (API version mismatches, missing scopes)

### Step 4 — Diagnose

Map the error to one of these common root causes:

| Category | Examples |
|---|---|
| **Auth / credential** | 401 Unauthorized, expired OAuth token, wrong credential type |
| **Malformed request** | 400 Bad Request, wrong field name, type mismatch |
| **Downstream API error** | 429 Rate limit, 5xx server error, API deprecation |
| **Expression error** | `Cannot read property … of undefined`, broken `{{ }}` expression |
| **Connection / timeout** | ECONNREFUSED, ETIMEDOUT |
| **Missing required field** | n8n "required field not set" validation error |

State the category clearly, then give the specific cause.

### Step 5 — Propose a fix

Provide a concrete, copy-pasteable fix:

- For credential issues: exact credential type to select and fields to check
- For bad request: the corrected field name / value / expression
- For API errors: the correct endpoint or request shape
- If a node config change is needed, sketch the corrected node JSON and validate it with
  `mcp__n8n-mcp__validate_node` before presenting it

Keep the fix to the minimum necessary change. Don't rewrite the whole workflow.

### Step 6 — Sub-workflow refactor note

After the fix, append a short **"Consider extracting this to a sub-workflow"** note if the
failing node is part of a long chain (more than ~6 nodes in one path) or is called from
multiple branches. Pattern: **break the monolith into a sub-workflow executor** — isolate
the brittle integration (e.g. the API call that keeps failing) into a dedicated workflow
with its own error handler and retry logic, then call it via the `Execute Workflow` node from
the parent. Benefits: isolated testing, independent retry, cleaner error surfaces. Keep this
note brief (3–5 sentences); don't force it if the workflow is simple.

## Hard rules

1. **Never deploy to n8n prod without asking.** Any fix that involves saving or activating a
   workflow must be confirmed by Gal first. Propose, don't push.
2. **Never guess at credentials.** If the fix requires a new credential, say which type and
   what fields are needed — do not fill in values.
3. **Always validate** a proposed node config with `mcp__n8n-mcp__validate_node` before
   presenting it as the fix.
4. **If execution data is unavailable** via MCP, ask Gal to paste the error text from the
   n8n UI — do not fabricate error messages.
