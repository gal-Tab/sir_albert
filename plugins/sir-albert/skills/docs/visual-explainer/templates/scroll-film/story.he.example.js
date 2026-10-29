/* story.he.example.js — the same bakery example in Hebrew, to show what RTL needs.
   To use it: copy this file's THEME and STORY over story.js (story.js stays the only file you edit), then delete this example from your project.
   To just look at it: temporarily point <script src="story.js"> in index.html at this file.
   RTL checklist (all handled by engine.js + index.html once THEME.dir is 'rtl'):
   - lang 'he' + dir 'rtl' on <html>, a Hebrew-capable font pair, no letter-spacing or forced caps
   - cards stay on the side opposite their object (the image is NOT mirrored), only the text inside flips
   - the before/after slider measures from the right edge, so "before" sits on the right and the arrows move the handle the way they point
   - keep English product names and numbers as they are; the browser's bidi handles them inside a Hebrew sentence */

const THEME = {
  lang: 'he', dir: 'rtl',
  title: 'איך המאפייה שלנו עובדת',
  image: 'assets/hero.svg',
  alt: 'דוכן מאפייה: לוח תפריט, אופה בכובע לבן, ספר מתכונים, טיימר תנור ופעמון שירות עם שלט.',
  fonts: {
    href: 'https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;700&family=Heebo:wght@400;500;600&display=swap',
    serif: "'Frank Ruhl Libre',Georgia,serif",
    sans: "'Heebo',-apple-system,'Segoe UI',sans-serif"
  },
  tokens: { '--accent': '#0081c0', '--highlight': '#e9b44c', '--wall': '#f4f1e6', '--ink': '#171717' },
  ui: {
    step: 'שלב', todo: 'כך עושים את זה', why: 'למה זה שווה: ', next: 'הבא',
    tbd: 'קישור יתווסף', tbdTitle: 'הקישור עדיין לא זמין', copyDone: 'הועתק ✅', copyBlocked: 'ההעתקה חסומה בתצוגה הזו',
    revealHint: 'גררו את הקו, לחצו בכל מקום, או השתמשו במקשי ← →.', demo: '(נתוני דמו)', goTo: 'מעבר אל ', start: 'התחלה'
  }
};

