# linkedin-in-my-voice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a write-only Claude Code skill that drafts LinkedIn posts in Gal's Hebrew voice — clear, human, deliberately not AI-polished — and learns from every post he approves.

**Architecture:** Mirrors the existing `slack-in-my-voice` skill: a thin `SKILL.md` orchestrator that loads a `knowledge/` voice file (rules + few-shot examples), an auto-growing `approved-posts.md`, and a `references/anti-ai-tells.md` kill-list. The skill drafts → self-checks against the kill-list → shows Gal → on approval offers to append the final post as a new example. No posting API; output is copyable text.

**Tech Stack:** Markdown skill files; `tools/publish-skills.sh` for publishing to `~/.claude/skills/`; registered in `REGISTRY.md` + `README.md`.

## Global Constraints

- `SKILL.md` body ≤150 lines (per `SKILL_GUIDELINES.md`); detail lives in `knowledge/` and `references/`.
- Output language: **Hebrew primary**; technical and product terms stay in English inline (LLM, MCP, GTM, Codex, agent, JSON, etc.).
- Write-only: the skill NEVER posts to LinkedIn or any channel. Output is text Gal copies.
- Auto-capture is opt-in per post: append to `approved-posts.md` ONLY on Gal's explicit confirmation.
- Follow the `slack-in-my-voice` file layout and frontmatter style (`name`, `description`, `status`, `owner`).
- Admired posts are the *target aesthetic*, not Gal's voice — extract structure/texture, never wording; never treat one author's tics as Gal's.
- Skill folder lives under `skills/biz/`.

---

### Task 1: Voice knowledge file

The core ground truth. Adapts Gal's documented Slack voice to LinkedIn length and folds in the two registers extracted from the admired posts.

**Files:**
- Create: `skills/biz/linkedin-in-my-voice/knowledge/gal-linkedin-voice.md`

**Interfaces:**
- Produces: a voice reference loaded by `SKILL.md` Step 1. Section headings referenced by later files: `## Registers`, `## Post anatomy`, `## Voice & rhythm`, `## Language`, `## Few-shot examples`, `## Self-check`.

- [ ] **Step 1: Write the file with this exact content**

```markdown
# Knowledge: Gal's LinkedIn Voice

Reference for drafting Gal's LinkedIn posts. Hebrew primary. Base is Gal's Slack
voice (point-first, no filler, English tech terms) stretched to post length, plus
structure/texture extracted from admired Hebrew posts (by others — aesthetic, not
his wording). Gal's true voice calibrates through the draft/edit loop; treat
`approved-posts.md` as the strongest signal once it fills.

## Language
- Hebrew by default. Technical/product terms stay in English inline: `LLM`, `MCP`,
  `GTM`, `sGTM`, `agent`, `agentic`, `JSON`, `RAG`, `Codex`, `Claude Code`, `API`,
  `proxy`, `context`, tool/product names, error strings. Never translate them.
- Authentic imperfection is fine — natural phrasing over polished grammar.

## Registers
Pick one based on the subject.
- **Personal-builder (default)** — for something Gal built, tried, or figured out.
  First person, in-the-trenches, a bit excited but self-aware.
- **Explainer / hot-take** — for an external thing (a tool, a talk, a market shift).
  Punchier and more structured, or a 2–3 sentence sharp observation.

## Post anatomy (flexible backbone — personal-builder)
1. Hook: a pain or a genuine spark, one line. `נמאס לי ש...` / `התוצרים פיצצו לי
   את המוח`. One expressive emoji near the top is allowed, never decorative bullets.
2. The thing, simply: what it is, in human terms.
3. How I actually worked with it: the concrete, hands-on part — the real signal.
   Name the hard part honestly (`החלק הקשה הוא...`, `החלק הכי מציק היה...`).
4. Close: a vivid or relatable line, or an honest takeaway. Never a CTA, never
   "עקבו אחריי", never a neat summary bow.

Explainer register instead: stat/insight hook → what it is → mechanism (short bullets
ok) → result with real numbers → optional "לינק בתגובות".

## Voice & rhythm
- Flowing, comma-chained sentences that read like thinking out loud — lines can end
  in commas and build momentum. This is the SIGNATURE. Avoid one-line-paragraph
  broetry.
- Self-aware hedges over hype: `יכול להיות שזה מלהיב רק אותי` beats "game-changing".
- Concrete specifics: real numbers, timeframes, "סופ״ש", "גרסה רביעית", "20 דק".
- Name tools matter-of-factly (`קודקס בנה הכל`, `בניתי עם Claude Code`).
- At most one expressive emoji, near the hook (🤯 / 👇). Zero decorative emoji, zero
  emoji bullets.

## Few-shot examples
> Seeded from real drafts Gal edits (Task 6). Until then, use the anatomy + rhythm
> rules. Never copy the admired posts' wording — they live in the design spec only
> as the target aesthetic.

## Self-check before showing a draft
- Hebrew? Technical terms left in English?
- Hook is a pain or a spark, not a headline?
- Flowing comma rhythm, not broetry? At most one emoji near the top?
- Named the hard part / a concrete specific?
- Close is vivid/honest, not a CTA or summary bow?
- Ran `references/anti-ai-tells.md` and fixed every hit?
```

