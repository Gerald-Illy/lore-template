---
name: mc
description: Mission Control — in-flight delivery board with milestone tracking, capability collaboration status, and Core Team contributions.
---

# Skill: /mc

Mission Control — the in-flight delivery board.
Tracks what's flying, what's blocked, and who's contributing across milestones.

Used for:
- Daily work (what needs attention today)
- Weekly reporting (milestone status, at-risk items)
- Collaboration clarity (Core Team vs. Capability contributions)

## --help

When invoked as `/mc --help` — print this and stop:

```
/mc — Mission Control

Usage:
  /mc                             regenerate full HTML from data model
  /mc update                      regenerate (same as no args)
  /mc add [cap] [item]            add an item to a capability
  /mc note [cap] [text]           add a note/annotation to a capability
  /mc status                      show current status summary
  /mc milestone [M1|M2|M3]       show milestone-specific view

Output: artifacts/mission-control/mission-control.html
Data:   artifacts/mission-control/data.json

Examples:
  /mc
  /mc add INFRA "PROJ-42: New operator CRD" --day 0 --milestone M1 --owner Smith --contributor core
  /mc add INFRA "INFRA-100: Cache HA" --day -1 --milestone M1 --contributor cap
  /mc note PLATFORM "Auth mechanism confirmed via standard protocol"
  /mc status
  /mc milestone M1
```

---

## Data Model

The source of truth is `artifacts/mission-control/data.json`.

### Top-level structure:
```json
{
  "meta": {
    "title": "Mission Control",
    "generated": "YYYY-MM-DD",
    "milestones": {
      "M1": { "name": "First milestone", "target": "YYYY-MM-DD", "status": "active" },
      "M2": { "name": "Second milestone", "target": "YYYY-MM-DD", "status": "planned" },
      "M3": { "name": "Third milestone", "target": "YYYY-MM-DD", "status": "planned" }
    }
  },
  "capabilities": [...]
}
```

### Structure per capability:
```json
{
  "id": "infra",
  "name": "Infrastructure",
  "short": "INFRA",
  "solution": "Solution Area",
  "capEngLead": "Capability Eng Lead",
  "engLead": "Core Team Eng Lead",
  "headerClass": "hdr-infra",
  "slideType": "grid",
  "status": "active",
  "statusLabel": "Active",
  "days": {
    "-1": [ { "type": "jira", "id": "...", "title": "...", "desc": "...", "link": "...", "milestone": "M1", "owner": "...", "contributor": "core|cap|core+cap", "tags": [] } ],
    "0": [...],
    "1": [...],
    "2": [...]
  },
  "notes": []
}
```

### Item types:
- `jira` — tracked in Jira (has link)
- `daci` — DACI decision record (has link)
- `gap` — identified gap, no tracking
- `done` — completed/PoC done
- `internal` — internal task, no Jira needed
- `decided` — decision made (DEC-*) but execution pending

### Contributor dimension:
- `core` — Core Team owns and drives this
- `cap` — Capability owns and drives this
- `core+cap` — Shared ownership (both must contribute)

---

## Views (HTML Slides)

The generated HTML has multiple views:

### 1. Overview (Slide 0)
- Status matrix: capability x day, color-coded
- Expandable items on click (with Jira/DACI links)
- Navigation: click capability name → goto detail slide
- Visual distinction: Core items vs. Cap items (badge/color)

### 2. Milestone View (Slide 1)
- Per milestone (M1, M2, M3):
  - Items due: total / green / at-risk / blocked
  - Grouped by contributor (Core Team vs. Capabilities)
  - Timeline bar showing progress
- Color coding: green (on-track), amber (at-risk), red (blocked), grey (not started)

### 3. Core Team View (Slide 2)
- All items where contributor = "core" or "core+cap"
- Grouped by day (-1/0/1/2)
- Shows which capability the item relates to
- This is "our work" — what the Core Team drives

### 4. Capability Detail Slides (Slide 3+)
- One per capability (grid or swimlane)
- Shows ALL items (core + cap) but visually marks contributor
- Back-to-overview navigation
- Notes section at bottom

## Slide Order

1. Overview (status matrix)
2. Milestone Tracking (M1/M2/M3)
3. Core Team (our contributions)
4–N. Capability details (in overview table order)

---

## Generation Workflow

1. Read `artifacts/mission-control/data.json`
2. Generate Overview slide (status matrix + expandable items)
3. Generate Milestone slide (per-milestone rollup with status counts)
4. Generate Core Team slide (all core/core+cap items)
5. For each capability: generate detail slide (grid or swimlane)
6. Write to `artifacts/mission-control/mission-control.html`
7. Report: changes made, items added/modified

## Status Calculation

Per item:
- `done` type → green
- Has owner + has milestone + not blocked tag → green (on-track)
- Has milestone but no owner OR has `at-risk` tag → amber
- Has `blocked` tag OR type is `gap` with no owner → red
- No milestone → grey (unplanned)

Per capability per day:
- All items green → green
- Any amber, no red → amber
- Any red → red
- No items → grey

Per milestone:
- Count items by status across all capabilities
- Show percentage complete (done / total)

---

## Update Workflow

When user says `/mc add`:
1. Parse capability ID, item details, `--contributor` flag
2. Default contributor to `cap` if not specified
3. Add to data.json in correct day bucket
4. Regenerate HTML
5. Report what was added

When user says `/mc note`:
1. Parse capability ID
2. Add note with timestamp to capability's notes array
3. Regenerate HTML (notes appear in slide footer)

When user says `/mc milestone [M1|M2|M3]`:
1. Filter all items by that milestone
2. Show summary: total / green / amber / red / grey
3. List blocked items with owners (or "no owner")
4. List at-risk items

---

## Index Read

- `knowledge/INDEX.md` (for cross-reference)
- `artifacts/mission-control/data.json` (primary data source)

## Index Write

- No index writes (artifact, not knowledge)

## HTML Template

The HTML uses:
- Inline CSS (self-contained, no external dependencies except Google Fonts)
- Keyboard navigation (arrows, Home/End)
- Click-to-expand overview items
- Slide anchors for deep-linking
- Back-to-overview button on each slide
- Visual badges for contributor type (Core / Cap / Shared)
- Color-coded status (green/amber/red/grey)

## Regeneration

On `/mc` or `/mc update`:
- Read data.json
- Generate complete HTML
- Write to `artifacts/mission-control/mission-control.html`
- No git operations (user controls commits)

This skill is RAG-light compliant.
