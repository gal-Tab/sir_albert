---
name: linkedin-in-my-voice
description: Draft a LinkedIn post in Gal's Hebrew voice — trigger on "write a LinkedIn post", "draft a linkedin post", "post about this on linkedin", "כתוב לי פוסט ללינקדאין", "נסח פוסט ללינקדאין".
status: draft
owner: galta@monday.com
---

# Skill: LinkedIn in My Voice

**Domain:** Content / personal brand

Draft LinkedIn posts that sound like Gal, not like AI: Hebrew, clear and simple,
first-person, a bit excited but self-aware — deliberately not polished into the
usual synthetic LinkedIn tone. Write-only: the skill drafts for review and NEVER
posts anywhere. Gal copies the final text himself.

## When to Use
- "write / draft a LinkedIn post", "post about this on LinkedIn", "turn this into a
  LinkedIn post"
- "כתוב לי פוסט ללינקדאין", "נסח פוסט ללינקדאין", "תהפוך את זה לפוסט"
- Any request to draft a LinkedIn post from a subject Gal brings.
- NOT for finding topics (that's idea-sourcing — out of scope) and NOT for other
  channels (use `slack-in-my-voice` for Slack).

## Workflow
1. Load `knowledge/gal-linkedin-voice.md` (rules + registers + anatomy),
   `knowledge/approved-posts.md` (weight these examples highest), and
   `references/anti-ai-tells.md` (kill-list).
2. Pick the register (personal-builder by default; explainer/hot-take for external
   subjects). Draft in Hebrew using the post anatomy and comma-flow rhythm. Ask at
   most ONE clarifying question, and only if the subject or angle is genuinely
   unclear.
3. Run the anti-ai-tells kill-list on the draft. Fix every hit. Then run the voice
   self-check. Only after both pass, show Gal the draft (plain text he can copy).
4. Gal edits or approves. On approval, OFFER to append the final version to
   `knowledge/approved-posts.md` with a one-line "why it worked" note. Append ONLY
   after Gal explicitly says yes. Never post to LinkedIn.

## DOs
- ✅ Hebrew; keep technical/product terms in English inline (`LLM`, `MCP`, `agent`,
  `Codex`, `GTM`, `JSON`).
- ✅ Open with a pain or a spark, not a headline. One expressive emoji near the top, max.
- ✅ Use flowing comma-chained sentences — the signature rhythm — over broetry.
- ✅ Name the hard/boring part honestly and include one concrete specific (a number,
  a timeframe, a version count).
- ✅ Prefer the newest `approved-posts.md` examples as the voice anchor.
- ✅ Show one draft by default; offer a variant only if asked.

## DON'Ts
- ❌ Never post or send anywhere — write-only, output is copyable text.
- ❌ No hype adjectives, em-dash drama, "זה לא X זה Y" reveals, or triadic rhythm.
- ❌ No CTA bait ("עקבו אחריי", "מה דעתכם? 👇"), no summary-bow closer, no hashtag stuffing.
- ❌ No emoji bullets or scattered decorative emoji.
- ❌ Don't translate technical terms to Hebrew. Don't over-polish grammar.
- ❌ Don't append to approved-posts.md without Gal's explicit yes.

## Related
- [Voice + examples](knowledge/gal-linkedin-voice.md)
- [Approved posts (grows over time)](knowledge/approved-posts.md)
- [Anti-AI kill-list](references/anti-ai-tells.md)
- Sibling: `slack-in-my-voice` (same voice, Slack channel).
