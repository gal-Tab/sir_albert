---
name: monday-presentation-v2
description: Creates branded monday.com HTML presentations using a design-system-first approach with responsive layouts, keyboard navigation, and professional monday branding. Use when the user asks to create a presentation, build slides, make a deck, or generate a slide deck with monday.com branding. Supports content from markdown files, rough outlines, or just a topic. Outputs a single self-contained HTML file.
---

# monday-presentation-v2

Generate professional, single-file monday.com branded HTML presentations with zero dependencies.

## Core Principles

1. **Design-System First** — All output uses official monday.com design tokens (dark bg, Poppins, purple #6164ff)
2. **Existing + Generated** — Reuse proven Deck_Dark_Page templates; generate novel slide types from design system
3. **Zero Dependencies** — Single, self-contained HTML file with inline CSS/JS. No external scripts.
4. **Responsive 16:9** — Every slide fits exactly within viewport (no scrolling, ever)
5. **Keyboard Navigation** — Arrow keys, Space, or click to advance. Slide counter included.

---

## Phase 0: Content Intake & Recipe Selection

### Step 0.1: Identify Recipe

**Read [RECIPES.md](RECIPES.md)** to find the best recipe for the user's presentation type.

**Use the `AskUserQuestion` tool** to present an interactive selection:

```
AskUserQuestion({
  questions: [{
    question: "What type of presentation are you creating?",
    header: "Recipe",
    multiSelect: false,
    options: [
      { label: "Quick Update", description: "Brief status update or announcement (5-8 slides)" },
      { label: "Product Launch", description: "Introduce a new product or major feature (10-15 slides)" },
      { label: "Team Review", description: "Update team on progress and plans (8-12 slides)" },
      { label: "Training", description: "Teach a topic or skill (15-20 slides)" }
    ]
  }]
})
```

> The user can also select "Other" to type a custom presentation type (e.g. Business Proposal).

Once chosen, explain the recipe structure:

> **Your Recipe: [Recipe Name]**
>
> This recipe includes [X] slides in this order:
> - Slide 1: Title (Cover Slide)
> - Slide 2: [Purpose]
> - ...
> - Slide N: Thank You (Closing Slide)
>
> All presentations follow this proven structure: **always start with a cover slide (Deck_Dark_Page_001) and end with a thank you slide (Deck_Dark_Page_001).**

### Step 0.2: Content Intake

After recipe selection, **use `AskUserQuestion`** for content intake:

```
AskUserQuestion({
  questions: [{
    question: "How much content do you have ready?",
    header: "Content",
    multiSelect: false,
    options: [
      { label: "Ready to go", description: "I have full content to paste or upload" },
      { label: "Rough outline", description: "I have bullet points or notes" },
      { label: "Just a topic", description: "Generate content for me from a topic" }
    ]
  }]
})
```

If user has content, ask them to paste or upload it.

**If `content.md` exists in cwd**, skip questions and read it directly.

---

## Phase 1: Layout Mapping

### Step 1.0: Consult Slide Inventory (MANDATORY)

**Read [SLIDE_INVENTORY.md](SLIDE_INVENTORY.md) FIRST** — Complete metadata catalog of every available `Deck_Dark_Page_*.html` template with:
- Exact HTML structure (never invent or modify)
- Content capacity limits per slide
- Editable vs. fixed elements
- Layout specifications (grid cols, flex direction, gaps, sizing)
- Design variables used
- Quick-reference matching table by purpose

**CRITICAL RULE:** Use ONLY templates listed in SLIDE_INVENTORY.md. Never mix elements from different slides. Never create new layouts—work only with existing templates.

### Step 1.1: Map Content to Recipe Slides

Using the recipe structure from Step 0.1:
1. For each slide in the recipe, read the user's content
2. Map content to the recipe's slide position
3. Verify content fits the template specified in the recipe

For example, if using **Recipe 1 (Product Launch)**:
- Slide 1: Use Deck_Dark_Page_001 (cover) — map headline + subtitle
- Slide 2: Use Deck_Dark_Page_010 (problem) — map problem statement + bullets
- Slide 3: Use Deck_Dark_Page_030 (solution) — map solution + key points
- ...and so on per recipe

### Step 1.2: Consult SLIDE_INVENTORY for Template Details

For each recipe slide, **read [SLIDE_INVENTORY.md](SLIDE_INVENTORY.md)** to understand:
- Exact HTML structure (never invent)
- Content capacity limits
- Editable vs. fixed elements
- Layout specifications

### Step 1.3: Create Layout Plan with Template Sources

Build a slide-by-slide plan following the recipe:

```
Slide 1 (Title)        → Deck_Dark_Page_001 (centered, h1 + p + logo)
Slide 2 (Two-Column)   → Deck_Dark_Page_030 (grid 1fr|1fr, title + bullets)
Slide 3 (Features)     → Deck_Dark_Page_044 (grid 0.6fr|1.4fr, title + 2x2 feature grid)
Slide 4 (Metrics)      → Deck_Dark_Page_031 (grid auto-fit, 4 stat blocks)
Slide 5 (Closing)      → Deck_Dark_Page_099 (centered, h1 + contact + logo)
```

**Every slide MUST map to an existing template. No exceptions.**

---

## Phase 2: Review & Approval

**Show the user the recipe-based layout plan:**

> **Proposed Layout (Following [Recipe Name])**
>
> Slide 1: Cover — Deck_Dark_Page_001 (headline + subtitle)
> Slide 2: [Purpose] — Deck_Dark_Page_XXX (content type)
> Slide 3: [Purpose] — Deck_Dark_Page_XXX (content type)
> ...
> Slide N: Thank You — Deck_Dark_Page_001 (closing)
>
> All slides follow the [Recipe Name] recipe structure. Does this look right? Any changes?

**Important:** Always verify that:
- Slide 1 is Deck_Dark_Page_001 (cover/title)
- Final slide is Deck_Dark_Page_001 (thank you/closing)
- All intermediate slides match recipe templates

**Wait for user feedback.** If changes needed, adjust the plan but maintain the recipe structure.

---

## Phase 3: Generate Presentation

When generating, **read these files:**
1. [SLIDE_INVENTORY.md](SLIDE_INVENTORY.md) — Confirm exact template structure
2. [design-system.css](design-system.css) — Inline this entire CSS file into `<style>` (tokens, typography, layouts)

The **brand SVG logo** and **navigation JS** are inlined below — no additional file reads needed.

### Step 3.0: Choose Generation Strategy

There are **two approaches** depending on deck size. Choose the right one:

#### Strategy A: Exact Template Copy (for small decks, 3-10 slides)

For each slide mapped in Phase 1:
1. **Read the source `Deck_Dark_Page_*.html` file** from `/Selected/` directory
2. **Extract EXACTLY** the `.slide-container` HTML and CSS
3. **Replace ONLY the editable content** per SLIDE_INVENTORY specs
4. **Preserve all structural HTML** — do not modify classes, grid, flex, etc.

This is the safest approach but becomes impractical for large decks (20+ slides) because:
- You'd need to read 8-10 template files individually
- CSS class names collide across templates (both use `.main-title`, `.bullet-list`, etc.)
- Each template has its own `<style>` block that must be merged and de-duplicated

#### Strategy B: Template Class Architecture (for large decks, 15+ slides) — RECOMMENDED

Instead of copying each template file verbatim, **extract the layout patterns into reusable CSS template classes**. This was validated in production on a 44-slide workshop deck.

**The 6 template classes** (mapped from Deck_Dark_Page templates):

| Template Class | Source Template | Display | Purpose |
|---------------|----------------|---------|---------|
| `tmpl-cover` | Page_001 | `flex` (column, centered) | Title, closing, minimal slides |
| `tmpl-center` | Page_021 | `flex` (column, centered) | Quotes, code blocks, centered content |
| `tmpl-twocol` | Page_030 | `grid` (1fr 1fr) | Title left + content right |
| `tmpl-compare` | Page_034 | `grid` (1fr 1fr) | Side-by-side comparison panels |
| `tmpl-features` | Page_044 | `grid` (0.6fr 1.4fr) | Title left + 2x2 feature grid right |
| `tmpl-content-img` | Page_038 | `grid` (1fr 1fr) | Title + bullets left, image right |

**How it works:**
1. Define all 6 template classes in `<style>` once — each with `.tmpl-xxx.slide-active { display: flex/grid; ... }` rules
2. Each slide gets: `class="slide-container tmpl-xxx slide-N"` and `data-slide-index="N"`
3. CSS handles show/hide via `.slide-container:not(.slide-active) { display: none !important; }`
4. Navigation JS only toggles `slide-active` class — never touches `style.display`

**CSS structure in the `<head>`:**
```css
/* 1. Design system variables (:root) */
/* 2. Reset + body */
/* 3. Slide base (.slide-container positioning + :not(.slide-active) hide rule) */
/* 4. Template classes (.tmpl-cover, .tmpl-center, etc.) */
/* 5. Shared components (.code-block, .quote-text, .part-label, etc.) */
```

**Benefits:**
- No CSS class name collisions — template classes are unique
- Easy to add/remove slides without touching CSS
- Grid/flex display types are always correct (never overridden by JS)
- Forward/backward navigation never breaks grid layouts
- Much smaller CSS footprint than duplicating per-slide styles

**Slide centering (critical for viewport fit):**
```css
.slide-container {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100vw;
    height: 56.25vw;
    max-height: 100vh;
    max-width: 177.78vh;
}
```

**When to extend:** If content doesn't fit any of the 6 template classes, first try adapting the content to fit. If truly needed, create a new `.tmpl-xxx` class following the same pattern. Never inline layout styles per slide.

### Step 3.1: Icon Selection

**For each slide that includes icons** (feature cards, timeline steps, bullet points with icons, etc.):

1. **Check recipe icon strategy** — [RECIPES.md](RECIPES.md) specifies icon categories for each recipe
2. **Identify icon slots** — Where are icons used in the slide template?
3. **Read [ICON_MATCHING.md](ICON_MATCHING.md)** — Find recommended icons by category for slide purpose
4. **Select best match** — Choose icon from category that fits semantic meaning
5. **Verify path exists** — Confirm icon file exists: `Icons/Property 1=IconName.svg`
6. **Replace in HTML** — Update icon path: `src="Icons/Property 1=SelectediconName.svg"`
7. **Validate rendering** — Ensure icon displays correctly with `ds-icon` class and sizing

**Icon Selection Rules:**
- Always use semantic icons (match meaning of content)
- Prefer consistency (use icons from same visual family)
- Avoid clutter (remove icon if it adds no value)
- Size appropriately (use `ds-icon-sm`, `ds-icon-md`, `ds-icon-lg` based on layout)
- Check file exists before using (Icon folder: `Icons/`)
- **NEVER use emojis** — always use icons from the Icons/ library instead
- **Icons use white** — apply `filter: brightness(0) invert(1)` or the `ds-icon-white` class. The default purple from the SVG files is too saturated on dark backgrounds. Never recolor icons to multiple brand colors (e.g. green + red together)
- **Bullet markers** — use regular dot bullets (`•`) or the default `list-style`. Never use ✓/✗ or other unicode symbols as bullet markers

**Icon Embedding — ALWAYS inline SVGs for portability:**
1. Find the icon file: `Icons/Property 1=IconName.svg`
2. **Read the SVG file** and embed its contents directly in the HTML
3. Add the `ds-icon` classes to the inline `<svg>` element
4. This ensures the HTML works anywhere — no dependency on the Icons/ folder

**Example:**
```
Slide 7 (Track 1 - Training):
- Purpose: Training, education, learning
- Recommended: Academy, Book open, Graduation cap
- Selected: Academy (best fit for training concept)
- Read: Icons/Property 1=Academy.svg
- HTML: <svg class="ds-icon ds-icon-md" ...>[SVG content from file]</svg>
```

### Step 3.2: Generation Requirements

**HTML Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation Title</title>
  <style>
    /* INLINE ALL OF design-system.css HERE */
    /* PLUS slide-specific styles */
  </style>
</head>
<body>
  <!-- Slides container with data-slide-index -->
  <div class="slide-container" data-slide-index="0">
    <!-- Slide content -->
  </div>

  <script>
    /* INLINE NAVIGATION JS FROM NAVIGATION.md */
  </script>
</body>
</html>
```

**Critical CSS Rules:**
- Inline the **entire** [design-system.css](design-system.css) into the `<style>` block first
- Use only CSS variables for sizing (no hardcoded px)
- Font: Poppins from Google Fonts `wght@300;400;500;600`
- Logo: Inline SVG from [BRAND_ASSETS.md](BRAND_ASSETS.md)
- No `text-transform: uppercase` — use letter-spacing instead
- **Multi-slide architecture:** Use `.slide-container:not(.slide-active) { display: none !important }` to hide inactive slides. Each template class (`.tmpl-xxx.slide-active`) defines its own display type (flex or grid). NEVER use inline `style.display` from JavaScript.
- **Slide centering:** Use `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%)` on `.slide-container` for proper viewport centering across all screen sizes.

**Per-Slide Requirements:**
1. `.slide-container` with `data-slide-index="N"`, a template class (e.g., `tmpl-twocol`), AND a unique class like `.slide-1`, `.slide-2`, etc.
2. Color accents: use CSS vars like `var(--color-purple)`, `var(--color-yellow)`, etc.
3. Spacing: `var(--space-4)` through `var(--space-10)` only
4. If using icons: **read the SVG file** from `Icons/Property 1=Name.svg` and **embed inline** — never use `<img src=...>` for icons. Inline SVGs can be recolored with `style="fill: var(--color-xxx)"`
5. **Monday logo on title + closing slides**: Use the inline SVG from the "Inlined Asset" section above — NEVER use external image files
6. **Part labels** (optional): Add `<span class="part-label">PART N — SECTION NAME</span>` for training/workshop decks where the speaker needs section tracking.

**Available Components (from [design-system.css](design-system.css)):**
- `.code-block` — Styled monospace code/prompt display (use for technical slides, file previews, prompt examples)
- `.quote-text` — Large centered italic quote with `.em` spans for highlighted words
- `.part-label` — Section tracker in top-left corner
- `.spectrum-bar` + `.spectrum-segment` — Horizontal progression bar
- `.panel-code` — Code block inside comparison panels

**Navigation JS:**
- Arrow Right / Space to advance
- Arrow Left to go back
- Display slide counter (e.g., "Slide 3 of 5")
- **IMPORTANT**: Use the navigation JS from the "Inlined Asset" section above which uses `classList.toggle('slide-active')` — NEVER inline `style.display`.

### Inlined Asset: monday.com Logo SVG

Use this inline SVG on title and closing slides. CSS class: `.monday-logo { height: 4vmin; width: auto; max-width: 15vmin; }` Place inside `<div class="logo-container">` with `position: absolute; bottom: var(--space-8); display: flex; justify-content: center; width: 100%;`.

```html
<svg class="monday-logo" width="282" height="50" viewBox="0 0 282 50" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5.68474 35.762C3.70108 35.7602 1.87466 34.7272 0.914601 33.0642C-0.0454546 31.4011 0.0120846 29.3698 1.06488 27.7591L10.8879 12.7341C11.8969 11.0981 13.7529 10.1154 15.7356 10.1675C17.7182 10.2196 19.5153 11.2982 20.4292 12.9847C21.3431 14.6713 21.2298 16.7001 20.1335 18.2836L10.3163 33.3086C9.31775 34.8373 7.56703 35.7647 5.68474 35.762Z" fill="#FB275D"/>
  <path d="M22.4209 35.7618C20.4405 35.7601 18.6171 34.7296 17.6586 33.0704C16.7001 31.4113 16.7576 29.3849 17.8086 27.778L27.6127 12.7887C28.6058 11.1288 30.4684 10.1226 32.4659 10.1668C34.4635 10.211 36.2755 11.2985 37.1875 13.0005C38.0995 14.7025 37.9651 16.7459 36.8373 18.325L27.0332 33.3143C26.0386 34.836 24.296 35.7607 22.4209 35.7618V35.7618Z" fill="#FFCC00"/>
  <path d="M38.7383 35.7925C41.7384 35.7925 44.1705 33.3647 44.1705 30.3698C44.1705 27.3749 41.7384 24.947 38.7383 24.947C35.7382 24.947 33.3062 27.3749 33.3062 30.3698C33.3062 33.3647 35.7382 35.7925 38.7383 35.7925Z" fill="#00CA72"/>
  <path d="M214.619 45.1879L219.096 34.827L209.273 11.9539H217.531L223.138 26.749L228.875 11.9539H236.786L222.617 45.1879H214.619Z" fill="white"/>
  <path d="M191.966 11.6026C195.617 11.6026 198.181 13.2709 199.485 15.4221V11.9538H206.918V36.4513H199.485V32.983C198.138 35.1342 195.574 36.8025 191.966 36.8025C186.011 36.8025 181.317 31.8855 181.317 24.1587C181.317 16.4318 186.011 11.6026 191.966 11.6026ZM188.88 24.1587C188.88 28.066 191.357 30.2611 194.183 30.2611C197.008 30.2611 199.485 28.1099 199.485 24.2026C199.485 20.2952 197.008 18.144 194.183 18.144C191.357 18.144 188.88 20.2513 188.88 24.1587Z" fill="white"/>
  <path d="M163.184 11.6027C166.4 11.6027 169.138 13.0954 170.616 15.3344V3.96375H178.092V36.4515H170.616V32.9393C169.312 35.1783 166.748 36.8027 163.14 36.8027C157.186 36.8027 152.491 31.8856 152.491 24.1588C152.491 16.432 157.186 11.6027 163.184 11.6027ZM160.054 24.1588C160.054 28.0661 162.532 30.2612 165.357 30.2612C168.182 30.2612 170.66 28.11 170.66 24.2027C170.66 20.2954 168.182 18.1442 165.357 18.1442C162.532 18.1442 160.054 20.2515 160.054 24.1588Z" fill="white"/>
  <path d="M142.006 23.1489C142.006 19.8123 140.137 17.9684 137.356 17.9684C134.487 17.9684 132.661 19.8123 132.661 23.1489V36.4513H125.229V11.9538H132.661V15.2465C134.139 13.1392 136.747 11.6904 140.007 11.6904C145.657 11.6904 149.395 15.5538 149.395 22.1392V36.4513H142.006V23.1489Z" fill="white"/>
  <path d="M109.31 37.022C102.182 37.022 96.8359 32.1927 96.8359 24.2025C96.8359 16.2123 102.312 11.383 109.441 11.383C116.569 11.383 122.045 16.2123 122.045 24.2025C122.045 32.1927 116.482 37.022 109.31 37.022ZM104.355 24.2025C104.355 28.3293 106.659 30.3049 109.31 30.3049C111.962 30.3049 114.483 28.3293 114.483 24.2025C114.483 20.0318 112.005 18.1001 109.397 18.1001C106.746 18.1001 104.355 20.0318 104.355 24.2025Z" fill="white"/>
  <path d="M52.8496 11.9538H60.2821V15.0709C61.7164 13.0514 64.2374 11.6904 67.3668 11.6904C71.0613 11.6904 74.0169 13.3148 75.6686 16.2563C77.2768 13.666 80.2759 11.6904 83.84 11.6904C89.8381 11.6904 93.7065 15.5538 93.7065 22.1392V36.4513H86.3175V23.1489C86.3175 19.944 84.4485 18.188 81.6667 18.188C78.7981 18.188 77.016 19.944 77.016 23.1489V36.4513H69.627V23.1489C69.627 19.944 67.758 18.188 64.9763 18.188C62.1076 18.188 60.2821 19.944 60.2821 23.1489V36.4513H52.8496V11.9538Z" fill="white"/>
  <path d="M236.725 31.4375C236.725 30.4075 236.936 29.5107 237.359 28.7473C237.782 27.9718 238.366 27.372 239.112 26.9479C239.871 26.5238 240.735 26.3117 241.705 26.3117C242.96 26.3117 243.992 26.6086 244.801 27.2023C245.621 27.7961 246.162 28.6201 246.423 29.6743H244.595C244.421 29.0685 244.079 28.5898 243.57 28.2384C243.072 27.887 242.451 27.7113 241.705 27.7113C240.735 27.7113 239.951 28.0385 239.355 28.6928C238.758 29.335 238.459 30.2499 238.459 31.4375C238.459 32.6371 238.758 33.5641 239.355 34.2184C239.951 34.8728 240.735 35.2 241.705 35.2C242.451 35.2 243.072 35.0303 243.57 34.691C244.067 34.3517 244.409 33.867 244.595 33.2369H246.423C246.15 34.2548 245.602 35.0727 244.782 35.6907C243.961 36.2966 242.935 36.5996 241.705 36.5996C240.735 36.5996 239.871 36.3875 239.112 35.9634C238.366 35.5393 237.782 34.9394 237.359 34.1639C236.936 33.3884 236.725 32.4796 236.725 31.4375Z" fill="white"/>
  <path d="M272.121 26.2935C272.916 26.2935 273.625 26.4571 274.247 26.7843C274.868 27.0993 275.36 27.578 275.72 28.2202C276.081 28.8625 276.261 29.644 276.261 30.565V36.436H274.582V30.8013C274.582 29.8076 274.328 29.0503 273.818 28.5292C273.32 27.996 272.643 27.7295 271.785 27.7295C270.902 27.7295 270.2 28.0082 269.677 28.5656C269.155 29.1109 268.894 29.9046 268.894 30.9467V36.436H267.216V30.8013C267.216 29.8076 266.961 29.0503 266.451 28.5292C265.953 27.996 265.276 27.7295 264.418 27.7295C263.535 27.7295 262.833 28.0082 262.31 28.5656C261.788 29.1109 261.527 29.9046 261.527 30.9467V36.436H259.83V26.4753H261.527V27.9112C261.863 27.3902 262.31 26.9903 262.87 26.7116C263.442 26.4329 264.07 26.2935 264.754 26.2935C265.612 26.2935 266.37 26.4813 267.029 26.857C267.688 27.2326 268.179 27.784 268.502 28.511C268.788 27.8082 269.261 27.2629 269.92 26.8752C270.579 26.4874 271.312 26.2935 272.121 26.2935Z" fill="white"/>
  <path d="M252.871 36.5996C251.913 36.5996 251.043 36.3875 250.26 35.9634C249.489 35.5393 248.88 34.9394 248.432 34.1639C247.997 33.3763 247.779 32.4675 247.779 31.4375C247.779 30.4196 248.003 29.5229 248.451 28.7473C248.911 27.9597 249.532 27.3599 250.316 26.9479C251.099 26.5238 251.976 26.3117 252.945 26.3117C253.915 26.3117 254.792 26.5238 255.575 26.9479C256.358 27.3599 256.974 27.9536 257.421 28.7292C257.882 29.5047 258.112 30.4075 258.112 31.4375C258.112 32.4675 257.875 33.3763 257.403 34.1639C256.943 34.9394 256.315 35.5393 255.519 35.9634C254.723 36.3875 253.841 36.5996 252.871 36.5996ZM252.871 35.1454C253.48 35.1454 254.052 35.0061 254.587 34.7274C255.121 34.4487 255.55 34.0306 255.873 33.4732C256.209 32.9158 256.377 32.2372 256.377 31.4375C256.377 30.6377 256.215 29.9591 255.892 29.4017C255.569 28.8443 255.215 28.4323 254.624 28.1657C254.102 27.887 253.536 27.7476 252.927 27.7476C252.305 27.7476 251.733 27.887 251.211 28.1657C250.701 28.4323 250.291 28.8443 249.98 29.4017C249.669 29.9591 249.514 30.6377 249.514 31.4375C249.514 32.2493 249.663 32.934 249.961 33.4914C250.272 34.0488 250.682 34.4669 251.192 34.7456C251.702 35.0122 252.262 35.1454 252.871 35.1454Z" fill="white"/>
  <path d="M232.606 36.5996C232.111 36.5996 231.701 36.439 231.376 36.1178C231.063 35.7826 230.907 35.3707 230.907 34.8819C230.907 34.3931 231.063 33.9881 231.376 33.6669C231.701 33.3318 232.111 33.1642 232.606 33.1642C233.088 33.1642 233.485 33.3318 233.798 33.6669C234.11 33.9881 234.266 34.3931 234.266 34.8819C234.266 35.3707 234.11 35.7826 233.798 36.1178C233.485 36.439 233.088 36.5996 232.606 36.5996Z" fill="white"/>
