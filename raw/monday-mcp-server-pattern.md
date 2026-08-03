---
title: "monday.com MCP Server Pattern"
type: concept
kw_capture: true
kw_date: 2026-08-02
aliases: ["Sphera mcp-server", "monday MCP microservice", "createMCPTool service", "OAuth-brokered upstream provider"]
domain_tags: [monday, mcp, trident, sphera, microservices, ads-api]
source_refs: []
created: 2026-08-02
updated: 2026-08-02
tags: [monday, mcp, trident, sphera, oauth, marketing-ai-tools]
---

# monday.com MCP Server Pattern

## Definition

The standard shape monday.com uses to expose a third-party API to LLM agents as an internal MCP (Model Context Protocol) server: a **thin TypeScript trident microservice**, Sphera-scaffolded as type `mcp-server` (system `bigbrain`), where the platform libraries handle transport and tool registration and the developer hand-writes only ~5 files. Reference implementation: `microservices/facebook-ads-mcp` in `DaPulse/marketing-ai-tools` (built by Shai Etzion, 2026-07).

## Context

### Skeleton — thin service, fat platform
- `src/app.ts` — default export extends `AppModule` (`@mondaydotcomorg/trident-backend-runtime`); `init()` calls `startServer()`.
- `src/server.ts` — builds an Express `Router`, mounts a global auth middleware, and calls `startServer` from `@mondaydotcomorg/http-server` with an `mcp` capability block; the platform does MCP transport + tool registration.
- Generator stubs (`clients/http`, `repl-console`, `constants`, `ignite-service.ts`) are left untouched.

### Transport / server config (in `server.ts`)
- `mcp: { enabled: true, tools, transport: 'streamable-http', sessionIdGenerator: undefined, route: '/mcp', serverInfo }` → **Streamable-HTTP, stateless**, served at `POST /mcp`, port **3000**.
- `auth.useAuthenticationMw: false` and `mcp.requireAuth: false` → monday JWT and MCP-layer auth are both OFF. The service authenticates nothing itself.

### Auth model — "OAuth-brokered upstream provider"
- The service holds **no** credentials of its own. A one-file middleware (`request-context.ts`) pulls `Authorization: Bearer <token>` off each request and stashes it in `AsyncLocalStorage`; the API client reads it via a getter (never passed as an argument).
- The **monday MCP gateway is the trust boundary** — it resolves the per-user token (from a vault, and in future via Okta SSO) and forwards it. Local dev passes the token the same way.

### Tools
- Declared with `createMCPTool` from `@mondaydotcomorg/mcp-core` (pinned, e.g. `3.25.0`); all tools live in one `src/tools/index.ts`.
- `inputSchema` is a **raw Zod shape** (object of Zod fields), NOT a wrapped `z.object`. `execute` returns `{ content: string /* JSON */, isError?: boolean }`.
- Read-only tools carry `annotations: { readOnlyHint: true }`. Shared Zod fragments are reused across tools.

### API client
- ~30-line `fetch` wrapper, base URL version-pinned to one constant, GET-only for read-only servers, errors returned as `{ content, isError: true }` rather than thrown.

### Tooling / deploy
- Key deps: `@modelcontextprotocol/sdk`, `@mondaydotcomorg/http-server`, `@mondaydotcomorg/mcp-core`, `@mondaydotcomorg/trident-backend-runtime`, `zod`. Tests via **vitest** (unit + api configs).
- No committed Dockerfile — injected from monday's dockerfile-registry via `.dockerrc.json`. Deploy via **Sphera / Okteto / Harmony**; CI at monorepo level. Scripts: `trident build`, `trident app --debug ./src/app.ts` (`start:dev`), `trident lint`.

### Gateway snapshot coupling
For the gateway to advertise tools *before* a user connects OAuth, a static JSON-Schema snapshot of the tools must be mirrored into `DaPulse/mcp-tools` (`external-tools/external-mcps/src/tool-schemas/<provider>.json`) and the provider registered. Update the snapshot whenever tools change.

### Adapting to an API with heavier auth
The FB pattern assumes a single bearer token and holds nothing server-side. APIs needing more — e.g. **Google Ads**: app-level `developer-token` + short-lived OAuth access token (~1h) + `login-customer-id` — require: widen the `AsyncLocalStorage` store, put app-level secrets in `.env`, and add a `refresh_token → access_token` mint+cache step. The `Authorization: Bearer` override stays the exact hook the gateway/Okta SSO uses later.

## Related Concepts
- Model Context Protocol (MCP) — general standard (practitioner knowledge; no KB page needed).

## See Also
- Reference implementation: `DaPulse/marketing-ai-tools` → `microservices/facebook-ads-mcp` [STATED]
- Future application: `google-ads-mcp` (in planning as of 2026-08-02, mirrors this pattern) [INFERRED]

## Source / Origin
Captured from session on 2026-08-02, while planning a `google-ads-mcp` service by reverse-engineering Shai Etzion's `facebook-ads-mcp` to reuse its architecture.
