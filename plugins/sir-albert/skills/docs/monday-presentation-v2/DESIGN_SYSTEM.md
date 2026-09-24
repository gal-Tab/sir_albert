# Design System — monday.com Presentations

Complete reference of all CSS variables, components, and patterns used in monday-presentation-v2 decks.

## CSS Variables (Root)

All presentations inline this complete CSS variable set. Use these consistently for brand compliance.

### Typography

**Font Sizes** (responsive with vmin)
```css
--text-display: 10.5vmin;   /* Hero headlines */
--text-h1: 8vmin;            /* Main slide titles */
--text-h2: 6vmin;            /* Section headers */
--text-h3: 4vmin;            /* Subsection titles */
--text-h4: 3vmin;            /* Labels, detail headers */
--text-body: 2.2vmin;        /* Body copy */
--text-body-sm: 1.8vmin;     /* Small body text */
--text-caption: 1.4vmin;     /* Captions, meta info */
```

**Font Weights**
```css
--weight-light: 300;         /* Light accents */
--weight-regular: 400;       /* Default, body text */
--weight-medium: 500;        /* Emphasis */
--weight-semibold: 600;      /* Bold, headings */
```

**Line Heights**
```css
--leading-tight: 1.1;        /* Compact headlines */
--leading-snug: 1.3;         /* Headlines with breathing room */
--leading-normal: 1.5;       /* Body text default */
--leading-relaxed: 1.7;      /* Loose, accessible body */
```

**Letter Spacing**
```css
--tracking-tight: -0.025em;  /* Negative tracking for display text */
--tracking-normal: -0.01em;  /* Subtle tightening */
--tracking-none: 0;          /* Normal spacing */
```

### Colors

**Backgrounds**
```css
--color-bg: #000000;               /* Page background (dark) */
--color-surface: #232427;          /* Card/panel background */
--color-surface-alt: #2D3035;      /* Alternate surface, dark accent */
```

**Text**
```css
--color-text: #ffffff;             /* Primary text (white) */
--color-text-secondary: #c3ced8;   /* Secondary text (muted white) */
--color-text-muted: #a0a0a0;       /* Tertiary text (gray) */
```

**Brand Accents**
```css
--color-purple: #6164ff;           /* Primary brand color */
--color-purple-light: #8A99FF;     /* Light purple for contrast */
--color-red: #ff3d57;              /* Status: alert, negative */
--color-yellow: #ffcb00;           /* Status: warning, highlight */
--color-green: #00c875;            /* Status: success, positive */
```

**Borders**
```css
--color-border: rgba(255, 255, 255, 0.15);    /* Subtle border */
--color-border-strong: rgba(255, 255, 255, 0.8); /* Prominent border */
```

### Spacing

All spacing uses viewport-relative units (`vmin`) for responsive scaling.

```css
--space-1: 0.5vmin;    /* 4-8px (tiny gap) */
--space-2: 1vmin;      /* 8-10px */
--space-3: 1.5vmin;    /* 12-15px */
--space-4: 2vmin;      /* 16-20px */
--space-5: 3vmin;      /* 24-30px */
--space-6: 4vmin;      /* 32-40px (comfortable gap) */
--space-7: 5vmin;      /* 40-50px */
--space-8: 6vmin;      /* 48-60px (section break) */
--space-9: 8vmin;      /* 64-80px */
--space-10: 10vmin;    /* 80-100px (large break) */
```

### Border Radius

```css
--radius-xs: 0.5vmin;   /* Tight corners */
--radius-sm: 1vmin;     /* Small curves */
--radius-md: 2vmin;     /* Medium, typical cards */
--radius-lg: 3vmin;     /* Large curves */
--radius-xl: 4vmin;     /* Extra large, panels */
--radius-full: 999px;   /* Fully rounded (pills, badges) */
```

### Icons

```css
--icon-xs: 3vmin;      /* 24-30px */
--icon-sm: 5vmin;      /* 40-50px */
--icon-md: 7vmin;      /* 56-70px (default) */
--icon-lg: 10vmin;     /* 80-100px */
--icon-xl: 15vmin;     /* 120-150px (display) */
```

### Slide Layout

```css
--slide-padding-y: 8vmin;   /* Vertical padding inside slide */
--slide-padding-x: 10vmin;  /* Horizontal padding inside slide */
```

---

## Base Classes

Apply these to any element to match design system:

### Typography Classes

```html
<h1 class="text-h1">Main Title</h1>
<h2 class="text-h2">Section Header</h2>
<h3 class="text-h3">Subsection</h3>
<p class="text-body">Body copy here</p>
<p class="text-caption">Small caption</p>
```

