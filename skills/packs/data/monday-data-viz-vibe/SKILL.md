---
name: monday-data-viz-vibe
description: Apply Monday.com's "Vibe" design system when generating Python (Plotly/Matplotlib), Streamlit, or Tableau visualizations. Use for charts, scorecards, and dashboards—typography (Figtree), color palettes, and data viz best practices.
---

# Monday.com Data Visualization & Vibe Design

**Branding:** Place the Monday.com logo to the **left of the dashboard title**. Use: `https://res.cloudinary.com/dpxbqzozn/image/upload/v1771335428/Monday_n3cyzp.png`

**Domain:** Cross-Domain (Data, BI, Analytics)
**Owner:** Data / Analytics Team

---

## Purpose

**When to use:** When generating Python (Plotly/Matplotlib), Streamlit, or Tableau code to visualize data. This skill ensures all charts adhere to Monday.com's strict "Vibe" design system, typography (Figtree), color palettes, and data visualization best practices.

**Example questions:**
- "Generate a Python script to visualize our funnel conversion rate."
- "Create an executive scorecard showing ARR and PoP changes."
- "Build a chart comparing sales across regions for the last 4 quarters."

---

## Chart Guide

| Chart Type | Purpose | Use When |
|---|---|---|
| `Horizontal Bar Chart` | Compare discrete numerical categories | Categorical data (sorted largest to smallest). Preferred over vertical columns for readability. **Y-axis must start from 0.** Default bar color: `#181B34`. |
| `Line Chart / Area Chart` | Show development over continuous intervals | Time series data. Limit to 3-4 lines to avoid visual clutter. **Do not start the y-axis from 0**—fit the scale to maximize view of the data. Default series color: `#181B34`. Place a dot in **`#6161FF`** on the **current period** point to distinguish it from the rest of the line. |
| `100% Stacked Bar` | Display part-to-whole relationships | Comparing proportions. **Use instead of Pie/Donut charts.** |
| `Scatter Plot` | Detect relationships/correlations | Paired numerical data. *Use Log Scale* if the spectrum is huge. |
| `Waterfall Chart` | Show cumulative effects | Financial bridges (e.g., ARR changes, positive/negative intermediate values). |
| `Funnel Alternative` | Visualize user flow by funnel stages | Instead of classic polygon funnels, use a Bar Chart (using length as a pre-attentive attribute) supplemented by a circle side-chart for percentages. |
| `KPI BAN` | Big A** Numbers for executives | Scorecards. Show total metric + context (PoP, vs Target). |

---

## Design Tokens / Formatting

### Typography

**Definition:** Monday.com uses **Figtree** exclusively to maintain brand consistency and readability.

**Calculation (Sizes & Weights):**
- **Dashboard Title:** 28px - 36px (Bold)
- **Chart Title:** 18px (Bold)
- **Body Text:** 12px (Regular)
- **Axis & Legend Titles:** 11px or 12px (Bold)
- **Axis Labels:** 10px or 11px
- **Tooltips:** `<Field Title: 11px Regular #787878>` | `<Value: 11px Bold Black>`

**Interpretation:**
- Good: Clean, readable hierarchy.
- Bad: Using default library fonts (e.g., Arial, sans-serif) or oversized axis labels.

---

### Key Colors & Palettes

| Palette Type | Meaning / Hex Codes | Common Usage |
|---|---|---|
| `Monday Primary` | `#00ca72`, `#00854d`, `#ffcc00`, `#d79700`, `#fb275d`, `#b1123b` | Main brand elements and diverse categorical data. |
| `Sales OS (Blues)` | `#012082`, `#0041c0`, `#0061ff`, `#428aff`, `#adc5ff`, `#dde7ff`, `#f2f6ff` | Sequential data or single-color intensity charts. |
| `Sequential Dark` | `#bfd2e2`, `#7e7ee5`, `#4646b3`, `#293458`, `#181b34` | Heatmaps or deep sequential data. |
| `KPI Status` | Up/Good: `#00ca72` or `#00867e`<br>Down/Bad: `#cf0636` or `#f83e69` | Period-over-Period (PoP) indicators and alerts. |
| `Background & UI` | Chart BG: `#ffffff`<br>Gridlines: `#c3c6d4` | Clean dashboard Canvas. |

