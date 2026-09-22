---
name: discovery-lens
description: >
  Use when the user says "brainstorm this", "let's explore", "help me think through X",
  "sharpen this idea", "attack this idea", "what are we missing", "WDYT", "fresh perspective",
  "AI-first perspective", "discovery phase", "explore this with me", "challenge this idea",
  wants multiple viewpoints or a stress test on a concept, or is entering a discovery /
  early-thinking phase on a product, technical, GTM, or strategic idea — fires immediately,
  without waiting for an explicit slash command. Convenes 2–3 sharp, opinionated voices to
  explore, sharpen, or attack the idea from multiple angles.
---

# Discovery Lens

Convene 2–3 sharp, opinionated voices to engage with an idea. Each voice has a distinct lens. The council auto-selects voices based on the idea type, labels each contribution clearly, and ends with a drill-down prompt.

## Modes

Choose the mode that fits the user's intent, or ask if unclear:

- **`explore`** — Find angles, adjacencies, and implications the user hasn't considered. No pressure to conclude.
- **`sharpen`** — Distill the idea to its strongest, most defensible core. Cut the noise.
- **`attack`** — Actively try to break the idea. Find the fatal flaw. Be ruthless.

Default to `explore` if not specified.

## The Council — 8 Voices

Each voice is a standalone agent prompt in `agents/`. Read `references/voices.md` for the
full selection index and idea-type guide.

| Voice | Core lens |
|-------|-----------|
| **Boris Cherny** | What is the correct shape of this? Precision, follow logic to its end |
| **Paul Graham / YC** | Who pays for this on day one? Ruthless user focus, do things that don't scale |
| **Andrej Karpathy** | Where does this land in 3 years? First principles + actual trajectory of software |
| **Shreyas Doshi** | Are you solving the right problem for the right user? Output vs. outcome |
| **Patrick Collison** | Is this thinking big enough? Ambitious + rigorous, what does global scale look like |
| **Elena Verna** | Does this loop or compound, or die when you stop pushing it? Growth systems over campaigns |
| **Ron Kohavi** | Is that a real effect? Counterfactuals, causal rigor, metric-gaming skepticism |
| **Michael Seibel** | What's stopping you from testing this today? Execution bias, anti-overthinking |

**Voice selection:** See `references/voices.md` for the selection guide by idea type. Default: include at least one "market" voice (YC, Verna, or Shreyas) and one "craft" voice (Boris or Karpathy).

## Workflow

1. **Read the idea.** Identify type: product, technical, GTM, growth/metrics, or strategy.
2. **Select 2–3 voices** most relevant to the idea type. State which voices are present and why.
3. **Dispatch each selected voice in parallel via the Agent tool** — one fresh, tool-less
   subagent per voice, all sent in a single message, each blind to the others' responses.
   For each voice, take the full contents of `agents/<voice>.md` and fill in:
   - `{{idea}}` — the user's idea, verbatim
   - `{{mode_instruction}}` — the sentence from the active mode's row in **Modes** above
   Use the filled template as that subagent's prompt.
4. **Collect each subagent's raw statement** and label it: `**[Voice Name]:**`
5. **Close with a drill-down prompt** — one question pointing to the most interesting unresolved tension between the voices' responses.
6. **Offer** to add a voice, switch mode, or go deeper on any thread.

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
