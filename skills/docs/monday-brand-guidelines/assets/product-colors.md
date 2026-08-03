# Monday.com Product Color Systems

Comprehensive color guidance for each Monday.com product line, including usage percentages, combinations, and product-specific patterns.

## Overview

While all Monday.com products share the core brand colors, each product has a unique primary color that defines its identity:

- **Work Management**: Monday Purple `#6161FF` (flagship, default)
- **CRM**: Turquoise `#00D2D2` (sales focus)
- **dev**: Green `#00CA72` (developer tools)
- **service**: Red `#FB275D` (customer support)

## Work Management Color System

### Primary Palette

| Role | Color | Hex | Usage % |
|------|-------|-----|---------|
| **Brand Hero** | Monday Purple | `#6161FF` | 25-30% |
| **Background** | White | `#FFFFFF` | 50-60% |
| **Text** | Monday Dark | `#181B34` | 10-15% |
| **Subtle** | Light Purple | `#F0F3FF` | 10-15% |

### Supportive Palette

| Role | Color | Hex | When to Use |
|------|-------|-----|-------------|
| **Success** | Green | `#00CA72` | Completions, positive metrics |
| **Warning** | Yellow | `#FFCC00` | In-progress, needs attention |
| **Error** | Red | `#FB275D` | Errors, blockers, overdue |

### Typical Work Management Composition

**Landing Page**:
- Hero section: White background, purple headline accents (70% white, 30% purple)
- Feature sections: Alternating white/light purple backgrounds
- CTAs: Purple buttons (purple bg, white text)
- Body text: Monday Dark throughout

**Dashboard/Product UI**:
- Main background: White
- Navigation header: Purple (or white with purple accents)
- Cards: White with subtle shadows on white/light purple backgrounds
- Status indicators: Green (done), yellow (working), red (stuck)
- Action buttons: Purple primary, outlined secondary

### CSS Variables (Work Management)

```css
:root {
  /* Work Management Specific */
  --wm-primary: #6161FF;
  --wm-primary-hover: #4B4BFF;
  --wm-primary-light: #F0F3FF;
  --wm-text: #181B34;
  --wm-background: #FFFFFF;

  /* Status colors */
  --wm-status-done: #00CA72;
  --wm-status-working: #FFCC00;
  --wm-status-stuck: #FB275D;
}
```

### Examples

**Good Work Management Color Usage**:
- 60% white background, 30% purple accents, 10% text/status colors
- Purple CTAs on white backgrounds
- Light purple section backgrounds alternating with white
- Monday Dark for all body text
- Green/yellow/red only for status indicators

**Avoid**:
- Using turquoise, or making green/red primary (those are other products)
- Less than 20% purple (loses Monday identity)
- More than 40% purple (overwhelming)
- Using light purple for text (fails contrast)

## CRM Color System

### Primary Palette

| Role | Color | Hex | Usage % |
|------|-------|-----|---------|
| **CRM Hero** | Turquoise | `#00D2D2` | 20-25% |
| **Brand Anchor** | Monday Purple | `#6161FF` | 10-15% |
| **Background** | White | `#FFFFFF` | 45-55% |
| **Text** | Monday Dark | `#181B34` | 10-15% |

### CRM-Specific Strategy

**Key Difference**: CRM uses turquoise as primary, but keeps Monday purple visible as a brand anchor. This creates differentiation while maintaining family connection.

**Turquoise Dominance**:
- Primary CTAs: Turquoise background, white text
- Headers and navigation: Turquoise
- Primary charts/graphs: Turquoise bars/lines
- Hover states: Darker turquoise

**Purple as Anchor**:
- Secondary CTAs: Purple background or purple outline
- Accent elements: Small purple touches
- Logos and brand marks: Purple remains
- Links: Can be purple or turquoise (be consistent)

### Supportive Palette

