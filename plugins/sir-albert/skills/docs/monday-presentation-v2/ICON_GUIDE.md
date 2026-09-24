# Icon Guide — 267 Monday.com Icons

Reference of all available icons for use in presentations.

## Icon Library

All icons are SVG files located in the `Icons/` folder relative to the HTML presentation file.

**File naming pattern:** `Icons/Property 1=IconName.svg`

**Example usage:**
```html
<img src="Icons/Property 1=Graph arrow up.svg" class="ds-icon ds-icon-lg">
```

---

## Available Icons by Category

### Navigation & UI
- Arrow up
- Arrow down
- Arrow left
- Arrow right
- Arrows
- Close
- Filter
- Search
- Menu
- List
- Toggle
- Toggle box

### Communication
- Bubble talk
- Megaphone
- Microphone
- Microphone mute
- Phone
- Phone ring
- Phone2
- No call
- Email
- Share

### Data & Analytics
- Graph up
- Graph arrow up
- Graph arrow down
- Stats
- Stats doc
- Desktop stats
- Bar Chart
- Chart up
- Funnel
- Scale balance
- Web meter

### Documents & Files
- Document bar
- Clipboard
- Label
- Book
- Book open
- Book open2
- No Image
- Image

### Organization & Workflow
- Organization
- Hierarchy
- Hierarchy files
- Users
- Users circle
- User
- User hand
- Point users
- Team (implied)
- Connection user
- Connection

### Status & Indicators
- Badge check
- Badge2
- Shield check
- Lock
- Unlock
- Key
- Warning
- Win
- Checkmark
- Checklist

### Objects & Items
- Calendar
- Calendar plus
- Calendar check
- Clock
- Hourglass
- Alarm
- Box
- Box2
- Shopping bag
- Shopping Cart
- Wallet
- Credit card
- Coins
- Gift
- Trophy
- Heart
- Bookmark
- Pin

### Location & Navigation
- Location
- Map
- Compass
- Sign
- Signal
- WiFi

### Time & Duration
- Clock
- Hourglass
- Alarm check
- Calendar
- Battery charge
- Loop
- Refresh
- Translate

### Media & Entertainment
- Video
- Film
- Play Button
- Camera
- Headphones (implied via audio)
- Music (implied via media)

### Business & Growth
- Rocket / Spaceship
- Mountain
- Target
- Lightbulb
- Flash
- Magic wand
- Binoculars (implied via search/magnifying)
- Magnifying
- Desktop check
- Desktop
- Desktop2
- Laptop
- Database
- Network
- Network2
- Cloud
- Desktop check

### Development & Technical
- Tool
- Gear
- Settings gear
- Code (implied)
- Flow
- Layers
- Connection
- Link
- API (via connection/integration)

### Collaboration & Team
- Collaboration
- Handshake
- Users circle
- Organization
- Connection

### Accessibility & General
- Suitcase
- Book open
- Paper plane
- Scale target
- Radar
- Molecular
- Goggles
- Thermometer
- Thumbs Up
- Thumbs Down

---

## Icon Usage

### Basic Icon Display

```html
<img src="Icons/Property 1=Graph arrow up.svg" class="ds-icon ds-icon-lg">
```

### Icon Size Classes

```css
.ds-icon-xs  /* 3vmin (24-30px) */
.ds-icon-sm  /* 5vmin (40-50px) */
.ds-icon-md  /* 7vmin (56-70px) - default */
.ds-icon-lg  /* 10vmin (80-100px) */
.ds-icon-xl  /* 15vmin (120-150px) */
```

### Icon with Text

```html
<div style="display: flex; align-items: center; gap: var(--space-3);">
  <img src="Icons/Property 1=Checkmark.svg" class="ds-icon ds-icon-sm">
  <p class="text-body">Success message</p>
</div>
```

### Icon Customization

**Change stroke color:**
```html
<img src="Icons/Property 1=Graph arrow up.svg"
     class="ds-icon ds-icon-lg"
     style="stroke: #ffffff; filter: none;">
```

**Make white (for dark backgrounds):**
```html
<img src="Icons/Property 1=Checkmark.svg"
     class="ds-icon ds-icon-lg ds-icon-white">
```

**Make dark (for light backgrounds):**
```html
<img src="Icons/Property 1=Checkmark.svg"
     class="ds-icon ds-icon-lg ds-icon-dark">
```

---

## Semantic Icon Matching

Use these icons to represent common concepts:

