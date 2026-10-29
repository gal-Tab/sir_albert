/* story.js — everything that changes between explainers (zoom-nest). Worked EXAMPLE on placeholder scenes.
   Layers are listed OUTERMOST first. Layer i (i > 0) is drawn inside a rectangle ("frame") of layer i-1.
   frame = [x, y, w, h] as fractions of the parent image. For 3:2 images keep w == h in fractions so the child keeps its 3:2 shape.
   The parent image must have a blank screen/window at exactly that rectangle (ask for it in the image prompt).
   direction: 'in' = start outside and zoom into the nested scenes; 'out' = start in the innermost scene and zoom out (Banyai's "Zoom"). */
const THEME = {
  lang: 'en', dir: 'ltr', direction: 'in',
  title: 'Zoom example',
  fonts: {
    href: 'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap',
    serif: "'Fraunces',Georgia,serif", sans: "'Inter',-apple-system,'Segoe UI',sans-serif"
  },
  tokens: { '--accent': '#0081c0', '--highlight': '#e9b44c', '--wall': '#f4f1e6', '--ink': '#171717' },
  ui: { step: 'Step', scrollHint: 'Scroll to zoom ↓' }
};

const STORY = {
  layers: [
    { image: 'assets/scene-1.svg', alt: 'A room with a TV on the wall.', hero: true, nav: 'Start',
      title: 'Start with the big picture', body: ['Every scene sits inside a screen of the one before it.'], side: 'center' },
    { image: 'assets/scene-2.svg', alt: 'The TV shows a desk with a laptop and a lamp.', frame: [.55, .18, .30, .30], nav: '1 The desk',
      title: 'Zoom into the desk', body: ['Same camera, one continuous move. The screen you were looking at becomes the whole world.'], side: 'left',
      refs: [['Motion scroll() docs', 'https://motion.dev/docs/scroll']] },
    { image: 'assets/scene-3.svg', alt: 'The laptop screen shows the detail.', frame: [.12, .30, .28, .28], nav: '2 The detail',
      title: 'And into the detail', body: ['Put one idea per scene. When the idea gets smaller, the picture gets closer.'], side: 'right' }
  ]
};
