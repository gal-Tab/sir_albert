---
name: slack-in-my-voice
description: Draft and send Slack messages in Gal's voice (Hebrew or English) — trigger on "send a Slack", "send a summary on slack", "draft a slack message", "write this for slack", "כתוב/נסח הודעה לסלאק".
status: draft
owner: galta@monday.com
---

# Skill: Slack in My Voice

**Domain:** Messaging

Write Slack messages that sound like Gal, not like an AI: short, point-first,
bulleted only when the content is structured, no filler. Best for substantive
messages — status updates, summaries, answers, announcements, task hand-offs.
Not for one-word replies.

## When to Use
- "send a Slack" / "send a summary on slack" / "post this to <channel>"
- "draft a slack message about…" / "write this for slack" / "message the team about…"
- "כתוב לי הודעה לסלאק" / "נסח לסלאק" / "תשלח סיכום בסלאק"
- Any request to compose, summarize, announce, or hand off work on Slack.

## Workflow
1. Load `knowledge/gal-slack-voice.md` for voice rules + few-shot examples.
   Auto-detect language: Hebrew for internal 1:1/group, English for public/broadcast
   channels; keep technical terms in English either way.
2. Draft per the voice rules (point first, ≤ ~5 short lines, bullets/numbered only
   when structured, ≤1 friendly emoji). Show the draft for review — do not send.
   Ask one clarifying question only if the goal or target channel is unclear.
3. On explicit confirmation, send/schedule via the Slack connector
   (`slack_send_message` / `slack_schedule_message`) to the given channel or thread.
   If no target was given, ask for it before sending.

## DOs
- ✅ Lead with the point in the first line — Gal never opens with preamble.
- ✅ Keep technical terms in English inside Hebrew (`GTM`, `source`, `event`,
  `consent status`, `ht`, `mcp`) — translating them reads wrong.
- ✅ Use numbered lists for step/answer sequences, `•` bullets for conditions —
  matches how Gal structures real answers.
- ✅ Use `@mention`, inline `-> link`, and close hand-offs with "ask me if needed".
- ✅ Quote errors / agent output in code blocks (```), as Gal does.
- ✅ At most one friendly emoji at the end (`:heart_hands:`, `:celebrate:`,
  `:slightly_smiling_face:`); zero on pure technical replies.

## DON'Ts
- ❌ No corporate intros ("Hi team, I wanted to share…") or wrap-up sentences.
- ❌ Don't over-explain or list every caveat — state the point + one reason.
- ❌ Don't translate technical vocabulary into Hebrew.
- ❌ No emoji spam, no exclamation hype, no over-polished formal grammar.
- ❌ Don't send before explicit confirmation.

## Related
- [Voice + examples](knowledge/gal-slack-voice.md)
- Slack connector: `slack_send_message`, `slack_schedule_message`
