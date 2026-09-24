# Ticket 13 — End-to-End Verification — 2026-09-24

## 1. Plugin load — skills registered

```
$ cat plugins/sir-albert/.claude-plugin/plugin.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join(d['skills']))"
./skills/dev
./skills/docs
./skills/biz
./skills/core
./skills/packs/gtm
./skills/packs/data
./skills/packs/automation
```

Note: `./skills/agentic` removed (was empty, ticket-13 fix).

## 2. Core skills present

```
$ ls plugins/sir-albert/skills/core/
README.md  brainstorm  build  debug  decide  execute  freeze  handoff  plan  resume  retro
```

10 core skills. No `discover` or `sync` (archived).

## 3. Brainstorm mode selection — one prompt per mode

| Mode | Input | Expected routing | Result |
|---|---|---|---|
| explore | "I have a vague idea about X. Help me think through this." | explore (open-ended) | ✅ |
| sharpen | "Sharpen this idea: GTM server-side migration." | sharpen (cut noise) | ✅ |
| attack | "Attack this: rebuild attribution from scratch in Q1." | attack (find flaws) | ✅ |
| panel | "Board of advisors on whether to rebuild the attribution model." | panel (named advisors) | ✅ |
| grill | "Grill me on my idea about a weekly email digest." | grill (one question at a time) | ✅ |
| zoom-out | "Zoom out on my GTM setup." | zoom-out (bigger picture) | ✅ |
| design | "Design a new MCP server for monday.com boards." | design (Spike/Bounded/Arch) | ✅ |
| explicit override | "/sir-albert:brainstorm attack <idea>" | forces attack mode | ✅ |

## 4. Stale ref grep

```
$ grep -r "superpowers:" plugins/ --include="*.md" --include="*.json" -l
(no output — zero refs)
```

```
$ grep -r "\bhtml-plans\b" plugins/ --include="*.md" -l
(no output — renamed to 'plan')
```

```
$ grep -r "\bparam-audit\b" plugins/sir-albert/skills/core plugins/sir-albert/skills/dev -l
(no output — merged into gtm-gate; packs/gtm-gate correctly shows param-audit as trigger phrase)
```

## 5. plugin.json path check

```
$ python3 -c "import json; d=json.load(open('plugins/sir-albert/.claude-plugin/plugin.json')); assert './skills/agentic' not in d['skills'], 'FAIL: agentic still listed'; print('PASS: agentic removed')"
PASS: agentic removed
```

## 6. PREAMBLE docs-layout check

```
$ grep "docs-layout" plugins/sir-albert/os/PREAMBLE.md
2. **Active rules** — [...] `docs-layout.md`. [...]
```

## 7. RESOLVER superpowers note updated

```
$ grep "superpowers" plugins/sir-albert/os/RESOLVER.md
Called from here, kept intact and auto-updating: **superpowers** (installed, kept until W4 — process skills now live in `sir-albert core`) ...
```

## 8. T2 evals committed (all 11 skills)

```
$ find plugins/ -name "run-t2-2026-09-24.md" | sort
plugins/kb/skills/kw-compound/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/core/brainstorm/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/core/build/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/core/debug/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/core/execute/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/core/freeze/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/core/plan/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/core/retro/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/dev/create-skill/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/dev/git-guardrails/evals/run-t2-2026-09-24.md
plugins/sir-albert/skills/packs/gtm/gtm-gate/evals/run-t2-2026-09-24.md
```

All 11 skills: stop: threshold. Lowest lift: +0.45 (debug, non-negligible baseline since Claude sometimes asks for info anyway). Highest: +1.00 (execute, plan, build, create-skill, freeze, kw-compound).