| Role | Color | Hex | CRM Context |
|------|-------|-----|-------------|
| **Won/Success** | Green | `#00CA72` | Deals won, targets hit |
| **In-Progress** | Yellow | `#FFCC00` | Deals in negotiation |
| **Lost/Risk** | Red | `#FB275D` | Deals lost, at-risk accounts |

### Typical CRM Composition

**Sales Dashboard**:
- Header: Turquoise background with white text
- Main area: White background
- Deal cards: White cards, turquoise accents on deal stages
- Pipeline chart: Turquoise bars, green (won), red (lost) indicators
- Primary CTA: Turquoise button ("Add deal")
- Secondary CTA: Purple outline button ("View reports")

**CRM Landing Page**:
- Hero: White background, turquoise headline or CTA
- Features: Mix of white and very light turquoise tint backgrounds
- Social proof: Purple accents for quotes/testimonials
- Final CTA: Turquoise button

### CSS Variables (CRM)

```css
:root {
  /* CRM Specific */
  --crm-primary: #00D2D2;
  --crm-primary-hover: #00B8B8;
  --crm-primary-light: #E5F9F9;
  --crm-secondary: #6161FF; /* Purple anchor */
  --crm-text: #181B34;
  --crm-background: #FFFFFF;

  /* Deal stages */
  --crm-won: #00CA72;
  --crm-active: #FFCC00;
  --crm-lost: #FB275D;
}
```

### Examples

**Good CRM Color Usage**:
- Turquoise dominates (20-25%), purple supports (10-15%)
- Turquoise CTAs, purple secondary actions
- Green/yellow/red for deal pipeline stages
- Clear turquoise identity while feeling like "Monday"

