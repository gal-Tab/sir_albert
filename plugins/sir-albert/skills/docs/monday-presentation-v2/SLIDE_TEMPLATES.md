# Slide Templates Catalog

Complete reference of all available slide layout templates for monday-presentation-v2.

Each template shows:
- **Purpose** — What content it's best for
- **Layout** — How it's structured
- **Variables** — What can be customized
- **Source** — Reference implementation (Deck_Dark_Page number or design system)
- **Example** — HTML pattern to use

---

## 1. Title Slide

**Purpose:** Cover slide with headline, subtitle, and logo

**Layout:** Centered content with logo at bottom

**Variables:**
- `headline` (large, primary text)
- `subtitle` (secondary text, optional)
- `accent_color` (optional, for logo tint)

**HTML Pattern:**

```html
<div class="slide-container" data-slide-index="0" style="
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
">
  <div style="margin-bottom: var(--space-8);">
    <h1 class="text-h1">
      Your Headline <span style="color: var(--color-purple);">Here</span>
    </h1>
    <p class="text-h3" style="color: var(--color-text-secondary); margin-top: var(--space-4);">
      Optional subtitle or tagline
    </p>
  </div>

  <div style="position: absolute; bottom: var(--space-8);">
    <!-- monday.com logo (from BRAND_ASSETS.md) -->
    <svg width="120" height="auto" viewBox="..."><!-- logo SVG --></svg>
  </div>
</div>
```

**Content Limit:** 1 headline + 1 subtitle max

**Source:** Deck_Dark_Page_001

---

## 2. Text + Image (Two-Column)

**Purpose:** Narrative content paired with supporting image or visual

**Layout:** Left column text, right column image/content

**Variables:**
- `headline` (section title)
- `body` (paragraph text, 1-2 paragraphs)
- `image_src` or `data-image-placeholder`
- `accent_color` (optional accent bar or highlight)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: var(--space-8);
  align-items: center;
">
  <div style="display: flex; flex-direction: column; gap: var(--space-5);">
    <h2 class="text-h2">Content Headline</h2>

    <p class="text-body" style="color: var(--color-text-secondary); max-width: 50vmin;">
      Your narrative content goes here. Keep it concise—1 to 2 paragraphs max.
    </p>

    <ul style="margin: 0; padding: 0; list-style: none; gap: var(--space-4); display: flex; flex-direction: column;">
      <li style="display: flex; align-items: center; gap: var(--space-3);">
        <span style="color: var(--color-purple); font-weight: 600;">✓</span>
        <span>Supporting point 1</span>
      </li>
      <li style="display: flex; align-items: center; gap: var(--space-3);">
        <span style="color: var(--color-purple); font-weight: 600;">✓</span>
        <span>Supporting point 2</span>
      </li>
    </ul>
  </div>

  <div data-image-placeholder="photo" style="
    width: 100%;
    height: 40vmin;
    border-radius: var(--radius-lg);
    background-color: var(--color-surface);
  "></div>
</div>
```

**Content Limit:** Headline + 2 paragraphs OR headline + 4 bullet points

**Source:** Deck_Dark_Page_003

---

## 3. Bullets (List)

**Purpose:** Key points with optional icons

**Layout:** Headline at top, vertical bullet list

**Variables:**
- `label` (optional section tag)
- `headline` (section title)
- `bullets` (array of 3-5 points)
- `icons` (optional, one per bullet)
- `accent_color` (for dash markers)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
">
  <div>
    <div style="display: inline-block; border: 1px solid var(--color-text);
                border-radius: var(--radius-full); padding: var(--space-1) var(--space-4);
                font-size: var(--text-caption); margin-bottom: var(--space-4);">
      Section Label
    </div>
    <h2 class="text-h2">Main Headline</h2>
  </div>

  <ul style="list-style: none; margin: 0; padding: 0; gap: var(--space-5); display: flex; flex-direction: column;">
    <li style="display: flex; align-items: flex-start; gap: var(--space-4);">
      <span style="color: var(--color-purple); font-weight: 600; flex-shrink: 0; margin-top: var(--space-1);">—</span>
      <p class="text-body" style="margin: 0;">
        First key point with optional supporting detail
      </p>
    </li>
    <li style="display: flex; align-items: flex-start; gap: var(--space-4);">
      <span style="color: var(--color-purple); font-weight: 600; flex-shrink: 0; margin-top: var(--space-1);">—</span>
      <p class="text-body" style="margin: 0;">
        Second key point
      </p>
    </li>
    <li style="display: flex; align-items: flex-start; gap: var(--space-4);">
      <span style="color: var(--color-purple); font-weight: 600; flex-shrink: 0; margin-top: var(--space-1);">—</span>
      <p class="text-body" style="margin: 0;">
        Third key point
      </p>
    </li>
  </ul>
</div>
```