**Font Weight Modifiers**
```html
<span class="font-light">Light text</span>
<span class="font-regular">Regular</span>
<span class="font-medium">Medium emphasis</span>
<span class="font-semibold">Bold</span>
```

### Color Classes

**Backgrounds**
```html
<div class="bg-surface">Card background</div>
<div class="bg-purple">Purple accent</div>
<div class="bg-green">Success green</div>
```

**Text Colors**
```html
<p class="text-secondary">Secondary text</p>
<p class="text-purple">Purple accent text</p>
<p class="text-yellow">Warning yellow</p>
```

---

## Component Patterns

### Card (Surface Panel)

```html
<div style="background-color: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: var(--space-6);">
  <h3 class="text-h3">Card Title</h3>
  <p class="text-body">Card content here</p>
</div>
```

**With Border**
```html
<div style="border: 1px solid var(--color-border-strong);
            border-radius: var(--radius-xl);
            padding: var(--space-6);">
  Content
</div>
```

### Pill / Badge

```html
<span style="display: inline-block;
             border: 1px solid var(--color-text);
             border-radius: var(--radius-full);
             padding: var(--space-1) var(--space-4);
             font-size: var(--text-caption);
             font-weight: var(--weight-regular);">
  Label
</span>
```

### Mini Title / Tag

```html
<div style="display: inline-block;
            border: 1px solid var(--color-text);
            border-radius: var(--radius-full);
            padding: var(--space-1) var(--space-5);
            font-size: var(--text-caption);
            font-weight: var(--weight-regular);
            margin-bottom: var(--space-4);">
  Section Tag
</div>
```

### Feature Card with Icon

```html
<div style="background-color: var(--color-surface);
            border-radius: var(--radius-md);
            padding: var(--space-6);
            display: flex;
            align-items: center;
            gap: var(--space-5);">
  <div style="width: 5vmin; height: 5vmin;
              border-radius: 50%;
              border: 1px solid var(--color-text);
              display: flex;
              justify-content: center;
              align-items: center;
              flex-shrink: 0;">
    📌 <!-- icon or emoji -->
  </div>
  <div>
    <h4 class="text-h4">Feature Name</h4>
    <p class="text-body-sm">Feature description</p>
  </div>
</div>
```

### Stat Block

```html
<div style="text-align: center;">
  <div class="text-display" style="color: var(--color-purple); margin-bottom: var(--space-2);">
    2.3x
  </div>
  <p class="text-body">Growth metric</p>
</div>
```

### Two-Column Layout

```html
<div style="display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--space-8);">
  <div>
    <h2 class="text-h2">Left Column</h2>
    <!-- Content -->
  </div>
  <div style="background-color: var(--color-surface);
              border-radius: var(--radius-lg);
              padding: var(--space-8);">
    <!-- Right column content -->
  </div>
</div>
```

### Grid Card Layout (2x2)

```html
<div style="display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--space-6);">
  <div class="card"><!-- Card 1 --></div>
  <div class="card"><!-- Card 2 --></div>
  <div class="card"><!-- Card 3 --></div>
  <div class="card"><!-- Card 4 --></div>
</div>
```

---

## Image Placeholders

Mark image areas with `data-image-placeholder` attribute:

```html
<!-- General photo -->
<div data-image-placeholder="photo"
     style="width: 40vmin; height: 25vmin; border-radius: var(--radius-lg);"></div>

<!-- Portrait / headshot -->
<div data-image-placeholder="portrait"
     style="width: 15vmin; height: 15vmin; border-radius: 50%;"></div>

<!-- Screenshot / UI -->
<div data-image-placeholder="screenshot"
     style="width: 50vmin; height: 30vmin; border-radius: var(--radius-md);"></div>

<!-- Small icon tile -->
<div data-image-placeholder="icon"
     style="width: 8vmin; height: 8vmin; border-radius: var(--radius-sm);"></div>
```

These show placeholder icons automatically. Replace with real images in HTML.

---

## Reusable Components (Added from Production Use)

These components were developed during real presentation builds and are broadly useful across slide types.

### Code Block (for technical/workshop slides)

Displays code, prompts, or file contents in a monospace styled container.

```css
.code-block {
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-6) var(--space-7);
    text-align: left;
    width: 75%;
    max-width: 120vmin;
    margin-top: var(--space-5);
}
.code-block pre {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: var(--text-body);
    line-height: 1.7;
    color: var(--color-text-secondary);
    white-space: pre-wrap;
    margin: 0;
}
.code-block .code-comment { color: var(--color-text-muted); }
.code-block .code-key     { color: var(--color-purple-light); }
.code-block .code-value   { color: var(--color-yellow); }
.code-block .code-heading  { color: var(--color-green); font-weight: var(--weight-medium); }
```

