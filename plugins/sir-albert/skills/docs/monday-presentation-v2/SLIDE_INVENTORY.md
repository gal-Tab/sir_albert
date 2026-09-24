# Slide Template Inventory & Metadata

Complete catalog of all available HTML slide templates with exact structure, content types, and layout specifications. **Use ONLY templates listed here. Never invent or mix layouts.**

## Contents
- [Template Categories](#template-categories)
  - Title & Opening Slides (001, 009, 099)
  - Two-Column Layouts (003, 030, 037, 044)
  - Agenda & Navigation (017)
  - Content Slides (007)
  - List & Bullet Slides (010, 011, 012)
  - Quote & Testimonial (021, 023)
  - Stats & Metrics (031, 032, 033)
  - Comparison (034, 035, 036)
  - Process / Timeline (038, 041, 042, 043)
  - Team & People (057, 058, 059, 061, 062)
  - Image & Media (014, 015, 016, 046+)
- [Content Matching Rules](#content-matching-rules)
- [Quick Reference by Purpose](#quick-reference-by-purpose)

---

## Template Categories

### 1. Title & Opening Slides

#### Deck_Dark_Page_001
**Type:** Title / Cover Slide
**Purpose:** Presentation opening or internal note slide
**Layout:** Centered content with logo at bottom
**Display:** `flex` (column, centered)

**HTML Structure:**
```
.slide-container
  ├─ .content-wrapper
  │  ├─ h1 (title with optional .highlight span)
  │  └─ p (subtitle/description)
  └─ .logo-container
     └─ img.monday-logo
```

**Content Capacity:**
- h1: 1-2 short lines
- p: 2-3 lines max (explanatory text)

**Editable Elements:**
- h1 text + .highlight span color (yellow default)
- p text content
- Logo (fixed)

**Design Variables Used:**
- `--text-h1`, `--text-h4`
- `--weight-regular`, `--weight-light`, `--weight-semibold`
- `--color-text`, `--color-yellow`
- `--space-8`

---

#### Deck_Dark_Page_009
**Type:** Product/Feature Opening Slide
**Purpose:** Introduce product section with visual mockup
**Layout:** Left text content (60%) + Right visual mockup (40%)
**Display:** `grid` (2-col layout with perspective transforms)

**HTML Structure:**
```
.slide-container (grid: 1.15fr 0.85fr)
  ├─ .content-left
  │  ├─ img.logo-top
  │  ├─ h1
  │  └─ p
  └─ .visual-right
     ├─ .ui-mockup-main (data-image-placeholder="screenshot")
     └─ .ui-mockup-float
        └─ .icon-tile (4x, data-image-placeholder="icon")
```

**Content Capacity:**
- h1: 2-3 lines
- p: 3-4 lines
- Mockups: 2 images (1 large, 4 small icons)

**Editable Elements:**
- h1, p text
- Logo top (removable)
- Image placeholders (data-image-placeholder attributes)

**Special Features:**
- Perspective transform on mockups (3D effect)
- Logo at top-left of left column

---

#### Deck_Dark_Page_099
**Type:** Closing / Thank You Slide
**Purpose:** End presentation with CTA
**Layout:** Centered content with logo at bottom
**Display:** `flex` (column, centered)

**HTML Structure:**
```
.slide-container
  ├─ .content-wrapper
  │  ├─ h1 (main message)
  │  └─ .subtitle (contact/CTA)
  └─ .logo-container
     └─ img.monday-logo
```

**Content Capacity:**
- h1: 1-2 words/short lines
- subtitle: 1 line (contact, email, etc.)

**Editable Elements:**
- h1 text
- subtitle text (email, contact, CTA)
- Logo (fixed)

---

### 2. Two-Column Layouts

#### Deck_Dark_Page_003
**Type:** Design System / Tips & Tools Slide
**Purpose:** Left content (tips, text) + Right panel (cards, images)
**Layout:** Left column (1.4fr) + Right column (1fr)
**Display:** `grid` (3 rows, 2 cols)

**HTML Structure:**
```
.slide-container (grid: 1.4fr 1fr, auto 1fr auto)
  ├─ .left-col
  │  ├─ h1
  │  ├─ .color-palette (optional)
  │  └─ .tip-section (repeatable, 3-4 max)
  │     ├─ [spacer] or .demo-box
  │     └─ .tip-content (h3, p with b, u tags)
  └─ .right-col
     ├─ .card (1-2)
     │  ├─ h2
     │  └─ p
     └─ .bordered-card
        ├─ .bordered-header (h2, a.btn-stock)
        └─ .image-grid (3 cols, data-image-placeholder)
```

**Content Capacity:**
- Left h1: 1-2 lines
- Tips: 3-4 sections, each with h3 + p
- Right cards: 2-3 cards max
- Images: 3x grid

**Editable Elements:**
- h1, h3, h2 titles
- p text content
- Color circles (style only)
- Button text
- Image placeholders

**Special Features:**
- Color palette row (9-10 circles)
- Demo boxes (grey/blue rows)
- Icons (via src path)
- Image grid with 3-col layout

---

#### Deck_Dark_Page_030
**Type:** Two-Column Title + Content
**Purpose:** Title on left, bullets/intro on right
**Layout:** Left (title only) | Right (intro text + bullets)
**Display:** `grid` (2 cols, centered)

**HTML Structure:**
```
.slide-container (grid: 1fr 1fr)
  ├─ .left-column
  │  ├─ .mini-title (optional, absolute positioned)
  │  └─ h1.main-title
  └─ .right-column
     ├─ p.intro-text
     └─ ul.bullet-list
        └─ li (3-5 items)
```

**Content Capacity:**
- h1: 2-3 lines
- intro text: 1-2 lines
- Bullets: 3-5 items, 1 line each max

**Editable Elements:**
- h1 text
- intro p text
- Bullet li content
- Mini title (optional)

**Design Notes:**
- Simple, clean layout
- Mini-title positioned top-left
- Bullets styled with • marker

---

#### Deck_Dark_Page_037
**Type:** Left Title + Bullets | Right Image + Panel
**Purpose:** Content on left, image + capabilities on right
**Layout:** Left (1fr) | Right (1.4fr) with two sub-sections
**Display:** `grid` (2 cols, gapped)

**HTML Structure:**
```
.slide-container (grid: 1fr 1.4fr, gap: 9)
  ├─ .mini-title (absolute, top-left)
  ├─ .left-column
  │  ├─ h1.main-title
  │  └─ ul.bullet-list
  │     └─ li (3 items max)
  └─ .right-column
     ├─ .image-panel (data-image-placeholder="photo")
     │  └─ img.placeholder-icon (optional)
     └─ .capabilities-panel
        ├─ h3.cap-header
        └─ .cap-grid (2x2)
           └─ .cap-button (4 items)
```

**Content Capacity:**
- h1: 2-3 lines
- Bullets: 3 items max
- Capabilities: 4 buttons (yellow background)
- 1 image placeholder

**Editable Elements:**
- h1, h3 titles
- Bullet content
- Cap-button text (4 items)
- Image placeholder

**Special Features:**
- Instruction box (red, absolute positioned, top-right) — optional
- Capability buttons with yellow background
- Image placeholder with optional icon overlay

---

#### Deck_Dark_Page_044
**Type:** Left Title | Right 2x2 Feature Grid
**Purpose:** Title + subtitle left, 4-feature cards right
**Layout:** Left (0.6fr) | Right panel (1.4fr)
**Display:** `grid` (2 cols)

**HTML Structure:**
```
.slide-container (grid: 0.6fr 1.4fr)
  ├─ .left-column
  │  ├─ h1.main-title
  │  └─ p.subtitle
  └─ .right-panel (grid: 1fr 1fr, 1fr 1fr)
     └─ .feature-item (4x)
        ├─ .feature-icon (svg inline)
        ├─ h3.feature-title
        └─ p.feature-desc
```

**Content Capacity:**
- h1: 2-3 lines
- subtitle: 1 line
- Features: 4 items (icon + title + desc)

**Editable Elements:**
- h1, subtitle text
- feature-title, feature-desc text (4 sets)
- Feature icons (inline SVG or img)

**Design Notes:**
- Right panel has dark surface background
- 2x2 grid layout
- Icons are small (32px) SVG inline
- Feature descriptions are muted color

---

### 3. Agenda & Navigation

#### Deck_Dark_Page_017
**Type:** Agenda / Chapter Navigation
**Purpose:** List multiple chapters with arrow buttons
**Layout:** Left large title | Right stacked chapter cards
**Display:** `grid` (0.8fr 1.2fr)

**HTML Structure:**
```
.slide-container (grid: 0.8fr 1.2fr)
  ├─ h1 (display size)
  └─ .cards-column
     └─ .chapter-card (5x repeatable)
        ├─ .arrow-circle (svg arrow)
        └─ .chapter-text (title + span)
```

**Content Capacity:**
- h1: 1 word ("Agenda")
- Chapter cards: 5 max
- Chapter text: 1 line each

**Editable Elements:**
- h1 text
- Chapter card title + span (secondary text)
- Arrow SVG (fixed)

**Design Notes:**
- Chapter cards have border, not fill
- Arrow circle is purple with white SVG
- Secondary text (span) is lighter color
- Cards are stacked vertically

---

### 4. Content Slides

#### Deck_Dark_Page_007
**Type:** Orbit / System Diagram Slide
**Purpose:** Text + complex visual with orbit system
**Layout:** Left text (42%) | Right graphic (58%)
**Display:** `flex` (row, gap)

**HTML Structure:**
```
.slide-container
  ├─ .content-wrapper
  │  ├─ .text-content
  │  │  ├─ h1
  │  │  ├─ p
  │  │  └─ ul (3 bullets)
  │  │     └─ li
  │  └─ .graphic-content
  │     └─ .orbit-system
  │        ├─ .central-circle (svg logo inside)
  │        ├─ .orbit-path (circle border)
  │        └─ .shape (7x - circles, rect, hexagon, star, sparkle)
```

**Content Capacity:**
- h1: 1-2 lines
- p: 2-3 lines
- Bullets: 3 items max

**Editable Elements:**
- h1, p text
- Bullet content
- Central logo SVG
- Shape colors (CSS vars)

**Special Features:**
- Complex orbit system with multiple shapes
- Central circle contains SVG logo
- Shapes positioned absolutely within orbit
- Transform 3D effects on shapes

**Design Complexity:** HIGH — use as-is, minimal text edits

---

### 5. List & Bullet Slides

#### Deck_Dark_Page_010
**Type:** Section Opener / Visual Grid
**Purpose:** Section opening slide with large title card + visual panels
**Layout:** 2-column grid with title card spanning full left height
**Display:** `grid` (0.9fr 1.1fr, 2 rows)

> **ACCURACY NOTE:** The actual template is a complex grid layout — NOT a simple bullet list. It has a bordered title card (left, spanning 2 rows), two image placeholders (top-right), and a purple info card (bottom-right). Use `tmpl-twocol` (Page_030) or `tmpl-center` (Page_021) if you need a simple bullet-list slide instead.

**HTML Structure:**
```
.slide-container (grid: 0.9fr 1.1fr, rows: 1fr 1fr)
  ├─ .title-card (grid-row: span 2, bordered)
  │  └─ h1 (display size, mixed weights)
  ├─ .top-right-row (grid: 1fr 1fr)
  │  ├─ .card-green (data-image-placeholder)
  │  └─ .card-white (data-image-placeholder)
  └─ .bottom-right-card (purple bg)
     ├─ p.info-text (department)
     └─ p.info-text (date)
```

**Content Capacity:**
- h1: 3-4 words in display size with mixed light/bold weights
- Info text: 2 lines (department + date)
- Images: 2 photo placeholders (top-right)

**Editable Elements:**
- h1 text + weight spans (.light / .bold)
- Info text in purple card
- Image placeholders

**Best suited for:** Section dividers, part openers. NOT for bullet-heavy content slides.

---

#### Deck_Dark_Page_011, 012
**Type:** Full-Width Bullet List
**Purpose:** Single column, large bullets
**Layout:** Vertical flex with top margin
**Display:** `flex` (column)

**HTML Structure:**
```
.slide-container
  ├─ h1 or h2 (title)
  └─ ul.bullet-list
     └─ li (3-6 items)
```

**Content Capacity:**
- Title: 1-2 lines
- Bullets: 3-6 items, 1-2 lines each

---

### 6. Quote & Testimonial Slides

#### Deck_Dark_Page_021, 023
**Type:** Pull Quote / Testimonial
**Purpose:** Large centered quote with attribution
**Layout:** Centered flex
**Display:** `flex` (column, centered, justify-center)

**HTML Structure:**
```
.slide-container
  ├─ "quotation-mark svg or large quote char
  ├─ blockquote
  └─ .attribution
```

**Content Capacity:**
- Quote: 2-3 sentences
- Attribution: 1 line (name, title)

**Editable Elements:**
- Quote text
- Attribution text

---

### 7. Stats & Metrics Slides

#### Deck_Dark_Page_031, 032, 033
**Type:** Statistics / Metrics Display
**Purpose:** Large numbers with labels
**Layout:** Grid with stat blocks
**Display:** `grid` (auto-fit columns)

**HTML Structure:**
```
.slide-container
  ├─ h2 (title)
  └─ .stats-grid
     └─ .stat-block (3-4 items)
        ├─ .stat-number (large)
        └─ .stat-label
```

**Content Capacity:**
- Title: 1-2 lines
- Stats: 3-4 blocks
- Each stat: 1 number + 1 label line

**Editable Elements:**
- Title text
- Stat numbers and labels

---

### 8. Comparison & Side-by-Side

#### Deck_Dark_Page_034, 035, 036
**Type:** Side-by-Side Comparison
**Purpose:** Before/After or Option A vs B
**Layout:** Two equal columns
**Display:** `grid` (2 cols, equal width)

**HTML Structure:**
```
.slide-container (grid: 1fr 1fr)
  ├─ .left-section
  │  ├─ h3
  │  └─ ul.bullet-list
  │     └─ li (3-4 items)
  └─ .right-section (.bg-surface optional)
     ├─ h3
     └─ ul.bullet-list
        └─ li (3-4 items)
```

**Content Capacity:**
- Each side: 1 title + 3-4 bullets max

**Editable Elements:**
- h3 titles (both sides)
- Bullet content (both sides)

---

### 9. Process / Timeline Slides

#### Deck_Dark_Page_038, 041, 042, 043
**Type:** Step-by-Step Process / Timeline
**Purpose:** Numbered steps with descriptions
**Layout:** Vertical flex with numbered items
**Display:** `flex` (column, gap)

**HTML Structure:**
```
.slide-container
  ├─ h2 (title)
  └─ .steps-container
     └─ .step-item (4-5 repeatable)
        ├─ .step-number (circle with number)
        ├─ h4.step-title
        └─ p.step-description
```

**Content Capacity:**
- Title: 1-2 lines
- Steps: 4-5 items max
- Each step: title + 1-2 line description

**Editable Elements:**
- Title
- Step titles and descriptions
- Numbers (auto-increment)

---

### 10. Team & People Slides

#### Deck_Dark_Page_057, 058, 059, 061, 062
**Type:** Team Member Cards
**Purpose:** Display 4-6 team members with portraits
**Layout:** Grid (4 cols for portraits)
**Display:** `grid` (auto, 4 cols)

**HTML Structure:**
```
.slide-container
  ├─ h2 (title)
  └─ .team-grid (grid: repeat(4, 1fr))
     └─ .team-member (4-6 items)
        ├─ .portrait (circular, data-image-placeholder="portrait")
        ├─ h4.name
        └─ p.role
```

**Content Capacity:**
- Title: 1 line
- Members: 4-6 cards
- Each: portrait + name (1 line) + role (1 line)

**Editable Elements:**
- Title
- Name, role text (per member)
- Portrait images

---

### 11. Image & Media Slides

#### Deck_Dark_Page_014, 015, 016
**Type:** Image Focus / Full-Width Photo
**Purpose:** Large image with optional text overlay
**Layout:** Image-dominant with text overlay
**Display:** Varies (flex or absolute overlay)

**HTML Structure:**
```
.slide-container (background-image or bg-color)
  └─ Optional overlay text
     ├─ h1 or h2
     └─ p (optional)
```

**Content Capacity:**
- Text: headline + 1-2 line description (optional)

**Editable Elements:**
- Background image
- Text content (if present)

---

#### Deck_Dark_Page_046, 047, 049, 050, 051, 052, 053, 054
**Type:** Image Grid / Gallery
**Purpose:** Multiple images in grid layout
**Layout:** 2-3 col grid
**Display:** `grid` (2-3 cols)

**HTML Structure:**
```
.slide-container
  ├─ h2 (title)
  └─ .image-grid (grid: repeat(2-3, 1fr))
     └─ .image-item (data-image-placeholder)
```

**Content Capacity:**
- Title: 1 line
- Images: 4-6 items

**Editable Elements:**
- Title
- Image placeholders

---

### 12. Complex / Visual Slides

#### Deck_Dark_Page_056
**Type:** Infographic / Data Visualization
**Purpose:** Custom layout with mixed elements
**Layout:** Custom flex/grid
**Display:** Varies by design

**Editable Elements:**
- Text, numbers, labels
- Colors (CSS vars)
- Image placeholders

**Design Complexity:** HIGH — review HTML carefully before use

---

#### Deck_Dark_Page_064, 065, 066, 067, 068, 069, 070, 071, 072, 073, 074, 075
**Type:** Specialized / Custom Layouts
**Purpose:** Various unique designs
**Layout:** Varies
**Display:** Mixed

**Action:** Inspect individually. Each has unique structure.

---

#### Deck_Dark_Page_077, 079, 080, 081, 083, 084, 085, 086, 088, 089, 091
**Type:** Variant Layouts
**Purpose:** Combinations of patterns above
**Layout:** Mixed
**Display:** Grid/flex hybrid

**Action:** Inspect as needed for specific use case.

---

## Content Matching Rules

### Match slide template based on:

1. **Layout needs** (1-col, 2-col, grid, centered, etc.)
2. **Content type** (text, image, bullets, numbers, cards, etc.)
3. **Visual density** (sparse, moderate, content-heavy)
4. **Interactive elements** (buttons, links, forms, etc.)

### Never:
- Mix elements from different templates
- Invent new CSS or HTML structure
- Modify grid columns, flex direction, or layout
- Remove or rename element classes

### Always:
- Use exact HTML structure provided
- Keep CSS rules unchanged
- Fill only the named editable elements
- Validate content fits within stated capacity

---

## Quick Reference by Purpose

| Purpose | Template | Layout |
|---------|----------|--------|
| Title / Cover | Page_001 | Centered flex |
| Product Intro | Page_009 | 2-col (60/40) |
| Closing | Page_099 | Centered flex |
| Two-Column Content | Page_030, 037 | Grid 2-col |
| Feature Cards (2x2) | Page_044 | Grid + panel |
| Agenda | Page_017 | Grid 2-col |
| Bullets | Page_010, 011, 012 | Flex column |
| Quote | Page_021, 023 | Centered flex |
| Stats | Page_031, 032, 033 | Grid auto-fit |
| Comparison | Page_034, 035, 036 | Grid 2-col |
| Timeline | Page_038, 041, 042, 043 | Flex column |
| Team | Page_057, 058, 059 | Grid 4-col |
| Images | Page_014, 015, 016 | Varies |
| Image Grid | Page_046, 047+ | Grid 2-3 col |

---

## Design System Validation

All templates use these CSS variables. **Verify they exist in `design-system.css`:**

- `--text-h1`, `--text-h2`, `--text-h3`, `--text-h4`, `--text-body`, `--text-body-sm`, `--text-caption`
- `--weight-light`, `--weight-regular`, `--weight-medium`, `--weight-semibold`
- `--color-text`, `--color-text-secondary`, `--color-text-muted`, `--color-bg`, `--color-surface`
- `--color-purple`, `--color-red`, `--color-yellow`, `--color-green`
- `--space-1` through `--space-10`
- `--radius-xs`, `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`, `--radius-full`
- `--icon-xs`, `--icon-sm`, `--icon-md`, `--icon-lg`, `--icon-xl`

All layouts use viewport-relative units (`vmin`, `vw`, `vh`) for responsive scaling. No hardcoded pixels except for inline SVG dimensions.

---

## How the Skill Uses This

1. **Content Intake** — User provides text, images, structure
2. **Template Matching** — Skill reads this file to find exact match
3. **HTML Extraction** — Skill reads matching `Deck_Dark_Page_XXX.html` file
4. **Content Mapping** — Skill fills only editable elements per this spec
5. **Validation** — Skill verifies content fits within stated capacity
6. **Output** — Generate single HTML file with exact template structure
