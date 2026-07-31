# Monday.com Color Palette

Complete color specifications for Monday.com brand identity, including technical values and accessibility ratings.

## Primary Brand Colors

The core colors that define Monday.com's visual identity:

### Monday Purple (Brand Hero)

| Format | Value |
|--------|-------|
| **Name** | Monday Purple |
| **Hex** | `#6161FF` |
| **RGB** | `rgb(97, 97, 255)` |
| **HSL** | `hsl(240, 100%, 69%)` |
| **CMYK** | `C62 M62 Y0 K0` |
| **Pantone** | 2716 C |

**Usage**: Primary brand color, CTAs, key UI elements, headlines accents
**Accessibility**: AAA on white backgrounds (7.8:1), AA for large text on #F0F3FF (3.2:1)

### Monday Dark (Text & Depth)

| Format | Value |
|--------|-------|
| **Name** | Monday Dark |
| **Hex** | `#181B34` |
| **RGB** | `rgb(24, 27, 52)` |
| **HSL** | `hsl(234, 37%, 15%)` |
| **CMYK** | `C91 M85 Y46 K62` |
| **Pantone** | 533 C |

**Usage**: Primary text, dark headers, dark UI components, high contrast elements
**Accessibility**: AAA on white backgrounds (14.2:1), AAA on light purple backgrounds

### Monday Light (Subtle Backgrounds)

| Format | Value |
|--------|-------|
| **Name** | Monday Light |
| **Hex** | `#F0F3FF` |
| **RGB** | `rgb(240, 243, 255)` |
| **HSL** | `hsl(228, 100%, 97%)` |
| **CMYK** | `C6 M5 Y0 K0` |
| **Pantone** | 649 C |

**Usage**: Section backgrounds, subtle highlights, light UI areas, cards on white
**Accessibility**: Use with Monday Dark text (13.5:1 AAA), avoid with Monday Purple text alone

### White (Clean Foundation)

| Format | Value |
|--------|-------|
| **Name** | White |
| **Hex** | `#FFFFFF` |
| **RGB** | `rgb(255, 255, 255)` |
| **HSL** | `hsl(0, 0%, 100%)` |
| **CMYK** | `C0 M0 Y0 K0` |

**Usage**: Main backgrounds, cards, clean space, maximum breathing room
**Accessibility**: Use with Monday Dark for text (14.6:1 AAA), Monday Purple for accents (7.8:1 AAA)

## Supportive Colors

Status indicators and visual variety:

### Green (Success & Progress)

| Format | Value |
|--------|-------|
| **Name** | Monday Green |
| **Hex** | `#00CA72` |
| **RGB** | `rgb(0, 202, 114)` |
| **HSL** | `hsl(154, 100%, 40%)` |
| **CMYK** | `C75 M0 Y62 K0` |
| **Pantone** | 7481 C |

**Usage**: Success states, completion indicators, positive metrics, growth charts
**Accessibility**: AA on white (3.2:1 for large text), use darker shade for body text

### Yellow (Attention & In-Progress)

| Format | Value |
|--------|-------|
| **Name** | Monday Yellow |
| **Hex** | `#FFCC00` |
| **RGB** | `rgb(255, 204, 0)` |
| **HSL** | `hsl(48, 100%, 50%)` |
| **CMYK** | `C0 M20 Y100 K0` |
| **Pantone** | Yellow C |

**Usage**: Warnings (non-critical), in-progress states, attention-grabbing elements
**Accessibility**: Fails on white for text (1.9:1), use only for large elements or icons

### Red (Errors & Urgency)

| Format | Value |
|--------|-------|
| **Name** | Monday Red |
| **Hex** | `#FB275D` |
| **RGB** | `rgb(251, 39, 93)` |
| **HSL** | `hsl(345, 96%, 57%)` |
| **CMYK** | `C0 M90 Y48 K0` |
| **Pantone** | 1915 C |

**Usage**: Error states, critical warnings, urgent items, negative metrics
**Accessibility**: AA on white (4.7:1), AAA for large text

## Product-Specific Primary Colors

Each Monday.com product has a unique primary color:

### Work Management Purple

| Format | Value |
|--------|-------|
| **Hex** | `#6161FF` |
| **RGB** | `rgb(97, 97, 255)` |

**Product**: monday.com Work Management (flagship)
**Same as**: Monday Purple (primary brand color)

### CRM Turquoise

| Format | Value |
|--------|-------|
| **Name** | CRM Turquoise |
| **Hex** | `#00D2D2` |
| **RGB** | `rgb(0, 210, 210)` |
| **HSL** | `hsl(180, 100%, 41%)` |
| **CMYK** | `C75 M0 Y25 K0` |
| **Pantone** | 3252 C |

**Product**: monday sales CRM
**Usage**: CRM-specific CTAs, headers, data visualizations
**Accessibility**: AA on white (3.5:1 for large text)

### dev Green

| Format | Value |
|--------|-------|
| **Hex** | `#00CA72` |
| **RGB** | `rgb(0, 202, 114)` |

**Product**: monday dev
**Same as**: Monday Green (supportive color)
**Usage**: Dev product CTAs, sprint charts, technical dashboards

### service Red

| Format | Value |
|--------|-------|
| **Hex** | `#FB275D` |
| **RGB** | `rgb(251, 39, 93)` |

**Product**: monday service
**Same as**: Monday Red (supportive color)
**Usage**: Service product CTAs, ticket systems, support dashboards

## Color Combinations

### Recommended Pairings

