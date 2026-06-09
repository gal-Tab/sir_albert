# SVG Patterns Library

Reusable SVG snippets for building README graphics. Copy and adapt these building blocks.

---

## Defs: Gradients

### Dark Background Gradient
```xml
<linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#000000"/>
  <stop offset="100%" stop-color="#0a0a1a"/>
</linearGradient>
```

### Purple Glow Gradient (radial, for behind text)
```xml
<radialGradient id="purple-glow" cx="50%" cy="50%" r="40%">
  <stop offset="0%" stop-color="#6161FF" stop-opacity="0.15"/>
  <stop offset="100%" stop-color="#6161FF" stop-opacity="0"/>
</radialGradient>
```

### Card Surface Gradient (subtle depth)
```xml
<linearGradient id="card-surface" x1="0%" y1="0%" x2="0%" y2="100%">
  <stop offset="0%" stop-color="#2D3035"/>
  <stop offset="100%" stop-color="#232427"/>
</linearGradient>
```

### Purple Connector Gradient (for animated flow)
```xml
<linearGradient id="flow-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="#6161FF" stop-opacity="0.3"/>
  <stop offset="50%" stop-color="#6161FF" stop-opacity="1"/>
  <stop offset="100%" stop-color="#6161FF" stop-opacity="0.3"/>
</linearGradient>
```

---

## Defs: Filters

### Drop Shadow (for cards)
```xml
<filter id="shadow" x="-5%" y="-5%" width="110%" height="120%">
  <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.4"/>
</filter>
```

### Purple Glow (for text or accent elements)
```xml
<filter id="text-glow" x="-20%" y="-20%" width="140%" height="140%">
  <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur"/>
  <feColorMatrix in="blur" type="matrix"
    values="0.38 0 0 0 0
            0.38 0 0 0 0
            1    0 0 0 0
            0    0 0 0.6 0" result="purple-blur"/>
  <feMerge>
    <feMergeNode in="purple-blur"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

### Subtle Inner Glow (for active/selected states)
```xml
<filter id="inner-glow">
  <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
  <feOffset dx="0" dy="0"/>
  <feComposite in2="SourceAlpha" operator="arithmetic" k2="-1" k3="1"/>
  <feColorMatrix type="matrix"
    values="0.38 0 0 0 0
            0.38 0 0 0 0
            1    0 0 0 0
            0    0 0 0.3 0"/>
  <feMerge>
    <feMergeNode/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

---

## Defs: Markers (Arrows)

### Standard Arrow (purple, filled)
```xml
<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="8" markerHeight="8" orient="auto-start-reverse">
  <path d="M 0 0 L 10 5 L 0 10 z" fill="#6161FF"/>
</marker>
```

### Open Arrow (outline only)
```xml
<marker id="arrow-open" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="8" markerHeight="8" orient="auto-start-reverse">
  <path d="M 1 1 L 9 5 L 1 9" fill="none" stroke="#6161FF" stroke-width="1.5"/>
</marker>
```

### Circle Dot (for node endpoints)
```xml
<marker id="dot" viewBox="0 0 10 10" refX="5" refY="5"
        markerWidth="6" markerHeight="6">
  <circle cx="5" cy="5" r="4" fill="#6161FF"/>
</marker>
```

**Usage on lines:**
```xml
<line x1="100" y1="200" x2="300" y2="200"
      stroke="#6161FF" stroke-width="2" marker-end="url(#arrow)"/>
```

---

## Defs: Patterns

### Dot Grid Background
```xml
<pattern id="dot-grid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
  <circle cx="10" cy="10" r="0.8" fill="rgba(255,255,255,0.04)"/>
</pattern>
```
**Usage:** `<rect width="900" height="400" fill="url(#dot-grid)"/>`

### Scan Lines (for terminal backgrounds)
```xml
<pattern id="scanlines" x="0" y="0" width="900" height="4" patternUnits="userSpaceOnUse">
  <rect width="900" height="1" fill="rgba(255,255,255,0.015)"/>
</pattern>
```

### Diagonal Hatch (for "disabled" or "placeholder" areas)
```xml
<pattern id="hatch" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <line x1="0" y1="0" x2="0" y2="8" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
</pattern>
```

---

## Components: Cards

### Standard Card
```xml
<g transform="translate(X, Y)">
  <rect width="200" height="100" rx="8" fill="#232427" filter="url(#shadow)"/>
  <text x="20" y="36" font-family="'Poppins', sans-serif" font-size="16" font-weight="600" fill="#FFFFFF">Card Title</text>
  <text x="20" y="58" font-family="'Poppins', sans-serif" font-size="13" font-weight="400" fill="#C3CED8">Description text here</text>
</g>
```

### Card with Top Accent
```xml
<g transform="translate(X, Y)">
  <rect width="200" height="100" rx="8" fill="#232427"/>
  <rect width="200" height="3" rx="8 8 0 0" fill="#6161FF"/>
  <text x="20" y="40" font-family="'Poppins', sans-serif" font-size="16" font-weight="600" fill="#FFFFFF">Title</text>
  <text x="20" y="62" font-family="'Poppins', sans-serif" font-size="13" font-weight="400" fill="#C3CED8">Subtitle</text>
</g>
```

