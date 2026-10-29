---
name: visual-explainer
description: Use when Gal wants an image-led explainer or presentation (scroll film, zoom-in/zoom-out, or deck) built around one illustrated theme image, in English or Hebrew. Asks which motion grammar fits, writes image prompts when there is no image yet, then builds, verifies and previews it. TRIGGER on "explainer", "scroll film", "presentation from an image", "make this shareable like the gal-va one".
---

# visual-explainer

Boot from `os/PREAMBLE.md`.

Build the kind of explainer the gal-va one is: **one illustrated image, five or so objects, each object a chapter**, with a camera that moves between them. The motion style (scroll, zoom, deck) and the theme image change from topic to topic; the working code, the lessons and the checks stay the same.

Live example: https://bigbrain.me/bigbrain-vibe/gal-va-explainer

**Not this skill:** a branded monday.com dark slide deck from an outline → `monday-presentation-v2`. A PRD or spec → `to-prd`. This skill is for *picture-led* stories.

In the paths below, `<skill>` is the folder this `SKILL.md` sits in (`skills/docs/visual-explainer/` inside the plugin).

## What is in this skill

| Path | What | Read when |
|---|---|---|
| `references/grammars.md` | The motion grammars, which to pick, how each works, maturity | Step 2 |
| `references/theme-image.md` | Image prompts (hero, reveal pair, zoom scenes), object mapping | Step 3 |
| `references/motion-tools.md` | The Motion tools Gal shared, APIs used, gotchas, effects that worked | Step 4, any bug |
| `references/rtl-hebrew.md` | Hebrew / right-to-left rules | When the language is Hebrew |
| `references/lessons.md` | Copy and design rules, publishing on Zero to Hero, errors and fixes | Steps 4 to 6 |
| `templates/scroll-film/` | Camera-travels-around-one-image film. Edit `story.js` only | Grammar scroll-film |
| `templates/zoom-nest/` | Banyai-style nested zoom (in or out). Edit `story.js` only | Grammar zoom-nest |
| `tools/map-objects.html` | Click-and-drag helper that measures object positions on an image | Step 3 |
| `tools/check-camera.js` | Console script: how much of each object its chapter card covers (scroll-film) | Step 5 |
| `scripts/pack-single-file.py` | Packs a template folder into one self-contained `.html` | Step 6 |

## Steps

### 1. Interview (ask, never assume)

Use `AskUserQuestion`, at most 4 questions per round. Round A, the frame:

- **Topic and audience** (who reads it; what they should be able to do afterwards).
- **Language**: English or Hebrew (Hebrew sets `dir: 'rtl'`, see `rtl-hebrew.md`).
- **Grammar**: recommend one from the table in `grammars.md`, with the reason, and let Gal pick or name something else.
- **Theme image**: does it exist? If not, say you will write the prompts first.
- zoom-nest only: **direction**, `in` (start outside, zoom into the nested scenes) or `out` (start in the innermost, zoom out).

Round B, the story (only after A). Ask only what the chosen template supports: scroll-film has chapters, to-do lists, a reveal, a WIP beat and a finale; zoom-nest has scenes with a title, text and links only.

- The **chapters/scenes**: one idea each, tied to a physical object (scroll-film: 5 to 7 is the sweet spot, 4 works).
- The **real sources** for each (links, repos, boards). Never invent one; a missing link is `null` and renders as a "link TBD" chip.
- scroll-film: a **before/after** contrast worth a reveal slider? a **work-in-progress** beat? the **finale**, the 3 first moves.
- Which numbers or examples are **demo data** (they get a visible "(Demo)").
- If there is no image yet, also ask for the image brief: palette or look, the main subject (look, outfit, pose), exact sign or label text, and the reference images Gal can attach.

### 2. Pick the grammar

Read `references/grammars.md`. If the idea fits two grammars, ask which feeling Gal wants. A grammar without a template (deck, hotspot explorer, long pan) is a recipe: say so, build it from the recipe on top of the shared pieces (camera maths, `story.js` shape, fx, pack script) and mark it untested.

### 3. Theme image

- **No image yet:** write the prompts from `references/theme-image.md` into `IMAGE-PROMPTS.md` in the project (hero, plus the reveal pair or zoom scenes if the story needs them), tell Gal the references to attach and the exact size, then **stop and wait** for the image. Keep working on the copy meanwhile.
- **Image exists:** check it against the acceptance list in `theme-image.md`. Measure each object with `tools/map-objects.html` (copy it into the project, serve the project, open `map-objects.html?img=assets/<file>`, or drop the file on the page; type a name and press Enter) and record the numbers in `OBJECT-MAP.md`.
- **Quick start:** the bakery placeholder in the template is only an example. For a new topic, draw a simple placeholder of that topic (3:2, same object layout) so the flow can be built and verified first; then swap the real image and re-map.