**Classic Monday** (Work Management default):
- Background: White `#FFFFFF`
- Primary: Monday Purple `#6161FF`
- Text: Monday Dark `#181B34`
- Accents: Light Purple `#F0F3FF`

**Accessibility Score**: AAA across all text combinations

**CRM Dynamic**:
- Background: White `#FFFFFF`
- Primary: CRM Turquoise `#00D2D2`
- Secondary: Monday Purple `#6161FF`
- Text: Monday Dark `#181B34`

**Accessibility Score**: AA for turquoise, AAA for purple

**dev Technical**:
- Background: Monday Dark `#181B34` or White `#FFFFFF`
- Primary: dev Green `#00CA72`
- Accents: Monday Purple `#6161FF`
- Text: White `#FFFFFF` (dark bg) or Monday Dark (white bg)

**Accessibility Score**: AA minimum on both background options

**service Energetic**:
- Background: White `#FFFFFF`
- Primary: service Red `#FB275D`
- Secondary: Yellow `#FFCC00`
- Text: Monday Dark `#181B34`

**Accessibility Score**: AA for red, use yellow for large elements only

## Gradients

When using gradients (use sparingly):

### Purple Gradient (Marketing)
```css
background: linear-gradient(135deg, #6161FF 0%, #8C8CFF 100%);
```

### Multi-Color Gradient (Celebratory moments)
```css
background: linear-gradient(135deg, #6161FF 0%, #00D2D2 50%, #00CA72 100%);
```

**Usage Note**: Gradients are acceptable for hero sections, celebration moments, and special features. Avoid in data-heavy UIs or business dashboards.

## Accessibility Ratings

Contrast ratios against white background:

| Color | Large Text (18px+) | Body Text (16px) | Rating |
|-------|-------------------|------------------|--------|
| Monday Purple `#6161FF` | 7.8:1 ✓ AAA | 7.8:1 ✓ AAA | Excellent |
| Monday Dark `#181B34` | 14.6:1 ✓ AAA | 14.6:1 ✓ AAA | Excellent |
| Green `#00CA72` | 3.2:1 ✓ AA | 3.2:1 ✓ AA | Good |
| Yellow `#FFCC00` | 1.9:1 ✗ Fail | 1.9:1 ✗ Fail | Decorative only |
| Red `#FB275D` | 4.7:1 ✓ AA | 4.7:1 ✓ AA | Good |
| CRM Turquoise `#00D2D2` | 3.5:1 ✓ AA | 3.5:1 ✗ Fail | Large text only |

**Minimum Standards**:
- AAA rating: 7:1 (body text), 4.5:1 (large text)
- AA rating: 4.5:1 (body text), 3:1 (large text)

**Monday.com Standard**: Target AAA for all body text, AA minimum for large UI elements.

## Color Usage Guidelines

### Do's

✓ Use Monday Purple prominently in Work Management contexts
✓ Use 60-70% neutral (white, light purple, dark text)
✓ Use 20-30% primary color (purple or product color)
✓ Use 10-20% supportive colors (green, yellow, red for status)
✓ Ensure text contrast meets AA minimum (AAA preferred)
✓ Use green for success, yellow for warnings, red for errors
✓ Apply product-specific colors when context is clear

### Don'ts

✗ Don't use yellow for body text (fails accessibility)
✗ Don't mix multiple product primary colors in one design
✗ Don't use colors at low opacity that fail contrast
✗ Don't use gradients in data tables or complex UIs
✗ Don't use more than 4-5 colors in a single composition
✗ Don't override product colors (CRM = turquoise, not purple)

## CSS Variables Setup

Use these CSS custom properties for consistent color management:

```css
:root {
  /* Primary Brand Colors */
  --monday-purple: #6161FF;
  --monday-dark: #181B34;
  --monday-light: #F0F3FF;
  --monday-white: #FFFFFF;

  /* Supportive Colors */
  --monday-green: #00CA72;
  --monday-yellow: #FFCC00;
  --monday-red: #FB275D;

  /* Product Colors */
  --crm-turquoise: #00D2D2;
  --dev-green: #00CA72;
  --service-red: #FB275D;

  /* Functional Colors */
  --color-success: var(--monday-green);
  --color-warning: var(--monday-yellow);
  --color-error: var(--monday-red);
  --color-text: var(--monday-dark);
  --color-background: var(--monday-white);
}
```

**Usage in CSS**:
```css
.button-primary {
  background-color: var(--monday-purple);
  color: var(--monday-white);
}

.success-message {
  color: var(--color-success);
}
```

## Color Testing Checklist

Before finalizing any Monday.com design, verify:

- [ ] Primary color is Monday Purple or correct product color
- [ ] Color hierarchy follows 60/30/10 rule
- [ ] All text meets AA contrast minimum (AAA preferred)
- [ ] Status colors (green/yellow/red) used consistently
- [ ] No product color mixing (one product context per design)
- [ ] Gradients used sparingly and appropriately
- [ ] Background colors don't compete with content
- [ ] Color blind users can distinguish all critical information
- [ ] Hover states have sufficient color change (10-15% darker/lighter)
- [ ] Focus states are clearly visible for accessibility

## Quick Reference

**Most Common Usage**:

- Headlines on white: Monday Purple `#6161FF`
- Body text: Monday Dark `#181B34`
- Background sections: White `#FFFFFF` or Light Purple `#F0F3FF`
- Primary CTA: Purple background, white text
- Success indicators: Green `#00CA72`
- Error indicators: Red `#FB275D`
- Warning/in-progress: Yellow `#FFCC00` (large elements only)

When in doubt, default to Monday Purple on white with Monday Dark text—this combination is brand-compliant and accessible.
