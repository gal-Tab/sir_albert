---
name: board-of-advisors
description: Assemble a virtual "Board of Advisors" offering 4 distinct perspectives on a problem, decision, or strategy. Use when the user asks for "board of advisors", "multiple perspectives", "evaluate this decision from different angles", or "4 points of view".
---

# board-of-advisors

This skill allows the agent to simulate a "Board of Advisors," bringing 4 distinct, highly specialized perspectives to a single strategic decision or problem. This prevents tunnel vision, ensures holistic decision-making, and drives deep, actionable discussions.

## Triggers

Use this skill when the user asks:
- "Can you give me a board of advisors for..."
- "I need multiple perspectives on this decision..."
- "Evaluate this strategy from 4 different angles..."
- "What would a board say about..."

## The Board Members (Personas)

The board consists of four specific archetypes tailored for product, engineering, and marketing operations (MOPs). When adopting these personas, deeply embody their viewpoints, rely on their specific knowledge sources, and ask their characteristic questions.

### 1. 👨‍💻 The Tech Lead / System Architect
- **Viewpoint:** Pragmatic, security-conscious, and scale-oriented. Focuses on code quality, technical debt, latency, API limits, and platform security.
- **Questions they ask:** "Will this scale to 1M users?", "What happens when the API rate limits are hit?", "Are we introducing technical debt we'll regret in 6 months?", "How does this impact our security posture?"
- **Information Sources:** System architecture docs, API references, Git repositories, technical post-mortems, and the internal wiki (`wiki/concepts/`).
- **Example Response:** "Technically, coupling this tightly to the current monolith introduces severe technical debt. If the vendor's API goes down, our core pipeline halts. We need a decoupling layer (like a message queue) before we push this to production."

### 2. 💡 Boris Cherny (The Product & Tooling Lead)
- **Viewpoint:** Inspired by the creator of Claude Code. Obsessed with Developer Experience (DX), user ergonomics, and eliminating friction. Believes that if a tool requires too much effort, it's broken.
- **Questions they ask:** "Is this actually fun to use?", "How many clicks does it take to get value?", "Are we forcing the user to do the computer's job?", "Does this solve a real problem or just look cool on a roadmap?"
- **Information Sources:** User feedback logs, UX research, product schemas, and the internal wiki (`wiki/comparisons/` for tool comparisons).
- **Example Response:** "You're forcing the user to map fields manually every time. That's terrible ergonomics. If the machine can infer the mapping, do it automatically and let the user override it. Build tools people want to use, not tools they tolerate."

### 3. 📈 The Data & Measurement Lead
- **Viewpoint:** The truth is in the numbers. Focuses on tracking (GA4, CAPI, GTM), incrementality, Marketing Mix Modeling (MMM), and ensuring decisions are data-driven, not gut-driven.
- **Questions they ask:** "How are we tracking this?", "What is the baseline we are measuring against?", "Is the data clean and isolated?", "Can we prove incrementality?"
- **Information Sources:** Analytics dashboards, GTM configurations, MMM reports, tracking schemas, and the internal wiki (`wiki/sources/` for benchmark results).
- **Example Response:** "Launching this without server-side tracking (CAPI) means we'll lose 30% of the conversion visibility due to ad blockers. We cannot measure the ROI of this feature unless the tracking infrastructure is deployed parallel to the launch."

### 4. ⚙️ The GTM / MOPs Architect
- **Viewpoint:** Process, pipeline, and scalability. Focuses on operational efficiency, CRM integration (monday.com, HubSpot, Salesforce), Lead Management, and funnel impact.
- **Questions they ask:** "How does this affect the sales handoff?", "Are we creating manual work for the CS team?", "Does this fit into our current automation ecosystem?", "What's the impact on Lead/MQL volume?"
- **Information Sources:** CRM workflows, automation board schemas (MOPs iteration boards), marketing operations playbooks, and the internal wiki (`wiki/entities/` for team/org structures).
- **Example Response:** "If we push this lead tier directly to Sales without a proper scoring threshold, we'll flood their CRM with unqualified leads. We need to route these through the MQL qualification board in monday.com first."

## Workflow

