/* story.js — EVERYTHING that changes between explainers lives in this file (theme, copy, object positions).
   This is a worked EXAMPLE ("How our bakery works") mapped onto the placeholder assets/hero.svg.
   For a new explainer: replace the image, then re-map every `cam`, `spot` and `fx` number (tools/map-objects.html helps) and rewrite the copy.
   Coordinates: fractions (0..1) for cam.f / cam.a, percentages (0..100) of the image for spot and fx. */

const THEME = {
  lang: 'en', dir: 'ltr',                      // Hebrew: lang 'he', dir 'rtl' (see story.he.example.js)
  title: 'How our bakery works',
  image: 'assets/hero.svg',                    // 3:2 image; the engine crops and zooms it
  alt: 'A bakery counter: a chalkboard menu, the baker in a white hat, a recipe book, an oven timer, a service bell with a sign.',
  fonts: {
    href: 'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap',
    serif: "'Fraunces',Georgia,serif",
    sans: "'Inter',-apple-system,'Segoe UI',sans-serif"
  },
  tokens: {                                    // CSS variables; swap these to re-skin the UI around the image
    '--accent': '#0081c0', '--highlight': '#e9b44c', '--wall': '#f4f1e6', '--ink': '#171717'
  },
  ui: {                                        // every fixed UI string, so a translation is one object
    step: 'Step', todo: 'Do this to copy it', why: 'Why you want it: ', next: 'Next',
    copyDone: 'Copied ✅', copyBlocked: 'Copy blocked in this view',
    revealHint: 'Drag the line, click anywhere, or use ← → keys.', demo: '(Demo data)', goTo: 'Go to ', start: 'Start'
  }
};