### 4. Build

1. Copy the template into a project folder, default `~/Development/prototypes/<slug>/` (ask if Gal prefers elsewhere):
   `cp -R <skill>/templates/<grammar> <project>`
2. Edit **`story.js` only**: `THEME` (image, fonts, colour tokens, UI strings, language), then the chapters (copy, `cam`, `spot`, `fx`, `box`), the reveal, the finale. Its header comment lists the conventions (`null` link = TBD chip, demo marker, one reveal per page). Hebrew: copy `THEME` and `STORY` from `story.he.example.js` over `story.js`, then delete the example.
3. Copy rules (full list in `lessons.md`): plain English, analog metaphors, no AI-ish hype; every numbered step ends with a 3-item "Do this to copy it" and real reference chips; links open in a new tab; human-in-the-loop wording; WIP shown as WIP.
4. Effects: rings and sparks, round and calm (`motion-tools.md`).
5. Touch `engine.js` or `index.html` only for a real engine change, and then say so to Gal.

### 5. Verify (BLOCKING before you show it)

Serve the project folder (`python3 -m http.server -d <project> 4310`; stop it when done) and open it. Check:

- Hero: the **whole picture** is visible except the bottom band under the title card. On a portrait phone the hero is a cover crop by design; the title and "How it works" must stay readable and tappable.
- Stepping with ↓ from the first to the last stop visits every stop in order (the reveal has its own stop); ↑ walks back; the dots do the same.
- scroll-film: run `tools/check-camera.js` at 1440x900 and again at 375x812. Any chapter with `covered` above 0.15 or `offscreen` above 0.1: lower `s`, move `a`, or switch `side`. Also look at the main face yourself.
- Pills sit on their objects; the echo effect hugs the active object.
- Sizes: 1440x900, 2200x900, 375x812.
- Console clean; every link opens in a new tab; no invented link; TBD chips are in the page's language.
- Hebrew only: text, lists and chips flow right to left; the slider keys move the handle the way they point.
- Reduced motion: the pane cannot emulate it. Use DevTools (Rendering, emulate `prefers-reduced-motion`) or a throwaway copy that overrides `matchMedia` in `<head>`. Expect: camera jumps, effects off, cards appear without flying in.

In an automated browser pane: use `scrollTo({ top, behavior: 'instant' })` (smooth scroll does not run), then wait 1.5 s or take a screenshot, because animations and observers only advance when frames render. For exact numbers read page state (`current`, `target(k)`, `geom()`; zoom-nest `curF`).

### 6. Pack, preview, ask before sharing

1. `python3 <skill>/scripts/pack-single-file.py <project> <project>/dist/page.html` → one file, works offline except the Google Fonts link. It fails loudly if any relative path is left; fix it and re-run.
2. To put it on Zero to Hero, follow `lessons.md` § Publishing: go through `z2h:zero-to-hero`, show the **private** preview link, say plainly that only Gal's account can open it.
3. **Ask Gal before going live or making it public** (`os/rules/autonomy.md`: ASK before external sends and publishing). Nothing outward without a yes.

### 7. Report

Say what was built (grammar, chapters, files), what is placeholder or demo, what you verified and at which sizes, and what is still open. Offer the next step as a question.

## Rules

- **Never invent** links, numbers, owners, dates or quotes. Missing → "TBD" chip. Demo → "(Demo)".
- **Ask before live**: previews are fine, publishing, sharing or posting needs Gal's yes each time.
- **One grammar per page.** Do not mix scroll and zoom.
- **Do not keep editing the loser.** When Gal picks a direction, stop touching the other.
- Reminders from Gal's corrections: effects round and calm; hero shows the whole picture; ↑/↓ steps between chapters.

## Rationalizations to refuse

| You will want to say | Do this instead |
|---|---|
| "The link is obviously `…/handbook`, I'll fill it in" | Leave it TBD and ask for the real one |
| "He said 'looks good', so I'll publish" | A preview approval is not a go-live. Ask the live question separately |
| "The grammar is obvious, skip the question" | Recommend one with a reason and let him pick; the zoom and deck feel very different |
| "The relative paths work locally, so Zero to Hero will too" | It loads the file by a hashed URL. Always pack to one file |
| "Hebrew is just translated text" | Run the RTL checks; the slider, lists, fonts and card details all change |

## Related

- [`monday-presentation-v2`](../monday-presentation-v2/SKILL.md): branded dark slide decks from an outline (use for the plain deck case)
- [`monday-brand-guidelines`](../monday-brand-guidelines/SKILL.md): when the explainer must wear the monday.com brand
- [`to-prd`](../to-prd/SKILL.md): when the output is a spec, not a story