- [ ] **Step 2: Verify the file exists and is well-formed**

Run: `test -f skills/biz/linkedin-in-my-voice/knowledge/gal-linkedin-voice.md && head -5 skills/biz/linkedin-in-my-voice/knowledge/gal-linkedin-voice.md`
Expected: prints the title line `# Knowledge: Gal's LinkedIn Voice`.

- [ ] **Step 3: Commit**

```bash
git add skills/biz/linkedin-in-my-voice/knowledge/gal-linkedin-voice.md
git commit -m "Add gal-linkedin-voice knowledge file"
```

---

### Task 2: Anti-AI-tells reference

The differentiator — an explicit kill-list the skill runs before showing a draft.

**Files:**
- Create: `skills/biz/linkedin-in-my-voice/references/anti-ai-tells.md`

**Interfaces:**
- Consumes: nothing.
- Produces: kill-list referenced by `gal-linkedin-voice.md` self-check and by `SKILL.md` Step 2.

- [ ] **Step 1: Write the file with this exact content**

```markdown
# Reference: Anti-AI Tells (kill-list)

Run this against every draft BEFORE showing Gal. Each hit must be fixed, not
flagged. Hebrew-aware.

## Kill on sight
- **Em-dash-itis** — sentences strung on em-dashes for drama. Use commas/periods.
- **"It's not X — it's Y"** cadence (`זה לא X, זה Y`) used as a rhetorical reveal.
- **Triadic rhythm everywhere** — "X, Y, ו-Z" triples in sentence after sentence.
- **Broetry** — every sentence as its own one-line paragraph. Gal's rhythm flows in
  comma-chained lines instead.
- **Hype adjectives** — "game-changing", "powerful", "seamless", "revolutionary",
  and Hebrew equivalents (`מהפכני`, `עוצמתי`, `פורץ דרך`, `חלק`).
- **Rhetorical-question opener** — "Ever wondered…?" / `אי פעם תהיתם...?`.
- **Summary-bow closer** — "The bottom line?" / "In short," / `בשורה התחתונה` +
  restating the post. End on a real thought instead.
- **CTA bait** — "Follow for more", "What do you think? 👇", `עקבו אחריי`, engagement
  prompts. Cut them.
- **Emoji bullets / decorative emoji** — ✅🚀🔥 as list markers or scattered accents.
  One expressive emoji near the hook, max.
- **Over-symmetry** — every paragraph the same length/shape; too-clean parallelism.
  Real writing is a little uneven.
- **Hashtag stuffing** — no hashtag clusters. Zero, or one only if genuinely apt.
- **Vague authority filler** — "In today's fast-paced world", `בעולם של היום`,
  "As we all know". Delete.

## Keep (these read human)
- A comma-spliced run-on that carries momentum.
- A self-aware hedge (`יכול להיות שזה מלהיב רק אותי`).
- One concrete oddly-specific detail (a number, a weekend, a version count).
- Naming the boring/hard part honestly.
```