const STORY = {
  hero: {
    title: 'Meet our bakery',
    subtitle: 'Fresh bread by six, orders on time, and nobody guessing what is in the oven.',
    cta: 'How it works ↓'
  },

  chapters: [
    {
      key: 'baker', nav: '1 Baker', title: 'The baker',
      body: ['The baker is the one person every order passes through. They know the recipes, the regulars and what is in the oven right now.'],
      why: 'one friendly person to ask, instead of five.',
      tip: 'Tip: write the baker’s rules on one page and keep them short. Link to the real source, e.g. [the shop handbook](https://example.com/handbook).',
      blocks: [{ type: 'buttons', items: [{ label: 'Open the handbook ↗', href: 'https://example.com/handbook', primary: true }, { label: '📋 Copy the starter rules', copy: 'You are the baker.\nBake what the orders say.\nIf you are not sure, ask. Never guess.' }] }],
      todo: ['Pick one person to own the counter.', 'Write their rules on one page.', 'Tell everyone how to reach them.'],
      refs: [['Shop handbook', 'https://example.com/handbook']],
      cam: { f: [.50, .40], s: 1.25, a: [.72, .45], side: 'left' },
      spot: [50, 14, 'Baker'],
      bubble: { at: [60, 8], text: 'Morning! 3 orders came in overnight. Say yes and I start the dough.' },
      fx: [['ring', 50, 32, 22, 'rgba(255,206,110,.95)', 0, 3600, { b: .5, s0: .5, s1: 2.8 }], ['ring', 50, 32, 22, 'rgba(255,206,110,.95)', 1200, 3600, { b: .5, s0: .5, s1: 2.8 }], ['ring', 50, 32, 22, 'rgba(255,206,110,.95)', 2400, 3600, { b: .5, s0: .5, s1: 2.8 }]]
    },
    {
      key: 'book', nav: '2 Recipe book', title: 'The recipe book',
      body: ['The recipe book holds everything the bakery knows:'],
      blocks: [{ type: 'chips', items: [['📝', 'Recipes'], ['📁', 'Supplier notes'], ['💬', 'Customer messages'], ['📋', 'The order sheet']] }],
      after: 'The baker checks it before answering anyone.',
      why: 'answers come from what the shop really knows, and say where they came from.',
      todo: ['Start one book.', 'Add recipes and notes as you go.', 'Ask a question and check the page it cites.'],
      refs: [['Recipe index', 'https://example.com/recipes']],
      cam: { f: [.23, .81], s: 1.05, a: [.28, .75], side: 'right' },
      spot: [23, 66.5, 'Recipe book'],
      fx: [['spark', 10, 80, 0], ['spark', 17, 75.5, 520], ['spark', 24, 81, 1040], ['spark', 30, 76.5, 1560], ['spark', 14, 83, 2080]]
    },
    {
      key: 'board', nav: '3 Menu board', title: 'The menu board',
      body: ['Each line on the board is a job card: step-by-step instructions for one product.', 'New cards are added by sending a short note to the shop owner.'],
      blocks: [{ type: 'grid', items: [['sourdough', 'Feed the starter, shape, 12h proof'], ['croissant', 'Fold the butter three times'], ['rye-loaf', 'Slow bake, steam first'], ['special-of-the-day', 'Whatever the baker feels like']], more: ['focaccia', 'bagels', 'brioche'], moreLabel: '+3 more', hideLabel: 'Hide' }],
      tip: 'Tip: add your specialty to the board.',
      todo: ['Write one card.', 'Pin it to the board.', 'Ask the baker to use it.'],
      refs: [['The menu', 'https://example.com/menu']],
      cam: { f: [.20, .25], s: 1.05, a: [.20, .40], side: 'right' },
      spot: [20.6, 43, 'Menu board'],
      fx: [['ring', 6, 12, 4.5, 'rgba(255,200,80,.95)', 0, 2600, { b: .35, s0: .4, s1: 2.6 }], ['ring', 34, 12, 4.5, 'rgba(255,200,80,.95)', 650, 2600, { b: .35, s0: .4, s1: 2.6 }], ['ring', 6, 36, 4.5, 'rgba(255,200,80,.95)', 1300, 2600, { b: .35, s0: .4, s1: 2.6 }]]
    },
    {
      key: 'timer', nav: '4 Oven timer', title: 'The oven timer',
      body: ['The timer is an alarm clock: at a set time the oven wakes up and runs a bake on its own. A person still checks every tray before it is sold.'],
      blocks: [{ type: 'rows', items: [['04:30', 'First bake', 'Bread for the morning rush.'], ['09:00', 'Pastries', 'Croissants, ready for coffee.'], ['13:00', 'Restock', 'One tray, counted and logged.']], note: 'Times are local.' }],
      why: 'the boring daily work is done before the doors open.',
      todo: ['Pick one small, safe job.', 'Set the timer.', 'Keep a person’s yes before anything is sold.'],
      refs: [['Bake schedule', 'https://example.com/schedule']],
      cam: { f: [.84, .50], s: 1.10, a: [.72, .50], side: 'left' },
      spot: [84.3, 33, 'Oven timer'],
      fx: [['ring', 84.3, 52.7, 7.5, '#0081c0', 0, 1700, { b: .22, s0: .5, s1: 1.9, o: .7 }]]
    },
    {
      key: 'bell', kind: 'reveal', nav: '5 Counter bell', title: 'The counter bell',
      body: ['Ring the bell and someone answers. The sign says who to ask, so questions never wait on one person.', 'The baker also calls the supplier when stock is the question, and brings back a concrete answer.'],
      why: 'customers get answers about what is really on the shelf, without waiting.',
      blocks: [{ type: 'note', text: 'Keep scrolling: before vs after ↓' }],
      todo: ['Put a bell and a sign at the counter.', 'Let anyone ring it.', 'Rule: the baker proposes, a person confirms.'],
      refs: [['Counter rules', 'https://example.com/counter']],
      cam: { f: [.85, .80], s: 1.05, a: [.72, .70], side: 'left' },
      spot: [79, 69, 'Counter bell'],
      fx: [['ring', 96.2, 81, 10, 'rgba(255,200,90,.95)', 0, 2200], ['ring', 96.2, 81, 10, 'rgba(255,200,90,.95)', 1100, 2200]],
      reveal: {
        kicker: 'Counter, side by side', heading: 'Before the bell, or after.',
        buttons: ['Before', 'After'],
        before: { src: 'assets/reveal-before.svg', tag: 'Before', alt: 'Before: orders pile up on a note and someone has to read it first.' },
        after: { src: 'assets/reveal-after.svg', tag: 'After', alt: 'After: orders flow straight to the oven.' },
        cols: [['Before.', 'Orders pile up on a note until someone has time to read it.'], ['After.', 'The baker answers right away from the recipe book and the order sheet, and calls the supplier when needed. If something is missing, it proposes an order and a person confirms.']],
        demo: true
      }
    },
    {
      key: 'next', nav: 'Next (WIP)', title: 'Orders, planned by the shop', numbered: false, badge: 'WIP', label: 'Next',
      body: ['We are building a flow where a new order is read, planned and sent to the oven without anyone re-typing it.'],
      blocks: [{ type: 'pipeline', items: [['📥', 'Order lands at the counter'], ['🧩', 'The baker plans the bake'], ['🔥', 'The oven starts on time'], ['🚚', 'Delivery is scheduled']] }],
      cam: { f: [.88, .80], s: 1.05, a: [.72, .70], side: 'left' }
    }
  ],

  finale: {
    title: 'Your first 3 moves',
    items: [
      ['Hire the baker', 'and give them one page of rules.'],
      ['Start the recipe book:', 'drop in one note. [See the book](https://example.com/recipes).'],
      ['Pin one card:', 'one product, step by step.']
    ],
    links: [['Shop handbook', 'https://example.com/handbook'], ['Menu', 'https://example.com/menu']],
    cam: { f: [.50, .50], s: 1.00, a: [.50, .50], side: 'left' }
  }
};
