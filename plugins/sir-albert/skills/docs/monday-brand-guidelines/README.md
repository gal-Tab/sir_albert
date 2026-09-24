# Monday.com Brand Guidelines Skill

A comprehensive Claude Code skill for applying Monday.com's official brand identity to designs, artifacts, and visualizations.

## What This Skill Does

Creates Monday.com branded content including:
- HTML/web designs with Monday purple (#6161FF) and brand colors
- Charts, graphs, and data visualizations
- Marketing materials and presentations
- Product-specific designs for Work Management, CRM, dev, or service
- UI mockups and prototypes using Monday's visual language
- Brand-compliant typography (Poppins/Figtree)
- Content following Monday's fluff-free, passionate voice

## Directory Structure

```
monday-brand-guidelines/
├── SKILL.md                          # Main skill (400-450 lines)
├── LICENSE.txt                       # Apache-2.0 license
├── README.md                         # This file
├── assets/
│   ├── color-palette.md             # Complete color specifications
│   ├── product-colors.md            # Product-specific color systems
│   └── logo-guidelines.md           # Logo usage rules
├── references/
│   ├── tone-guide.md                # 50+ voice examples
│   ├── design-principles.md         # Visual design philosophy
│   └── product-personas.md          # Product brand personalities
└── templates/
    ├── html-starter.html            # Monday-branded HTML template
    ├── chart-template.html          # Chart/graph template
    └── presentation-slide.html      # Slide deck template
```

## Installation

This skill ships bundled in the `sir-albert` plugin at `skills/docs/monday-brand-guidelines/` and requires no manual copy or symlink into `~/.claude/skills/`. It is loaded automatically via the plugin.

## Usage

The skill automatically activates when you request Monday.com branded content:

### Example Prompts

**General Monday.com**:
- "Create a landing page for Monday.com"
- "Design a Monday.com dashboard"
- "Build a Monday-branded presentation"

**Product-Specific**:
- "Create a CRM dashboard for monday sales CRM"
- "Design a sprint chart for monday dev"
- "Build a support ticket view for monday service"

**Charts & Visualizations**:
- "Create a sprint velocity chart with Monday.com branding"
- "Build a sales pipeline visualization for CRM"
- "Design a project status dashboard"

**Content**:
- "Write Monday.com style copy for a new feature"
- "Create headline options following Monday's voice"
- "Draft email copy in Monday's tone"

## Skill Features

### Brand Coverage
- All 4 products (Work Management, CRM, dev, service)
- Complete color systems (primary, supportive, product-specific)
- Typography guidelines (Poppins, Figtree)
- Logo usage rules

### Voice & Tone
- Core principles (confident, fluff-free, playful, passionate)
- Product-specific personas with 25+ examples each
- Jargon blacklist and power words
- Context-specific guidance

### Visual Design
- Whitespace philosophy and spacing scale
- Component library (buttons, cards, forms)
- Grid systems and responsive patterns
- Accessibility requirements (WCAG AA/AAA)

### Working Templates
- HTML starter with CSS variables
- Chart template with 4 chart types
- Presentation template with navigation

## Verification

After installation, test the skill:

1. **Ask Claude**: "Create a Monday.com landing page"
2. **Expected behavior**: Skill loads, applies brand guidelines, creates HTML
3. **Check for**: Purple colors, Poppins font, sentence case copy, generous whitespace

## Product Colors Quick Reference

| Product | Primary Color | Hex |
|---------|---------------|-----|
| Work Management | Monday purple | `#6161FF` |
| CRM | Turquoise | `#00D2D2` |
| dev | Green | `#00CA72` |
| service | Red | `#FB275D` |

## File Sizes

- Total: ~1,800-2,200 lines across 11 files
- SKILL.md: ~450 lines (core instructions)
- Supporting files: ~1,400-1,750 lines (references, templates)

## License

Apache-2.0 (see LICENSE.txt)

## Updates

To update the skill:

1. Edit files in this directory
2. Changes take effect immediately — the skill is loaded directly from the plugin bundle, so no re-copy is needed.

## Troubleshooting

**Skill not activating?**
- Verify SKILL.md exists and has proper YAML frontmatter
- Restart Claude Code

**Wrong colors appearing?**
- Check if prompt mentioned specific product (CRM, dev, service)
- Default is Work Management (purple) if unspecified

**Templates not loading?**
- Verify templates/ directory exists
- Check file paths in SKILL.md reference correct locations

## Support

For issues with this skill, check:
1. SKILL.md for brand guidelines
2. references/ for detailed examples
3. templates/ for working code samples

---

Created following the Anthropic skills specification pattern.
