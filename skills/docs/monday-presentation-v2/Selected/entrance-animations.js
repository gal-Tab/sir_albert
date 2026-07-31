/**
 * Entrance Animations — auto-detects slide layout and applies
 * staggered reveal animations following natural reading flow.
 *
 * Reads the DOM structure, groups elements into visual rows
 * using vertical-overlap analysis, then sorts top-to-bottom
 * and left-to-right within each row. Each element gets a
 * CSS animation with an increasing delay.
 *
 * Animations defined in design-system.css:
 *   revealUp   — opacity 0→natural + translateY(1.5vmin)→0
 *   revealFade — opacity 0→natural (for elements with existing transforms)
 */
(function () {
  'use strict';

  const STAGGER = 100;
  const DURATION = 600;
  const EASE = 'cubic-bezier(0.23, 1, 0.32, 1)';
  const OVERLAP_THRESHOLD = 0.3;
  const MAX_SIMILAR = 8;
  const MAX_RECURSE_CHILDREN = 6;
  const MAX_DEPTH = 2;

  const ATOMIC = new Set([
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img', 'svg',
    'ul', 'ol', 'blockquote', 'figure', 'hr', 'canvas', 'video', 'table',
  ]);

  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return;

  document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.slide-container');
    if (!container) return;

    const elements = [];
    collect(container, elements, 0);
    sortReadingFlow(elements);

    elements.forEach((el, i) => {
      const delay = 100 + i * STAGGER;
      const xform = getComputedStyle(el).transform;
      const anim = (xform && xform !== 'none') ? 'revealFade' : 'revealUp';
      el.style.animation = `${anim} ${DURATION}ms ${EASE} ${delay}ms backwards`;
    });
  });

  function collect(parent, list, depth) {
    if (depth > MAX_DEPTH) {
      list.push(parent);
      return;
    }

    const kids = visible(parent);
    if (!kids.length) return;

    for (const child of kids) {
      if (ATOMIC.has(child.tagName.toLowerCase())) {
        list.push(child);
        continue;
      }

      const inner = visible(child);

      if (!inner.length) {
        list.push(child);
        continue;
      }

      if (inner.length >= 2 && inner.length <= MAX_SIMILAR && similar(inner)) {
        for (const el of inner) list.push(el);
        continue;
      }

      if (inner.length <= MAX_RECURSE_CHILDREN && depth < MAX_DEPTH) {
        collect(child, list, depth + 1);
      } else {
        list.push(child);
      }
    }
  }

  function similar(els) {
    const classes = els[0].className.trim().split(/\s+/).filter(Boolean);
    for (const cls of classes) {
      if (els.every(el => el.classList.contains(cls))) return true;
    }
    const tag = els[0].tagName;
    return els.every(el => el.tagName === tag && el.children.length > 0);
  }

  function visible(parent) {
    return [...parent.children].filter(el => {
      if (!el?.tagName) return false;
      const s = getComputedStyle(el);
      return s.display !== 'none' && s.visibility !== 'hidden';
    });
  }

  function sortReadingFlow(elements) {
    if (elements.length <= 1) return;

    const items = elements.map(el => ({ el, rect: el.getBoundingClientRect() }));

    const rows = [];
    for (const item of items) {
      let placed = false;
      for (const row of rows) {
        if (vOverlap(item.rect, row[0].rect) > OVERLAP_THRESHOLD) {
          row.push(item);
          placed = true;
          break;
        }
      }
      if (!placed) rows.push([item]);
    }

    rows.sort((a, b) => top(a) - top(b));
    for (const row of rows) row.sort((a, b) => a.rect.left - b.rect.left);

    let idx = 0;
    for (const row of rows) {
      for (const item of row) elements[idx++] = item.el;
    }
  }

  function vOverlap(a, b) {
    const oTop = Math.max(a.top, b.top);
    const oBot = Math.min(a.bottom, b.bottom);
    const overlap = Math.max(0, oBot - oTop);
    const shorter = Math.min(a.bottom - a.top, b.bottom - b.top);
    return shorter > 0 ? overlap / shorter : 0;
  }

  function top(row) {
    return Math.min(...row.map(i => i.rect.top));
  }
})();
