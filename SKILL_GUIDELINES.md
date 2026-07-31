# SKILL.md Writing Guidelines

Skills tell the agent **what to do and when**. Keep them concise — the agent reads every word.

> ≤150 lines per SKILL.md. Put depth in `knowledge/` and `references/`, not in the skill body.

---

## Required Structure

```markdown
---
name: skill-name-in-kebab-case
description: One sentence — what task this handles and when to trigger it.
---

# Skill: [Human Name]

**Domain:** Messaging | Content | Media  
**Owner:** name@monday.com

## When to Use
- Bullet list of triggering phrases or task types
- Be specific — the agent uses this to decide whether to load this skill

## Workflow
Step-by-step instructions for the agent. Reference knowledge files, not inline.

1. Load `knowledge/<file>.md` for context
2. [action step]
3. [action step]

## DOs
- ✅ Specific rule with the why

## DON'Ts
- ❌ Common mistake to avoid

## Related
- [Other Skill](../other-skill/SKILL.md)
- [Knowledge file](../../knowledge/relevant-file.md)
```

---

## Rules

| Rule | Detail |
|---|---|
| ≤150 lines | Longer skills slow the agent down and increase errors |
| ≤3 workflow steps | Complex workflows → break into multiple skills |
| Knowledge in `knowledge/` | Rich context (brand guides, playbooks) belongs there, not inline |
| Connector usage → `connectors/` | If the skill touches an external platform, load the connector skill |
| Fully qualified paths | Always use relative paths from the skill file (`../../knowledge/`) |
| No duplicate content | If two skills share rules, extract to a knowledge file and reference it |

---

## Skill vs Knowledge vs Connector — When to Use Each

| Type | Purpose | Example |
|---|---|---|
| `skills/<name>/SKILL.md` | Task the agent executes | Write an email subject line |
| `knowledge/<file>.md` | Context the agent reads to ground work | Brand voice guidelines |
| `connectors/<platform>/SKILL.md` | How to interact with an external system | How to pull Google Ads data |
| `references/<file>.md` | Lookup data (team, IDs, channels) | Team roster |

---

## Good examples in this repo

- `messaging/skills/brand-messaging/SKILL.md` — clean trigger + workflow + knowledge reference
- `media/connectors/google-ads/SKILL.md` — API connector pattern
- `messaging/skills/_template/SKILL.md` — copy this to start a new skill