**Content Limit:** Headline + 3-5 bullets

**Source:** Deck_Dark_Page_017, Page_018

---

## 4. Metrics (Stats)

**Purpose:** Key performance numbers with labels

**Layout:** Grid of large numbers with supporting text

**Variables:**
- `headline` (section title)
- `stats` (array with `value`, `label`, `accent_color`)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
">
  <h2 class="text-h2">Key Metrics</h2>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(20vmin, 1fr)); gap: var(--space-8);">
    <div style="text-align: center;">
      <div class="text-display" style="color: var(--color-purple); margin-bottom: var(--space-2);">
        2.3x
      </div>
      <p class="text-body" style="color: var(--color-text-secondary); margin: 0;">
        Growth metric
      </p>
    </div>

    <div style="text-align: center;">
      <div class="text-display" style="color: var(--color-green); margin-bottom: var(--space-2);">
        94%
      </div>
      <p class="text-body" style="color: var(--color-text-secondary); margin: 0;">
        Adoption rate
      </p>
    </div>

    <div style="text-align: center;">
      <div class="text-display" style="color: var(--color-yellow); margin-bottom: var(--space-2);">
        Q1
      </div>
      <p class="text-body" style="color: var(--color-text-secondary); margin: 0;">
        Launch timing
      </p>
    </div>
  </div>
</div>
```

**Content Limit:** Headline + 3-4 stat blocks

**Source:** Deck_Dark_Page_037, Page_038

---

## 5. Two-Column (Side-by-Side)

**Purpose:** Comparison or detailed layout with distinct left/right sections

**Layout:** Left text column + right dark card panel

**Variables:**
- `mini_label` (optional top-left tag)
- `headline` (left side)
- `left_content` (bullets or text)
- `right_content` (text, bullets, or visual)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-9);
  position: relative;
">
  <div style="position: absolute; top: var(--space-6); left: var(--space-6);">
    <div style="display: inline-block; border: 1px solid var(--color-text);
                border-radius: var(--radius-full); padding: var(--space-1) var(--space-3);
                font-size: var(--text-body-sm); font-weight: var(--weight-regular);">
      Mini Label
    </div>
  </div>

  <div style="margin-top: var(--space-10);">
    <h2 class="text-h2">Left Column Headline</h2>
    <!-- Left content (bullets, text, etc.) -->
  </div>

  <div style="background-color: var(--color-surface); border-radius: var(--radius-lg);
              padding: var(--space-8); height: 100%; box-sizing: border-box; margin-top: 0;">
    <h3 class="text-h3" style="margin-bottom: var(--space-5);">Right Panel Title</h3>
    <!-- Right panel content -->
  </div>
</div>
```

**Content Limit:** Headline + 3-4 bullets per side

**Source:** Deck_Dark_Page_034, Page_035

---

## 6. Feature Grid (2x2)

**Purpose:** Cards highlighting features, benefits, or categories

**Layout:** 2x2 card grid with icons, titles, descriptions

