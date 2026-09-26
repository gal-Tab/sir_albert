# 02 — HOOK_CONTEXT.md (injection template)

**Blocked by:** 01
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 1 — Injection text

## Goal

Create `plugins/sir-albert/hooks/HOOK_CONTEXT.md`, the static template that `session-start.sh` reads and fills. This file is the canonical source for injection text — edit it (not the script) to change what Claude Code sees on startup.

## Steps

1. Create `plugins/sir-albert/hooks/HOOK_CONTEXT.md` with the draft text from the spec (§Injection text):
   - The core skill table (10 rows)
   - Map + rules pointers (RESOLVER.md, docs-layout.md)
   - `{PACK_LIST}` placeholder (replaced at runtime)
   - `{RESUME_HINT}` placeholder (replaced at runtime; empty string when no handoff found)
2. Measure baseline character count: `wc -c plugins/sir-albert/hooks/HOOK_CONTEXT.md` — record in a comment at the top of the file.
3. Verify the table renders correctly in a markdown viewer or `cat` — no broken pipes, no binary.

## Definition of Done

- [ ] `HOOK_CONTEXT.md` exists with the core skill table
- [ ] Both `{PACK_LIST}` and `{RESUME_HINT}` placeholders present
- [ ] Character count ≤ 800 chars (static portion excluding placeholders)
- [ ] Passes `grep -c "{PACK_LIST}" plugins/sir-albert/hooks/HOOK_CONTEXT.md` → 1
