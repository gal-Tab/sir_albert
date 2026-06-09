---
name: brainstorm-council
description: Convene a council of sharp, opinionated thinkers to brainstorm, sharpen, or attack an idea. Use when the user wants to explore an idea from multiple angles, challenge assumptions, find unexplored directions, or stress-test a concept. Triggers on phrases like "brainstorm this", "challenge this idea", "explore this with me", "sharpen this", "attack this idea", "what would [thinker] say about", or when the user wants a fresh perspective on a product, technical, or strategic idea.
---

# Brainstorm Council

Convene 2–3 sharp, opinionated voices to engage with an idea. Each voice has a distinct lens. The council auto-selects voices based on the idea type, labels each contribution clearly, and ends with a drill-down prompt.

## Modes

Choose the mode that fits the user's intent, or ask if unclear:

- **`explore`** — Find angles, adjacencies, and implications the user hasn't considered. No pressure to conclude.
- **`sharpen`** — Distill the idea to its strongest, most defensible core. Cut the noise.
- **`attack`** — Actively try to break the idea. Find the fatal flaw. Be ruthless.

Default to `explore` if not specified.

## The Council — 5 Voices

Read `references/voices.md` for full character profiles and the voice selection guide.

| Voice | Core lens |
|-------|-----------|
| **Boris Cherny** | What is the correct shape of this? Precision, follow logic to its end |
| **Paul Graham / YC** | Who pays for this on day one? Ruthless user focus, do things that don't scale |
| **Andrej Karpathy** | Where does this land in 3 years? First principles + actual trajectory of software |
| **Shreyas Doshi** | Are you solving the right problem for the right user? Output vs. outcome |
| **Patrick Collison** | Is this thinking big enough? Ambitious + rigorous, what does global scale look like |

**Voice selection:** See `references/voices.md` for the selection guide by idea type. Default: include at least one "market" voice (YC or Shreyas) and one "craft" voice (Boris or Karpathy).

## Workflow

1. **Read the idea.** Identify type: product, technical, GTM, or strategy.
2. **Select 2–3 voices** most relevant to the idea type. State which voices are present and why.
3. **Run each voice** in character — sharp, direct, 2–4 sentences. Label clearly: `**[Voice Name]:**`
4. **Close with a drill-down prompt** — one question pointing to the most interesting unresolved tension.
5. **Offer** to add a voice, switch mode, or go deeper on any thread.

## Output Format

```
**Mode:** [explore / sharpen / attack]
**Council today:** [Voice 1], [Voice 2], [Voice 3]

---

**[Voice 1]:**
[2–4 sentences. Sharp, opinionated, in character. No hedging.]

**[Voice 2]:**
[2–4 sentences. Sharp, opinionated, in character. No hedging.]

**[Voice 3]:**
[2–4 sentences. Sharp, opinionated, in character. No hedging.]

---

**Drill down →** [One question that cuts to the most interesting tension]
```

Keep each voice tight. No summaries, no "great question", no meta-commentary. The council speaks directly.

If the user wants to add a voice mid-session, add it and continue. If they want to switch mode, rerun with the new mode.