### Categories / segments palette (multi-line or multi-series)

When you need to **distinguish categories or segments** (e.g. multiple lines in a line chart, series in a bar chart by region/product), use this palette. Do not use it for single-series bars where length alone encodes the value.

```
#147244  #92CA32  #C1AC42  #FCC32B  #FCA5A5  #FB6D6D  #B0324C  #FB57BB
#6D47C7  #72377D  #391C86  #234884  #1973AA  #4DC4BE  #62C5FC  #C48879
#2865D6  #9E99B8  #B5A0F5  #A1B6E3
```

Use in order; cycle back to the start if you have more than 21 categories.

### Metric units

- **MAPP** and **WAPP** are measured in **users** (count), not currency. Format as whole numbers or compact counts (e.g. 1.2M users), not $.

### Number formatting

- **Scale:** When value **≥ 1,000,000,000** → show in **B** with one decimal (e.g. 1.2B). When **≥ 1,000,000** → **M** with one decimal (e.g. 425.2M). When **> 1,000** → **K** with one decimal (e.g. 12.5K). Else show as is.
- **Thousands:** Include **thousand separator** where applicable (e.g. 1,240).
- **Currency:** When the metric is ARR, ACV, or any **money/currency**, add **$** to the left of the number (e.g. $425.2M, $12.5K).
- **Percent:** When the metric is a **percent**, show with **%** and **one decimal** (e.g. 98.2%).
- **PoP for % metrics:** When comparing metrics with **%** unit of measure, express PoP in **percent points (pp)**: (current period − previous period), then display with one decimal and "pp" (e.g. +2.3pp, −1.1pp). Do not use percentage change of a percentage.

---

## KPI & Metric Context (Required)

When generating KPIs or metrics, **never show a standalone number**. A number by itself doesn't tell a story or give any real insights. You must always provide context alongside the number, such as:

- **Period-over-Period (PoP)** comparison
- **vs. Target**
- **vs. Average**

When you calculate and show **Period-over-Period (PoP)** context, the default timeframe is **monthly**. You must strictly ensure an **apples-to-apples** comparison based on the current period status:

1. **Full/Closed Period:** If you are showing data for the last closed month, compare it to the previous full closed month (e.g., Full December vs. Full November).
2. **Partial/Month-to-Date Period:** If the current month is still ongoing (e.g., today is Jan 15th), compare the data strictly to the **exact same partial period** in the previous month (e.g., Jan 1st–15th vs. Dec 1st–15th).

**Never compare a partial month's data to a full month's data.**

**PoP and metric direction:** When calculating PoP, distinguish between **high-is-good** metrics (e.g. Net ARR, Active Users, Signups) and **high-is-bad** metrics (e.g. Lost ARR, Churn, Cancellations). Apply green/red accordingly:
- **High-is-good:** Positive PoP change → green (`#00ca72`). Negative change → red (`#cf0636`).
- **High-is-bad:** Negative PoP change (e.g. less churn) → green. Positive change (e.g. more churn) → red.

### Context & Comparison Colors

| Use Case | Hex | Notes |
|----------|-----|------|
| Current period | `#6161FF` | Use for **current period** data points (series/bars), for the **numbers in KPI cards** (the current period value), and when the chart distinguishes current vs previous period. |
| Previous period | `#736E88` | Use for the prior period in PoP (previous period series/bars). |
| Dashboard background | `#F2F5FF` | Page/canvas background. |
| KPI cards / charts background | `#FFFFFF` | Background of charts and KPI cards only. |
| Default chart color (line/bar) | `#181B34` | Default color for line charts and bar charts when **not** distinguishing current vs previous period. When you do distinguish periods, use current `#6161FF` and previous `#736E88` instead. |

---

## Dos and Don'ts

