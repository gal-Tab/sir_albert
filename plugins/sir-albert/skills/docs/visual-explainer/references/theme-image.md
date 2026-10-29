# The theme image: prompts, mapping, reveal pair

The whole explainer is built around **one illustrated image per theme**. The first gal-va explainer used a desk (cork board, notebook, alarm clock, service bell, the assistant in a tuxedo). The next one can be a kitchen pass, a workshop, a newsroom, a harbour. Everything else (camera, pills, effects) is derived from where the objects sit in the image.

## 1. Choose the metaphor first

- One **physical place** with 5 to 7 **objects you can point at**. Each object = one chapter. The objects should already be in the copy's vocabulary (gal-va: new colleague, notebook, job cards, alarm clock, front desk).
- Avoid generic "AI art": neon, purple gradients, chrome robots, glowing circuits, brain icons. It reads as AI-ish and fights the copy. Warm, slightly imperfect, analog objects work.
- Plan an empty zone on both sides of the picture where a card can sit without covering an object.

## 2. Hero prompt template (GPT image / Nano Banana)

Attach references if you have them (a character, the brand look, a previous image). Output **3:2, at least 1536 x 1024** (4800 x 3200 if you plan zoom 2.5x or more).

```
Same 3D animated-film look: warm soft lighting, rounded forms, shallow depth of field, [palette: e.g. cream and wood tones with deep blue accents and brass]. No neon, no purple, no glowing circuits, no brain icons.
A single wide scene, 3:2, straight-on camera: [PLACE].
Objects, each clearly separate and readable:
1. [object A] at the upper left
2. [CHARACTER / main subject] in the centre, [outfit], [pose]
3. [object C] at the lower left
4. [object D] at the right middle
5. [object E + a small sign] at the lower right
Leave calm, uncluttered space around the edges of the picture.
All text must be crisp and legible, spelled exactly as given: [exact words for signs and labels]. No extra text.
```

Acceptance check before you map anything: every object present, in a readable spot, text clean, the main subject's face not at a crop edge, empty zones available for cards.

## 3. Map the objects

Use `tools/map-objects.html` (drop the image, drag a box around each object, name it, copy the snippet). Units:

| Where | Unit |
|---|---|
| `cam.f`, `cam.a` | fractions 0..1 of the image / the screen |
| `spot`, `fx` x and y | percent 0..100 of the image width / height |
| `fx` ring width | percent of the image **width** (heights are in the same unit, so a "square" is square) |

Record the map in a table in the project (object, meaning, x range, y range). The gal-va one looked like this:

| Object | Meaning | x % | y % |
|---|---|---|---|
| Cork board | Skills | 3-38 | 4-45 |
| The assistant (head x 47-60, y 11-33) | The agent | 26-74 | 11-70 |
| Open notebook | AI Brain | 1-41 | 70-93 |
| Alarm clock | Loops | 76-93 | 35-65 |
| Sign + bell | #ask-tracking | 70-98 | 68-90 |

Tuning the camera per chapter: start from `s: 1.05 to 1.25`, `a` at the opposite side from the card (`side: 'left'` → `a.x ≈ 0.72`). Keep `s` modest: gal-va's agent chapter looked wrong at higher zoom ("less zoom and bigger circles").

## 4. The before/after reveal pair

Used by the `reveal` chapter in scroll-film. Two images that **share camera and layout** and differ only in what the idea changes (gal-va: "waiting on Gal" vs "asking gal-va").

- Generate the first image, then ask the tool to **edit that image** into the second ("keep the exact layout, camera, header and avatars' positions; change X"). Separate generations drift and the slider shows every shift.
- Attach the same references each time (the cast, the look image).
- Text inside the images: keep it short. If it comes out garbled, regenerate with all text areas **blank** and overlay real HTML text. The engine already draws the corner tags (`before.tag`, `after.tag`) as HTML, so do **not** ask the image to contain them.
- Any invented numbers or names in the images are demo data. Keep "(Demo)" visible until real answers are wired.
- For Hebrew, the "before" image sits on the right (the slider starts from the right edge). Compose accordingly, or generate a mirrored layout.

## 5. zoom-nest scene sets

Each scene except the last needs a **blank screen** (TV, window, laptop, picture frame, porthole) at a known rectangle. Prompt: "…a wall TV showing a plain flat light-blue screen occupying x 55-85%, y 18-48% of the picture, no reflections." Measure the screen with `tools/map-objects.html`, put the numbers in `frame`. The child image should start with the colour that surrounds the screen so the seam disappears. For a 3:2 child inside a 3:2 parent the frame must satisfy `w == h` in fractions.

## 6. Known weak spots

- Generated text is the weakest part of any image. Check every letter.
- Characters drift between generations. Always attach the cast image.
- A clock shows whatever time it likes. If it matters, say "clock showing 08:37".
- Photo of a real person in an avatar: use only with that person's say-so. Gal approved his own photo for the gal-va explainer; do not assume the same for others.