**Variables:**
- `headline` (section title)
- `cards` (array with `icon`, `title`, `description`, `accent_color`)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
">
  <h2 class="text-h2">Feature Overview</h2>

  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-6);">
    <div style="background-color: var(--color-surface); border-radius: var(--radius-md); padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-4);">
      <div style="width: 5vmin; height: 5vmin; border-radius: 50%; border: 1px solid var(--color-text); display: flex; justify-content: center; align-items: center;">
        🎯
      </div>
      <h4 class="text-h4">Feature Name</h4>
      <p class="text-body-sm" style="color: var(--color-text-secondary); margin: 0;">
        Short description of the feature benefit
      </p>
    </div>

    <!-- Repeat for 3 more cards -->
    <div style="background-color: var(--color-surface); border-radius: var(--radius-md); padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-4);">
      <div style="width: 5vmin; height: 5vmin; border-radius: 50%; border: 1px solid var(--color-text); display: flex; justify-content: center; align-items: center;">
        🚀
      </div>
      <h4 class="text-h4">Feature Name</h4>
      <p class="text-body-sm" style="color: var(--color-text-secondary); margin: 0;">
        Short description of the feature benefit
      </p>
    </div>
  </div>
</div>
```

**Content Limit:** Headline + 4 cards max (2x2)

**Source:** Deck_Dark_Page_044, Page_045

---

## 7. Quote (Pull Quote)

**Purpose:** Testimonial, insight, or emphasis statement

**Layout:** Centered, large text with optional attribution

**Variables:**
- `quote_text` (large, centered)
- `attribution` (optional, smaller)
- `accent_color` (optional, for quote mark or bar)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: var(--space-6);
">
  <div style="font-size: 4.5vmin; color: var(--color-purple); opacity: 0.3; line-height: 1;">
    "
  </div>

  <blockquote style="
    margin: 0;
    font-size: var(--text-h2);
    font-weight: var(--weight-light);
    max-width: 60vmin;
    line-height: var(--leading-normal);
  ">
    Your quote text goes here. This is perfect for testimonials, key insights, or memorable statements.
  </blockquote>

  <div style="color: var(--color-text-secondary); font-size: var(--text-h4);">
    — Attribution Name, Title
  </div>
</div>
```

**Content Limit:** Quote (2-3 sentences) + optional attribution

**Source:** Deck_Dark_Page_021, Page_023

---

## 8. Table (Data)

**Purpose:** Structured data presentation

**Layout:** Styled table with headers and rows

**Variables:**
- `headline` (optional section title)
- `columns` (column names)
- `rows` (array of row data)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
">
  <h2 class="text-h2">Data Table</h2>

  <table style="
    width: 100%;
    border-collapse: collapse;
    font-size: var(--text-body);
  ">
    <thead>
      <tr style="border-bottom: 1px solid var(--color-border-strong);">
        <th style="text-align: left; padding: var(--space-4); color: var(--color-text-secondary); font-weight: var(--weight-regular);">
          Column 1
        </th>
        <th style="text-align: left; padding: var(--space-4); color: var(--color-text-secondary); font-weight: var(--weight-regular);">
          Column 2
        </th>
        <th style="text-align: left; padding: var(--space-4); color: var(--color-text-secondary); font-weight: var(--weight-regular);">
          Status
        </th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid var(--color-border);">
        <td style="padding: var(--space-4);">Item A</td>
        <td style="padding: var(--space-4);">Value</td>
        <td style="padding: var(--space-4);"><span style="color: var(--color-green);">✓ Done</span></td>
      </tr>
      <tr style="border-bottom: 1px solid var(--color-border);">
        <td style="padding: var(--space-4);">Item B</td>
        <td style="padding: var(--space-4);">Value</td>
        <td style="padding: var(--space-4);"><span style="color: var(--color-yellow);">⚠ In Progress</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

**Content Limit:** Headline + 6-7 rows max

**Source:** Deck_Dark_Page_050+

---

## 9. Team (Portraits)

**Purpose:** Team members with headshots, names, roles

**Layout:** Portrait cards in grid

