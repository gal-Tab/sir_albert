# Lessons from building the gal-va explainer

These are Gal's decisions and corrections. Follow them as defaults; ask only when a new topic clearly needs otherwise.

## Copy

- **Plain English, analog metaphors.** New colleague, notebook, job cards, alarm clock, front desk. Short sentences. Gal's own verdict on the first draft: "It's just very AI-ish". So no hype words, no "supercharge", no slogans like "Same question. Two answers".
- **Explain the idea where it is shown.** Gal asked to drop a row of "ask, answer, consult, confirm" buttons because the before/after reveal already explains it. Do not explain the same thing twice.
- **Name things the way Gal does.** "AI Brain" (it holds a team's or person's business context: notes, decisions, Slack channels, Monday boards), "Skills" (job cards), "Loops" (alarm clock), "#ask-tracking" (front desk).
- **Concrete over abstract in the reveal.** Without: the request waits on Gal. With: the answer comes from what actually exists (GTM, ticket status, open issues), via the second agent. Say what changes for the reader.
- **scroll-film: every numbered step ends with "Do this to copy it"**: a short todo list (3 items) plus reference chips linking the real sources. (zoom-nest has captions only.)
- **Links open in a new tab** (`target="_blank" rel="noopener noreferrer"`). `[text](url)` in the copy becomes such a link.
- **Never invent a link, number, owner or date.** A missing link is `null` in `refs` or `finale.links` and renders as a dashed "link TBD" chip (the text comes from `THEME.ui.tbd`, so it is translated). Placeholder or demo data is labelled with `THEME.ui.demo` in the copy and "(Demo)" in the image.
- **Human in the loop language.** The agent proposes; a person confirms. Say it wherever something would be created.
- **Work in progress is shown as work in progress** ("Next (WIP)" beat), never as shipped.
- Hero: title large and central ("Meet Gal-va (Virtual assistant)"), one subtitle line, a "How it works ↓" button **underneath, outside the card**.

## Design and interaction

- **The hero shows the whole picture**, with every detail visible. Scrolling then focuses on details.
- **Up and down arrows move between steps.** The dots and keyboard share one list of stops; a reveal gets its own stop so ↓ never skips it.
- Cards never cover the main character's face or the object they are about. If a card clips an ear, move `a` or switch `side`.
- Effects are round and calm (see `motion-tools.md`). Less zoom, bigger circles.
- The UI around the image keeps ink outlines and offset shadows plus a few tokens (serif headings, sans body, one accent colour) so it still looks like a monday-adjacent doc, not a neon demo.
- Faces: the chat mock avatars use real faces only where the person agreed (Gal's own photo, generated characters).

## Process that worked

1. Interview → pick grammar → theme image → map → write `story.js` → verify → pack → preview → ask → publish.
2. Show two directions when the direction is unclear (a deck and a scroll film), let Gal pick, then keep working on the winner only. Do not keep editing the loser.
3. Verify in a browser at **1440x900**, a wide screen (**2200x900**) and a phone portrait (**375x812**). Check all stops, and run `tools/check-camera.js` at desktop and phone size.
4. Placeholder image first is fine: build and verify the whole flow on the placeholder, then swap the real image and re-map.

## Publishing on Zero to Hero (Gal's team link)

Zero to Hero loads a page file inside an iframe by a hashed URL, so **relative paths break**. The page must be one self-contained file.

1. `python3 <skill>/scripts/pack-single-file.py <project> <project>/dist/page.html` (inlines Motion, scripts and images; big PNGs become JPEG).
2. Start from the `z2h:zero-to-hero` skill; it routes to `z2h:create-app` and `z2h:preview` (do not call those two directly). New app: `create-app` with `html_file=<out>/page.html` and Gal's answer to "manage the code in GitHub yourself?" (No = Z2H stores and backs up the code; recommended). It generates `src/index.tsx` with an iframe. Existing app: copy the packed file over `~/zth-projects/<app>/src/page.html`.
3. In `src/index.tsx` add `allow="clipboard-write"` to the iframe (the generated one does not have it) so copy buttons work.
4. `z2h:preview` → a **private** preview link (only Gal's account). Say so plainly.
5. **Ask Gal** before going live. Only after a yes: commit, `z2h-cli deploy`, then `z2h-cli grant --public` if he wants everyone at monday.com to see it, then tags (the tag list is closed: `App` or `Dashboard`, plus a team; ask Gal which team, never guess).
6. Do not screenshot or drive the deployed app: Gal checks it in his own browser.

## Errors we hit and the fix

| Symptom | Fix |
|---|---|
| Scrolling back up does not update the chapter | `inView` callback returns a function |
| Speech bubble loses its centring after animating | Centre a wrapper, animate the inner element |
| "x is not defined" after editing the shared file | Browser cache: hard reload |
| Effects land in the wrong place / wrong size | Use `cqw` inside a size container the exact size of the image |
| ↓ from the last step jumped over the slider | Give the reveal its own stop |
| `sed -i` fails on macOS | `sed -i ''`, or edit with Python |
| `guard.sh` blocks an `rm` | Do not retry or work around. Ask Gal; a relative-path `rm` inside the project folder is allowed |
| Page opens blank inside Zero to Hero | A relative asset path survived: re-run the pack script and check it reports no unresolved references |
