# Monday.com Design Principles

Comprehensive visual design philosophy, component patterns, and technical guidelines for creating Monday.com branded artifacts.

## Core Design Philosophy

Monday.com's visual language is built on three pillars:

1. **Clarity**: Information is easy to find, understand, and act on
2. **Breathing Room**: Generous whitespace creates calm, focused experiences
3. **Delight**: Subtle moments of joy without sacrificing usability

## Whitespace Philosophy

### The Power of Space

Monday.com designs are **airy and breathable**. More whitespace is better than less.

**Spacing scale** (use consistently):
- `4px`: Tight spacing (icon to label)
- `8px`: Close spacing (related elements)
- `16px`: Default spacing (paragraph margins)
- `24px`: Component spacing (card padding)
- `32px`: Section spacing (within containers)
- `48px`: Large spacing (between sections)
- `64px`: Extra large (major sections)
- `80px`: Hero spacing (landing page sections)

### Padding Guidelines

**Cards/Containers**:
- Small cards: 16-24px padding
- Standard cards: 24-32px padding
- Large sections: 40-64px padding
- Hero sections: 60-80px padding (desktop), 40px (mobile)

**Responsive Padding**:
```css
.section {
  padding: 80px 20px; /* Mobile */
}

@media (min-width: 768px) {
  .section {
    padding: 80px 40px; /* Tablet */
  }
}

@media (min-width: 1200px) {
  .section {
    padding: 80px 60px; /* Desktop */
  }
}
```

**Rule**: When uncertain, add more padding. Monday designs are never cramped.

## Grid Systems

### Desktop Grid

**Max content width**: 1200-1400px
**Columns**: 12-column grid
**Gutter**: 24-32px between columns
**Margin**: 40-80px on sides (responsive)

### Breakpoints

| Breakpoint | Width | Columns | Use Case |
|------------|-------|---------|----------|
| **Mobile** | < 768px | 4 | Single column layouts |
| **Tablet** | 768-1023px | 8 | Two column layouts |
| **Desktop** | 1024-1439px | 12 | Full layouts |
| **Large** | ≥ 1440px | 12 | Wide screens, max content width |

### Layout Patterns

**Two-column (50/50)**:
```
[Content]  [Image]
```
Use for feature sections, alternating sides

**Three-column**:
```
[Card] [Card] [Card]
```
Use for features, testimonials, pricing

**Sidebar layout** (25/75 or 30/70):
```
[Nav] [Main Content]
```
Use for documentation, dashboards

## Component Design Patterns

### Buttons

**Primary Button**:
- Background: Monday Purple `#6161FF` (or product color)
- Text: White `#FFFFFF`
- Border radius: 8-12px
- Padding: 12-16px vertical, 24-32px horizontal
- Font: Poppins Semi-bold, 14-16px
- Hover: Darken by 10-15% (`#4B4BFF`)
- Active: Darken by 20% (`#3636FF`)
- Focus: 2px outline, purple with 50% opacity

```css
.button-primary {
  background: #6161FF;
  color: #FFFFFF;
  padding: 14px 28px;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: background 0.2s ease;
}

.button-primary:hover {
  background: #4B4BFF;
}

.button-primary:focus {
  outline: 2px solid rgba(97, 97, 255, 0.5);
  outline-offset: 2px;
}
```

**Secondary Button**:
- Background: White `#FFFFFF`
- Text: Monday Purple `#6161FF`
- Border: 2px solid Monday Purple
- Same padding, radius, and font as primary
- Hover: Light purple background `#F0F3FF`, keep purple text

**Tertiary Button** (text only):
- Background: Transparent
- Text: Monday Purple `#6161FF`
- Padding: 8px 16px
- Hover: Underline, or light purple background

**Button Sizes**:
- Small: 10px/20px padding, 14px font
- Default: 14px/28px padding, 16px font
- Large: 16px/32px padding, 18px font

### Cards

**Standard Card**:
- Background: White `#FFFFFF`
- Border radius: 8-12px
- Shadow: `0 2px 8px rgba(0, 0, 0, 0.08)`
- Padding: 24-32px
- Hover effect: Lift card (`0 4px 16px rgba(0, 0, 0, 0.12)`)
- Border: None (rely on shadow for depth)

```css
.card {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}
```

**Card Variants**:
- **Flat card**: No shadow, 1px border `#E6E9EF`
- **Highlighted card**: Purple left border (4px), white background
- **Dark card**: Monday Dark background, white text (dev product)

### Forms

**Input Fields**:
- Height: 44-48px (touch-friendly)
- Border: 1px solid `#C5CAE9` (light gray)
- Border radius: 6-8px
- Padding: 12px 16px
- Font: Poppins Regular, 16px (prevents zoom on iOS)
- Focus: 2px purple border, no outline

```css
.input {
  width: 100%;
  height: 48px;
  border: 1px solid #C5CAE9;
  border-radius: 8px;
  padding: 0 16px;
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  transition: border-color 0.2s ease;
}

.input:focus {
  border-color: #6161FF;
  border-width: 2px;
  outline: none;
}

.input::placeholder {
  color: #9FA2B4;
}
```