Note: SVG `rx` on `<rect>` applies to all corners equally. For top-only rounding, use a `<clipPath>` or two overlapping rects (rounded full rect + a small rect covering the bottom corners).

### Metric Card (big number + label)
```xml
<g transform="translate(X, Y)">
  <rect width="160" height="90" rx="8" fill="#232427"/>
  <text x="80" y="48" text-anchor="middle" font-family="'Poppins', sans-serif" font-size="32" font-weight="700" fill="#6161FF">20</text>
  <text x="80" y="72" text-anchor="middle" font-family="'Poppins', sans-serif" font-size="12" font-weight="400" fill="#C3CED8">Scanners</text>
</g>
```

---

## Components: Terminal Window

### Terminal Frame (top bar + content area)
```xml
<g transform="translate(X, Y)">
  <!-- Window frame -->
  <rect width="W" height="H" rx="10" fill="#1a1a2e"/>
  <!-- Title bar -->
  <rect width="W" height="32" rx="10 10 0 0" fill="#232427"/>
  <!-- Clip the title bar to only round the top -->
  <!-- Traffic lights -->
  <circle cx="20" cy="16" r="6" fill="#FF5F57"/>
  <circle cx="38" cy="16" r="6" fill="#FFBD2E"/>
  <circle cx="56" cy="16" r="6" fill="#27C93F"/>
  <!-- Title -->
  <text x="{W/2}" y="21" text-anchor="middle" font-family="'Poppins', sans-serif" font-size="12" font-weight="400" fill="#A0A0A0">Terminal — tool-name</text>
  <!-- Content area -->
  <rect x="0" y="32" width="W" height="{H-32}" rx="0 0 10 10" fill="#0d0d1a"/>
</g>
```

### Terminal Text Lines
```xml
<!-- Command line -->
<text x="20" y="Y" font-family="'SF Mono', 'Consolas', monospace" font-size="13" fill="#A0A0A0">$ <tspan fill="#FFFFFF">./run_forensics.sh ./repo</tspan></text>

<!-- Finding with severity -->
<text x="20" y="Y" font-family="'SF Mono', 'Consolas', monospace" font-size="13">
  <tspan fill="#FB275D">[CRITICAL]</tspan>
  <tspan fill="#FFFFFF"> tools.json Full-Schema Poisoning</tspan>
</text>

<!-- Indented detail -->
<text x="116" y="Y" font-family="'SF Mono', 'Consolas', monospace" font-size="12" fill="#A0A0A0">Hidden instructions in tool definitions</text>

<!-- Verdict line -->
<text x="20" y="Y" font-family="'SF Mono', 'Consolas', monospace" font-size="13" font-weight="600" fill="#FFFFFF">VERDICT: 0 findings — safe to install</text>
```

---

## Components: Badges / Pills

### Version Badge
```xml
<g transform="translate(X, Y)">
  <rect width="80" height="24" rx="12" fill="#2D3035"/>
  <text x="40" y="16" text-anchor="middle" font-family="'Poppins', sans-serif" font-size="11" font-weight="600" fill="#00CA72">v2.9.2</text>
</g>
```

### Status Pill
```xml
<g transform="translate(X, Y)">
  <rect width="100" height="24" rx="12" fill="rgba(97,97,255,0.15)"/>
  <text x="50" y="16" text-anchor="middle" font-family="'Poppins', sans-serif" font-size="11" font-weight="600" fill="#6161FF">20 Scanners</text>
</g>
```

---

## Components: Connectors

### Straight Horizontal with Arrow
```xml
<line x1="200" y1="200" x2="350" y2="200" stroke="#6161FF" stroke-width="2" marker-end="url(#arrow)"/>
```

### Curved Connector (fan-out)
```xml
<path d="M 200,200 C 250,200 300,150 350,150" stroke="#6161FF" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
```

### Dashed Connector (optional/weak relationship)
```xml
<line x1="200" y1="200" x2="350" y2="200" stroke="#6161FF" stroke-width="1.5" stroke-dasharray="6 4" marker-end="url(#arrow)"/>
```

---

## Animations (GitHub-compatible)

### Fade In
```xml
<g opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur="0.8s" fill="freeze" begin="0.3s"/>
  <!-- content -->
</g>
```

### Bar Growth (for charts)
```xml
<rect x="200" y="180" width="0" height="28" rx="4" fill="#6161FF">
  <animate attributeName="width" from="0" to="350" dur="1.2s" fill="freeze" begin="0.2s" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>
</rect>
```

### Pulse Glow (for emphasis)
```xml
<circle cx="450" cy="200" r="8" fill="#6161FF" opacity="0.6">
  <animate attributeName="r" values="8;12;8" dur="2s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0.6;0.3;0.6" dur="2s" repeatCount="indefinite"/>
</circle>
```

### Flowing Dash (along a connector line)
```xml
<line x1="200" y1="200" x2="400" y2="200" stroke="#6161FF" stroke-width="2" stroke-dasharray="8 4">
  <animate attributeName="stroke-dashoffset" from="24" to="0" dur="1s" repeatCount="indefinite"/>
</line>
```

Use animations sparingly. One or two per SVG max. They should draw attention to the key message, not create visual noise.