</svg>
```

### Inlined Asset: Navigation JS Controller

Inline this in every generated presentation's `<script>` tag. Uses class-based toggling only — never sets inline `style.display`.

```javascript
(function() {
    let currentSlide = 0;
    let slides = [];

    function init() {
        slides = document.querySelectorAll('[data-slide-index]');
        if (slides.length === 0) return;
        showSlide(0);
        addNavigationUI();
        document.addEventListener('keydown', handleKeyDown);
        addTouchNavigation();
    }

    function showSlide(n) {
        if (n >= slides.length) currentSlide = 0;
        else if (n < 0) currentSlide = slides.length - 1;
        else currentSlide = n;
        slides.forEach(function(slide, index) {
            slide.classList.toggle('slide-active', index === currentSlide);
        });
        updateCounter();
    }

    function handleKeyDown(e) {
        switch (e.key) {
            case 'ArrowRight': case ' ':
                e.preventDefault(); showSlide(currentSlide + 1); break;
            case 'ArrowLeft':
                e.preventDefault(); showSlide(currentSlide - 1); break;
        }
    }

    function addNavigationUI() {
        var counter = document.createElement('div');
        counter.id = 'slide-counter';
        counter.style.cssText = 'position:fixed;bottom:3vmin;right:3vmin;font-family:Poppins,sans-serif;font-size:1.8vmin;color:#a0a0a0;cursor:pointer;user-select:none;padding:1vmin 2vmin;border-radius:999px;transition:all .2s ease;z-index:100;';
        counter.addEventListener('click', jumpToSlide);
        counter.addEventListener('mouseover', function(){ counter.style.backgroundColor='#232427'; counter.style.color='#fff'; });
        counter.addEventListener('mouseout', function(){ counter.style.backgroundColor='transparent'; counter.style.color='#a0a0a0'; });
        document.body.appendChild(counter);
    }

    function updateCounter() {
        var counter = document.getElementById('slide-counter');
        if (counter) counter.textContent = (currentSlide + 1) + ' / ' + slides.length;
    }

    function jumpToSlide() {
        var input = prompt('Enter slide number (1-' + slides.length + '):', String(currentSlide + 1));
        if (input !== null) {
            var n = parseInt(input, 10);
            if (!isNaN(n) && n >= 1 && n <= slides.length) showSlide(n - 1);
        }
    }

    function addTouchNavigation() {
        var startX = 0;
        document.addEventListener('touchstart', function(e) { startX = e.changedTouches[0].screenX; });
        document.addEventListener('touchend', function(e) {
            var diff = startX - e.changedTouches[0].screenX;
            if (Math.abs(diff) > 50) { diff > 0 ? showSlide(currentSlide + 1) : showSlide(currentSlide - 1); }
        });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
```

---

## Phase 4: PPT Conversion (Optional)

If user has a .pptx file:

1. Extract content using `python scripts/extract-pptx.py <file.pptx> output/`
   - Install python-pptx if needed: `pip install python-pptx`
2. Review extracted slides
3. Return to Phase 0 (content intake)
4. Follow phases 1-3 normally

---

## Phase 5: Delivery

**Open the file:**
```
open presentation.html
```

**Summarize for the user:**

> **Your deck is ready!**
>
> **File:** `presentation.html` (self-contained, no external dependencies)
>
> **Navigation:**
> - Arrow keys or Space to advance
> - Click slide counter to jump to a specific slide
> - Bottom-right: current slide / total slides
>
> **Customization:**
> Want to tweak colors, text, or layout? Edit the HTML file directly:
> - Colors: Find `:root { --color-purple: ...}` to change brand color
> - Text: Edit content inside `<h1>`, `<h2>`, `<p>` tags
> - Layout: Modify grid or flex properties in `<style>` block
>
> To regenerate: Create a `content.md` file and run the skill again with `update`.

**Optional:** Offer to create a `content.md` template for future updates.

---

## `content.md` Format (Optional)

Users can provide a `content.md` file in the working directory for repeatable deck generation. Format:

```markdown
# Presentation Meta
title: [Title]
audience: [Audience]

## Slide N: [Name]
type: [title|text-body|bullets|metrics|two-col|feature-grid|quote|comparison|steps|closing]
headline: [Text]
subtitle/body/bullets/stats: [Content]
accent: [purple|green|yellow|red]
```

See [SLIDE_TEMPLATES.md](SLIDE_TEMPLATES.md) for all supported slide types.

---

## Supported Slide Types

See [SLIDE_TEMPLATES.md](SLIDE_TEMPLATES.md) for full documentation:

- `title` — Cover slide with logo, headline, subtitle
- `text-body` — Text + optional image/content
- `bullets` — Headline + bullet list with optional icons
- `metrics` — Large numbers with labels (stats)
- `two-col` — Two-column layout with distinct sections
- `feature-grid` — 2x2 card grid (cards with icons/descriptions)
- `quote` — Full-slide pull quote
- `table` — Styled data table
- `team` — Team member cards (portrait + name + role)
- `comparison` — Side-by-side comparison
- `full-bleed` — Full background image with overlay text
- `section-divider` — Large section number + label
- `steps` — Numbered timeline/action steps
- `closing` — Closing slide with CTA + logo

---

## Supporting Files

| File | Purpose |
|------|---------|
| [RECIPES.md](RECIPES.md) | **Phase 0** — 5 pre-designed presentation recipes with slide sequences and best practices |
| [SLIDE_INVENTORY.md](SLIDE_INVENTORY.md) | **Phase 1** — MANDATORY metadata of every Deck_Dark_Page_*.html template with exact structure and content limits |
| [ICON_MATCHING.md](ICON_MATCHING.md) | **Phase 3.1** — Semantic icon recommendations by slide purpose and content type |
| [design-system.css](design-system.css) | CSS tokens, typography, spacing — inline directly into generated HTML |
| [ICON_GUIDE.md](ICON_GUIDE.md) | 267 icon names and categories |

> **Note:** Brand SVG logo and navigation JS are inlined directly in this SKILL.md — no need to read BRAND_ASSETS.md or NAVIGATION.md separately.

---

## Examples

### Example 1: 3-Slide Quick Deck

User: "Create a 3-slide board update for leadership"

Layout plan:
1. Title (Impact Snapshot)
2. Metrics (Key outcomes)
3. Closing (Next steps)

Output: `board-update.html` (~15KB self-contained)

### Example 2: Full Product Presentation

User: "Build a 10-slide product launch deck. I have these talking points: [...]"

Layout plan:
1. Title
2. Problem
3. Solution overview
4. Feature 1 + demo
5. Feature 2 + demo
6. Metrics / social proof
7. Roadmap
8. Pricing
9. Q&A
10. Closing

Output: `product-launch.html` (~35KB self-contained)

### Example 3: 44-Slide Workshop (Template Class Architecture)

User: "Build a training deck from claude-code-workshop.md — 68-minute workshop with demos"

**Strategy:** Used Template Class Architecture (Strategy B) because 44 slides is too many for exact template copy.

**Template class usage:**
- `tmpl-cover` (2 slides): Title + closing
- `tmpl-center` (14 slides): Quotes, code blocks, tasks, centered content
- `tmpl-twocol` (9 slides): Two-column title + content
- `tmpl-compare` (7 slides): Side-by-side comparisons
- `tmpl-features` (8 slides): Feature grids and card layouts
- `tmpl-content-img` (1 slide): Content + image placeholder

**Components used:** `.code-block` for 8 file-preview slides, `.quote-text` for emphasis, `.part-label` on all slides for speaker section tracking, `.spectrum-bar` for progression concepts, `.panel-code` inside comparison panels.

**Key decisions:**
- Part labels on every slide so speaker knows which section they're in
- Code block slides (showing .md file contents) condensed to 5-8 lines each
- Comparison panels adapted for text-only content (no image placeholders needed)

Output: `claude-code-workshop.html` (~35KB self-contained, 44 slides)

---

## Quality Checklist

Before delivery, ensure:

- [ ] All slides fit within viewport (no scroll)
- [ ] Typography uses only Poppins 300/400/500/600
- [ ] Colors use CSS variables from design system
- [ ] No external images/scripts (all inline or relative paths)
- [ ] Keyboard navigation works (arrows, space, slide counter)
- [ ] Logo appears on title and closing slides (inline SVG, not `<img>`)
- [ ] Spacing uses `var(--space-*)` consistently
- [ ] On mobile 16:9 still locked (no reflow)
- [ ] **Each template class has `.tmpl-xxx.slide-active { display: flex/grid; }` — no inline style.display from JS**
- [ ] **Navigation uses only `.classList.toggle('slide-active', ...)` — never touches `style.display`**
- [ ] **Test navigation: move forward/backward/forward on grid slides to ensure layout is preserved**
- [ ] **Slides use absolute centering (`position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%)`) for proper viewport fit**
- [ ] Icons render with correct colors (test on all slides)
- [ ] `.slide-container:not(.slide-active) { display: none !important }` rule is present

