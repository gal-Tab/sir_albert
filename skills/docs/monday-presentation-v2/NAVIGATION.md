# Navigation Controller — Keyboard & Click Navigation

JavaScript controller for multi-slide presentation navigation. Inline this in every generated presentation.

---

## Features

- **Keyboard Controls:** Arrow Right/Left, Space to advance
- **Click Navigation:** Slide counter click to jump to specific slide
- **Slide Counter:** Shows "Slide N of Total" in bottom-right
- **Smooth Transitions:** Fade effect between slides
- **Responsive:** Works on desktop, tablet, mobile

---

## JavaScript Code (Inline in `<script>` Tag)

**IMPORTANT:** This controller uses **class-based toggling only** — it never sets inline `style.display`. Each slide's display type (flex, grid) is defined in CSS via `.tmpl-xxx.slide-active` rules. The controller only adds/removes the `slide-active` class.

```javascript
(function() {
    let currentSlide = 0;
    let slides = [];

    function init() {
        slides = document.querySelectorAll('[data-slide-index]');
        if (slides.length === 0) return;
        showSlide(0);
        addNavigationUI();
        document.addEventListener('keydown', handleKeyDown);
        addTouchNavigation();
    }

    function showSlide(n) {
        if (n >= slides.length) currentSlide = 0;
        else if (n < 0) currentSlide = slides.length - 1;
        else currentSlide = n;

        // CLASS-BASED ONLY — never touch style.display
        slides.forEach(function(slide, index) {
            slide.classList.toggle('slide-active', index === currentSlide);
        });
        updateCounter();
    }

    function handleKeyDown(e) {
        switch (e.key) {
            case 'ArrowRight':
            case ' ':
                e.preventDefault();
                showSlide(currentSlide + 1);
                break;
            case 'ArrowLeft':
                e.preventDefault();
                showSlide(currentSlide - 1);
                break;
        }
    }

    function addNavigationUI() {
        var counter = document.createElement('div');
        counter.id = 'slide-counter';
        counter.style.cssText = 'position:fixed;bottom:3vmin;right:3vmin;font-family:Poppins,sans-serif;font-size:1.8vmin;color:#a0a0a0;cursor:pointer;user-select:none;padding:1vmin 2vmin;border-radius:999px;transition:all .2s ease;z-index:100;';
        counter.addEventListener('click', jumpToSlide);
        counter.addEventListener('mouseover', function(){ counter.style.backgroundColor='#232427'; counter.style.color='#fff'; });
        counter.addEventListener('mouseout', function(){ counter.style.backgroundColor='transparent'; counter.style.color='#a0a0a0'; });
        document.body.appendChild(counter);
    }

    function updateCounter() {
        var counter = document.getElementById('slide-counter');
        if (counter) counter.textContent = (currentSlide + 1) + ' / ' + slides.length;
    }

    function jumpToSlide() {
        var input = prompt('Enter slide number (1-' + slides.length + '):', String(currentSlide + 1));
        if (input !== null) {
            var n = parseInt(input, 10);
            if (!isNaN(n) && n >= 1 && n <= slides.length) showSlide(n - 1);
        }
    }

    function addTouchNavigation() {
        var startX = 0;
        document.addEventListener('touchstart', function(e) { startX = e.changedTouches[0].screenX; });
        document.addEventListener('touchend', function(e) {
            var diff = startX - e.changedTouches[0].screenX;
            if (Math.abs(diff) > 50) { diff > 0 ? showSlide(currentSlide + 1) : showSlide(currentSlide - 1); }
        });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
```

---

## HTML Requirements

For the navigation controller to work, every slide must have the `data-slide-index` attribute:

```html
<div class="slide-container" data-slide-index="0">
  <!-- Slide 1 content -->
</div>

<div class="slide-container" data-slide-index="1">
  <!-- Slide 2 content -->
</div>

<div class="slide-container" data-slide-index="2">
  <!-- Slide 3 content -->
</div>
```

---

## CSS Requirements

Slides must use class-based show/hide — **never inline `style.display` from JS.**

```css
/* Base: all slides hidden, absolutely centered in viewport */
.slide-container {
  width: 100vw;
  height: 56.25vw;
  max-height: 100vh;
  max-width: 177.78vh;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-sizing: border-box;
  overflow: hidden;
  padding: var(--slide-padding-y) var(--slide-padding-x);
  background-color: var(--color-bg);
}

/* Hide inactive slides via CSS — JS only toggles the class */
.slide-container:not(.slide-active) {
  display: none !important;
}

/* Each template class defines its own display type when active */
.tmpl-cover.slide-active   { display: flex; }
.tmpl-center.slide-active  { display: flex; }
.tmpl-twocol.slide-active  { display: grid; }
.tmpl-compare.slide-active { display: grid; }
.tmpl-features.slide-active { display: grid; }
.tmpl-content-img.slide-active { display: grid; }
```

**Why this matters:** When JS sets inline `style.display = 'flex'`, it overrides CSS. If a grid-based slide was shown as flex, the layout breaks. By using class-based toggling, each slide's CSS defines its correct display type and the layout is always preserved.

---

## Usage in Generated HTML

Complete integration example:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation</title>
  <style>
    /* All CSS here (design-system.css + slide-specific) */
  </style>
</head>
<body>
  <div class="slide-container" data-slide-index="0">
    <!-- Slide 1 -->
  </div>

  <div class="slide-container" data-slide-index="1">
    <!-- Slide 2 -->
  </div>

  <div class="slide-container" data-slide-index="2">
    <!-- Slide 3 -->
  </div>

  <script>
    /* Navigation controller code above */
  </script>
</body>
</html>
```

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| Right Arrow | Next slide |
| Left Arrow | Previous slide |
| Space | Next slide |
| Click counter | Jump to slide (prompt) |

---

## Mobile Controls

| Gesture | Action |
|---------|--------|
| Swipe left | Next slide |
| Swipe right | Previous slide |
| Tap counter | Jump to slide (prompt) |

---

## Customization

### Change Counter Position

```javascript
counter.style.cssText = `
  position: fixed;
  bottom: 20px;       /* Move higher or lower */
  right: 20px;        /* Or left: 20px for left side */
  /* ... rest of styles ... */
`;
```

### Change Transition Speed

```javascript
slide.style.transition = 'opacity 0.3s ease-in-out';
// Change 0.3s to 0.5s for slower fade, or 0.1s for faster
```

### Hide Counter

```javascript
if (counter) {
  counter.style.display = 'none';
}
```

### Custom Slide Format

If slides don't use `data-slide-index`, modify the selector:

```javascript
slides = document.querySelectorAll('.your-slide-class');
```

---

## Accessibility

- **Keyboard-first:** All controls work without mouse
- **ARIA labels:** Add to counter for screen readers
- **Reduced motion:** Respects `prefers-reduced-motion` media query (can be added)

**Enhanced version with reduced motion:**

```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const transitionDuration = prefersReducedMotion ? '0ms' : '300ms';
slide.style.transition = `opacity ${transitionDuration} ease-in-out`;
```

---

## Troubleshooting

### Counter doesn't appear
- Check that `[data-slide-index]` attributes exist on slides
- Verify CSS variables are defined (--space-5, --text-body-sm, etc.)
- Open browser console for errors

### Slides don't change
- Ensure `display: flex` and `flex-direction: column` on `.slide-container`
- Check that `showSlide()` is being called (look for console logs)
- Verify keyboard events are firing (listen in console)

### Swipe doesn't work
- Touch events must not be prevented elsewhere
- Test on actual mobile device, not browser emulation
- Swipe threshold is 50px — adjust in `handleSwipe()` if needed

