# Brainstorm modes

## Mode table

| Mode | What it does | Runner | Trigger phrase examples |
|---|---|---|---|
| `explore` | 2–3 blind parallel voice agents explore angles; coordinator synthesizes | parallel subagents (`agents/`) | "brainstorm this", "let's explore", "help me think through X", "WDYT", "fresh perspective" |
| `sharpen` | same council, sharpen mode prompt — distill to strongest core | parallel subagents | "sharpen this", "what's the core of this", "cut the noise" |
| `attack` | same council, attack mode prompt — find fatal flaws ruthlessly | parallel subagents | "attack this", "play devil's advocate", "stress test this", "challenge my idea", "find holes" |
| `panel` | named-persona panel from `agents/` (advisors); 4 distinct viewpoints | parallel subagents | "board of advisors", "4 perspectives", "multiple viewpoints", "panel on this" |
| `grill` | 1-question-at-a-time relentless interview in main conversation | main conversation | "grill me", "interview me about this", "stress-test my thinking" |
| `zoom-out` | single turn: map modules/callers/big-picture context | main conversation | "zoom out", "bigger picture", "how does this fit", "I don't know this area" |
| `design` | Spike / Bounded / Architectural classify → gates → 2–3 approaches + recommendation → spec to `docs/specs/` → self-review → hand off to `plan` | main conversation | "let's design this", "design X", "I want to build X", "plan this out", "architect this" |

## Runner types

- **Parallel subagents:** dispatch blind via Agent tool; each persona file is in `agents/`; coordinator labels output.
- **Main conversation:** single-turn or interactive; no subagents spawned.

## Explicit arg syntax

```
/sir-albert:brainstorm                          — auto-detect from phrase table
/sir-albert:brainstorm <mode>                   — force mode
/sir-albert:brainstorm panel --voices graham,verna <idea>  — panel with named voices
/sir-albert:brainstorm attack <idea>            — attack mode
```
