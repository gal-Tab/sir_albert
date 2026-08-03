# Monday.com Logo Guidelines

Official guidelines for using the Monday.com logo, including construction, variants, spacing, and usage rules.

## Logo Concept

The Monday.com logo consists of three elliptical shapes representing the core workflow states:

- **Red ellipse**: "Stuck" (left)
- **Yellow ellipse**: "Working on it" (middle)
- **Green ellipse**: "Done" (right)

This visual metaphor communicates Monday.com's purpose: moving work from stuck through in-progress to completion.

## Logo Variants

### Primary Logo (Horizontal)

**Components**:
- Three colored ellipses (red, yellow, green)
- "monday.com" wordmark to the right
- Proper spacing between icon and wordmark

**Markdown representation**:
```
●  ●  ●  monday.com
```
(Red, Yellow, Green)

**When to use**:
- Website headers
- Marketing materials with adequate width
- Presentations
- Email signatures
- Business cards

**File formats**: SVG (preferred), PNG (high-res), PDF (print)

### Avatar + Text

**Components**:
- Three colored ellipses stacked or horizontal
- "monday" wordmark below or beside
- Compact composition

**When to use**:
- Social media profiles
- App icons with text
- Small marketing spaces
- Favicons (larger sizes)

### Avatar Only (Icon)

**Components**:
- Three colored ellipses only
- No text
- Square or circular container

**When to use**:
- Favicons (16x16, 32x32)
- App icons (mobile, desktop)
- Social media avatars (when Monday.com is established)
- Watermarks
- Loading states

**Minimum size**: 24x24px (digital), 0.5 inch (print)

## Logo Construction

### Ellipse Proportions

The three ellipses should be:
- **Width to height ratio**: Approximately 1:1.2 (slightly taller than wide)
- **Spacing between ellipses**: 0.3x the width of one ellipse
- **Size**: All three ellipses are identical in size
- **Alignment**: Vertically centered on the same baseline

### Color Specifications

| Ellipse | Position | Color | Hex |
|---------|----------|-------|-----|
| **1st** | Left | Red | `#FB275D` |
| **2nd** | Middle | Yellow | `#FFCC00` |
| **3rd** | Right | Green | `#00CA72` |

**Critical**: Always use these exact colors. Never substitute or adjust.

### Wordmark Typography

**Font**: Custom Monday.com font (proprietary)
**Fallback for mockups**: Poppins Bold
**Color**: Monday Dark `#181B34` (on light backgrounds), White `#FFFFFF` (on dark backgrounds)
**Letter spacing**: Tight, custom kerning
**Case**: Lowercase only ("monday.com" not "Monday.com" in logo)

## Clear Space

### Minimum Clear Space

Maintain clear space around the logo equal to the height of one ellipse on all sides.

```
          [clear space]
[clear]  ●  ●  ●  monday.com  [clear]
          [clear space]
```

**Clear space zone**: No text, graphics, or other elements should enter this area.

### Recommended Clear Space

For maximum impact, use 2x the ellipse height as clear space when possible.

## Size Requirements

### Digital

**Minimum sizes**:
- **Horizontal logo**: 120px wide minimum
- **Avatar + text**: 80px wide minimum
- **Avatar only**: 24px minimum (recognizable at 16px but not preferred)

**Optimal sizes**:
- **Website header**: 180-220px wide
- **Email signature**: 150px wide
- **Social media cover**: 400-600px wide

### Print

**Minimum sizes**:
- **Horizontal logo**: 1.5 inches wide
- **Avatar + text**: 1 inch wide
- **Avatar only**: 0.5 inches wide

**Business card**: 1.5-2 inches wide

## Background Usage

### On White Backgrounds

**Primary logo**:
- Ellipses: Full color (red, yellow, green)
- Wordmark: Monday Dark `#181B34`
- This is the preferred, default usage

### On Light Backgrounds

**Light purple** (`#F0F3FF`), light gray, or other light backgrounds:
- Ellipses: Full color (red, yellow, green)
- Wordmark: Monday Dark `#181B34`
- Ensure sufficient contrast (4.5:1 minimum)

### On Dark Backgrounds

**Monday Dark** (`#181B34`), black, or other dark backgrounds:
- Ellipses: Full color (red, yellow, green)
- Wordmark: White `#FFFFFF`
- Ellipses remain vibrant against dark backgrounds

### On Purple Backgrounds

**Monday Purple** (`#6161FF`):
- Ellipses: Full color (red, yellow, green)
- Wordmark: White `#FFFFFF`
- Ellipses pop beautifully on purple

### On Photographic Backgrounds

**When logo must overlay photos**:
- Use horizontal logo (better legibility)
- Place on area with consistent background color/tone
- Add subtle drop shadow if needed (0 2px 4px rgba(0,0,0,0.3))
- Or place on semi-transparent rectangle: white 80% opacity (light photos) or Monday Dark 80% opacity (dark photos)

**Prefer**: Placing logo on solid color sections rather than busy photos

## Logo Do's and Don'ts

### ✓ Do's

- Use official logo files from Monday.com brand assets
- Maintain original color specifications exactly
- Preserve aspect ratio (never stretch or squash)
- Ensure adequate clear space around logo
- Use on high-contrast backgrounds
- Scale logo proportionally
- Use horizontal version when space allows
- Download high-resolution files for print

### ✗ Don'ts

**Color violations**:
- ✗ Never change ellipse colors (always red, yellow, green)
- ✗ Never use all one color (monochrome logo not permitted)
- ✗ Never apply gradients to ellipses
- ✗ Never use low opacity that makes colors muddy
- ✗ Never add outlines or strokes to ellipses

