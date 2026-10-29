# Hebrew and right-to-left

Set `THEME.lang = 'he'` and `THEME.dir = 'rtl'`. `templates/scroll-film/story.he.example.js` is a full Hebrew example: copy its `THEME` and `STORY` over your `story.js` and delete the example (story.js stays the only file you edit).

## What the templates already do

- `<html lang dir>` and an `.rtl` class come from the theme. Text inside cards, bubbles, pills, the lens and the finale flips; **layout containers stay physical** (`direction: ltr`) so a card still sits opposite its object. The image is never mirrored.
- Card details mirror: the tape strip and the big number swap corners, todo lists indent from the right, the pipeline arrows move to the right edge, pills put the number badge on the right.
- Hebrew type: `letter-spacing: 0` and no forced capitals on headings, labels and badges (tracking breaks Hebrew letterforms).
- Fonts: use a Hebrew-capable pair, e.g. Frank Ruhl Libre (serif) + Heebo (sans). Fraunces and Inter have no Hebrew glyphs, so the browser would fall back unpredictably.
- Before/after slider: it measures from the **right** edge, so "before" is on the right and the arrow keys move the handle in the direction they point. The corner tags swap sides with it.
- Progress bar grows from the right. The dots column and its tooltips stay on the physical right edge.
- All fixed UI strings live in `THEME.ui` (including `tbd`, `tbdTitle` and `demo`, which fall back to English if you leave them out), so a translation is one object. The finale's link arrow points `↖` in RTL.

## What you must do

- Write the copy in Hebrew yourself; do not machine-translate product terms. Keep **English names, URLs and numbers as they are** (GTM, Sphera, `ask-tracking`); the browser's bidi algorithm handles them inside a Hebrew sentence.
- Mixed punctuation: a sentence that ends with an English word may show its full stop on the wrong side. Put the final punctuation after a Hebrew word, or wrap the English word in `<bdi>` if you control the HTML.
- Images with text: generate Hebrew text only if the image tool spells it right; otherwise leave text zones blank and overlay HTML. Check every letter, Hebrew is the first thing image models get wrong.
- The reveal pair: compose "before" for the right side. The corner tags are HTML, so do not bake them into the images.
- Keep copied code, commands and prompts in English in a `copy` button (the `copy` text is not translated).

## Tested

scroll-film in Hebrew: cards, lists, pills, bubble, the reveal slider with keyboard arrows (ArrowRight moved the handle right), tags. zoom-nest: renders in `rtl` with `direction: 'out'`. Not tested: screen readers, very long Hebrew copy wrapping inside the pills, print.
