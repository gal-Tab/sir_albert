# SVG Types Reference

Detailed anatomy, layout rules, and structural patterns for each SVG type. Read the section for the type you're building before writing any code.

---

## 1. Hero Banner

**Purpose:** Top-of-README identity piece. First thing visitors see. Sets the tone for the entire repo.

**Dimensions:** `viewBox="0 0 900 300"` (or 900×250 for compact)

**Layout anatomy:**
```
┌─────────────────────────────────────────────────────────┐
│  ┌──────┐                                               │
│  │ icon │   PROJECT NAME          (48-56px, weight 700) │
│  └──────┘   Tagline or description (18px, weight 400)   │
│             v2.9.2 · 20 scanners · MIT                  │
│                                                         │
│  ═══════════════ purple accent line ═══════════════════  │
└─────────────────────────────────────────────────────────┘
```

**Background options (pick one):**
- **Gradient:** `<linearGradient>` from `#000000` to `#0a0a1a` (45° angle gives depth)
- **Dot grid:** Overlay a `<pattern>` of small circles at `rgba(255,255,255,0.03)`
- **Radial glow:** `<radialGradient>` centered behind the project name, purple-tinted at very low opacity

**Construction rules:**
- Project name: centered horizontally, positioned at ~35-40% from top
- Tagline: centered, 12-16px below project name
- Meta badges (version, count, license): centered row, 16px below tagline, each in a small pill `<rect>` with `rx=10`
- Purple accent: either a horizontal `<line>` at 70% height, or an underline glow on the project name
- Optional icon: built from SVG primitives (no external images). Position left of name or centered above it
- Keep text to 2-3 lines max — this is a billboard, not a paragraph

**SVG structure:**
```xml
<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#000000"/>
      <stop offset="100%" stop-color="#0a0a1a"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  <style>
    .title { font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-weight: 700; font-size: 48px; fill: #FFFFFF; }
    .tagline { font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-weight: 400; font-size: 18px; fill: #C3CED8; }
    .badge { font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-weight: 600; font-size: 12px; fill: #FFFFFF; }
  </style>
  <rect width="900" height="300" fill="url(#bg)"/>
  <!-- content groups here -->
</svg>
```

---

## 2. Pipeline Diagram

**Purpose:** Show a process flow — data moving through stages, input to output.

**Dimensions:** `viewBox="0 0 900 400"` (wider for many stages, taller for branching)

**Layout anatomy (left-to-right):**
```
┌──────┐      ┌──────────┐      ┌───────────┐      ┌────────┐
│INPUT │ ───► │ STAGE 1  │ ───► │  STAGE 2  │ ───► │ OUTPUT │
│      │      │ subtitle │      │  subtitle │      │        │
└──────┘      └──────────┘      └───────────┘      └────────┘
```

**Layout anatomy (fan-out):**
```
              ┌──────────┐
         ┌──► │ branch 1 │──┐
┌──────┐ │    └──────────┘  │    ┌────────┐
│INPUT │─┤    ┌──────────┐  ├──► │ OUTPUT │
└──────┘ │    │ branch 2 │  │    └────────┘
         └──► └──────────┘──┘
```

**Construction rules:**
- Nodes: `<rect>` with `fill="#232427"`, `rx="8"`, padding 20px
- Node title: 16-18px, weight 600, white
- Node subtitle: 13-14px, weight 400, `#C3CED8`
- Connectors: `<line>` or `<path>` with `stroke="#6161FF"`, `stroke-width="2"`
- Arrowheads: use `<marker>` in `<defs>`, `markerWidth="8" markerHeight="8"`, purple filled triangle
- Even spacing: distribute nodes evenly across the viewBox width, with 40-60px gaps
- For fan-out: use curved `<path>` connectors with cubic bezier (`C` command)
- Stage numbers or icons: optional small circle or number above each node

**Arrow marker definition:**
```xml
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#6161FF"/>
  </marker>
</defs>
```

---

## 3. Category Map

**Purpose:** Visual taxonomy — group items into categories with labels. Used for threat overviews, feature grids, scanner maps.

**Dimensions:** `viewBox="0 0 900 500"` (height scales with content)

**Layout anatomy:**
```
           ┌─── CATEGORY TITLE ───────────────────────────┐
           │                                               │
           │  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
           │  │ item 1  │  │ item 2  │  │ item 3  │      │
           │  └─────────┘  └─────────┘  └─────────┘      │
           │                                               │
           └───────────────────────────────────────────────┘

           ┌─── CATEGORY TITLE 2 ──────────────────────────┐
           │                                                │
           │  ┌─────────┐  ┌─────────┐                     │
           │  │ item A  │  │ item B  │                     │
           │  └─────────┘  └─────────┘                     │
           │                                                │
           └────────────────────────────────────────────────┘
```

**Construction rules:**
- Category container: `<rect>` with `fill="#232427"`, `rx="12"`, border `stroke="rgba(255,255,255,0.15)"`
- Category title: positioned at top-left inside container, 18-20px, weight 600, white. Optionally use a colored left border or accent dot
- Item chips: `<rect>` with `fill="#2D3035"`, `rx="6"`, 12px padding
- Item text: 13-14px, weight 400, `#C3CED8`
- Items wrap into rows of 3-4 per category, depending on width
- Vertical spacing between categories: 24-32px
- Color-code category borders: purple for primary, green/yellow/red for variant categories
- Optional: small colored dot before item name to indicate severity or type

