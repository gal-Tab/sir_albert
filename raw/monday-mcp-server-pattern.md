---
title: "monday.com MCP Server Pattern"
type: concept
kw_capture: true
kw_date: 2026-08-02
aliases: ["Sphera mcp-server", "monday MCP microservice", "createMCPTool service", "OAuth-brokered upstream provider"]
domain_tags: [monday, mcp, trident, sphera, microservices, ads-api]
source_refs: []
created: 2026-08-02
updated: 2026-08-04
tags: [monday, mcp, trident, sphera, oauth, marketing-ai-tools, google-ads-mcp]
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

## Implementation learnings (from building google-ads-mcp, 2026-08-03/04)

`google-ads-mcp` was built mirroring this pattern (PR `DaPulse/marketing-ai-tools#528`) and validated live against a real Google Ads MCC. It confirmed the skeleton and surfaced three non-obvious gotchas that will recur on the next MCP service:

### 1. Register the service in Sphera — generator, NOT copy
Scaffolding a new MS by copying an existing service dir (`rsync` + rename) leaves it **unregistered in Sphera**. Monorepo CI then fails at the `prepare` / `export-repo-params` step: `GET https://sphera.monday.beer/api/services/<name>` → **404** → `TypeError: Cannot read properties of undefined (reading 'system')` → "Fail to evaluate job outputs" → template error in `DaPulse/github-actions-shared` `ms-main-shared-pipeline.yaml`. **Symptom→cause: a 404 on `/api/services/<name>` in CI == the service isn't registered in Sphera.** Fix: create/onboard the service through the Sphera generator so the services API returns `{ system, ... }`.

### 2. Local run with env secrets (`.env.override` + `LOAD_SECRETS_FROM_ENV` + zombie ports)
`trident app --debug` (`yarn start:dev`) tries **AWS Secrets Manager by default** (fails locally) and does **not** forward arbitrary shell env to the app. Put local secrets in **`.env.override`** (the gitignored local-secrets file — NOT `.env.local`, which is not ignored) and boot with inline prefixes: `set -a; . ./.env.override; set +a; LOAD_SECRETS_FROM_ENV=true yarn start:dev`. It spawns a **`tsx watch` child that survives killing the yarn/nohup wrapper** and keeps holding ports **3000** (app) + **3130** (internal) — so new boots fail `EADDRINUSE` and curl silently hits the stale zombie (very confusing). Always kill by port: `lsof -tiTCP:3000 -sTCP:LISTEN | xargs kill` (and 3130).

### 3. Gateway onboarding is config-only now
The mcp-gateway supports **config-only external OAuth providers** — mechanism landed in `DaPulse/mcp-tools#925`; FB example in merged **#944**. To add a provider: `oauth` block in `external-tools/external-mcps/mcpServers.json` (auth/token URLs, scope, PKCE, `supportsRefresh`, `url`→the self-hosted MS) + register snapshot in `src/index.ts` + run the `add-external-oauth-mcp` skill to populate `src/tool-schemas/<provider>.json` + OAuth client id/secret in the **mcp-gateway** Sphera `oauthCredentials` secret. The gateway brokers per-user tokens (**email-keyed**, Redis vault, auto-refresh) and forwards them as `Authorization: Bearer` — the MS just needs a Bearer-override path. **App-level secrets that aren't per-user** (e.g. Google's `developer-token`) go in the **MS's own** Sphera secrets, not the gateway. Per-user/tool permissions at **`bigbrain.me/mcp/admin`** (service owner gets admin). Gateway owner: **Itay Maslovich** (`U07AJ19CZKN`) — Shai Etzion, who built `facebook-ads-mcp`, left monday.

## Related Concepts
- Model Context Protocol (MCP) — general standard (practitioner knowledge; no KB page needed).

## See Also
- Reference implementation: `DaPulse/marketing-ai-tools` → `microservices/facebook-ads-mcp` [STATED]
- Second implementation: `google-ads-mcp` — built + live-validated, PR `DaPulse/marketing-ai-tools#528` open as of 2026-08-04; mirrors this pattern with a widened store + OAuth mint/cache for Google's heavier auth [STATED]

## Source / Origin
Captured from session on 2026-08-02, while planning a `google-ads-mcp` service by reverse-engineering Shai Etzion's `facebook-ads-mcp` to reuse its architecture.
