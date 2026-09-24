# Task graph — execute skill reference

## Concepts

**Task graph:** A directed acyclic graph of tickets where edges represent blocking dependencies. Ticket B is blocked by ticket A if A's output is required before B can start.

**Frontier:** The set of tickets that are currently unblocked — all their `Blocked by:` tickets are in the "done" set. The frontier is the work that can be started right now.

**Frontier expansion:** After a ticket completes and is merged, re-evaluate the graph. Any ticket whose last remaining blocker just completed becomes part of the new frontier.

## How to build the graph

1. Read all tickets. For each, record: `{id, slug, blocked_by: [list of ids]}`.
2. Start with `done = {}`.
3. `frontier = {tickets where blocked_by is empty or all blocked_by ids are in done}`.
4. As each implementer finishes: add its id to `done`, re-compute frontier.

## Example

```
01-schema        blocked_by: —           → frontier at start
02-auth-service  blocked_by: 01          → unblocked after 01 done
03-login-route   blocked_by: 01, 02      → unblocked after 02 done
04-tests         blocked_by: 03          → unblocked after 03 done
```

Initial frontier: `[01]`
After 01: frontier `[02]`
After 02: frontier `[03]`
After 03: frontier `[04]`

## Concurrency

Tickets with no shared blockers can run in parallel. Example: if both 02-auth-service and 05-email-service are blocked only by 01-schema, both enter the frontier simultaneously and can be dispatched as concurrent subagents.
