# monday-presentation-v2

Generate professional, single-file monday.com branded HTML presentations with a design-system-first approach.

## Features

✨ **Design System First** — Every deck uses official monday.com brand colors, Poppins font, and responsive layouts

📐 **67 HTML Templates & 14 Slide Types** — Comprehensive library of design variations (Deck_Dark_Page_001 through Deck_Dark_Page_044+) supporting title, text+image, bullets, metrics, two-column, feature grid, quote, table, team, comparison, full-bleed, section divider, steps, and closing

⌨️ **Keyboard Navigation** — Arrow keys, Space, or click slide counter to advance

📱 **Responsive 16:9** — Automatically scales from desktop to tablet to mobile

🎯 **Single-File Output** — All CSS, JS, and logos inline. No external dependencies.

🎨 **Customizable** — Easily override colors, text, images, and spacing using CSS variables

---

## Quick Start

```bash
/monday-presentation-v2
```

Then answer the prompts:
1. What's your deck about?
2. Who's the audience?
3. How many slides?
4. Do you have content ready?

Claude generates a complete `presentation.html` file you can open immediately.

---

## Workflow

1. **Phase 0 — Content Intake** — Share your topic and slides
2. **Phase 1 — Layout Mapping** — Claude assigns templates to each slide
3. **Phase 2 — Review** — Confirm the layout plan
4. **Phase 3 — Generate** — Get a polished HTML deck
5. **Phase 5 — Delivery** — Open, customize, and present

---

## Slide Templates

| Template | Best For | Content |
|----------|----------|---------|
| `title` | Cover slide | Headline + subtitle + logo |
| `text-body` | Narrative | Text + optional image |
| `bullets` | Key points | Heading + 3-5 bullets |
| `metrics` | Stats | Large numbers with labels |
| `two-col` | Details | Left text + right panel |
| `feature-grid` | Features | 2x2 card grid |
| `quote` | Testimonials | Large centered quote |
| `table` | Data | Structured rows/columns |
| `team` | People | Portraits + names + roles |
| `comparison` | Options | Side-by-side comparison |
| `full-bleed` | Emphasis | Full-background image |
| `section-divider` | Transitions | Section number + label |
| `steps` | Process | Numbered action items |
| `closing` | End | CTA + logo |

---

## Example Usage

### Example 1: 3-Slide Quick Pitch

```
User: Create a 3-slide investor pitch deck

Layout plan:
1. Title — Your Company
2. Metrics — Key results
3. Closing — Let's talk

Output: Single HTML file, ready to present
```

### Example 2: 6-Slide Product Update

```
User: Build a 6-slide product launch deck with these talking points: [...]

Layout plan:
1. Title
2. Problem
3. Solution (text + image)
4. Key metrics
5. Feature grid
6. Closing

Output: Professional deck with monday branding, keyboard nav, responsive design
```

---

## Customization

### Change Colors

Find the `:root` CSS variables at the top of the HTML file:

```css
--color-purple: #6164ff;  /* Change to your brand color */
--color-text: #ffffff;
--color-bg: #000000;
```

### Edit Text

Simply edit the HTML content:
- `<h1>`, `<h2>`, `<h3>` for headings
- `<p>` for body text
- `<li>` for bullets

### Add Images

Replace `data-image-placeholder` divs with real images:

```html
<!-- Before -->
<div data-image-placeholder="photo" style="width: 40vmin; height: 25vmin;"></div>

<!-- After -->
<img src="your-image.jpg" style="width: 40vmin; height: 25vmin; border-radius: var(--radius-lg);">
```

### Use Icons

Reference monday.com icons from the `Icons/` folder:

```html
<img src="Icons/Property 1=Graph arrow up.svg" class="ds-icon ds-icon-lg">
```

See [ICON_GUIDE.md](ICON_GUIDE.md) for all 267 available icons.

---

## Design System

Every presentation uses the official monday.com design tokens:

- **Colors:** Purple (#6164ff), Green (#00c875), Yellow (#ffcb00), Red (#ff3d57)
- **Typography:** Poppins font, weights 300/400/500/600
- **Spacing:** Responsive scale using vmin units
- **Components:** Cards, badges, pills, buttons, grids

See [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) for complete reference.

---

## Navigation

**Desktop:**
- ➡️ Right Arrow or Space → Next slide
- ⬅️ Left Arrow → Previous slide
- Click "X / Y" counter to jump to slide

**Mobile:**
- ← Swipe left → Next slide
- Swipe right → Previous slide
- Tap counter to jump

---

## Files Included

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Main workflow and phases |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) | Complete design tokens and CSS variables |
| [SLIDE_TEMPLATES.md](SLIDE_TEMPLATES.md) | 14 templates with HTML patterns |
| [BRAND_ASSETS.md](BRAND_ASSETS.md) | monday.com SVG logos |
| [ICON_GUIDE.md](ICON_GUIDE.md) | 267 icon reference and usage |
| [NAVIGATION.md](NAVIGATION.md) | Keyboard/click navigation JS controller |
| [README.md](README.md) | This file |

---

## Tips for Best Results

✅ **Do:**
- Keep slides focused (1 headline + supporting content)
- Use images to break up text
- Leverage icons for visual interest
- Test keyboard navigation before presenting

❌ **Don't:**
- Overload slides with bullet points (max 5)
- Use external image URLs (icons and logos must be inline or local)
- Change the font family (Poppins only)
- Scroll content (split into multiple slides instead)

---

## Output

Every deck is a **single, self-contained HTML file** with:
- ✅ Inline CSS (all design-system tokens)
- ✅ Inline JavaScript (navigation controller)
- ✅ Inline SVG logos (monday.com branding)
- ✅ Relative icon paths (to `Icons/` folder)
- ✅ No external dependencies
- ✅ Works offline

---

## Support

For detailed workflow, see [SKILL.md](SKILL.md)

For design tokens and customization, see [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)

For slide layout patterns, see [SLIDE_TEMPLATES.md](SLIDE_TEMPLATES.md)

