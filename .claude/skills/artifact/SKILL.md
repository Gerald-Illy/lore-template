---
name: artifact
description: Create and manage HTML slide decks — single-file artifacts with project branding, navigation, and copy-to-clipboard. Use when the user wants to build presentation slides.
---

# Skill: /artifact

Create, update, and manage single-file HTML slide decks with project design system,
keyboard navigation, and copy-to-clipboard functionality.

---

## --help

When invoked as `/artifact --help` or `/artifact -h` — print this and stop:

```
/artifact — Create and manage HTML slide decks

Usage:
  /artifact create "Title" [description]   → New slide deck in artifacts/
  /artifact update <file> [instructions]   → Modify content in existing deck
  /artifact add-slide <file> [pos] [desc]  → Insert slide at position
  /artifact remove-slide <file> <number>   → Remove slide, fix counters

Examples:
  /artifact create "Architecture Overview" 3 slides about system architecture
  /artifact update overview-slide.html "change slide 2 title to 'Compliance Matrix'"
  /artifact add-slide kickoff-slides.html 3 "timeline of Q3 milestones"
  /artifact remove-slide kickoff-slides.html 4

Notes:
  - All decks land in artifacts/ with naming: YYYY-MM-DD-[slug]-slide(s).html
  - Single-file HTML, no external deps except CDN fonts + html2canvas
  - Slide content is freely designed — no fixed templates
  - Design tokens and navigation boilerplate are automatic
```

---

## Actions

### create

Generate a new slide deck from scratch.

**Input:** Title + content description (free text describing what each slide should show)

**Steps:**
1. Determine slide count from description (or user-specified number)
2. Generate file name: `artifacts/YYYY-MM-DD-[slug]-slide(s).html`
   - Use today's date
   - Slug: lowercase, hyphenated, from title (max 4 words)
   - Use `slide` (singular) for 1 slide, `slides` for 2+
3. Write complete HTML file with:
   - Shared boilerplate (see § Shared Infrastructure)
   - Per-slide CSS (creative, fitting the content)
   - Per-slide HTML content
   - Correct `slideIds` array and `total` count in JS
4. Show the user the file path and slide count

### update

Modify content in an existing slide deck.

**Input:** File path (or partial name) + instructions describing what to change

**Steps:**
1. Read the existing file
2. Identify which slide(s) the instructions target
3. Modify ONLY the targeted content — never touch:
   - The `<head>` boilerplate (fonts, tokens, shared CSS)
   - Navigation CSS/JS
   - Copy-button CSS/JS
   - Other slides not mentioned
4. If structural changes affect slide count → update `total` and `slideIds`
5. Write the modified file

### add-slide

Insert a new slide into an existing deck.

**Input:** File path + position (1-based) + description of the new slide

**Steps:**
1. Read the existing file
2. Create new slide HTML + CSS for the described content
3. Insert at the specified position (or append if no position given)
4. Assign slide ID: `slide-{position}` (renumber subsequent slides if needed)
5. Update in JS:
   - `total` constant
   - `slideIds` array
   - Slide counter display
6. Add copy-button group to the new slide
7. Write the modified file

### remove-slide

Remove a slide from an existing deck.

**Input:** File path + slide number (1-based)

**Steps:**
1. Read the existing file
2. Remove the slide's HTML block and its dedicated CSS
3. Update in JS:
   - `total` constant
   - `slideIds` array
   - Slide counter display
4. Write the modified file

---

## Shared Infrastructure

Every deck MUST include this exact infrastructure. This is the boilerplate that
makes slides navigable, copyable, and visually consistent.

### Design Tokens

Customize these in `.lore/config.md` under "Branding" to match your project:

```css
:root {
  --brand-primary: #6F2DA8;
  --brand-primary-dark: #4A1D6E;
  --brand-primary-light: #9B6BC6;
  --brand-success: #2AB571;
  --brand-danger: #E5484D;
  --brand-warning: #F5A623;
  --brand-dark: #1A1A2E;
  --brand-gray: #64748B;
  --brand-light: #F8FAFC;
  --brand-white: #FFFFFF;
  --brand-border: #E2E8F0;
}
```

### Font Imports

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
```

### Shared CSS, Navigation JS, Copy functionality

See the reference implementation for the full boilerplate (navigation, copy-to-clipboard via html2canvas, slide container, keyboard shortcuts). The pattern is standard across all Lore instances.

---

## File Naming Convention

```
artifacts/YYYY-MM-DD-[slug]-slide.html    (single slide)
artifacts/YYYY-MM-DD-[slug]-slides.html   (multiple slides)
```

- Date: today's date (ISO format)
- Slug: 2-4 words from title, lowercase, hyphenated

---

## Quality Rules

1. **Viewport-fitting** — every slide must fill 100vw × 100vh without scrollbars
2. **Responsive text** — use relative sizing that works at both 1080p and 4K
3. **High contrast** — text must be readable against its background (WCAG AA minimum)
4. **No external images** — use unicode emojis, CSS shapes, or inline SVG only
5. **Copy-safe** — slides must render correctly when cloned at 1200×675 (16:9) and 1200×900 (4:3)
6. **Performance** — no animations that consume CPU at rest; transitions only on interaction
7. **Semantic IDs** — slide IDs should be descriptive when possible

---

## Creative Freedom

The skill does NOT enforce templates. Each slide's content, layout, and visual style
is freely designed to match what the user describes. The constants are:

- Project design tokens as the color palette
- Inter as body font, JetBrains Mono for code/technical content
- The navigation and copy infrastructure
- Single-file HTML architecture

Everything else — grid layouts, card systems, timelines, terminal mockups,
equations, illustrations — is designed fresh per request based on the content.

---

## RAG-Light Compliance

This skill is RAG-light compliant (trivially — it is a pure generator).

### Index Read
- None (does not query knowledge/log/contributions)

### Index Write
- None (artifacts are not indexed — they are output files)