### Growth / Positive Metrics
- Graph arrow up
- Graph up
- Stats
- Chart up
- Arrow up
- Rocket
- Mountain

### Success / Completion
- Checkmark
- Badge check
- Shield check
- Win
- Thumbs Up
- Trophy

### Alert / Warning / Negative
- Warning
- Thumbs Down
- Arrow down (decline)
- Graph arrow down

### Information / Help
- Lightbulb
- Question (implied in various icons)
- Book open
- Information icon (if available)

### Security / Privacy
- Lock
- Unlock
- Shield check
- Key

### Communication
- Bubble talk
- Megaphone
- Email
- Share
- Microphone

### Time / Schedule
- Calendar
- Clock
- Hourglass

### People / Team
- Users
- Users circle
- User
- Organization
- Team (implied via Users)
- Collaboration

### Integration / Connection
- Connection
- Link
- Network
- Flow

### Action / Process
- Refresh
- Loop
- Arrows
- Flow
- Checklist

---

## Icon Placement Patterns

### In Bullet Lists
Small icons (sm) next to each bullet:
```html
<li style="display: flex; align-items: flex-start; gap: var(--space-3);">
  <img src="Icons/Property 1=Arrow up.svg" class="ds-icon ds-icon-sm" style="flex-shrink: 0;">
  <p>Growth metric description</p>
</li>
```

### In Card Headers
Medium icons (md) at top of cards:
```html
<div style="text-align: center; margin-bottom: var(--space-4);">
  <img src="Icons/Property 1=Stats.svg" class="ds-icon ds-icon-md">
</div>
<h4 class="text-h4">Card Title</h4>
```

### In Stat Blocks
Large icons (lg) above numbers:
```html
<div style="text-align: center;">
  <img src="Icons/Property 1=Graph arrow up.svg" class="ds-icon ds-icon-lg" style="margin-bottom: var(--space-3);">
  <div class="text-h1" style="color: var(--color-green);">2.3x</div>
  <p class="text-body">Growth metric</p>
</div>
```

### In Feature Circles
Emoji or icon inside circular border:
```html
<div style="width: 5vmin; height: 5vmin; border-radius: 50%; border: 1px solid var(--color-text);
            display: flex; justify-content: center; align-items: center;">
  <img src="Icons/Property 1=Rocket.svg" class="ds-icon ds-icon-sm">
</div>
```

---

## Icon File Reference

All icons are located at:
`Icons/Property 1=IconName.svg`

Where `IconName` is one of:

Academy, Alarm, Alarm check, Apps, Archive, Arrow Path, Arrow up, Arrows, Badge check, Badge star, Bar Chart, Bell, Book, Book open, Book open2, Bookmark, Box, Box2, Bubble talk, Calculator (implied), Calendar, Calendar check, Calendar plus, Camera, Chart up, Checkmark, Checklist, Chip, Click, Clock, Close, Cloud, Coins, Collaboration, Compass, Connection, Connection user, Credit card, Cube, Database, Desktop, Desktop2, Desktop check, Diamond, Dollar, Document bar, Edit, Email, Eye, Filter, Filter2, Flash, Flow, Folder, Funnel, Gear, Gift, Globe, Goggles, Graph arrow down, Graph arrow up, Graph up, Grid3, Handshake, Heart, Hierachy, Hirarcy files, Home, Hourglass, Image, Key, Label, Launch, Layers, Lightbulb, Link, List, Location, Lock, Log Out, Loop, Magnifying, Map, Megaphone, Microphone, Microphone mute, Minus, Molecular, Moon, Mountain, Network, Network2, No call, No Image, No ring, No video, Organization, Paper plane, Phone, Phone2, Phone ring, Pin, Plus, Point users, Puzzle, Radar, Refresh, Scale balance, Scale target, Search, Settings gear, Share, Shield check, Shopping bag, Shopping Cart, Sign, Signal, Spaceship, Speaker, Stats, Stats doc, Thermometer, Thumbs Down, Thumbs Up, Toggle, Toggle box, Tool, Translate, Trophy, Truck, Unlock, User, User hand, Users, Users circle, Video, Warning, Web meter, WiFi, Win, and others.

---

## Tips

- Always use relative paths: `Icons/Property 1=Name.svg` (not absolute URLs)
- Icons are SVG — they scale perfectly at any size
- Default stroke color matches your text color
- Use size classes consistently for visual hierarchy
- Test icon visibility in dark mode (use `ds-icon-white` if needed)