**Avoid**:
- All purple (that's Work Management, not CRM)
- No purple at all (loses Monday brand connection)
- Turquoise + green as co-primaries (confusing)
- More than 30% turquoise (too dominant)

## dev Color System

### Primary Palette

| Role | Color | Hex | Usage % |
|------|-------|-----|---------|
| **dev Hero** | Green | `#00CA72` | 20-30% |
| **Background** | White or Dark | `#FFFFFF` / `#181B34` | 50-60% |
| **Text** | Monday Dark or White | `#181B34` / `#FFFFFF` | 10-15% |
| **Accents** | Monday Purple | `#6161FF` | 10-15% |

### dev-Specific Strategy

**Key Difference**: dev can use dark backgrounds (Monday Dark `#181B34`), unlike other products that default to white. This creates a code editor, technical aesthetic.

**Green Dominance**:
- Primary CTAs: Green background, white text
- Code blocks: Green accents, syntax highlighting touches
- Success indicators: Green (tests passing, builds successful)
- Chart highlights: Green bars for sprint velocity, story points

**Dark Mode Acceptable**:
- Option 1 (Light): White background, green accents, Monday Dark text
- Option 2 (Dark): Monday Dark background, green accents, white text
- Both are brand-compliant for dev product

### Supportive Palette

| Role | Color | Hex | dev Context |
|------|-------|-----|-------------|
| **Success/Shipped** | Green | `#00CA72` | Completed sprints, shipped features |
| **In-Progress** | Yellow | `#FFCC00` | Active sprints, WIP |
| **Blocked/Failed** | Red | `#FB275D` | Failed builds, blockers |
| **Code Accent** | Purple | `#6161FF` | Links, highlights, Monday brand anchor |

### Typical dev Composition

**Developer Dashboard (Light)**:
- Background: White
- Header: White with green logo/accents
- Cards: White with green left border for active sprints
- Charts: Green bars (velocity), red (bugs), yellow (in progress)
- Primary CTA: Green button ("Start sprint")
- Code blocks: Light gray bg, green syntax highlights

**Developer Dashboard (Dark)**:
- Background: Monday Dark `#181B34`
- Header: Dark with green logo/accents
- Cards: Slightly lighter dark (`#242742`) with green borders
- Text: White
- Charts: Green/yellow/red on dark background
- Code blocks: Darker gray bg, green syntax highlights

### CSS Variables (dev)

```css
:root {
  /* dev Light Mode */
  --dev-primary: #00CA72;
  --dev-primary-hover: #00B065;
  --dev-primary-light: #E5F9F2;
  --dev-accent: #6161FF;
  --dev-text: #181B34;
  --dev-background: #FFFFFF;

  /* dev Dark Mode */
  --dev-dark-background: #181B34;
  --dev-dark-surface: #242742;
  --dev-dark-text: #FFFFFF;
  --dev-dark-primary: #00CA72; /* Same green works on dark */

  /* Sprint status */
  --dev-completed: #00CA72;
  --dev-active: #FFCC00;
  --dev-blocked: #FB275D;
}
```

### Examples

**Good dev Color Usage**:
- Green as primary action color (20-30%)
- Dark backgrounds acceptable for technical feel
- Purple links/accents maintain Monday connection
- Code-friendly aesthetic with proper contrast
- Green/yellow/red for sprint and build statuses

**Avoid**:
- All green (loses Monday brand)
- Purple as primary (that's Work Management)
- Low contrast on dark backgrounds (ensure AA minimum)
- Bright, marketing-heavy compositions (too non-technical)

## service Color System

### Primary Palette

| Role | Color | Hex | Usage % |
|------|-------|-----|---------|
| **service Hero** | Red | `#FB275D` | 20-25% |
| **Background** | White | `#FFFFFF` | 50-60% |
| **Text** | Monday Dark | `#181B34` | 10-15% |
| **Accents** | Yellow & Purple | `#FFCC00` / `#6161FF` | 10-15% |

### service-Specific Strategy

**Key Difference**: service uses red (typically an "error" color) as primary, creating energetic, urgent, dynamic feeling appropriate for customer support teams.

**Red as Energy** (not error):
- Primary CTAs: Red background, white text
- Urgent tickets: Red (but this is primary, not negative)
- Headers: Red or white with red accents
- Charts: Red bars for ticket volume, activity

**Yellow Complements Red**:
- In-progress tickets: Yellow
- Medium priority: Yellow indicators
- Attention items: Yellow highlights
- Creates warm, energetic palette with red

### Supportive Palette

| Role | Color | Hex | service Context |
|------|-------|-----|-------------|
| **Resolved** | Green | `#00CA72` | Tickets resolved, SLAs met |
| **Open/Active** | Red | `#FB275D` | Active tickets (primary color) |
| **Waiting** | Yellow | `#FFCC00` | Pending customer, awaiting response |
| **Link/Accent** | Purple | `#6161FF` | Monday brand anchor |

### Typical service Composition

**Support Dashboard**:
- Header: Red background, white text
- Ticket list: White background
- Ticket cards: White with left border (red=active, yellow=waiting, green=resolved)
- Charts: Red bars for open tickets, green for resolved
- Primary CTA: Red button ("New ticket")
- Secondary CTA: Purple outline ("View reports")

**service Landing Page**:
- Hero: White background, red CTA or red headline accent
- Features: White with occasional light red tint backgrounds
- Testimonials: Purple accents for quotes
- Stats: Red numbers, green positive changes
- Final CTA: Red button

### CSS Variables (service)

```css
:root {
  /* service Specific */
  --service-primary: #FB275D;
  --service-primary-hover: #E91548;
  --service-primary-light: #FFF0F4;
  --service-secondary: #FFCC00; /* Yellow complements */
  --service-accent: #6161FF; /* Purple anchor */
  --service-text: #181B34;
  --service-background: #FFFFFF;

  /* Ticket status */
  --service-active: #FB275D; /* Red = active (not error!) */
  --service-waiting: #FFCC00;
  --service-resolved: #00CA72;
}
```

### Examples

**Good service Color Usage**:
- Red dominates (20-25%) but not overwhelming
- Red is energetic/active, NOT error-only
- Yellow complements red for warm palette
- Purple anchor maintains Monday brand
- Green for positive outcomes (resolved, goals met)

**Avoid**:
- Treating red only as errors (it's the primary!)
- Red + purple co-primaries (choose red for service)
- More than 30% red (too intense)
- Green as primary (that's dev)
- All red with no yellow (loses warmth)

## Cross-Product Color Transitions

### When Showing Multiple Products

If a design must show multiple products (e.g., Monday.com homepage showcasing all products):

**Approach 1: Sequential Sections**
- Hero: Monday Purple (overarching brand)
- Work Management section: Purple dominates
- CRM section: Turquoise dominates (with purple touch)
- dev section: Green dominates (with purple touch)
- service section: Red dominates (with purple touch)
- Closing: Purple (returns to overarching brand)

**Approach 2: Unified Purple**
- Use Monday Purple throughout
- Small accents of product colors (icons, small badges)
- Maintains cohesion over product differentiation

**Rule**: Never mix product colors within a single section. Each section is one product context.

### Color Percentage Guidelines by Product

| Product | Primary Color % | Purple Anchor % | Neutrals % | Status Colors % |
|---------|----------------|-----------------|------------|-----------------|
| **Work Management** | 25-30% (purple) | — (is primary) | 60-65% | 10-15% |
| **CRM** | 20-25% (turquoise) | 10-15% | 55-60% | 10-15% |
| **dev** | 20-30% (green) | 10-15% | 50-60% | 10-15% |
| **service** | 20-25% (red) | 10-15% | 55-60% | 10-15% |

**Neutrals**: White, light purple, Monday Dark for text

## Quick Decision Tree

**Use this to choose product color scheme**:

1. **User mentions "CRM", "sales", "deals", "pipeline"** → CRM (turquoise primary)
2. **User mentions "dev", "developer", "sprint", "code"** → dev (green primary)
3. **User mentions "service", "support", "tickets", "customers"** → service (red primary)
4. **User mentions "Work Management", "workflows", "projects"** → Work Management (purple primary)
5. **User mentions "Monday.com" generically** → Work Management (purple primary, default)

## Product Color Checklist

Before finalizing a product-specific design:

**Work Management**:
- [ ] Monday Purple is the most prominent color (25-30%)
- [ ] No other product primary colors used
- [ ] Green/yellow/red only for status
- [ ] White backgrounds with light purple sections

**CRM**:
- [ ] Turquoise is primary (20-25%)
- [ ] Purple is visible as brand anchor (10-15%)
- [ ] Turquoise + purple don't compete
- [ ] Green/yellow/red for deal stages

**dev**:
- [ ] Green is primary (20-30%)
- [ ] Dark backgrounds acceptable
- [ ] Purple accents maintain brand connection
- [ ] Technical, code-friendly aesthetic

**service**:
- [ ] Red is primary (20-25%), used positively
- [ ] Yellow complements red (warm palette)
- [ ] Purple anchor visible
- [ ] Red doesn't feel error-only

## Advanced: Color Psychology by Product

**Work Management (Purple)**:
- Associations: Premium, trustworthy, creative, visionary
- Emotion: Confidence, reliability, forward-thinking
- Target: Senior leaders who value strategic platforms

**CRM (Turquoise)**:
- Associations: Fresh, modern, calm confidence, clarity
- Emotion: Refreshing alternative to stale CRMs
- Target: Sales teams tired of clunky legacy tools

**dev (Green)**:
- Associations: Growth, progress, success, go-ahead
- Emotion: Productive, efficient, indie spirit
- Target: Developers who value speed and autonomy

**service (Red)**:
- Associations: Energy, urgency, responsiveness, passion
- Emotion: Dynamic, fast-paced, empowering
- Target: Support teams handling high-volume, time-sensitive work

Use these associations when choosing imagery, copy tone, and secondary elements to reinforce the product's color psychology.
