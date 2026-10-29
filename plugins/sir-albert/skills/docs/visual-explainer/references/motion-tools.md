# Motion tools Gal shared, what was used, what was not

## What each link is

| Tool | Link | Used? | Notes |
|---|---|---|---|
| **Motion** (library) | https://github.com/motiondivision/motion | Yes, the engine of both templates | Pinned `motion@14.7.1`, CDN `https://cdn.jsdelivr.net/npm/motion@14.7.1/dist/motion.js`, global `Motion`. |
| **Motion Studio** | https://github.com/motiondivision/motion#-motion-studio | No | A visual editor. It was not installable from the page that was read, so no Studio code is in the templates. Revisit if Gal wants to tune springs visually. |
| **Image reveal slider** | https://motion.dev/examples/vue-image-reveal-slider | Pattern rebuilt | This is a Motion+ example and its source is paywalled. The templates rebuild the pattern as the page describes it: **one position value drives a `clip-path`**, plus pointer drag, keyboard arrows and spring easing. |
| **Drever** | https://github.com/Zhangdroid/drever | Grammar only | A slide framework (MDX slides, `<Step>` reveals, Studio). Needs Node ≥ 24.18; Gal's machine had 24.13.1, so the deck prototype reproduced its grammar in plain HTML. Use the real thing if a deck is chosen for good. |
| **Zoom** (Istvan Banyai) | the picture book | Grammar | Each picture sits inside a screen of the next. Implemented as `zoom-nest`. |

## Motion APIs used (14.x)

```js
const { animate, scroll, inView, hover, stagger } = Motion;
```

| API | Used for | Pattern |
|---|---|---|
| `animate(0, 1, { type:'spring', stiffness:60, damping:16, mass:1.1, onUpdate })` | The camera flight between chapters | Interpolate tx/ty/scale yourself in `onUpdate`; one spring drives all three so they arrive together. |
| `animate(el, { opacity:[0,1], y:[50,0], rotate:[-1.6,0] }, { type:'spring', stiffness:130, damping:16 })` | Card entrance | Children marked `data-in` get a `stagger(.07)` fade-up. |
| `inView(el, cb, { margin, amount })` | Chapter detection, card entrance | **`cb` must return a function** to stay armed (see below). |
| `scroll(fn, { target, offset })` | Lens fade, hint timing, zoom position | With a function it gives progress 0..1. `scroll(animate('#bar', { scaleX:[0,1] }, { ease:'linear' }))` links an animation to page scroll. |
| `hover(el, enter => leave)` | Pill spring on hover | Return the "leave" animation from the callback. |
| `stagger(.14, { startDelay })` | Pills and hero text pop in | |

## Gotchas we hit (so you do not)

1. **`inView` fires once unless the callback returns a function.** Symptom: scrolling back up does not re-activate the previous chapter. Fix: `inView(el, () => { setActive(k); return () => {}; }, opts)`.
2. **Motion's `animate` on `transform` replaces CSS transforms on that element.** A speech bubble centred with `translate(-50%,-100%)` jumped to the corner. Fix: put the centring on a wrapper element and animate the inner one.
3. **Browser cache hides edits to a shared `content.js`.** Symptom: "x is not defined" after an edit. Fix: hard reload, or `fetch(url, { cache: 'reload' })` once.
4. **Synthetic key events have `document` as target**, which has no `closest`. Use `e.target.closest?.('input,textarea')`.
5. **SVG used as `<img>` cannot load external files.** Avatars inside an SVG mock must be embedded as base64 data URIs (with a `clipPath` circle).
6. **Overlay units.** Echo-effect sizes in `%` of the *height* come out wrong. Put effects in a container the exact size of the image with `container-type: size` and size everything in `cqw` (1% of the image width).
7. **A smooth scroll does nothing in a hidden browser pane** (no frames). When testing in an automated pane, use `scrollTo({ top, behavior:'instant' })`.
8. **Reduced motion.** Respect `prefers-reduced-motion`: no camera spring, no effects loop, no smooth scroll.
9. **CSS `@property`** (for the animated spotlight vignette `--vx/--vy`) needs a modern browser; it degrades to a static vignette.
10. **Clipboard inside an iframe** needs `allow="clipboard-write"` on the iframe (Zero to Hero loads the page in one).

## Effects: what felt right to Gal and what did not

Rule: the echo effect should be **round and calm**, hugging the object.

| Object | Kept | Rejected |
|---|---|---|
| The character | Three big gold rings leaving him (`w 22`, thick border) with **less** camera zoom | Small rings (looked weird at high zoom) |
| Notebook | ✦ stars drifting up | Sheen sweeps, animated tabs ("not natural") |
| Cork board | Gold pulse on each pushpin, one after another | Squares around the cards |
| Clock | The round blue ripple | A sweeping hand ("not relevant") |
| Bell | Gold circles only | Anything else |

## Where the full worked example lives

The finished gal-va explainer is live at https://bigbrain.me/bigbrain-vibe/gal-va-explainer (Zero to Hero). Its source files (prototypes A and B, `IMAGE-PROMPTS.md`) are in Gal's local `~/Development/prototypes/gal-va-explainer/v10/`, not in this repo; the scroll-film template here is the cleaned-up, data-driven version of prototype B.