**Variables:**
- `headline` (section title, optional)
- `team_members` (array with `name`, `role`, `image_src`)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
">
  <h2 class="text-h2">Meet the Team</h2>

  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-6);">
    <div style="text-align: center;">
      <div data-image-placeholder="portrait" style="
        width: 12vmin; height: 12vmin; border-radius: 50%;
        background-color: var(--color-surface); margin: 0 auto var(--space-4) auto;
      "></div>
      <h4 class="text-h4" style="margin: 0 0 var(--space-1) 0;">Name</h4>
      <p class="text-caption" style="color: var(--color-text-secondary); margin: 0;">Role or Title</p>
    </div>

    <!-- Repeat for more team members -->
  </div>
</div>
```

**Content Limit:** Headline + 4-6 team members

**Source:** Deck_Dark_Page_057+

---

## 10. Comparison (Side-by-Side)

**Purpose:** Before/After, Option A vs B, or contrast layout

**Layout:** Two-column comparison with headers and bullets

**Variables:**
- `headline` (section title)
- `left_title`, `left_items` (bullets)
- `right_title`, `right_items` (bullets)
- `accent_color` (for emphasis)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-8);
">
  <div style="display: flex; flex-direction: column; gap: var(--space-5);">
    <h3 class="text-h3" style="color: var(--color-text-secondary);">Option A</h3>
    <ul style="list-style: none; margin: 0; padding: 0; gap: var(--space-3); display: flex; flex-direction: column;">
      <li style="display: flex; align-items: flex-start; gap: var(--space-2);">
        <span style="color: var(--color-red); font-weight: 600; flex-shrink: 0;">✗</span>
        <p class="text-body" style="margin: 0;">Point 1</p>
      </li>
      <li style="display: flex; align-items: flex-start; gap: var(--space-2);">
        <span style="color: var(--color-red); font-weight: 600; flex-shrink: 0;">✗</span>
        <p class="text-body" style="margin: 0;">Point 2</p>
      </li>
    </ul>
  </div>

  <div style="display: flex; flex-direction: column; gap: var(--space-5); background-color: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-8);">
    <h3 class="text-h3" style="color: var(--color-green);">Option B</h3>
    <ul style="list-style: none; margin: 0; padding: 0; gap: var(--space-3); display: flex; flex-direction: column;">
      <li style="display: flex; align-items: flex-start; gap: var(--space-2);">
        <span style="color: var(--color-green); font-weight: 600; flex-shrink: 0;">✓</span>
        <p class="text-body" style="margin: 0;">Benefit 1</p>
      </li>
      <li style="display: flex; align-items: flex-start; gap: var(--space-2);">
        <span style="color: var(--color-green); font-weight: 600; flex-shrink: 0;">✓</span>
        <p class="text-body" style="margin: 0;">Benefit 2</p>
      </li>
    </ul>
  </div>
</div>
```

**Content Limit:** Title + 3-4 points per side

**Source:** Deck_Dark_Page_046+

---

## 11. Full-Bleed Image

**Purpose:** Background image with overlay text

**Layout:** Full-width/height image with text overlay

**Variables:**
- `image_src` or `background_image_url`
- `headline` (overlaid text, large and bold)
- `subtext` (optional, smaller overlay)
- `overlay_opacity` (default 0.4)

**HTML Pattern:**

```html
<div class="slide-container" style="
  background-image: url('image.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
">
  <div style="
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 1;
  "></div>

  <div style="position: relative; z-index: 2; max-width: 60vmin;">
    <h1 class="text-display" style="color: var(--color-text); margin-bottom: var(--space-4);">
      Headline Text
    </h1>
    <p class="text-h3" style="color: var(--color-text-secondary);">
      Optional subheading or description
    </p>
  </div>
</div>
```

**Content Limit:** Headline + optional subheading

**Source:** Deck_Dark_Page_065+

---

## 12. Section Divider

**Purpose:** Section break or transition slide

**Layout:** Large number/label with minimal content