### ✅ DO
- ✅ **Maximize Data-Ink Ratio:** Remove all top and right borders. **Do not show gridlines** on charts. Keep the view clean.
- ✅ **Chart axis labels:** Show labels for the **min and max periods** on the chart (e.g. first and last date or category on the x-axis) so the time range is clear without gridlines.
- ✅ **Data freshness:** From the data you use, identify the **latest (maximum) date** available in the data and display it in the data freshness line **below the title**. Show that max date only—the most recent date in the dataset. **Always format it as `dd-mm-yyyy`** (e.g. "Data through 15-01-2026").
- ✅ **Provide Context:** Always provide context to numbers/metrics (PoP, vs Target, vs Average) where it is available. **Never show a standalone number** for KPIs or metrics—a number by itself does not tell a story or give real insights.
- ✅ **KPI BAN cards:** When showing KPI cards (BANs), try to **always show the trend** (e.g. PoP %, sparkline, or up/down indicator) to provide more context.
- ✅ **Y-axis by chart type:** **Bar charts** must always start the y-axis from 0. **Line charts** must not start from 0—fit the y-axis to the data to maximize view.
- ✅ **Period toggle (when possible):** Add a toggle so users can choose between **"Last closed"** (e.g. full last month) and **"To date"** (e.g. MTD). Show the selected dates, and label current period vs previous period accordingly (using `#6161FF` for current and `#736E88` for previous).
- ✅ **Date granularity (strict):** Only show a **date granularity** control (month / week / day / quarter) when it **actually filters or aggregates the viz** from underlying granular data. If the data is already aggregated, not granular enough, or changing the control would not change the result, **do not show this feature**—leave the view at month level. Be strict: the control must be applicable and must work.
- ✅ **Date format by context (strict):** Use these formats only: **Last closed (month)** → **`mmm-yy`** (e.g. Jan-26). **To date (month)** and **weeks** → **`mmm-dd`** with ordinal (e.g. Jan-15th). When the user selects **"To date"**, never use mmm-yy for that view—always use mmm-dd (e.g. Jan-1st, Jan-15th). For weeks always use mmm-dd.
- ✅ **Crosstabs:** When showing data in a crosstab (e.g. table with dates and metrics), use the provided colors to **highlight low and high values** (e.g. KPI Status green for high-good, red for low-good or high-bad, depending on metric direction).
- ✅ **Optimize for Personas:** If the request is for an "Executive Scorecard", use static KPI BANs. If "Exploratory", add interactive filters.

### ❌ DON'T
- ❌ **Avoid "Red" Charts:** Do not use chart types marked as "Red" in the guidelines (e.g., Pie Charts, Donut Charts, Radar Charts, Radial Bar/Column, Nightingale Rose, Sunburst, Chord Diagram, Marimekko, Stream Graph) because they force the user to put too much effort into understanding the data. Prioritize "Green" recommended charts (Bar, Line, Scatter, etc.) unless the user asks specifically for a red chart type.
- ❌ **Avoid Stacked Bar Charts:** Do not use stacked bar charts unless specifically requested by the user (as the inner segments are difficult to compare accurately).
- ❌ **NO meaningless bar colors:** Do not add colors to bars that simply reflect bar length (e.g. gradient or intensity by value). **Length is enough** to encode the value. Use a single bar color (e.g. `#181B34`) unless you need to **distinguish between categories or segments** (e.g. Region A vs Region B, or current vs previous period)—then use the categorical palette below.
- ❌ **NO Dual Axes:** Never use two different quantitative scales on the same chart (comparing apples to oranges).
- ❌ **NO Default Styling:** Never return a raw, unstyled Matplotlib/Plotly chart. Always apply the Monday Vibe colors and Figtree font.

---

## Example Use Cases

**Executive Scorecard:** "Create a KPI summary for Q3 ARR."
→ *Cursor Action:* Generate a large text KPI BAN (24px+ Figtree) showing total ARR, with a smaller sub-text showing PoP growth in `#00ca72` (Green) or `#cf0636` (Red), providing clear context.

**Time Series Trend:** "Show the flow of users by funnel stage over time."
→ *Cursor Action:* Generate an Area Chart or Sankey diagram. Apply the `Sales OS (Blues)` palette. Remove top/right borders and format the tooltip to show `Stage (gray)` and `Value (bold)`.

---

## Related Skills
- SQL Data Modeling
- Python Data Analysis (Pandas)
- Streamlit / Plotly Dashboarding
