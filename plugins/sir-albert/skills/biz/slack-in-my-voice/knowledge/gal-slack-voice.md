# Knowledge: Gal's Slack Voice

Reference for drafting Slack messages in Gal's voice. Derived from ~120 of Gal's
real messages across DMs, group DMs, and public channels (Jul 2026).

## Language
- **Hebrew** by default for internal 1:1 and group conversations.
- **English** for public / cross-team / broadcast channels and community posts.
- **Code-switching:** technical terms stay in English/Latin even inside Hebrew.
  Never translate: `mcp`, `GTM`, `sGTM`, `source`, `event`, `consent status`,
  `attribution window`, `soft signup`/`soft su`, `bb event`, `GA4`, `hightouch`/`ht`,
  `api`, `BYOA`, `floodlight`, `webhook`, tool/product names, error strings.

## Length & structure
- Very short. One line or a fragment for replies; a few short lines for substance.
- Split a longer thought across short lines, not one dense block.
- **Numbered lists** for step/answer sequences; **`•` bullets** for conditions.
- Quote errors or agent/tool output in code blocks (```).
- Point comes first. No preamble, no wrap-up, no AI filler.

## Voice & register
- Direct, pragmatic, conclusion-first on technical topics: finding, then one reason.
- Task hand-offs: `@mention` + what you want + `-> link` + "ask me if needed".
- Warm and light with people; casual, lowercase, occasionally clipped.
- Authentic imperfection: lowercase "i", minor typos — do not over-polish.
- Emoji: at most one, at the end, friendly not decorative
  (`:heart_hands:`, `:celebrate:`, `:slightly_smiling_face:`, `:sweat_smile:`,
  `:melting_face:`, `:brain:`). None on pure technical replies.
- English: bold (`*...*`) only for the key term or the bottom line.

## Anti-patterns
- Long intros, corporate hedging, restating the question.
- Over-explaining / listing every caveat.
- Translating technical terms to Hebrew.
- Emoji spam, exclamation hype, formal grammar.

## Few-shot examples

**HE — structured conditions**
```
לפי:
• מזהי היוזר שיש לו (אימייל, fbp cookie וכו')
• חלון האטריביושן להמרה (אם צפה במודעה / לחץ על מודעה וזה עדיין בחלון)
```

**HE — direct question**
```
תגיד, אתה מסתכל על איוונטים שנרשמו או המרות לקמפיינים?
```

**HE — warm one-liner**
```
תרגיש טוב נשמה :heart_hands:
```

**EN — task hand-off (team channel)**
```
@Jose I want to migrate the 'MB - DV360 *' tags from website container to sGTM container.
We should use the floodlight event tag in sGTM and maintain the tag settings.
This is part of this ticket -> <link> (no context on it regarding this task).
I want Alejandro to plan this, create a PR with the plan, then we'll share it with Gabriella.
ask me if needed
```

**EN — numbered answer / approval**
```
@Jose
1. visit = page view, so use the page_view event as trigger
2. product=crm + goal=work + description NOT team_member/freelance
3. product=service + goal=work + description NOT team_member/freelance

fix these three and then approved
```

**EN — concise problem report**
```
I have an issue where my trigger doesn't work. I've set it up on the correct board,
added the webhook, and it works for my other two agents but not for this one.
```

**EN — quoting tool/error output**
```
`403 — the current token doesn't have write permission on this board. This matches the known graveyard entry`
```

**EN — broadcast / community**
```
For all you out there working on team brains/AI brains :brain:
I've created a concept repo with my take on how to create and manage that -> <link>
```

## Self-check before showing a draft
- Correct language? Technical terms left in English?
- Point in the first line? No preamble / wrap-up / filler?
- ≤ ~5 short lines; numbered/bulleted only if structured?
- ≤1 friendly emoji (0 if purely technical)?
