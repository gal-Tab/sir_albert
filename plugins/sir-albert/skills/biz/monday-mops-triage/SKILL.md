---
name: monday-mops-triage
description: Automatically triage and inject text requests into the monday.com MOPs iteration board. Triggers when the user asks to add a task, open a ticket, or add an item to the MOPs iteration or queue (e.g., "Add a task for X", "Open a ticket for Y in the iteration", "Add this to the MOPs queue"). It uses the monday-com skill capabilities to find the right group and add the item with Gal as the owner and the correct status.
---

# monday-mops-triage

This skill handles spontaneous text requests to create tickets in the MOPs Iteration board (ID: 5582014840).

## Triggers

Use this skill when the user says things like:
- "Add a task for [Task Name]"
- "Open a ticket to fix the tracking issue"
- "Add this to the MOPs queue for tomorrow"
- "Put [Task] in the active iteration"

## Context

- **Board ID:** 5582014840 (🏃‍♂️ MOPs iteration)
- **Target Groups:**
  - `New items go here` (for general new requests)
  - `Iteration Queue` (if specified for the queue)
  - `Enrolled to Iteration` (if specifically asked for the active iteration)
- **Default Owner:** Gal Tabakman (ID: 80561057)

## Workflow

1. **Identify the Intent & Group:**
   - Determine the task name from the user's prompt.
   - Determine the target group based on context (default to `Iteration Queue` or `New items go here`).
2. **Execute via monday-com Skill:**
   - You do NOT need to write a new python script. You can use the `monday-com` tools or standard GraphQL API scripts you already know to create the item.
   - Create the item in board `5582014840`.
   - Assign the owner column (`task_owner`) to Gal (`{"personsAndTeams": [{"id": 80561057, "kind": "person"}]}`).
   - Set the status column (`task_status`) to match the group (e.g., "Iteration Queue").
3. **Report Back:**
   - Provide the direct link to the newly created item.
   - Ask if any additional details (effort, urgency, tags) should be added.

## Examples

### Example 1: Basic Task
**User:** "Add a task to check the new HubSpot forms to the iteration queue."
**Action:**
1. Determine task name: "Check the new HubSpot forms".
2. Group: "Iteration Queue".
3. Create the item on board 5582014840, group `new_group61559` (Iteration Queue), assign Gal, set status.
4. Reply: "I've added 'Check the new HubSpot forms' to the Iteration Queue. Here is the link: ..."

### Example 2: Detailed Ticket with Description and Urgency (Text Parsing)
**User:** "קח את ההודעה הבאה: 'יש בעיה עם המעקב אחרי קליקים על כפתור ההרשמה בדף הבית. גוגל אנליטיקס לא קולט את האירועים מאז העדכון אתמול, צריך לבדוק את הטאג ב-GTM ולתקן דחוף.' תפתח טיקט לאיטרציה הנוכחית עם כותרת ותיאור."
**Action:**
1. **Analyze Text:**
   - Extracted Title: "Fix GA4 click tracking issue on homepage signup button"
   - Extracted Description/Update: "יש בעיה עם המעקב אחרי קליקים על כפתור ההרשמה בדף הבית. גוגל אנליטיקס לא קולט את האירועים מאז העדכון אתמול, צריך לבדוק את הטאג ב-GTM ולתקן דחוף."
   - Extracted Urgency: High / Urgent (from "דחוף")
2. **Determine Group:** "Enrolled to Iteration" (because user specified "לאיטרציה הנוכחית").
3. **Execute:**
   - Create item with the generated title in group `new_group22071` (Enrolled to Iteration).
   - Set Owner to Gal (`80561057`).
   - Set Urgency column (`task_priority`) based on the keyword "דחוף".
   - Create an update on the item with the full description text.
4. **Reply:** "Created the ticket 'Fix GA4 click tracking issue...' in the Active Iteration and added the description. Marked as Urgent. Here is the link: ..."