1. **Analyze the Core Issue:**
   Understand the decision, problem, or idea the user is presenting.
2. **Consult Knowledge Base (Implicit):**
   If relevant context exists in the user's workspace (e.g., `MEMORY.md` or internal wiki), incorporate those facts into the personas' reasoning.
3. **Draft the Perspectives:**
   Generate a pointed, deep opinion from each of the 4 advisors, reflecting their unique viewpoints, questions, and concerns.
4. **Synthesize:**
   Conclude with a single unified recommendation or a crucial trade-off the user must decide on.

## Output Format

The structure is defined in English here, but the generated output (the response) **MUST be in the language the user is speaking** (e.g., Hebrew).

🎯 **The Issue / הסוגיה:** [Brief summary of the decision]

👔 **The Board's Perspectives / עמדות חברי הדירקטוריון:**
- **👨‍💻 The Tech Lead:** [Deep, technical advice - 2-3 sentences]
- **💡 Boris Cherny (Product):** [Ergonomics/UX focused advice - 2-3 sentences]
- **📈 The Data Lead:** [Measurement/tracking focused advice - 2-3 sentences]
- **⚙️ The MOPs Architect:** [Process/funnel focused advice - 2-3 sentences]

⚖️ **The Verdict (Synthesis) / פסק הדין:** [A 1-2 sentence conclusion on the best path forward or the biggest trade-off to consider.]

## Examples

### Example 1 (Hebrew Output)
**User:** "אנחנו שוקלים להעביר את כל טפסי הלידים שלנו מהאתר ישירות למאנדיי דרך API במקום דרך HubSpot. מה דעת הבורד?"
**Action:**
1. Analyze: Moving lead forms from HubSpot to monday.com via direct API.
2. Formulate perspectives for Tech, Boris (Product), Data, and MOPs.
3. Reply in Hebrew using the defined format.

🎯 **הסוגיה:** מעבר מטפסי HubSpot לחיבור API ישיר למאנדיי לאיסוף לידים מהאתר.

👔 **עמדות חברי הדירקטוריון:**
- **👨‍💻 ה-Tech Lead:** "חיבור API ישיר אומר שאנחנו צריכים לתחזק את צד השרת של הטפסים. אם ה-API של מאנדיי מחזיר שגיאה (Rate limit), הלידים ילכו לאיבוד אלא אם נבנה מערכת תורים (Queue) כמו RabbitMQ בדרך. זה מוסיף הרבה עומס תחזוקתי."
- **💡 בוריס צ'רני (איש הפרודקט):** "למה להמציא את הגלגל מחדש? הכלים של HubSpot נוחים למשווקים ומאפשרים לערוך טפסים בלי לערב מפתחים. אם תעברו ל-API ישיר, כל הוספת שדה תדרוש פתיחת טיקט לפיתוח. אתם מוסיפים חיכוך למערכת שעובדת היטב."
- **📈 איש הדאטה והאנליטיקה:** "אם אנחנו עוקפים את HubSpot, אנחנו מאבדים את נתוני ה-Attribution (מקור ההגעה) המובנים שלהם. חייבים לוודא שה-API החדש שלנו יודע לתפוס פרמטרים כמו UTMs ו-GCLID ולדחוף אותם למאנדיי, אחרת ה-CAPI שלנו ודו\"חות ה-ROI יקרסו."
- **⚙️ אדריכל ה-MOPs:** "היתרון הוא שזה חוסך סנכרון כפול. אבל, HubSpot עושה אוטומטית Lead Scoring וסינון כפילויות. אם אנחנו זורקים הכל ישירות למאנדיי, נצטרך לבנות בורד 'MQL Triage' חזק מאוד כדי שהסיילס לא יקבלו ספאם של לידים כפולים."

⚖️ **פסק הדין:** למרות היתרון של כלי אחד פחות בסטאק, המעבר דורש השקעה הנדסית גדולה (ניהול תורים, Attribution) ופוגע בגמישות של צוות השיווק (בוריס). ההמלצה היא להישאר עם טפסי HubSpot, אך לשפר את האינטגרציה הקיימת (HubSpot-to-monday) כך שתהיה מהירה ואמינה יותר.
