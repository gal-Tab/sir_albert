---
name: self-reflection
description: Triggered when the owner asks to improve your operations, behavior, or skills, or when performing a periodic self-reflection. Converts vague dissatisfaction or observed inefficiencies into concrete technical improvements (e.g., editing MEMORY.md, SOUL.md, USER.md, or custom skills).
---

# self-reflection

This skill transforms the agent's behavior based on user feedback or self-audits. Inspired by continuous evolution concepts (like SkillClaw), this protocol ensures the agent doesn't just "promise to do better" but makes durable, concrete, technical changes to its own system files, memory, or skills.

## Triggers

Use this skill when:
- The user expresses dissatisfaction with how you handled a task ("You should have done X instead of Y").
- The user explicitly asks you to improve or change a behavior ("Let's improve your coding process").
- You are prompted to perform a weekly or periodic self-reflection.
- You identify a recurring failure or inefficiency in your own operations.

## Core Principle
"I'll be more careful next time" is **NOT** a valid outcome. Every reflection must result in a concrete technical change: modifying a prompt, updating `MEMORY.md`, altering a skill's `SKILL.md`, or creating a new cron job.

## Workflow

### 1. Understand the Problem (Diagnose)
If the user's feedback is vague, ask 1-2 focused questions to pin down:
- What specifically went wrong? (Ask for a concrete example).
- What would "good" look like? (Expected vs. actual behavior).
- How important/frequent is this?

### 2. Deep System Scan
Audit ALL relevant parts of your system before proposing changes. 
- **Core Identity & Behavior:** Review `SOUL.md`, `MEMORY.md`, `USER.md`, `AGENTS.md`.
- **Skills:** Review existing `SKILL.md` files in the `skills/` directory.
- **Configuration:** Check currently active model, tools, or channel settings.
- **Cron Jobs:** Check scheduled heartbeat or reminder jobs.

*Rule: Read broadly, change surgically. Scan everything related, modify only what's needed.*

### 3. Diagnose & Propose
Present your findings to the user for approval BEFORE executing changes.
Structure your proposal:
1. **Root Cause:** What in the system caused the unwanted behavior?
2. **Proposed Changes:** Exactly which files (`MEMORY.md`, `SKILL.md`, etc.) will be edited, and what text will be added/removed.
3. **Side Effects:** Will this change impact other behaviors?
4. **Alternatives:** Are there other ways to solve this?

### 4. Implement Changes
After the user approves the plan, use your file editing tools (`edit` / `write`) or `cron` tool to make the actual changes. 

### 5. Verify & Document
- Document what changed and why (usually in `MEMORY.md` under a changelog or learned preferences section).
- If the change involves git-tracked files (like the `sir_albert` repo), commit the changes to preserve the evolution.

## Output Format (for Step 3 - Proposal)
Output should be in the user's preferred language (e.g., Hebrew).

🔍 **אבחון הבעיה (Root Cause):** [Brief explanation of why the agent acted incorrectly based on current system state]

🛠️ **שינויים מוצעים (Proposed Changes):**
- **[File Name / Skill]:** [Exact change to be made]
- **[File Name / System]:** [Exact change to be made]

⚠️ **תופעות לוואי (Side Effects / Trade-offs):** [Any potential risks or impacts on other tasks]

האם לאשר ולבצע את השינויים האלו בקבצי המערכת?