**Variables:**
- `number` (section number, large)
- `label` (section name)
- `optional_subtext` (brief description)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding-left: var(--space-9);
">
  <div style="font-size: 15vmin; font-weight: var(--weight-light); color: var(--color-purple); opacity: 0.3; line-height: 0.9;">
    02
  </div>

  <h2 class="text-h2" style="margin-top: var(--space-3); margin-bottom: var(--space-4);">
    Section Name
  </h2>

  <p class="text-body" style="color: var(--color-text-secondary); max-width: 40vmin;">
    Optional brief description of what's coming up in this section
  </p>
</div>
```

**Content Limit:** Number + label + optional 1-line description

**Source:** Deck_Dark_Page_009, Page_010

---

## 13. Steps (Timeline/Process)

**Purpose:** Numbered action items, roadmap, or sequential process

**Layout:** Vertical timeline with numbered items

**Variables:**
- `headline` (section title)
- `steps` (array with `number`, `title`, `description`)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
">
  <h2 class="text-h2">Implementation Timeline</h2>

  <div style="display: flex; flex-direction: column; gap: var(--space-6);">
    <div style="display: flex; gap: var(--space-6); align-items: flex-start;">
      <div style="
        width: 4vmin; height: 4vmin; border-radius: 50%;
        background-color: var(--color-purple); color: var(--color-bg);
        display: flex; justify-content: center; align-items: center;
        font-weight: var(--weight-semibold); flex-shrink: 0;
      ">1</div>
      <div>
        <h4 class="text-h4" style="margin: 0 0 var(--space-2) 0;">Step One</h4>
        <p class="text-body" style="color: var(--color-text-secondary); margin: 0;">
          Description of first step
        </p>
      </div>
    </div>

    <div style="display: flex; gap: var(--space-6); align-items: flex-start;">
      <div style="
        width: 4vmin; height: 4vmin; border-radius: 50%;
        background-color: var(--color-green); color: var(--color-bg);
        display: flex; justify-content: center; align-items: center;
        font-weight: var(--weight-semibold); flex-shrink: 0;
      ">2</div>
      <div>
        <h4 class="text-h4" style="margin: 0 0 var(--space-2) 0;">Step Two</h4>
        <p class="text-body" style="color: var(--color-text-secondary); margin: 0;">
          Description of second step
        </p>
      </div>
    </div>
  </div>
</div>
```

**Content Limit:** Headline + 3-5 steps

**Source:** Deck_Dark_Page_030+

---

## 14. Closing Slide

**Purpose:** End slide with call-to-action and logo

**Layout:** Centered headline, subtext, and logo

**Variables:**
- `headline` (main closing message)
- `subtext` (contact, email, or CTA)
- `cta_button` (optional, link/action)

**HTML Pattern:**

```html
<div class="slide-container" style="
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: var(--space-8);
">
  <div>
    <h1 class="text-h1">Thank You</h1>
    <p class="text-h3" style="color: var(--color-text-secondary); margin: var(--space-5) 0 0 0;">
      Questions? Let's chat.
    </p>
  </div>

  <div style="
    border: 1px solid var(--color-border-strong);
    border-radius: var(--radius-full);
    padding: var(--space-3) var(--space-6);
    font-size: var(--text-body);
    color: var(--color-purple);
  ">
    your.email@monday.com
  </div>

  <div style="position: absolute; bottom: var(--space-8);">
    <!-- monday.com logo -->
    <svg width="120" height="auto" viewBox="..."><!-- logo SVG --></svg>
  </div>
</div>
```

**Content Limit:** Headline + subtext/email + logo

**Source:** Deck_Dark_Page_099, Page_100

---

## Customization Tips

- **Accent Colors:** Replace `var(--color-purple)` with `var(--color-green)`, `var(--color-yellow)`, or `var(--color-red)`
- **Spacing:** Use `var(--space-N)` (1-10) consistently
- **Icons:** Reference from `Icons/Property 1=Name.svg` with size class `.ds-icon-lg`, `.ds-icon-sm`, etc.
- **Typography:** Use only `.text-h1` through `.text-caption` classes
- **Images:** Use `data-image-placeholder="type"` (photo, portrait, screenshot, icon) as a fallback

