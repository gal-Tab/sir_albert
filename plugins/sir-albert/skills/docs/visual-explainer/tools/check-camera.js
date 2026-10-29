/* check-camera.js — scroll-film only. Paste into the page's DevTools console (or run it with a browser tool).
   For every chapter that has `box: [x0, y0, x1, y1]` (percent of the image, see story.js), it scrolls to the chapter, waits for the camera to
   settle, projects the box onto the screen, and reports
     covered  = share of the object hidden by the chapter's card
     offscreen = share of the object outside the viewport
   Fix anything with covered > 0.15 by lowering `s`, moving `a`, or switching `side` in that chapter's `cam`.
   Run it at 1440x900 and again at a phone size (375x812); the mobile layout is different.
   Note: in a hidden or background browser pane the camera only advances when frames render, so this waits 1.8 s per chapter. */
(async () => {
  const rows = [];
  for (const c of CHAPS) {
    if (!c.box) continue;
    chap(c.key).scrollIntoView({ block: c.kind === 'reveal' ? 'start' : 'center', behavior: 'instant' });
    await new Promise(r => setTimeout(r, 1800));
    const { tx, ty, s } = target(c.key), { W, H } = geom();
    const [x0, y0, x1, y1] = c.box;
    const obj = { l: tx + s * W * x0 / 100, t: ty + s * H * y0 / 100, r: tx + s * W * x1 / 100, b: ty + s * H * y1 / 100 };
    const card = chap(c.key).querySelector('.card').getBoundingClientRect();
    const area = q => Math.max(0, q.r - q.l) * Math.max(0, q.b - q.t);
    const inter = (p, q) => ({ l: Math.max(p.l, q.l), t: Math.max(p.t, q.t), r: Math.min(p.r, q.r), b: Math.min(p.b, q.b) });
    const full = area(obj) || 1;
    const view = { l: 0, t: 0, r: innerWidth, b: innerHeight };
    rows.push({
      chapter: c.key,
      covered: +(area(inter(obj, { l: card.left, t: card.top, r: card.right, b: card.bottom })) / full).toFixed(2),
      offscreen: +(1 - area(inter(obj, view)) / full).toFixed(2),
      zoom: +s.toFixed(2)
    });
  }
  scrollTo({ top: 0, behavior: 'instant' });
  console.table(rows);
  window.__cameraCheck = rows;
  return rows;
})();
