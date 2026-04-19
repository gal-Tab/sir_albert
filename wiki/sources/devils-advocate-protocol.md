---
title: "Devil's Advocate Protocol"
type: source
slug: devils-advocate-protocol
created: 2026-04-19
updated: 2026-04-19
key_entities: []
key_concepts:
  - pre-commitment-adversarial-reasoning
tags: [decision-making, strategy, llm-patterns]
---

# Devil's Advocate Protocol

## Overview
A protocol established by Majestic Labs for pre-commitment adversarial reasoning. It is designed to interrupt the pattern where LLMs (and humans) commit to answers early and rationalize backward.

## Key Claims
- Decisions must be stress-tested *before* execution or lock-in.
- The adversarial challenge must attack the strongest version of an argument (Steel-Manning) rather than providing token objections.
- If no viable alternatives exist or the task is purely mechanical, the protocol should be skipped.

## Workflow / Process
1. **Identify the Commitment:** State the decision, the inclination, and the rationale.
2. **Steel-Man the Opposition:** Find non-obvious failure modes, question assumptions, and identify opportunity costs.
3. **Defend or Pivot:** Re-evaluate the inclination based on the adversarial pass.
4. **Calibrate Confidence:** Output the final recommendation along with key assumptions that must hold and signals to monitor.