**Modification violations**:
- ✗ Never rotate logo (except 90° for vertical layouts, rarely)
- ✗ Never stretch or compress (maintain aspect ratio)
- ✗ Never rearrange ellipse order (always red, yellow, green)
- ✗ Never replace ellipses with other shapes
- ✗ Never add effects (shadows, glows, 3D) to logo itself

**Composition violations**:
- ✗ Never place on busy backgrounds without backdrop
- ✗ Never crowd with other elements (respect clear space)
- ✗ Never make smaller than minimum size
- ✗ Never place ellipses and wordmark at different scales
- ✗ Never recreate logo with system fonts

**Typography violations**:
- ✗ Never use Title Case in wordmark ("Monday.com")
- ✗ Never substitute different fonts for wordmark
- ✗ Never add taglines or descriptors to logo
- ✗ Never change letter spacing

## Product Logos

Each Monday.com product can append product name to the base logo:

### monday.com work management

**Structure**:
```
●  ●  ●  monday.com
         work management
```
(Product name in smaller, lighter weight below)

### monday sales CRM

**Structure**:
```
●  ●  ●  monday
         sales CRM
```
("sales CRM" replaces ".com", or appears below)

### monday dev

**Structure**:
```
●  ●  ●  monday
         dev
```

### monday service

**Structure**:
```
●  ●  ●  monday
         service
```

**Product name styling**:
- Font: Poppins Regular or Light
- Size: 0.4x the size of "monday" wordmark
- Color: Same as wordmark (Monday Dark or White)
- Alignment: Left-aligned with "monday"

## Logo in HTML/CSS

### Using SVG Logo

```html
<svg width="200" height="40" viewBox="0 0 200 40" xmlns="http://www.w3.org/2000/svg">
  <!-- Red ellipse -->
  <ellipse cx="20" cy="20" rx="10" ry="12" fill="#FB275D"/>

  <!-- Yellow ellipse -->
  <ellipse cx="40" cy="20" rx="10" ry="12" fill="#FFCC00"/>

  <!-- Green ellipse -->
  <ellipse cx="60" cy="20" rx="10" ry="12" fill="#00CA72"/>

  <!-- Wordmark text -->
  <text x="80" y="27" font-family="Poppins, sans-serif" font-weight="700" font-size="20" fill="#181B34">monday.com</text>
</svg>
```

**Note**: This is a simplified representation. Use official logo files for production.

### Favicon Implementation

```html
<!-- In <head> -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

**Favicon file**: Avatar only (three ellipses, no text)

## Logo Accessibility

### Contrast Requirements

- **Logo on white**: Excellent contrast, no issues
- **Logo on light purple** (`#F0F3FF`): Good contrast, readable
- **Logo on Monday Dark**: Excellent contrast with white wordmark
- **Logo on Monday Purple**: Good contrast with white wordmark

**Always verify**: Wordmark color has at least 4.5:1 contrast ratio with background.

### Alt Text

When using logo as image, provide descriptive alt text:

```html
<img src="monday-logo.svg" alt="Monday.com logo">
```

**For product logos**:
```html
<img src="monday-crm-logo.svg" alt="Monday.com sales CRM logo">
```

### Semantic HTML

For logos in headers:
```html
<header>
  <h1>
    <img src="monday-logo.svg" alt="Monday.com" width="200" height="40">
  </h1>
</header>
```

Or with linked logo:
```html
<a href="/" aria-label="Monday.com home">
  <img src="monday-logo.svg" alt="Monday.com logo" width="200" height="40">
</a>
```

## Special Use Cases

### Loading States

When showing loading/progress:
- Use avatar only (three ellipses)
- Optionally animate ellipses: fade in/out left to right (red → yellow → green)
- Loop animation to indicate ongoing process

**Animation example**:
```css
@keyframes mondayLoading {
  0%, 100% { opacity: 0.3; }
  33% { opacity: 1; }
}

.loading-ellipse-1 { animation: mondayLoading 1.5s infinite; }
.loading-ellipse-2 { animation: mondayLoading 1.5s 0.2s infinite; }
.loading-ellipse-3 { animation: mondayLoading 1.5s 0.4s infinite; }
```

### Watermarks

For protecting screenshots or marketing images:
- Use avatar only (three ellipses)
- Size: Small (40-60px)
- Opacity: 50-70%
- Position: Bottom right corner with clear space
- Do not watermark customer-facing product screenshots

### App Icon (Mobile/Desktop)

- Use avatar only
- Fill entire icon space (no wordmark needed)
- Maintain ellipse colors exactly
- Ensure ellipses are centered and clearly visible at small sizes

## Co-Branding

When Monday.com logo appears with partner logos:

**Hierarchy**:
- Give equal or greater prominence to Monday.com logo
- Maintain same height as partner logos
- Use visual separator if needed (vertical line, spacing)

**Spacing**:
- Minimum 2x clear space between logos
- Align logos on baseline or center

**Example**:
```
●  ●  ●  monday.com    |    Partner Logo
```

**Never**:
- Combine logos into one mark
- Place partner logo inside Monday.com clear space
- Use partner colors on Monday.com logo

## Quick Reference

**Default usage**:
- Background: White `#FFFFFF`
- Ellipses: Red `#FB275D`, Yellow `#FFCC00`, Green `#00CA72`
- Wordmark: Monday Dark `#181B34`
- Clear space: 1x ellipse height minimum
- Minimum width: 120px (digital), 1.5 inches (print)

**When in doubt**: Use horizontal logo on white background with Monday Dark wordmark—this is always correct.
