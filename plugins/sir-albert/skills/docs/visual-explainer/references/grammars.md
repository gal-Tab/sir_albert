# Motion grammars: how the explainer moves

A "grammar" is the rule for how a viewer moves through the story. Pick one per topic. Do not mix two in one page.

| Grammar | Template | Maturity | Pick it when |
|---|---|---|---|
| **scroll-film** | `templates/scroll-film/` | Built, shipped (the gal-va explainer), tested in English and Hebrew | The story is a set of **things** (5 to 7 objects), each is one chapter, people read it alone, async. |
| **zoom-nest** | `templates/zoom-nest/` | Built, tested in a browser (zoom in, zoom out, RTL render). Not shipped yet | The story is about **scale or containment**: system → part → detail, or "what is inside what". One idea per level. |
| **deck** | none (recipe below) | Built once as prototype A, not packaged | Someone **presents live** and clicks through. One idea per slide. |
| **hotspot explorer** | none (recipe below) | Idea only | The picture is dense and the reader should **choose** what to open. |
| **long pan / parallax** | none (recipe below) | Idea only | A **journey in time or space** along one very wide image. |

If the topic fits two grammars, ask Gal which feeling he wants; do not decide silently.

## scroll-film (template)

- One illustrated image stays on screen. A single `.cam` element (image + overlays) is translated and scaled; each chapter is a camera target.
- Camera target for chapter `k`: focus point `f` (fraction of the image), zoom `s`, landing point `a` (where on the screen the focus should land). `tx = a.x*vw - s*f.x*W`, `ty = a.y*vh - s*f.y*H`, clamped so the image never leaves the screen. `W = max(vw, 1.5*vh)` (3:2 cover).
- **The hero shows the whole picture** (contain-fit, centered, a blurred copy of the image behind it fills the bars). Scrolling then focuses on details. This was an explicit request; never open on a crop.
- Chapter detection: Motion `inView` on a band at the viewport centre (`margin: '-48% 0px -48% 0px'`). The callback must **return a function**, otherwise it fires once and scrolling back up never re-activates a chapter.
- Cards sit opposite the object (`side: 'left'` means the card is on the left, the object lands on the right). Choose `a` so the card never covers a character's face or the object itself.
- Pills (numbered hotspots) live inside the camera and are counter-scaled with `--inv = 1/scale`, so labels stay the same size while the image zooms.
- Optional pieces: speech `bubble` per chapter, a `reveal` chapter (before/after slider; **one per page**), a numberless "Next (WIP)" chapter, a finale with the first moves.
- Phones: the card takes the bottom half and scrolls inside itself, the camera lifts the object into the top half, speech bubbles are hidden, and the hero is a cover crop (not the whole picture).
- Reduced motion: no camera spring, no effects, cards appear instead of flying in.
- Navigation: ↑/↓, PageUp/PageDown, j/k step between **stops**; the dots use the same list. A reveal chapter adds its own stop (`<key>lens`) so ↓ from it does not skip the slider.
- Echo effects (`fx`) loop around the active object: `ring` (round pulse) and `spark` (✦ drifting up). Plain Web Animations, no library.

## zoom-nest (template)

- Scene `i+1` is drawn **inside a blank screen/window of scene `i`**. The DOM is nested the same way, so the whole film is one CSS transform on one element.
- `frame = [x, y, w, h]` fractions of the parent image. With 3:2 images keep `w == h` in fractions so the child keeps its 3:2 shape (`w*1536 : h*1024 = 3:2`).
- View rectangle at position `f`: width is interpolated in log space (constant perceived zoom speed); the centre moves linearly with the fraction of width zoomed so far, which keeps the target still on screen as you zoom.
- Scroll → `f` with Motion `scroll()`; a dwell plateau (30% of scroll at every stop) leaves time to read the caption.
- `direction: 'in'` starts outside and zooms into the nested scenes. `direction: 'out'` starts in the innermost scene and zooms out to reveal where it sat, like Istvan Banyai's book *Zoom*. `hero: true` goes on the layer shown first (outermost for `in`, innermost for `out`).
- Captions only: no finale, to-do list, reveal, pills or effects. If the story needs those, use scroll-film.
- Each child layer bleeds 0.12% past its frame so no hairline of the parent shows at the seam.
- The image prompt must ask for the blank screen at the exact rectangle (see `theme-image.md`), and the child image should match the screen's colour at its edges so the seam hides.
- Limits: all scenes should be 3:2; deep nests (4+) get blurry at the outermost layer at max zoom, so give the outer scene a high resolution (up to 4800 x 3200) or keep nests to 3.

## deck (recipe, no template)

Built once as "prototype A" in Gal's local `gal-va-explainer/v10/A-deck.html`. For a plain branded monday.com deck without a theme image, use the `monday-presentation-v2` skill instead.

- 16:9 canvas sized in `cqw` units so everything scales with the slide.
- `[data-step]` elements appear one click at a time (→, space, wheel, swipe). ↑/↓ also step.
- The same hero image is shared between slides with the View Transitions API (`view-transition-name: desk`), so the image **morphs** between crops instead of cutting.
- Crops are a plane with CSS variables `--fx --fy --z` (focus x, focus y, zoom).
- Drever (github.com/Zhangdroid/drever) is the real framework for this grammar (MDX slides, `<Step>`, Studio). It needs Node ≥ 24.18; Gal's machine had 24.13.1, so the prototype reproduced the grammar in plain HTML. If a deck wins, port it to a real Drever project and keep the content file as the source.

## hotspot explorer (recipe, untested)

Whole image always visible; clicking a hotspot zooms in (reuse the scroll-film `target()` camera) and opens a panel; Esc zooms back out. Reuse `STORY.chapters`; replace the scroll-driven detection with click handlers.

## long pan / parallax (recipe, untested)

A very wide image (e.g. 3:1 or wider), translated horizontally by Motion `scroll()`; 2 or 3 layers moving at different speeds for depth; chapters are positions along the pan. Needs layered images (foreground, midground, background) from the image prompt.
