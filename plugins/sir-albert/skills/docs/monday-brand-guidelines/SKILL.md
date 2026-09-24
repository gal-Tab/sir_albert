---
name: monday-brand-guidelines
description: Apply Monday.com's official brand identity to designs, artifacts, and visualizations. Use when creating Monday.com branded content including (1) HTML/web designs with Monday purple (#6161FF) and brand colors, (2) Charts, graphs, or data visualizations, (3) Marketing materials or presentations, (4) Product-specific designs for Work Management, CRM, dev, or service, (5) Any artifact requiring Monday.com's bold, playful, confident tone, (6) UI mockups or prototypes needing Monday's visual language, (7) Brand-compliant typography (Poppins/Figtree), or (8) Content following Monday's fluff-free, passionate voice.
license: Apache-2.0
---

# Monday.com Brand Guidelines Skill

This skill helps you create artifacts that authentically embody Monday.com's brand identity—from web pages and dashboards to charts and presentations.

## Two-Step Pattern

When creating Monday.com branded content, follow this proven workflow:

**Step 1: Internalize the brand**
- Review the relevant brand foundations (values, tone, colors, typography)
- Identify the product context (Work Management, CRM, dev, service, or overarching Monday.com)
- Understand the target audience and communication goals

**Step 2: Create the artifact**
- Apply brand guidelines systematically
- Use provided templates as starting points
- Run through the quality checklist before delivering
- Iterate based on brand compliance

## 1. Brand Foundation

### Core Brand Values

Monday.com's brand is built on four pillars:

1. **Bold**: Take strong positions, make definitive statements, lead don't follow
2. **Best in Class**: Premium quality, attention to detail, excellence in execution
3. **Authentic**: Real, honest, transparent—no corporate BS
4. **Direct**: Clear communication, no fluff, get to the point

### Overarching Tone Attributes

Every Monday.com communication should embody these characteristics:

- **Confident**: Assured without arrogance, expert without condescension
- **Fluff-free**: Concise, direct, no jargon or buzzwords
- **Playful**: Light-hearted touches, occasionally whimsical, never silly
- **Passionate**: Genuine enthusiasm for helping teams succeed

### Visual Identity Philosophy

Monday.com's visual language is:
- **Vibrant**: Bold use of color, especially the signature Monday purple
- **Clean**: Generous whitespace, uncluttered layouts, breathing room
- **Modern**: Contemporary design patterns, forward-looking aesthetic
- **Accessible**: High contrast, legible typography, inclusive design

### When to Apply This Skill

Use this skill when creating:
- Landing pages or web designs requiring Monday branding
- Product dashboards, UI mockups, or prototypes
- Marketing materials (presentations, ads, collateral)
- Data visualizations (charts, graphs, infographics)
- Email templates or communication assets
- Documentation or help content for Monday products

## 2. Color System

### Primary Colors

These are your foundation—use them in every Monday.com artifact:

| Color | Hex | Usage |
|-------|-----|-------|
| **Monday purple** | `#6161FF` | Primary brand color, CTAs, key UI elements |
| **Monday dark** | `#181B34` | Text, headers, dark UI components |
| **Monday light** | `#F0F3FF` | Backgrounds, subtle highlights, light sections |
| **White** | `#FFFFFF` | Main backgrounds, cards, clean space |