**Form Layout**:
- Label above input (not inline)
- 8px spacing between label and input
- 24px spacing between form groups
- Error messages below input, red text
- Helper text below input, gray text

### Typography Hierarchy in Components

**Hero Section**:
- H1: Poppins Bold, 48-64px (desktop), 32-40px (mobile)
- Subheading: Poppins Regular, 18-20px, line-height 1.6
- CTA: 16-18px button text

**Feature Section**:
- H2: Poppins Semi-bold, 36-42px (desktop), 28-32px (mobile)
- Body: Poppins Regular, 16-18px, line-height 1.6
- Caption: Poppins Light, 14px

**Card Content**:
- Card title: Poppins Semi-bold, 20-24px
- Card body: Poppins Regular, 16px, line-height 1.5
- Card footer: Poppins Regular, 14px

## Depth & Elevation

Monday.com uses subtle shadows to create depth hierarchy:

### Shadow Scale

| Level | Elevation | Shadow | Use Case |
|-------|-----------|--------|----------|
| **0** | Flat | None | Backgrounds, flat surfaces |
| **1** | Low | `0 1px 3px rgba(0,0,0,0.06)` | Subtle cards |
| **2** | Default | `0 2px 8px rgba(0,0,0,0.08)` | Standard cards, dropdowns |
| **3** | Raised | `0 4px 16px rgba(0,0,0,0.12)` | Hover states, important cards |
| **4** | Floating | `0 8px 24px rgba(0,0,0,0.15)` | Modals, popovers |
| **5** | High | `0 16px 48px rgba(0,0,0,0.2)` | Dialogs, critical overlays |

**Guideline**: Use shadows sparingly. Most surfaces are at level 0-2.

## Border Radius Standards

**Consistent corner radius**:
- Buttons: 8-12px
- Cards: 8-12px
- Inputs: 6-8px
- Images: 8-12px (or 50% for avatars)
- Modals: 12-16px
- Large containers: 12-16px

**Rule**: Never use sharp corners (0px) except for full-bleed layouts or intentional design statements. Never use excessive radius (> 20px) except for circular elements.

## Animation Guidelines

### Principles

Monday.com animations are:
- **Fast**: 200-400ms (not slow)
- **Purposeful**: Communicate state changes
- **Subtle**: Never distracting
- **Celebratory**: For positive moments (tasks completed, goals hit)

### Timing Functions

- **Default**: `ease` or `cubic-bezier(0.4, 0.0, 0.2, 1)`
- **Entrance**: `ease-out` or `cubic-bezier(0.0, 0.0, 0.2, 1)`
- **Exit**: `ease-in` or `cubic-bezier(0.4, 0.0, 1, 1)`

### Common Animations

**Button hover**:
```css
transition: background 0.2s ease, transform 0.2s ease;
```

**Card hover**:
```css
transition: box-shadow 0.3s ease, transform 0.3s ease;
transform: translateY(-2px);
```

**Modal entrance**:
```css
animation: fadeIn 0.3s ease;

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

**Celebration (task completed)**:
```css
animation: celebrate 0.6s ease;

@keyframes celebrate {
  0%, 100% { transform: scale(1); }
  30% { transform: scale(1.15); }
  60% { transform: scale(0.95); }
}
```

**When to animate**:
- Button interactions (hover, active)
- Card hover states
- Modal/dialog open/close
- Success messages (slide in from top)
- Loading states (skeleton screens, spinners)
- Celebration moments (confetti for goals, subtle bounce for completions)

**When NOT to animate**:
- Navigation (keep instant)
- Data tables (performance)
- Continuous updates (too distracting)

## Accessibility Requirements

### Color Contrast

**WCAG AA Minimum** (Monday.com standard):
- Body text (16px): 4.5:1 contrast ratio
- Large text (18px+): 3:1 contrast ratio
- UI elements (icons, borders): 3:1 contrast ratio

**Monday.com meets these**:
- Monday Dark `#181B34` on white: 14.6:1 ✓ AAA
- Monday Purple `#6161FF` on white: 7.8:1 ✓ AAA
- Green `#00CA72` on white: 3.2:1 ✓ AA (large text)
- Red `#FB275D` on white: 4.7:1 ✓ AA

**Action**: Always check contrast before finalizing colors. Target AAA when possible.

### Font Sizes

**Minimum sizes**:
- Body text: 16px (never smaller)
- Small text: 14px (use sparingly)
- Tiny text: 12px (labels only, high contrast required)

**Optimal reading**:
- Body: 16-18px
- Line height: 1.5-1.6
- Paragraph width: 60-80 characters max

### Focus States

**All interactive elements must have visible focus**:
- Buttons: 2px purple outline with offset
- Inputs: 2px purple border
- Links: Underline or background highlight
- Cards: Outline around entire card

```css
:focus {
  outline: 2px solid #6161FF;
  outline-offset: 2px;
}

:focus:not(:focus-visible) {
  outline: none; /* Remove for mouse users */
}

:focus-visible {
  outline: 2px solid #6161FF;
  outline-offset: 2px;
}
```

