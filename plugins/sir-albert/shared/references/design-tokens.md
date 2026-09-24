# Design Tokens — html-plans

CSS variables and components for plan HTML files. Inline this entire set into your `<style>` block.

## CSS Variables

```css
:root {
  /* Colors — dark theme */
  --color-bg: #000000;
  --color-surface: #232427;
  --color-surface-alt: #2D3035;
  --color-text: #ffffff;
  --color-text-secondary: #c3ced8;
  --color-text-muted: #a0a0a0;
  --color-border: rgba(255, 255, 255, 0.15);
  --color-border-strong: rgba(255, 255, 255, 0.8);

  /* Brand accents */
  --color-purple: #6164ff;
  --color-purple-light: #8A99FF;
  --color-green: #00c875;
  --color-yellow: #ffcb00;
  --color-red: #ff3d57;

  /* Typography */
  --font-main: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'SF Mono', 'Fira Code', 'Consolas', 'Monaco', monospace;
  --weight-regular: 400;
  --weight-semibold: 600;

  /* Type scale (vmin for responsive) */
  --text-display: 4vmin;
  --text-h1: 3.2vmin;
  --text-h2: 2.6vmin;
  --text-h3: 2.2vmin;
  --text-body: 1.8vmin;
  --text-body-sm: 1.5vmin;
  --text-caption: 1.2vmin;

  /* Spacing */
  --space-1: 0.5vmin;
  --space-2: 1vmin;
  --space-3: 1.5vmin;
  --space-4: 2vmin;
  --space-5: 3vmin;
  --space-6: 4vmin;
  --space-7: 5vmin;
  --space-8: 6vmin;
  --space-9: 8vmin;
  --space-10: 10vmin;

  /* Radii */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 999px;
}
```

**Note on type scale:** These values are tuned for plan documents viewed in a browser at normal zoom, not for 16:9 slides. They're smaller than the presentation design system because plans are read like documents, not projected.

## Base Styles

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-main);
  font-weight: var(--weight-regular);
  background: var(--color-bg);
  color: var(--color-text);
  line-height: 1.6;
  padding: var(--space-8) var(--space-6);
  max-width: 1100px;
  margin: 0 auto;
}

h1, h2, h3, h4 {
  font-weight: var(--weight-semibold);
  line-height: 1.3;
}
```

## Components

### Header Card

Top of the plan — goal, architecture, tech stack, metadata badges.

```css
.plan-header {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-7);
  margin-bottom: var(--space-7);
}

.plan-title {
  font-size: var(--text-display);
  font-weight: var(--weight-semibold);
  margin-bottom: var(--space-4);
}

.plan-goal {
  font-size: var(--text-h3);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-5);
}

.meta-badges {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.badge {
  background: var(--color-surface-alt);
  color: var(--color-text-secondary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-caption);
  font-weight: var(--weight-semibold);
}

.badge-purple { border: 1px solid var(--color-purple); color: var(--color-purple); }
.badge-green { border: 1px solid var(--color-green); color: var(--color-green); }
.badge-yellow { border: 1px solid var(--color-yellow); color: var(--color-yellow); }
```

### DOD Section

```css
.dod-section {
  background: var(--color-surface);
  border-left: 3px solid var(--color-purple);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  margin-bottom: var(--space-7);
}

.dod-section h2 {
  font-size: var(--text-h2);
  margin-bottom: var(--space-3);
}

.dod-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-2) 0;
  color: var(--color-text-secondary);
  font-size: var(--text-body);
}

.dod-item input[type="checkbox"] {
  accent-color: var(--color-purple);
  margin-top: 3px;
  flex-shrink: 0;
}
```

### Milestone Cards

```css
.milestone {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  margin-bottom: var(--space-5);
}

.milestone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.milestone-title {
  font-size: var(--text-h2);
}

.milestone-meta {
  font-size: var(--text-caption);
  color: var(--color-text-muted);
}
```

### Collapsible Task

```css
.task {
  background: var(--color-surface-alt);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
  overflow: hidden;
}

.task-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  cursor: pointer;
  user-select: none;
  transition: background 0.15s ease;
}

.task-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.task-chevron {
  transition: transform 0.2s ease;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.task.open .task-chevron {
  transform: rotate(90deg);
}

.task-number {
  font-size: var(--text-body);
  font-weight: var(--weight-semibold);
  color: var(--color-purple);
  min-width: 3ch;
}

.task-name {
  font-size: var(--text-body);
  font-weight: var(--weight-semibold);
  flex: 1;
}

.task-files {
  font-size: var(--text-caption);
  color: var(--color-text-muted);
}

.task-body {
  padding: 0 var(--space-4) var(--space-4);
  display: none;
}

.task.open .task-body {
  display: block;
}
```

### Code Block

```css
.code-block {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin: var(--space-3) 0;
  overflow-x: auto;
}

.code-block pre {
  font-family: var(--font-mono);
  font-size: var(--text-body-sm);
  line-height: 1.5;
  color: var(--color-text-secondary);
  white-space: pre;
  margin: 0;
}

.code-block .code-comment { color: var(--color-text-muted); }
.code-block .code-key { color: var(--color-purple-light); }
.code-block .code-value { color: var(--color-yellow); }
.code-block .code-keyword { color: var(--color-purple); }
.code-block .code-string { color: var(--color-green); }

.code-label {
  font-family: var(--font-mono);
  font-size: var(--text-caption);
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}
```

### Risk Callout

```css
.risk-callout {
  border-left: 3px solid var(--color-yellow);
  background: rgba(255, 203, 0, 0.06);
  padding: var(--space-3) var(--space-4);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  margin: var(--space-3) 0;
  font-size: var(--text-body-sm);
}

.risk-callout.high {
  border-left-color: var(--color-red);
  background: rgba(255, 61, 87, 0.06);
}

.risk-label {
  font-weight: var(--weight-semibold);
  color: var(--color-yellow);
  font-size: var(--text-caption);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}

.risk-callout.high .risk-label {
  color: var(--color-red);
}
```

### Step List

```css
.step {
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
}

.step:last-child {
  border-bottom: none;
}

.step-label {
  font-size: var(--text-body-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-purple-light);
  margin-bottom: var(--space-2);
}

.step-command {
  font-family: var(--font-mono);
  font-size: var(--text-body-sm);
  background: var(--color-bg);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  margin: var(--space-2) 0;
}

.step-expected {
  font-size: var(--text-caption);
  color: var(--color-text-muted);
  font-style: italic;
}
```

### Task DOD (inline)

```css
.task-dod {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.task-dod-title {
  font-size: var(--text-caption);
  font-weight: var(--weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}
```

### Diagram Container

```css
.diagram-container {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  margin: var(--space-5) 0;
  overflow-x: auto;
}

.diagram-title {
  font-size: var(--text-body);
  font-weight: var(--weight-semibold);
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

.mermaid {
  display: flex;
  justify-content: center;
}
```

### Open Question

```css
.open-question {
  background: rgba(97, 100, 255, 0.06);
  border-left: 3px solid var(--color-purple);
  padding: var(--space-3) var(--space-4);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  margin: var(--space-3) 0;
  font-size: var(--text-body-sm);
}

.question-owner {
  font-size: var(--text-caption);
  color: var(--color-purple-light);
  margin-top: var(--space-1);
}
```

## Collapsible Toggle JS

```js
document.querySelectorAll('.task-header').forEach(header => {
  header.addEventListener('click', () => {
    header.closest('.task').classList.toggle('open');
  });
});

// Open first task by default
const firstTask = document.querySelector('.task');
if (firstTask) firstTask.classList.add('open');
```