- [ ] **Step 2: Verify**

Run: `test -f skills/biz/linkedin-in-my-voice/references/anti-ai-tells.md && grep -c "Em-dash-itis" skills/biz/linkedin-in-my-voice/references/anti-ai-tells.md`
Expected: prints `1`.

- [ ] **Step 3: Commit**

```bash
git add skills/biz/linkedin-in-my-voice/references/anti-ai-tells.md
git commit -m "Add anti-ai-tells kill-list reference"
```

---

### Task 3: Approved-posts scaffold

The auto-growing example store. Starts as a template with instructions, no examples yet.

**Files:**
- Create: `skills/biz/linkedin-in-my-voice/knowledge/approved-posts.md`

**Interfaces:**
- Produces: append target used by `SKILL.md` Step 4 (capture). Each entry: a `## <date> — <topic>` heading, the post body in a fenced block, and a `**Why it worked:**` line.

- [ ] **Step 1: Write the file with this exact content**

```markdown
# Gal's Approved LinkedIn Posts

Grows one entry per approved post. This is the strongest voice signal — once it has
a few entries, weight it above the general rules in `gal-linkedin-voice.md`.

Append format (newest at top):

## <YYYY-MM-DD> — <short topic>

​```
<final approved Hebrew post, exactly as Gal will paste it>
​```

**Why it worked:** <one line — the hook move, the rhythm, the specific that landed>

---

<!-- No approved posts yet. First entry gets added via the capture step (Task 6). -->
```

- [ ] **Step 2: Verify**

Run: `test -f skills/biz/linkedin-in-my-voice/knowledge/approved-posts.md && grep -c "Append format" skills/biz/linkedin-in-my-voice/knowledge/approved-posts.md`
Expected: prints `1`.

- [ ] **Step 3: Commit**

```bash
git add skills/biz/linkedin-in-my-voice/knowledge/approved-posts.md
git commit -m "Add approved-posts scaffold"
```

---

### Task 4: SKILL.md orchestrator

The thin entry point Claude Code loads. ≤150 lines.

**Files:**
- Create: `skills/biz/linkedin-in-my-voice/SKILL.md`

**Interfaces:**
- Consumes: `knowledge/gal-linkedin-voice.md`, `knowledge/approved-posts.md`, `references/anti-ai-tells.md`.
- Produces: the skill triggerable in Claude Code sessions after publishing.

- [ ] **Step 1: Write the file with this exact content**

```markdown
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
```

- [ ] **Step 2: Verify frontmatter and length**

Run: `awk 'NR<=6' skills/biz/linkedin-in-my-voice/SKILL.md && echo "---LINES---" && wc -l < skills/biz/linkedin-in-my-voice/SKILL.md`
Expected: frontmatter shows `name: linkedin-in-my-voice`; line count ≤150.

- [ ] **Step 3: Commit**

```bash
git add skills/biz/linkedin-in-my-voice/SKILL.md
git commit -m "Add linkedin-in-my-voice SKILL.md orchestrator"
```

---

### Task 5: Register in REGISTRY.md and README.md

Make the skill discoverable per repo convention.

**Files:**
- Modify: `REGISTRY.md` (biz category table)
- Modify: `README.md` (biz category row + skill count)

**Interfaces:**
- Consumes: the skill folder from Tasks 1–4.

- [ ] **Step 1: Add a row to the `biz` table in `REGISTRY.md`**

Add under the biz category table (match existing column format):

```markdown
| linkedin-in-my-voice | `skills/biz/linkedin-in-my-voice/` | "write a LinkedIn post", "draft a linkedin post", "כתוב פוסט ללינקדאין" |
```

- [ ] **Step 2: Update `README.md`**

In the category table, add `linkedin-in-my-voice` to the `biz` row's skill list. Bump the "12 skills" count in the Skills section intro to the correct new total (count the folders under `skills/*/` after this addition).