### ARIA & Semantic HTML

**Use semantic HTML**:
- `<header>`, `<nav>`, `<main>`, `<footer>`, `<article>`, `<section>`
- `<button>` for buttons (never `<div onClick>`)
- `<a>` for links
- `<h1>`-`<h6>` in hierarchical order

**ARIA labels for clarity**:
```html
<button aria-label="Close modal">✕</button>
<nav aria-label="Main navigation">...</nav>
<img src="chart.png" alt="Sales pipeline showing 45% conversion rate">
```

### Keyboard Navigation

**All interactions must be keyboard-accessible**:
- Tab order follows visual order
- `Enter` activates buttons and links
- `Escape` closes modals and dropdowns
- Arrow keys navigate lists and menus

## Mobile & Responsive Considerations

### Mobile-First Principles

1. **Touch targets**: Minimum 44x44px
2. **Font size**: 16px minimum (prevents iOS zoom)
3. **Simplified layouts**: Single column preferred
4. **Generous spacing**: Easier to tap
5. **Sticky headers**: Keep navigation accessible

### Responsive Patterns

**Navigation**:
- Desktop: Horizontal nav bar
- Mobile: Hamburger menu or bottom nav

**Hero sections**:
- Desktop: 60-70% width content, 30-40% image (side by side)
- Mobile: Stack vertically, full-width image

**Cards**:
- Desktop: 3-column grid
- Tablet: 2-column grid
- Mobile: 1-column stack

**Forms**:
- Desktop: Two columns for short fields (first name, last name)
- Mobile: Single column all fields

## Component Library Reference

### Common Monday.com Components

**Hero Section**:
- Large headline (Poppins Bold, purple accent)
- Subheading (Poppins Regular, 18-20px)
- Primary CTA (purple button)
- Optional image/illustration on right
- White or light purple background
- 80px padding top/bottom (desktop)

**Feature Grid (3 columns)**:
- Icon or small image
- Feature headline (Poppins Semi-bold, 20-24px)
- Feature description (2-3 sentences)
- Optional link ("Learn more →")
- 48px spacing between features

**Testimonial Card**:
- Quote text (Poppins Regular, 18px, line-height 1.6)
- Attribution (name, title, company)
- Optional avatar (circular, 48-64px)
- Light purple or white background
- Purple accent (left border or quote marks)

**Stats Section**:
- Large number (Poppins Bold, 48-56px, purple)
- Label (Poppins Regular, 16px, Monday Dark)
- Aligned in row or grid
- Minimal design, focus on numbers

**CTA Section** (end of page):
- Headline (Poppins Bold, 36-48px)
- Short subheading (1 sentence)
- Primary CTA (purple button)
- White background or light purple
- Generous padding (80px+)

## Visual Consistency Checklist

Before finalizing Monday.com designs, verify:

**Spacing**:
- [ ] Uses spacing scale (4, 8, 16, 24, 32, 48, 64, 80px)
- [ ] Generous padding on all sections (60-80px minimum)
- [ ] Consistent gutters between columns (24-32px)

**Typography**:
- [ ] Poppins loaded and applied correctly
- [ ] Hierarchy clear (size, weight, color)
- [ ] Body text 16px minimum
- [ ] Line height 1.5-1.6 for readability

**Colors**:
- [ ] Primary color (purple or product) used appropriately
- [ ] High contrast text (Monday Dark on white)
- [ ] Status colors (green, yellow, red) used correctly

**Components**:
- [ ] Border radius 8-12px consistent
- [ ] Shadows subtle (level 2 default)
- [ ] Buttons have hover states
- [ ] Cards have consistent padding

**Accessibility**:
- [ ] All text meets AA contrast minimum
- [ ] Interactive elements 44x44px minimum
- [ ] Focus states visible
- [ ] Semantic HTML used

**Responsive**:
- [ ] Mobile, tablet, desktop layouts defined
- [ ] Touch targets 44x44px on mobile
- [ ] Text scales appropriately
- [ ] Images responsive

## Design Resources

**Figma/Sketch variables**:
```
Colors: See assets/color-palette.md
Typography: Poppins (Bold, Semi-bold, Regular, Light)
Spacing: 4px base unit
Border radius: 8-12px
Shadows: Levels 0-5 defined above
```

**Code references**:
- HTML starter: `templates/html-starter.html`
- CSS variables setup included in templates
- Component examples in templates

## Philosophy Summary

Monday.com designs are:
- **Spacious**: More whitespace, never cramped
- **Clean**: Minimal elements, high clarity
- **Vibrant**: Bold use of purple and brand colors
- **Accessible**: High contrast, semantic, keyboard-friendly
- **Responsive**: Mobile-first, works everywhere
- **Delightful**: Subtle animations, celebration moments

When in doubt, add more space, use more contrast, and keep it simple. Monday.com is premium, but never stuffy. Modern, but never trendy. Bold, but never overwhelming.