const STORY = {
  hero: {
    title: 'הכירו את המאפייה שלנו',
    subtitle: 'לחם טרי עד שש, הזמנות בזמן, ואף אחד לא מנחש מה יש בתנור.',
    cta: 'איך זה עובד ↓'
  },

  chapters: [
    {
      key: 'baker', nav: '1 האופה', title: 'האופה',
      body: ['האופה הוא האדם שכל הזמנה עוברת דרכו. הוא מכיר את המתכונים, את הלקוחות הקבועים ואת מה שיש עכשיו בתנור.'],
      why: 'אדם ידידותי אחד לשאול, במקום חמישה.',
      tip: 'טיפ: כתבו את הכללים של האופה בעמוד אחד קצר, וקשרו למקור האמיתי, למשל [חוברת המאפייה](https://example.com/handbook).',
      blocks: [{ type: 'buttons', items: [{ label: 'פתחו את החוברת ↗', href: 'https://example.com/handbook', primary: true }, { label: '📋 העתיקו כללים להתחלה', copy: 'You are the baker.\nBake what the orders say.\nIf you are not sure, ask. Never guess.' }] }],
      todo: ['בחרו אדם אחד שאחראי על הדלפק.', 'כתבו את הכללים שלו בעמוד אחד.', 'ספרו לכולם איך מגיעים אליו.'],
      refs: [['חוברת המאפייה', 'https://example.com/handbook']],
      cam: { f: [.50, .40], s: 1.25, a: [.72, .45], side: 'left' },
      spot: [50, 14, 'האופה'],
      box: [41.7, 16.6, 58.3, 67.4],   // percent of the image: x0, y0, x1, y1 (tools/check-camera.js reads it)
      bubble: { at: [60, 8], text: 'בוקר טוב! נכנסו 3 הזמנות בלילה. תגידו כן ואני מתחיל בבצק.' },
      fx: [['ring', 50, 32, 22, 'rgba(255,206,110,.95)', 0, 3600, { b: .5, s0: .5, s1: 2.8 }], ['ring', 50, 32, 22, 'rgba(255,206,110,.95)', 1200, 3600, { b: .5, s0: .5, s1: 2.8 }], ['ring', 50, 32, 22, 'rgba(255,206,110,.95)', 2400, 3600, { b: .5, s0: .5, s1: 2.8 }]]
    },
    {
      key: 'book', nav: '2 ספר המתכונים', title: 'ספר המתכונים',
      body: ['בספר המתכונים נמצא כל מה שהמאפייה יודעת:'],
      blocks: [{ type: 'chips', items: [['📝', 'מתכונים'], ['📁', 'הערות ספקים'], ['💬', 'הודעות מלקוחות'], ['📋', 'גיליון ההזמנות']] }],
      after: 'האופה בודק בו לפני שהוא עונה לכל אחד.',
      why: 'התשובות מגיעות ממה שהחנות באמת יודעת, ומציינות מאיפה.',
      todo: ['פתחו ספר אחד.', 'הוסיפו מתכונים והערות תוך כדי עבודה.', 'שאלו שאלה ובדקו את העמוד שהתשובה מצטטת.'],
      refs: [['אינדקס המתכונים', 'https://example.com/recipes']],
      cam: { f: [.23, .81], s: 1.05, a: [.28, .75], side: 'right' },
      spot: [23, 66.5, 'ספר המתכונים'],
      box: [4.6, 68.4, 41.0, 92.8],   // percent of the image: x0, y0, x1, y1 (tools/check-camera.js reads it)
      fx: [['spark', 10, 80, 0], ['spark', 17, 75.5, 520], ['spark', 24, 81, 1040], ['spark', 30, 76.5, 1560], ['spark', 14, 83, 2080]]
    },
    {
      key: 'board', nav: '3 לוח התפריט', title: 'לוח התפריט',
      body: ['כל שורה בלוח היא כרטיס עבודה: הוראות צעד אחר צעד למוצר אחד.', 'כרטיסים חדשים מתווספים בהודעה קצרה לבעלי המקום.'],
      blocks: [{ type: 'grid', items: [['sourdough', 'מאכילים את המחמצת, מעצבים, 12 שעות התפחה'], ['croissant', 'מקפלים את החמאה שלוש פעמים'], ['rye-loaf', 'אפייה איטית, קודם אדים'], ['special-of-the-day', 'מה שהאופה מרגיש']], more: ['focaccia', 'bagels', 'brioche'], moreLabel: '+3 נוספים', hideLabel: 'הסתירו' }],
      tip: 'טיפ: הוסיפו ללוח את המומחיות שלכם.',
      todo: ['כתבו כרטיס אחד.', 'תלו אותו על הלוח.', 'בקשו מהאופה להשתמש בו.'],
      refs: [['התפריט', 'https://example.com/menu']],
      cam: { f: [.20, .25], s: 1.05, a: [.20, .40], side: 'right' },
      spot: [20.6, 43, 'לוח התפריט'],
      box: [4.0, 6.1, 35.0, 40.0],   // percent of the image: x0, y0, x1, y1 (tools/check-camera.js reads it)
      fx: [['ring', 6, 12, 4.5, 'rgba(255,200,80,.95)', 0, 2600, { b: .35, s0: .4, s1: 2.6 }], ['ring', 34, 12, 4.5, 'rgba(255,200,80,.95)', 650, 2600, { b: .35, s0: .4, s1: 2.6 }], ['ring', 6, 36, 4.5, 'rgba(255,200,80,.95)', 1300, 2600, { b: .35, s0: .4, s1: 2.6 }]]
    },
    {
      key: 'timer', nav: '4 טיימר התנור', title: 'טיימר התנור',
      body: ['הטיימר הוא שעון מעורר: בשעה קבועה התנור מתעורר ומריץ אפייה לבד. אדם עדיין בודק כל מגש לפני שהוא נמכר.'],
      blocks: [{ type: 'rows', items: [['04:30', 'אפייה ראשונה', 'לחם לשעת הלחץ של הבוקר.'], ['09:00', 'מאפים', 'קרואסונים, מוכנים לקפה.'], ['13:00', 'חידוש מלאי', 'מגש אחד, נספר ונרשם.']], note: 'שעות לדוגמה ' + THEME.ui.demo + '.' }],
      why: 'העבודה המשעממת נעשית לפני שהדלתות נפתחות.',
      todo: ['בחרו משימה קטנה ובטוחה אחת.', 'הגדירו את הטיימר.', 'השאירו "כן" של אדם לפני שמשהו נמכר.'],
      refs: [['לוח האפייה', null]],
      cam: { f: [.84, .50], s: 1.10, a: [.72, .50], side: 'left' },
      spot: [84.3, 33, 'טיימר התנור'],
      box: [77.5, 40.0, 90.8, 64.3],   // percent of the image: x0, y0, x1, y1 (tools/check-camera.js reads it)
      fx: [['ring', 84.3, 52.7, 7.5, '#0081c0', 0, 1700, { b: .22, s0: .5, s1: 1.9, o: .7 }]]
    },
    {
      key: 'bell', kind: 'reveal', nav: '5 פעמון הדלפק', title: 'פעמון הדלפק',
      body: ['מצלצלים בפעמון ומישהו עונה. השלט אומר את מי לשאול, ככה שאף שאלה לא מחכה לאדם אחד.', 'האופה גם מתקשר לספק כשהשאלה היא על מלאי, וחוזר עם תשובה מוחשית.'],
      why: 'לקוחות מקבלים תשובות על מה שבאמת על המדף, בלי לחכות.',
      blocks: [{ type: 'note', text: 'המשיכו לגלול: לפני מול אחרי ↓' }],
      todo: ['שימו פעמון ושלט ליד הדלפק.', 'תנו לכל אחד לצלצל.', 'כלל: האופה מציע, אדם מאשר.'],
      refs: [['כללי הדלפק', 'https://example.com/counter']],
      cam: { f: [.85, .80], s: 1.05, a: [.72, .70], side: 'left' },
      spot: [79, 69, 'פעמון הדלפק'],
      box: [71.0, 70.3, 99.2, 85.9],   // percent of the image: x0, y0, x1, y1 (tools/check-camera.js reads it)
      fx: [['ring', 96.2, 81, 10, 'rgba(255,200,90,.95)', 0, 2200], ['ring', 96.2, 81, 10, 'rgba(255,200,90,.95)', 1100, 2200]],
      reveal: {
        kicker: 'הדלפק, צד לצד', heading: 'לפני הפעמון, או אחריו.',
        buttons: ['לפני', 'אחרי'],
        before: { src: 'assets/reveal-before.svg', tag: 'לפני', alt: 'לפני: הזמנות נערמות על פתק ומישהו צריך לקרוא אותו קודם.' },
        after: { src: 'assets/reveal-after.svg', tag: 'אחרי', alt: 'אחרי: ההזמנות זורמות ישר לתנור.' },
        cols: [['לפני.', 'הזמנות נערמות על פתק עד שיש למישהו זמן לקרוא אותו.'], ['אחרי.', 'האופה עונה מיד מספר המתכונים וגיליון ההזמנות, ומתקשר לספק כשצריך. אם משהו חסר, הוא מציע הזמנה ואדם מאשר.']],
        demo: true
      }
    },
    {
      key: 'next', nav: 'הבא (בעבודה)', title: 'הזמנות, מתוכננות על ידי החנות', numbered: false, badge: 'בעבודה', label: 'הבא',
      body: ['אנחנו בונים תהליך שבו הזמנה חדשה נקראת, מתוכננת ונשלחת לתנור בלי שמישהו מקליד אותה מחדש.'],
      blocks: [{ type: 'pipeline', items: [['📥', 'ההזמנה מגיעה לדלפק'], ['🧩', 'האופה מתכנן את האפייה'], ['🔥', 'התנור מתחיל בזמן'], ['🚚', 'המשלוח נקבע']] }],
      cam: { f: [.88, .80], s: 1.05, a: [.72, .70], side: 'left' }
    }
  ],

  finale: {
    title: 'שלושת הצעדים הראשונים שלכם',
    items: [
      ['גייסו אופה', 'ותנו לו עמוד אחד של כללים.'],
      ['התחילו את ספר המתכונים:', 'הוסיפו פתק אחד. [לספר](https://example.com/recipes).'],
      ['תלו כרטיס אחד:', 'מוצר אחד, צעד אחר צעד.']
    ],
    links: [['חוברת המאפייה', 'https://example.com/handbook'], ['תפריט', null]],
    cam: { f: [.50, .50], s: 1.00, a: [.50, .50], side: 'left' }
  }
};