Run to get the true count: `find skills -name SKILL.md | wc -l`
Use that number in the README intro line.

- [ ] **Step 3: Verify**

Run: `grep -c "linkedin-in-my-voice" REGISTRY.md README.md`
Expected: each file reports ≥1.

- [ ] **Step 4: Commit**

```bash
git add REGISTRY.md README.md
git commit -m "Register linkedin-in-my-voice in REGISTRY and README"
```

---

### Task 6: Publish, smoke-test a real draft, capture first example

Verification-by-use: publish the skill, draft a real post from one of Gal's topic seeds, confirm it passes the kill-list, and capture Gal's edited version as the first `approved-posts.md` entry. This is the step where Gal's true voice starts calibrating.

**Files:**
- Modify: `skills/biz/linkedin-in-my-voice/knowledge/approved-posts.md` (first entry — only after Gal approves a draft)

**Interfaces:**
- Consumes: all files from Tasks 1–4.

- [ ] **Step 1: Publish the skill**

Run: `tools/publish-skills.sh linkedin-in-my-voice`
Expected: prints `✓ ~/.claude/skills/linkedin-in-my-voice`.

- [ ] **Step 2: Verify publish**

Run: `test -f ~/.claude/skills/linkedin-in-my-voice/SKILL.md && ls ~/.claude/skills/linkedin-in-my-voice/knowledge ~/.claude/skills/linkedin-in-my-voice/references`
Expected: lists `gal-linkedin-voice.md`, `approved-posts.md`, `anti-ai-tells.md`.

- [ ] **Step 3: Draft a real post (smoke test)**

Using the skill, draft a Hebrew post from one topic seed — recommended: **"GTM container migration automated end-to-end with Claude Code + the GTM API (snapshot → plan → execute → Slack update)."** Personal-builder register. Run the anti-ai-tells kill-list and the voice self-check; fix all hits before showing Gal.

- [ ] **Step 4: Manual verification gate (Gal)**

Show Gal the draft. Confirm: reads as him, Hebrew with English tech terms, flowing rhythm, no kill-list hits, honest and specific, no CTA/summary bow. Gal edits to taste.

Expected: Gal has a final version he'd actually post.

- [ ] **Step 5: Capture the first approved example (only on Gal's yes)**

Prepend the final edited post to `approved-posts.md` in the append format (heading `## <date> — GTM migration`, fenced post body, one-line "why it worked"). Do this ONLY if Gal says yes.

- [ ] **Step 6: Re-publish and commit**

```bash
tools/publish-skills.sh linkedin-in-my-voice
git add skills/biz/linkedin-in-my-voice/knowledge/approved-posts.md
git commit -m "Capture first approved LinkedIn post as voice example"
```

---

## Self-Review

**1. Spec coverage:**
- Purpose/scope (write-only, subject-in) → Task 4 SKILL.md workflow. ✓
- File structure (SKILL + knowledge/voice + approved-posts + references/anti-ai-tells) → Tasks 1–4. ✓
- Voice bootstrapping (Slack base + admired-post texture; true voice via edits) → Task 1 + Task 6. ✓
- Two registers → Task 1 `## Registers`. ✓
- Default post anatomy → Task 1 `## Post anatomy`. ✓
- Anti-AI guardrails → Task 2. ✓
- Workflow (load → draft → self-check → review → capture) → Task 4 + Task 6. ✓
- Publish + register → Tasks 5–6. ✓
- Success criteria (≤150 lines, Hebrew, opt-in capture, published/registered) → Global Constraints + Tasks 4/5/6. ✓
- Topic seeds → Task 6 Step 3. ✓

**2. Placeholder scan:** No "TBD/TODO/implement later". `approved-posts.md` intentionally starts empty by design (documented), not a placeholder gap.

**3. Type consistency:** File paths and section headings (`## Registers`, `## Post anatomy`, `## Self-check`, append format) are used identically across Tasks 1, 3, 4, and 6.