**Usage in HTML:**
```html
<div class="code-block">
    <pre><span class="code-heading"># Section</span>
<span class="code-key">-</span> Item one
<span class="code-key">-</span> Item two: <span class="code-value">highlighted</span></pre>
</div>
```

### Quote / Pull Quote

Large centered italic text for emphasis slides.

```css
.quote-text {
    font-size: var(--text-h2);
    font-weight: var(--weight-light);
    font-style: italic;
    line-height: 1.4;
    max-width: 80%;
    text-align: center;
    letter-spacing: -0.01em;
}
.quote-text .em {
    color: var(--color-yellow);
    font-weight: var(--weight-medium);
}
```

**Usage:** `<p class="quote-text">"<span class="em">Memory</span> is the mind."</p>`

### Part Label (Speaker Section Tracker)

Small label in top-left showing which part of the presentation is active. Useful for workshops and training decks where the speaker needs to track sections.

```css
.part-label {
    position: absolute;
    top: var(--space-7);
    left: var(--slide-padding-x);
    font-size: var(--text-caption);
    font-weight: var(--weight-medium);
    color: var(--color-purple-light);
    letter-spacing: 0.1em;
}
```

**Usage:** `<span class="part-label">PART 3 — UNPACK THE MAGIC</span>`

### Spectrum Bar

Horizontal segmented bar showing a progression or range. Good for "low to high" or timeline concepts.

```css
.spectrum-bar {
    display: flex;
    align-items: center;
    gap: 0;
    margin-top: var(--space-5);
    margin-bottom: var(--space-4);
}
.spectrum-segment {
    flex: 1;
    padding: var(--space-4) var(--space-3);
    text-align: center;
    font-size: var(--text-body-sm);
    font-weight: var(--weight-medium);
    border-right: 1px solid rgba(255,255,255,0.15);
}
.spectrum-segment:last-child { border-right: none; }
.spectrum-label {
    display: flex;
    justify-content: space-between;
    font-size: var(--text-caption);
    color: var(--color-text-muted);
    margin-bottom: var(--space-2);
}
```

### Panel Code (for comparison slides)

Styled code/text block inside comparison panels.

```css
.panel-code {
    background-color: rgba(255,255,255,0.05);
    border-radius: var(--radius-md);
    padding: var(--space-4) var(--space-5);
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: var(--text-body-sm);
    line-height: 1.7;
    color: var(--color-text-secondary);
    white-space: pre-wrap;
}
```

---

## Animation Keyframes

Included in every presentation for entrance effects:

```css
@keyframes revealUp {
  from {
    opacity: 0;
    transform: translateY(1.5vmin);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes revealFade {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes chartBarGrow {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}
```

**Usage:**
```css
.slide-content {
  animation: revealUp 0.5s ease-out forwards;
}
```

---

## Icons

267 monday.com brand icons available. Reference by file path relative to HTML:

```html
<img src="Icons/Property 1=Graph arrow up.svg"
     class="ds-icon ds-icon-lg"
     style="stroke: #ffffff;">
```

**Icon Classes**
```css
.ds-icon-xs      /* 3vmin (24-30px) */
.ds-icon-sm      /* 5vmin (40-50px) */
.ds-icon-md      /* 7vmin (56-70px) - default */
.ds-icon-lg      /* 10vmin (80-100px) */
.ds-icon-xl      /* 15vmin (120-150px) */
.ds-icon-white   /* filter: brightness(0) invert(1) */
.ds-icon-dark    /* filter: brightness(0) */
```

See [ICON_GUIDE.md](ICON_GUIDE.md) for full icon list and semantic matching.

---

## Responsive Behavior

All sizes use `vmin` units, which scale based on the smaller viewport dimension. This ensures:

- **Desktop 1920x1080:** Text scales normally
- **Tablet 1024x768:** Text and spacing scale down proportionally
- **Laptop 1366x768:** Maintains 16:9 aspect, responsive sizing
- **All 16:9 locked:** `.slide-container` never reflows

**No breakpoints needed** — the vmin scaling is the responsive strategy.

---

## Font Import

Every presentation includes:

```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
```

Fallback stack in CSS:
```css
font-family: 'Poppins', sans-serif;
```

Weights available: `300, 400, 500, 600` only. Do not use 700+ (not imported).

---

## Accessibility

- **Reduced motion:** Animations disabled for `prefers-reduced-motion: reduce`
- **Color contrast:** All text meets WCAG AA on dark background
- **Keyboard navigation:** Arrow keys to navigate slides
- **Semantic HTML:** Use proper heading levels (h1, h2, h3, h4)