**Monday purple (#6161FF)** is the hero. It should be the most prominent non-neutral color in Work Management contexts and present as an accent in all product contexts.

### Supportive Colors

Use these for status, data visualization, and visual interest:

| Color | Hex | Meaning |
|-------|-----|---------|
| **Green** | `#00CA72` | Success, completion, positive metrics |
| **Yellow** | `#FFCC00` | In-progress, warnings, attention |
| **Red** | `#FB275D` | Errors, urgent, critical metrics |

### Product-Specific Colors

Each Monday.com product has its own primary color while maintaining the Monday purple as a connecting thread:

| Product | Primary Color | Hex | Usage |
|---------|---------------|-----|-------|
| **Work Management** | Monday purple | `#6161FF` | Default for general Monday.com |
| **CRM** | Turquoise | `#00D2D2` | CRM-specific designs |
| **dev** | Green | `#00CA72` | Developer product designs |
| **service** | Red | `#FB275D` | Service product designs |

**Choosing product context**: If the user mentions a specific product (CRM, dev, service), use that product's color scheme. If they mention "Monday.com" generally or "Work Management," use Monday purple.

### Color Hierarchy

In a typical Monday.com design:
- 60-70% neutral (white, light purple, dark for text)
- 20-30% primary color (purple or product color)
- 10-20% supportive colors (green, yellow, red for data/status)

For detailed color specifications including RGB, CMYK, and accessibility ratings, see `assets/color-palette.md`.

For comprehensive product-specific color systems, see `assets/product-colors.md`.

## 3. Typography

### Font Families

Monday.com uses two primary typefaces:

**Poppins** (Brand & Marketing)
- **Bold** (700): Main headlines, hero text, major CTAs
- **Semi-bold** (600): Subheadings, section titles
- **Regular** (400): Body text in marketing materials
- **Light** (300): Supporting text, captions

**Figtree** (Platform & Product)
- Use for platform UI, emails, in-app content
- Provides excellent readability at small sizes
- Use Regular (400) and Semi-bold (600)

### Loading Fonts in HTML

```html
<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Figtree:wght@400;600&display=swap" rel="stylesheet">

<style>
  :root {
    --font-brand: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-platform: 'Figtree', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  body {
    font-family: var(--font-brand);
  }
</style>
```

### Type Hierarchy

**Marketing/Landing Pages**:
- H1: Poppins Bold, 48-64px (desktop), 32-40px (mobile)
- H2: Poppins Semi-bold, 36-48px (desktop), 28-32px (mobile)
- H3: Poppins Semi-bold, 24-32px
- Body: Poppins Regular, 16-18px
- Caption: Poppins Light, 14px

**Platform/Product UI**:
- Headings: Figtree Semi-bold, 20-32px
- Body: Figtree Regular, 14-16px
- Small: Figtree Regular, 12-14px

### Typography Rules

- Line height: 1.5-1.6 for body text, 1.2-1.3 for headings
- Letter spacing: Default for body, slightly tighter (-0.02em) for large headings
- Never use all caps except for very small labels (10-12px)
- Maintain high contrast: dark text on light backgrounds, light text on dark

## 4. Writing & Content Principles

### Formatting Rules

**Critical formatting conventions**:

1. **Sentence case everywhere**: "Get started today" not "Get Started Today"
2. **No periods on headlines**: Headlines and section titles end without periods
3. **No title case**: Only capitalize the first word and proper nouns
4. **Short paragraphs**: 2-3 sentences maximum per paragraph
5. **Active voice required**: "Create workflows" not "Workflows can be created"

### Tone Application by Context

| Context | Confidence | Playfulness | Directness | Example |
|---------|------------|-------------|------------|---------|
| Marketing headlines | High | Medium | High | "Work without limits" |
| Product descriptions | High | Low | High | "Track deals from lead to close" |
| UI labels/buttons | Medium | Low | Very High | "Add team member" |
| Error messages | Medium | Low | High | "Email address required" |
| Success messages | High | High | Medium | "You're all set" |
| Help documentation | Medium | Low | Very High | "Select a board to begin" |

### Voice Examples: Good vs Avoid

**Good Monday Voice**:
- "Build better workflows"
- "See your entire project at a glance"
- "Work the way you want"
- "Track everything in one place"
- "Automate the boring stuff"

**Avoid** (Too corporate/jargony):
- "Leverage synergies to optimize outcomes"
- "Seamlessly integrate your workflow ecosystem"
- "Unlock next-generation productivity solutions"
- "Empower your digital transformation journey"
- "Drive strategic alignment across stakeholders"

### Jargon Blacklist

Never use these words in Monday.com content:
- Leverage, synergy, paradigm, utilize, facilitate
- Seamlessly, effortlessly (unless genuinely describing UX)
- Next-generation, cutting-edge, revolutionary
- Empower (overused), transform, disrupt
- Ecosystem, holistic, robust, innovative (as adjectives)

### Content Guidelines

- **Be specific**: "Save 5 hours per week" beats "Save time"
- **Use numbers**: Data and metrics add credibility
- **Ask questions**: "Tired of messy spreadsheets?" engages readers
- **Paint pictures**: "Scattered tasks, missed deadlines, confused teams" shows problems vividly
- **End with action**: Every section should drive toward doing something

For 50+ detailed voice examples across different contexts, see `references/tone-guide.md`.

## 5. Product-Specific Guidelines

Monday.com has four main product lines, each with distinct brand personalities:

### Work Management (monday.com)

**Visual Identity**:
- Primary color: Monday purple (#6161FF)
- Generous use of purple in CTAs, headers, accents
- Clean white backgrounds with light purple (#F0F3FF) sections
- Professional, organized aesthetic

**Tone & Voice**:
- **Premium**: This is the flagship, enterprise-grade product
- **Visionary**: Forward-thinking, strategic perspective
- **Knowledgeable**: Expert guidance without condescension
- Speak to senior managers, operations leaders, executives

**Example Copy**:
- Headline: "Run your entire operation on one platform"
- CTA: "See how Work Management scales"
- Feature: "Customizable workflows that grow with your team"

### CRM (monday sales CRM)

**Visual Identity**:
- Primary color: Turquoise (#00D2D2)
- Purple as secondary accent color
- More colorful, energetic than Work Management
- Data-rich, dashboard-focused designs

**Tone & Voice**:
- **Self-aware**: Knows the CRM space is crowded
- **Spicy**: Bold, occasionally edgy, stands out
- **Honest**: Doesn't overpromise, realistic benefits
- Speak to sales teams, revenue leaders

**Example Copy**:
- Headline: "A CRM that doesn't make you want to quit sales"
- CTA: "Try the CRM salespeople actually like"
- Feature: "Track deals without the busywork"

### dev (monday dev)

**Visual Identity**:
- Primary color: Green (#00CA72)
- Dark backgrounds acceptable (dark mode aesthetic)
- Code-friendly, technical aesthetic
- Clean, minimal, fast-feeling

**Tone & Voice**:
- **Edgy**: Challenges status quo, anti-legacy
- **Indie**: Developer-first, built by devs for devs
- **Expert**: Technical depth, no hand-holding
- Speak to developers, engineering teams

**Example Copy**:
- Headline: "Project management that doesn't get in your way"
- CTA: "Ship faster with monday dev"
- Feature: "Sprint planning for teams who actually ship"

### service (monday service)

**Visual Identity**:
- Primary color: Red (#FB275D)
- Energetic, dynamic compositions
- Service/support iconography
- Warm, approachable aesthetic

**Tone & Voice**:
- **Dynamic**: Fast-paced, responsive, agile
- **Empowering**: Helps teams be heroes
- **Cool**: Modern support, not old-school ticketing
- Speak to support teams, service managers

**Example Copy**:
- Headline: "Support software that supports your team"
- CTA: "Make every customer happy"
- Feature: "Resolve issues before they escalate"

For comprehensive product persona deep-dives with 20+ examples each, see `references/product-personas.md`.

## 6. Creating Artifacts

### Pre-Creation Checklist

Before you start building, confirm:

1. **Product context identified**: Which product (or general Monday.com)?
2. **Primary color selected**: Purple, turquoise, green, or red?
3. **Tone calibrated**: Match the product persona
4. **Audience understood**: Who will see this?
5. **Goal clarified**: What action should users take?

### HTML Artifacts

When creating HTML pages, dashboards, or web content:

**Structure Requirements**:
- Start from `templates/html-starter.html` as base
- Use semantic HTML5 (header, main, section, article)
- Include meta tags (viewport, description)
- Add CSS variables for all Monday colors

**Layout Principles**:
- Generous padding: 60-80px on sections (desktop), 40px (mobile)
- Wide max-width: 1200-1400px for content
- Card-based components with subtle shadows
- Sticky headers acceptable for navigation

**Starter Code Pattern**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monday.com - [Your Title]</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --monday-purple: #6161FF;
      --monday-dark: #181B34;
      --monday-light: #F0F3FF;
      /* Add more colors as needed */
    }

    body {
      font-family: 'Poppins', sans-serif;
      margin: 0;
      background: #FFFFFF;
      color: var(--monday-dark);
      line-height: 1.6;
    }

    /* Your Monday-branded styles */
  </style>
</head>
<body>
  <!-- Your content -->
</body>
</html>
```

### Chart & Graph Guidelines

When creating data visualizations:

**Color Selection**:
- Use Monday purple for single-series data
- Use green/yellow/red for status-based data
- Use product color + supportive colors for multi-series
- Ensure sufficient contrast between series

**Chart Best Practices**:
- Clean axes, no unnecessary gridlines
- Large, legible labels (14px minimum)
- Tooltips on hover for detailed data
- Responsive sizing for mobile
- Export options when appropriate

**Starting Point**: Use `templates/chart-template.html` which includes Chart.js with Monday color schemes pre-configured.

### Design Elements

**Buttons**:
- Primary: Monday purple background, white text, 8-12px border radius
- Secondary: White background, purple border, purple text
- Hover states: Darken by 10-15%
- Padding: 12-16px vertical, 24-32px horizontal

**Cards**:
- White background
- Border radius: 8-12px
- Subtle shadow: `0 2px 8px rgba(0,0,0,0.08)`
- Padding: 24-32px
- Hover effect: Lift slightly (`0 4px 16px rgba(0,0,0,0.12)`)

**Spacing Scale**:
- 4px, 8px, 16px, 24px, 32px, 48px, 64px, 80px
- Use consistently across components
- More whitespace is better than less

### Template Resources

| Template | Purpose | Use When |
|----------|---------|----------|
| `templates/html-starter.html` | Complete HTML boilerplate | Creating any web page or dashboard |
| `templates/chart-template.html` | Chart.js setup with Monday colors | Building data visualizations |
| `templates/presentation-slide.html` | Slide deck framework | Creating presentations or pitch decks |

## 7. Example Workflows

### Scenario 1: Marketing Landing Page for Work Management

**User Request**: "Create a landing page for Monday.com Work Management"

**Application**:
1. **Product context**: Work Management → use Monday purple (#6161FF)
2. **Tone**: Premium, visionary, knowledgeable
3. **Typography**: Poppins Bold for hero headline (56px), Regular for body (18px)
4. **Colors**: 70% white/light purple, 30% Monday purple accents
5. **Copy examples**:
   - Hero: "Work without limits" (sentence case, no period)
   - Subhead: "One platform for every team, project, and workflow"
   - CTA: "Get started free" (purple button)
6. **Layout**: Hero section with generous whitespace, feature cards below, ending CTA section

### Scenario 2: CRM Dashboard Mockup

**User Request**: "Design a sales dashboard for Monday CRM"

**Application**:
1. **Product context**: CRM → use turquoise (#00D2D2) primary, purple accents
2. **Tone**: Self-aware, spicy, honest—"Your deals, finally organized"
3. **Typography**: Figtree for UI elements (this is platform, not marketing)
4. **Colors**: Turquoise for headers/CTAs, green/yellow/red for deal stages
5. **Charts**: Pipeline chart (turquoise bars), conversion funnel (green/yellow/red stages)
6. **Layout**: Top nav (turquoise header), left sidebar, main dashboard grid with cards

### Scenario 3: Dev Sprint Velocity Chart

**User Request**: "Make a sprint velocity chart for Monday dev"

**Application**:
1. **Product context**: dev → use green (#00CA72) primary
2. **Tone**: Edgy, expert—"Ship faster, stress less"
3. **Chart type**: Bar chart, velocity over sprints
4. **Colors**: Green bars for completed points, yellow for incomplete
5. **Starting point**: `templates/chart-template.html`
6. **Customization**: Dark background option (acceptable for dev product), clean axis labels

### Scenario 4: Service Team Dashboard

**User Request**: "Create a support ticket dashboard for Monday service"

**Application**:
1. **Product context**: service → use red (#FB275D) primary
2. **Tone**: Dynamic, empowering—"Support your team supports"
3. **Colors**: Red for urgent tickets, yellow for open, green for resolved
4. **Layout**: Ticket list (left), individual ticket view (right), status filters (top)
5. **Data viz**: Donut chart showing ticket status distribution (red/yellow/green)
6. **Typography**: Figtree (platform UI), clear labels, large status indicators

## 8. Quality Checklist

Before delivering any Monday.com branded artifact, verify:

### Visual Compliance

- [ ] **Primary color correct**: Monday purple or appropriate product color used prominently
- [ ] **Color hierarchy**: 60-70% neutral, 20-30% primary, 10-20% supportive
- [ ] **Typography loaded**: Poppins and/or Figtree fonts successfully loading
- [ ] **Whitespace generous**: Sections have 60-80px padding (desktop)
- [ ] **Clean aesthetic**: Uncluttered, breathing room, modern feel
- [ ] **Accessible contrast**: WCAG AA minimum (4.5:1 for body text, 3:1 for large)

### Content Compliance

- [ ] **Sentence case**: All headlines and CTAs in sentence case
- [ ] **No periods on headlines**: Headlines end without punctuation
- [ ] **Active voice**: All copy uses active voice
- [ ] **No jargon**: Zero usage of blacklisted corporate buzzwords
- [ ] **Tone aligned**: Voice matches product persona (premium/spicy/edgy/dynamic)
- [ ] **Clear CTAs**: Every section has obvious next action

### Product Alignment

- [ ] **Product identified**: Correct product context applied
- [ ] **Product color**: Using correct primary color for product
- [ ] **Product voice**: Tone matches product personality
- [ ] **Audience appropriate**: Language suited to target users

### Technical Quality

- [ ] **Responsive**: Works on mobile, tablet, desktop
- [ ] **Semantic HTML**: Proper HTML5 tags (header, main, section, etc.)
- [ ] **Performance**: Fast load, optimized assets
- [ ] **Accessibility**: ARIA labels, keyboard navigation, screen reader friendly
- [ ] **Cross-browser**: Works in modern browsers
- [ ] **Comments**: Code includes comments explaining brand choices

## 9. Resources & References

### Supporting Files in This Skill

**Assets** (Factual references):
- `assets/color-palette.md`: Complete color specifications (Hex, RGB, CMYK, Pantone, accessibility ratings)
- `assets/product-colors.md`: Deep-dive on product-specific color systems with usage percentages
- `assets/logo-guidelines.md`: Logo construction, versions, usage rules

**References** (Guidance & examples):
- `references/tone-guide.md`: 50+ voice examples with before/after corrections
- `references/design-principles.md`: Detailed visual design philosophy, grids, components
- `references/product-personas.md`: Comprehensive product brand personalities with 20+ examples each

**Templates** (Code starters):
- `templates/html-starter.html`: Complete HTML boilerplate with Monday branding
- `templates/chart-template.html`: Chart.js setup with Monday color schemes
- `templates/presentation-slide.html`: Slide deck framework

### When in Doubt Defaults

If you're unsure which direction to take:

- **Product**: Default to Work Management (Monday purple #6161FF)
- **Tone**: Default to confident, direct, professional
- **Typography**: Default to Poppins for marketing content
- **Background**: Default to white (#FFFFFF)
- **Layout**: Default to generous whitespace (more is better)
- **Copy style**: Default to sentence case, active voice, no jargon

### Brand Principles Summary

Remember Monday.com's brand essence:

1. **Bold but not brash**: Strong opinions, humble delivery
2. **Best in class but accessible**: Premium without pretension
3. **Authentic but professional**: Real without being casual
4. **Direct but not cold**: Clear without being robotic
5. **Confident but not arrogant**: Expert without condescension
6. **Playful but not silly**: Light-hearted without being frivolous

Apply these principles consistently across all artifacts, and you'll create content that truly embodies the Monday.com brand.
