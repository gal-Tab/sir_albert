# Design: `linkedin-in-my-voice` skill

**Date:** 2026-07-19
**Owner:** galta@monday.com
**Status:** Approved design — ready for implementation plan

## Problem

Gal wants to post on LinkedIn ~weekly. LinkedIn is flooded with AI-written posts
that read as synthetic — hype adjectives, em-dash-itis, "it's not X, it's Y"
cadence, emoji bullets, broetry line breaks. Gal wants the opposite: his own
plain, direct voice, in **Hebrew**, on real topics (something he built, found, or
figured out), so good content + clear writing makes him stand out.

He has no existing corpus of LinkedIn posts to mimic — this is a fresh voice that
must be bootstrapped and then refined post-by-post.

## Scope

**Write-only.** Input: a subject Gal brings. Output: a drafted LinkedIn post in
his voice for him to review, edit, and copy out manually. It learns from every
post he approves.

**Out of scope:** idea-sourcing / topic mining (covered by Gal's existing
self-reflection skill and the Cathryn "first AI loop" pattern), scheduling, and
any direct posting to LinkedIn (no API — Gal copies the text himself).

## Voice bootstrapping (four layered sources)

The voice file starts from the strongest available ground truth and layers in the
rest over time:

1. **Adapt Gal's documented Slack voice** (`slack-in-my-voice/knowledge/gal-slack-voice.md`)
   — point-first, no preamble/wrap-up, Hebrew with English technical terms,
   authentic imperfection (lowercase, minor typos) — stretched to LinkedIn length.
2. **Posts Gal admires** — Gal pastes 2–5 posts whose *style* he likes after the
   plan is written. We extract structural patterns only, never their words.
3. **Session-mined cues** — how Gal actually explains and articulates things in his
   Claude/agent sessions (optional, opportunistic).
4. **Gal's edits** — the real engine. Every edit on a real draft is captured back
   as ground truth.

## File structure

Follows the `slack-in-my-voice` pattern and `SKILL_GUIDELINES` (thin `SKILL.md`,
detail in `references/`; body ≤150 lines).

```
skills/biz/linkedin-in-my-voice/
├── SKILL.md                        when-to-use, workflow, DOs/DON'Ts (≤150 lines)
├── knowledge/
│   ├── gal-linkedin-voice.md       voice rules + few-shot examples (ground truth)
│   └── approved-posts.md           auto-grows: each approved post + one-line "why it worked"
└── references/
    └── anti-ai-tells.md            explicit kill-list of AI-vibe patterns (Hebrew-aware)
```

Published via `tools/publish-skills.sh linkedin-in-my-voice`; registered in
`REGISTRY.md` (biz category) and `README.md`.

## Default post anatomy (flexible backbone)

Gal's signature arc — take a subject, simplify it, show how he worked with it:

1. **Hook** — one plain sentence stating the interesting thing. No clickbait, no
   rocket emojis, no rhetorical-question opener.
2. **The thing, simply** — what it is, in human terms.
3. **How I actually worked with it** — the concrete, hands-on part. This is the
   real signal and the differentiator.
4. **So what** — one honest takeaway. No "Follow me for more", no CTA.

This is a flexible default, not a rigid template — the skill may deviate when a
subject calls for it, but this is the backbone. One draft by default (not two
"viral variants"); Gal can request a variant.

## Anti-AI-vibe guardrails

`references/anti-ai-tells.md` is an explicit kill-list the skill self-checks
against *before* showing a draft, then fixes. Written Hebrew-aware. Targets:

- Em-dash-itis and the "it's not X — it's Y" cadence.
- Triadic "X, Y, and Z" rhythm used everywhere.
- Emoji bullets and decorative emoji.
- LinkedIn broetry (every sentence its own one-line paragraph).
- Hype adjectives ("game-changing", "powerful", "seamless", Hebrew equivalents).
- Rhetorical-question openers and summary-bow closers.
- Over-symmetry / over-polish that reads as machine-generated.

## Workflow (each run)

1. **Load** `gal-linkedin-voice.md`, `approved-posts.md`, and `anti-ai-tells.md`.
2. **Draft** the post in Hebrew using Gal's arc. Run the anti-AI self-check, fix
   issues, *then* show the draft. Ask at most one clarifying question if the
   subject or angle is unclear.
3. **Review** — Gal edits or approves. The skill never posts anywhere; output is
   copyable text.
4. **Capture** — on approval, offer to append the final version to
   `approved-posts.md` with a one-line "why this worked" note. Save only on Gal's
   explicit confirmation.

## Success criteria

- A drafted post reads as Gal, not as AI — passes the anti-AI kill-list.
- Hebrew primary; technical/product terms stay in English.
- `SKILL.md` body ≤150 lines; detail lives in `knowledge/` and `references/`.
- `approved-posts.md` grows only with Gal's confirmation and visibly improves later
  drafts.
- Skill is published and registered alongside the other `biz` skills.

## Open items (resolved during implementation, not blocking)

- Gal pastes admired posts + topic seeds (Boris Cherny video, the other post) when
  we build the voice file.
- Seed few-shot examples: generated by drafting 1–2 real posts from Gal's listed
  topic ideas and capturing his edits.
