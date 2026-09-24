---
name: readme-svg-generator
description: Generate professional, monday.com-branded SVG graphics for GitHub README files. Use this skill whenever the user wants to create SVG banners, hero images, pipeline diagrams, architecture flows, scanner/feature maps, data visualizations, status bars, terminal mockups, or any visual asset intended for embedding in a GitHub README.md. Also trigger when the user says "make an SVG for my repo", "create a README banner", "diagram for my README", "hero image", "pipeline SVG", "feature map", "architecture diagram as SVG", or asks for any visual that will be rendered inline on GitHub. Trigger even for casual requests like "I need a graphic for my repo" or "make my README look professional". This skill produces GitHub-compatible SVGs — no JavaScript, no foreignObject, no external font imports — using monday.com brand tokens (Poppins embedded, #6161FF purple, dark theme default).
---

# README SVG Generator

Create professional, monday.com-branded SVG graphics for GitHub READMEs. Every SVG this skill produces renders correctly on GitHub (no JS, no foreignObject, no external resources).

## Why This Skill Exists

GitHub READMEs that include polished SVG graphics (hero banners, pipeline diagrams, feature maps) dramatically outperform text-only READMEs in engagement and comprehension. But crafting GitHub-compatible SVGs by hand is tedious — GitHub strips JavaScript, blocks external fonts, and ignores foreignObject. This skill encodes all those constraints so you get production-ready SVGs on the first try.

## SVG Types This Skill Produces

There are **6 SVG categories**, each with distinct anatomy. Read `references/svg-types.md` for full specs, then pick the right one for the user's request.

| Type | When to Use | Typical Size |
|------|-------------|--------------|
| **Hero Banner** | Top of README, project identity, logo + tagline | 900×300 |
| **Pipeline Diagram** | Show data/process flow left-to-right or top-to-bottom | 900×400 |
| **Category Map** | Visual taxonomy, grouped features, scanner overview | 900×500 |
| **Data Chart** | Bar charts, progress bars, comparison visuals | 800×400 |
| **Terminal Mockup** | Fake terminal output showing tool in action | 800×350 |
| **Status/Feature Strip** | Horizontal strip of labeled feature boxes | 900×120 |

## GitHub SVG Constraints (Non-Negotiable)

GitHub sanitizes SVGs aggressively. Every SVG this skill produces MUST comply:

1. **No `<script>` tags** — GitHub strips all JavaScript
2. **No `<foreignObject>`** — GitHub strips it entirely
3. **No external resources** — no `<image href="https://...">`, no `@import url()`, no `<use xlink:href="https://...">`
4. **No `style` attribute with `url()`** — GitHub may strip these
5. **Fonts must be embedded** — use `<style>` with `@font-face` and base64 WOFF2, or fall back to system fonts via `font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif`
6. **Inline `<style>` is allowed** — use it for all CSS (classes, animations, gradients)
7. **SVG animations work** — `<animate>`, `<animateTransform>`, CSS `@keyframes` all render on GitHub
8. **`viewBox` is required** — always set `viewBox` for responsive scaling
9. **`xmlns` is required** — always include `xmlns="http://www.w3.org/2000/svg"`
10. **Keep file size under 200KB** — GitHub renders SVGs inline; large files slow the page

## Design System (monday.com branded)

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-dark` | `#000000` | Default SVG background |
| `bg-surface` | `#232427` | Cards, panels, boxes |
| `bg-surface-alt` | `#2D3035` | Nested surfaces, secondary panels |
| `purple` | `#6161FF` | Primary brand accent, highlights, connectors |
| `purple-light` | `#8A99FF` | Secondary purple, hover states |
| `green` | `#00CA72` | Success, positive, "safe" |
| `yellow` | `#FFCC00` | Warning, in-progress, attention |
| `red` | `#FB275D` | Critical, error, urgent |
| `text-primary` | `#FFFFFF` | Headlines, primary text |
| `text-secondary` | `#C3CED8` | Body copy, descriptions |
| `text-muted` | `#A0A0A0` | Labels, captions |
| `border` | `rgba(255,255,255,0.15)` | Subtle borders |

### Typography

**Font stack** (in order of preference for GitHub SVGs):
```
font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
```

**Weight mapping:**
- `400` — body text, descriptions, labels
- `600` — headlines, section titles, emphasis
- `700` — hero text, project names (use sparingly)

**Size scale (px, for a 900-wide viewBox):**
- Display: `48-56px` — hero banner project name
- H1: `32-36px` — section headlines in diagrams
- H2: `22-26px` — sub-sections, card titles
- Body: `14-16px` — descriptions, labels
- Caption: `11-13px` — annotations, small labels

### Spacing & Layout

- **Corner radius:** `8px` for cards/panels, `12px` for large containers, `4px` for small chips
- **Padding:** `20-24px` inside cards, `16px` inside small elements
- **Gap:** `12-16px` between cards, `24-32px` between sections
- **Connector lines:** `stroke-width: 2`, color `#6161FF`, use `marker-end` for arrows

### Visual Effects

- **Glow:** `<filter>` with `feGaussianBlur` stdDeviation 4-8, purple tint
- **Gradient backgrounds:** linear gradients from `#000000` to `#0a0a1a` (subtle navy tint)
- **Card shadows:** `feDropShadow` with `dx=0 dy=2 stdDeviation=4` and `flood-opacity=0.3`
- **Dot grid pattern:** subtle background dots at `rgba(255,255,255,0.03)` spacing 20px
- **Scan lines:** horizontal lines at `rgba(255,255,255,0.02)` for terminal mockups

## Workflow

### Step 1: Identify SVG Type

Ask the user what they need, or infer from context. Map to one of the 6 types. Read `references/svg-types.md` for the detailed anatomy of the chosen type.

### Step 2: Gather Content

Depending on the type:
- **Hero Banner:** project name, tagline, optional version/badges
- **Pipeline Diagram:** stages/nodes, connections, labels
- **Category Map:** categories, items per category, optional icons
- **Data Chart:** data points, labels, values
- **Terminal Mockup:** command output text, tool name
- **Status Strip:** feature names, optional status colors

### Step 3: Generate the SVG

Write the SVG following these rules:

1. Start with the `<svg>` root: `<svg viewBox="0 0 W H" xmlns="http://www.w3.org/2000/svg">`
2. Add `<defs>` block with reusable elements: gradients, filters, clip paths, arrow markers
3. Add `<style>` block with font declarations and CSS classes
4. Build the layout using `<g>` groups with `transform="translate(x,y)"`
5. Use `<rect>` with `rx` for cards, `<line>` or `<path>` for connectors
6. Use `<text>` for all typography — set `font-family`, `font-size`, `font-weight`, `fill` explicitly
7. Run through the quality checklist below

### Step 4: Save and Present

Save to `/mnt/user-data/outputs/` with a descriptive filename (e.g., `hero-banner.svg`, `pipeline-diagram.svg`). Use `present_files` to deliver.

## Quality Checklist

Before delivering any SVG:

- [ ] `viewBox` is set, `xmlns` is present
- [ ] No `<script>`, no `<foreignObject>`, no external URLs
- [ ] All text uses the Poppins font stack with explicit fallbacks
- [ ] Background uses `#000000` or the dark gradient
- [ ] Primary accent is `#6161FF` (Monday purple)
- [ ] Text fills use `#FFFFFF` (primary), `#C3CED8` (secondary), or `#A0A0A0` (muted)
- [ ] Cards use `#232427` fill with `rx="8"`
- [ ] File size is under 200KB
- [ ] No hardcoded widths on the root `<svg>` (use `viewBox` + optional `width` attribute for default render size)
- [ ] All `<text>` elements have explicit `font-family`, `font-size`, `fill`
- [ ] Connector arrows use `<marker>` definitions, not manual triangles
- [ ] Verify the SVG renders by opening it (if filesystem available)

## Examples

### Example 1: Hero Banner Request

**User:** "Create a hero SVG for my repo called Repo Forensics — it's a security scanner"

**Action:** Generate a Hero Banner SVG (900×300) with:
- Dark gradient background with subtle dot pattern
- "REPO FORENSICS" in Poppins 700, 48px, white
- "Security scanner for AI-agent repos" in Poppins 400, 18px, `#C3CED8`
- Purple accent line or glow effect
- Optional: small shield icon built from SVG primitives

### Example 2: Pipeline Diagram Request

**User:** "Show my scanning pipeline: Input → 20 Scanners → Correlation Engine → Verdict"

**Action:** Generate a Pipeline Diagram SVG (900×400) with:
- 4 stage boxes arranged left-to-right
- Purple connector arrows between stages
- Each box: `#232427` card with `rx=8`, white title, gray description
- Optional: fan-out from "20 Scanners" showing parallel lines

### Example 3: Terminal Mockup Request

**User:** "Make a terminal SVG showing my CLI tool output with some findings"

**Action:** Generate a Terminal Mockup SVG (800×350) with:
- Dark terminal window frame with three dot buttons (red/yellow/green)
- Monospace text body with syntax-highlighted output
- `[CRITICAL]` in `#FB275D`, `[HIGH]` in `#FFCC00`, `[SAFE]` in `#00CA72`
- `$` prompt character in `#A0A0A0`

## Supporting Files

| File | Purpose |
|------|---------|
| `references/svg-types.md` | Detailed anatomy, layout rules, and SVG code patterns for each of the 6 types |
| `references/svg-patterns.md` | Reusable SVG snippet library: gradients, filters, arrow markers, dot grids, terminal frames |