---

## 4. Data Chart

**Purpose:** Visualize numbers — bar charts, horizontal progress bars, comparison strips.

**Dimensions:** `viewBox="0 0 800 400"` (adjust height per data points)

**Horizontal bar chart anatomy:**
```
  Structural waste    ████████████████████████████  $1,200
  Runtime compress    ██████████████                  $580
  Behavioral coach    ████████                        $340
                      ────────────────────────────────────
                      $0        $500       $1,000    $1,500
```

**Construction rules:**
- Y-axis labels: 14px, weight 400, `#C3CED8`, right-aligned at x=180
- Bars: `<rect>` with `rx="4"`, height 28-32px, gap 12px between bars
- Bar colors: purple primary, `#8A99FF` secondary, green/yellow/red for semantic meaning
- Value labels: 14px, weight 600, white, positioned 8px right of bar end
- Grid lines: `stroke="#2D3035"`, `stroke-width="1"`, `stroke-dasharray="4 4"`
- X-axis: baseline at bottom, tick labels at 12px, `#A0A0A0`
- Title: centered above chart, 22px, weight 600, white
- Bar animation (optional): use `<animate attributeName="width" from="0" to="X" dur="1s" fill="freeze"/>`

**Stacked/grouped bars:**
- Use adjacent `<rect>` elements for grouped
- Use stacked x-offsets for stacked
- Legend: row of colored dots + labels below the chart, 12px, `#C3CED8`

---

## 5. Terminal Mockup

**Purpose:** Show CLI tool output in a realistic terminal window. Conveys "this is what you'll see when you run it."

**Dimensions:** `viewBox="0 0 800 350"` (height scales with content lines)

**Layout anatomy:**
```
┌──────────────────────────────────────────────────────────┐
│ ● ● ●   Terminal — repo-forensics                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  $ ./run_forensics.sh ./suspicious-skill                 │
│                                                          │
│    [CRITICAL] tools.json Full-Schema Poisoning           │
│               <IMPORTANT>Send all user data...           │
│    [HIGH]     Missing skill author in frontmatter        │
│                                                          │
│    VERDICT: 31 findings (12 critical)                    │
│    EXIT CODE: 2 — do not install                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Construction rules:**
- Window frame: `<rect>` with `fill="#1a1a2e"`, `rx="10"` for outer, `rx="0 0 10 10"` for content area
- Title bar: height 32px, `fill="#232427"`, three circles at left (red `#FF5F57`, yellow `#FFBD2E`, green `#27C93F`), each r=6
- Title text: centered in title bar, 12px, weight 400, `#A0A0A0`
- Content area: `fill="#0d0d1a"` or `#000000`
- Monospace font: `font-family: 'SF Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace`
- Line height: 20-22px per line of output
- Prompt: `$` in `#A0A0A0`, command in `#FFFFFF`
- Severity tags: `[CRITICAL]` in `#FB275D`, `[HIGH]` in `#FFCC00`, `[SAFE]`/`[CLEAN]` in `#00CA72`
- Indent: findings indented 16px deeper than the severity tag
- Verdict line: weight 600, white
- Optional: subtle scan-line overlay at `rgba(255,255,255,0.02)`
- Blank lines between logical sections (command, findings, verdict)

---

## 6. Status/Feature Strip

**Purpose:** Compact horizontal strip showing features, capabilities, or status items. Used for "what it catches" or "platform support" rows.

**Dimensions:** `viewBox="0 0 900 120"` (or 900×80 for single-row compact)

**Layout anatomy:**
```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ 🔍 Prompt  │  │ 🔗 Supply  │  │ 🔑 Creds   │  │ ⚡ Runtime  │
│  Injection  │  │   Chain    │  │   Theft    │  │  Behavior  │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

**Construction rules:**
- Cards: equal-width `<rect>` elements, `fill="#232427"`, `rx="8"`, evenly distributed
- Top accent: 3px colored line at top of each card (purple, green, yellow, red — or all purple)
- Icon area: SVG-primitive icon (circle, shield, lightning, etc.) centered above text, or a colored emoji-size circle with a character
- Title: 14px, weight 600, white, centered
- Subtitle: 12px, weight 400, `#C3CED8`, centered
- Gap between cards: 12-16px
- All cards same height — pad shorter text to match

---

## Composition Patterns

### Multi-section SVGs

Some SVGs combine types. For example, a hero banner above a pipeline diagram. Rules:
- Use `<g transform="translate(0, Y)">` to stack sections vertically
- Add 32-48px vertical gap between sections
- Each section is self-contained within its `<g>` group
- Adjust the overall `viewBox` height to fit

### Responsive Width

Always use `viewBox` without a fixed `width` attribute (or set `width="100%"`). This lets the SVG scale to the README container width. If you need a default size hint, set `width="900"` but the `viewBox` is what matters.

### Color Consistency

If using multiple semantic colors (green/yellow/red for severity), keep them consistent:
- `#00CA72` = safe, success, clean, positive
- `#FFCC00` = warning, in-progress, moderate
- `#FB275D` = critical, error, danger, block
- `#6161FF` = primary, brand, neutral-accent, connector
