---
name: brainstorm
description: Use when exploring angles, sharpening thinking, attacking a plan, running a panel of advisors, drilling an idea with relentless questions, zooming out on context, or designing a solution. Triggers on "brainstorm this", "grill this", "attack this", "zoom out", "play devil's advocate", "let's design this", "board of advisors", "sharpen this", "stress test this", "find holes in this", "fresh perspective", "4 perspectives", "want to build X".
---

# brainstorm

Boot from `os/PREAMBLE.md`. For `design` mode also load `os/rules/docs-layout.md`.

## Mode selection

State the mode picked and one-line reason before running. Explicit arg overrides auto-detect.

| Mode | Trigger phrases | Runner |
|---|---|---|
| `explore` | "brainstorm this", "let's explore", "help me think through X", "WDYT", "fresh perspective" | parallel subagents |
| `sharpen` | "sharpen this", "what's the core of this", "cut the noise" | parallel subagents |
| `attack` | "attack this", "play devil's advocate", "stress test this", "challenge my idea", "find holes" | parallel subagents |
| `panel` | "board of advisors", "4 perspectives", "multiple viewpoints", "panel on this" | parallel subagents |
| `grill` | "grill me", "interview me about this", "stress-test my thinking" | main conversation |
| `zoom-out` | "zoom out", "bigger picture", "how does this fit", "I don't know this area" | main conversation |
| `design` | "let's design this", "design X", "I want to build X", "plan this out", "architect this" | main conversation |

**Explicit arg syntax:**
```
/sir-albert:brainstorm                           — auto-detect
/sir-albert:brainstorm <mode>                    — force mode
/sir-albert:brainstorm panel --voices graham,verna <idea>
/sir-albert:brainstorm attack <idea>
```

## Per-mode execution

### explore
- Dispatch 2–3 blind parallel voice agents from `agents/` via the Agent tool (fresh subagent per voice, each unaware of the others).
- Select voices from `references/voices.md` based on topic domain.
- Each voice responds in character (2–4 sentences, no meta-commentary).
- Coordinator labels each voice's output by name, then synthesizes: strongest agreement + sharpest tension.
- Do not reveal which voice files were selected until after synthesis.

### sharpen
- Same parallel dispatch as `explore` — same voices, same blind structure.
- Mode instruction to each voice: "Distill to the strongest core. What is the single most important insight? Cut everything else."
- Synthesize: one-sentence core + what was cut and why.

### attack
- Dispatch 2–3 voices including `agents/devils-advocate.md`.
- Mode instruction: "Find the fatal flaw. Steel-man the strongest objection. Name the most dangerous assumption. Be genuinely adversarial."
- Each voice attacks independently (blind). Coordinator labels and synthesizes: top 2–3 threats + whether they are fatal or manageable.

### panel
- Dispatch the 4 board-advisor agents from `agents/`: `board-advisor-tech-lead.md`, `board-advisor-boris-product.md`, `board-advisor-operator.md`, `board-advisor-metrics.md`.
- If `--voices` flag present, use the named voices instead.
- Each advisor responds in full character (2–4 sentences, no hedging).
- Coordinator labels by role, then gives a single unified recommendation or the key tradeoff to decide.

### grill
- One question at a time in main conversation. Ask the next question only after the user answers.
- Questions are relentless — push on assumptions, definitions, evidence, and consequences.
- If docs are provided (paste or file reference), ground questions in the doc content.
- Continue until user says stop or a clear answer crystallizes.
- No synthesis until explicitly asked.

### zoom-out
- Single-turn main conversation response.
- Map the current module/topic to its callers, dependents, and big-picture context.
- Use domain glossary vocabulary (from `os/state/` if available).
- Go up at least one layer of abstraction. Identify what system-level constraints apply.
- Output: a brief map (bullets or 2-column table: "this component / wider system"), then 1–2 implications for the current question.

### design
- **Classify first** (out loud, before any design work): Spike / Bounded / Architectural.
  - **Spike:** time-boxed exploration; unknown is the feasibility. Gate: agree on timebox + question to answer.
  - **Bounded:** well-understood scope, one team. Gate: user approves the problem statement.
  - **Architectural:** cross-system, affects data contracts or interfaces. Gate: stakeholder sign-off documented.
- **Hard gate:** do not proceed to approaches until the gate artifact for the path is confirmed.
- Run `kb:learn-research` first to pull past decisions relevant to this domain.
- Present 2–3 approaches with trade-offs; give a clear recommendation.
- Write spec to `docs/specs/YYYY-MM-DD-<topic>.md` (OKF frontmatter: status/date/owner).
- Self-review the spec: confirm gate artifact is satisfied, no implementation started, approaches are real alternatives (not one real + two strawmen).
- Hand off explicitly: "Spec written. Ready to run `/sir-albert:plan` to break this into tickets."
