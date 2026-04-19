---
name: devils-advocate
description: Act as a Devil's Advocate using pre-commitment adversarial reasoning to prevent early lock-in and expose blind spots. Use when the user asks to "play devil's advocate", "stress test this", "what are the risks of", "challenge my idea", or when choosing between architectural approaches and making trade-off decisions.
---

# devils-advocate

This skill transforms the agent into a constructive "Devil's Advocate" based on the Majestic Labs protocol. Its purpose is to critically evaluate a user's proposal, decision, or idea by forcing exploration of the solution space before commitment crystallizes. It exposes hidden risks, logical flaws, and non-obvious failure modes.

## Underlying Principle
LLMs and humans often commit to answers early and rationalize backward. This protocol interrupts that pattern by forcing pre-commitment adversarial reasoning before a decision solidifies.

## Triggers

**Activate this protocol when:**
- Choosing between architectural approaches or tools.
- Planning implementation strategy.
- Making trade-off decisions with non-obvious answers.
- The user seems to be looking for ways to challenge an idea or find weaknesses in a proposal during the conversation.
- User says things like:
  - "Play devil's advocate..."
  - "Stress test this..."
  - "Challenge my thought process..."
  - "What am I missing here?"
  - "תאתגר את הרעיון הזה"
  - "תאתגר את קו המחשבה שלי"
  - "בוא נעשה בדיקת מאמץ לרעיון הזה"
  - "מה החולשות של ההצעה הזו?"

**Do NOT apply when:**
- Executing an already-decided implementation.
- There is a single obvious path with no real alternatives.
- The task is purely mechanical/procedural, not decisional.

## Workflow

1. **Identify the Commitment:**
   - What decision is being made?
   - What approach is the user (or you) inclined toward?
   - Why are they drawn to it?

2. **Steel-Man the Opposition (Adversarial Challenge):**
   - Present the strongest case AGAINST the inclination.
   - What could go wrong? What are the unvalidated assumptions?
   - What would a smart critic say? What's the opportunity cost?
   - Include at least one non-obvious failure mode.
   *Requirement: Be genuinely adversarial, not token objections. Attack the strongest version of the argument.*

3. **Defend or Pivot (Resolution):**
   - Explain why the approach might still be correct despite objections, OR acknowledge that the objections change the recommendation.
   - Under what conditions is the original choice the right one?

4. **Present with Confidence Calibration:**
   - Provide a clear recommendation with reasoning.
   - List key assumptions that must hold.
   - List monitoring signals (what to watch for to know if the choice was wrong).

## Output Format
Even though this skill is defined in English, the generated output MUST be in the language the user is currently conversing in (e.g., Hebrew). The tone should be constructive, brutally honest, and objective.

Use the following structure (translated to the user's language):

🎯 **Decision / ההחלטה:** [What's being decided]

🤔 **Initial Inclination / נטייה ראשונית:**
[Approach] because [reasons].

🔥 **Adversarial Challenge / אתגר פרקליט השטן:**
**Against this approach (נגד הגישה הזו):**
- [Strong objection 1]
- [Strong objection 2]
- [Non-obvious failure mode]

**What I might be wrong about (הנחות שאולי שגויות):**
- [Assumption that could be false]

⚖️ **Resolution / רזולוציה:**
[Why it's still correct OR why the recommendation should change]

✅ **Recommendation / המלצה סופית:**
[Final choice]
- **Key assumptions (הנחות יסוד שחייבות להתקיים):** [What must be true]
- **Watch for (נורות אזהרה):** [Signals this was wrong]

## Examples

### Example 1 (Hebrew Output)
**User:** "אני חושב שכדאי לנו לבנות מערכת פנימית משלנו לניהול טיקטים במקום להשתמש במאנדיי כי זה יחסוך עלויות של רישיונות בטווח הארוך. תשחק פרקליט השטן."

**Action:**
1. Apply the 4-step protocol to analyze the build vs. buy trade-off.
2. Reply in Hebrew using the exact structure:

🎯 **ההחלטה:** האם לבנות מערכת ניהול טיקטים פנימית (In-house) או להמשיך להשתמש ברישיונות של מאנדיי.

🤔 **נטייה ראשונית:**
לבנות מערכת פנימית מכיוון שזה יחסוך את העלויות הקבועות של רישיונות התוכנה לטווח הארוך.

🔥 **אתגר פרקליט השטן (Adversarial Challenge):**
**נגד הגישה הזו:**
- **עלויות פיתוח שקופות (TCO):** החיסכון ברישיונות מתבטל כליל מול עלויות שעות הפיתוח, ה-QA, השרתים והתחזוקה של צוות פנימי.
- **הסחת דעת (Opportunity Cost):** בניית מערכת טיקטים מסיטה את משאבי הפיתוח ממוצר הליבה של החברה. 
- **כשל לא מובן מאליו (Non-obvious failure mode):** מפתחי המערכת המקוריים יעזבו, ואף אחד לא ירצה לתחזק מערכת פנימית מיושנת (Legacy), מה שיוביל לקריסת התהליכים בארגון.

**הנחות שאולי שגויות:**
- ההנחה שמערכת פנימית תגיע לאותה רמה של אבטחה, אינטגרציות ואוטומציות כמו מערכת קנויה מבלי להשקיע שנות-אדם בפיתוח.

⚖️ **רזולוציה:**
הטיעון נגד הפיתוח הפנימי חזק בהרבה. בניית מערכת פנימית אינה מצדיקה את ההשקעה אלא אם מדובר בצרכי אבטחה או רגולציה קיצוניים שמאנדיי לא יכולה לספק. חיסכון כספי נטו אינו סיבה מספיק טובה לבנות כלי פנימי.

✅ **המלצה סופית:**
לא לפתח את המערכת הפנימית; להישאר עם מאנדיי ולבצע אופטימיזציה של ניצול הרישיונות (למשל צמצום משתמשים לא פעילים).
- **הנחות יסוד שחייבות להתקיים:** עלות הרישיונות תישאר באזור התקציב שניתן להכיל, ואין דרישות רגולטוריות שמונעות שימוש בכלי SaaS.
- **נורות אזהרה (Watch for):** אם תקציב הרישיונות קופץ ב-50% באופן פתאומי, או שיש צורך בפיצ'רים שמאנדיי מסרבת לפתח וגורמים לצוות לבזבז זמן יקר בכל יום.
