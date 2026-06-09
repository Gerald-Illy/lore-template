# Briefing Variant: Weekly

Target: Delivery Lead
Presented by: Lore (self-serve)
Tone: Strategic compass — what must happen this week. Run weekly (typically Monday).
Cadence: Weekly (complements /briefing leads which is the daily checklist).

---

## Load (index-driven)

1. Check `log/state/` for most recent state file (≤24h) → use as primary summary
2. Derive weekly compass from state (decisions due, escalation candidates, stalled items, deadlines this week)
3. If weekly needs more (watch-list history, trend comparison across weeks, contributions since state was written) → load additional:
   a. `knowledge/INDEX.md` — scan Key Topics for: milestones, workstreams, open decisions, dependencies, ownership, watch list
   b. Read ONLY matched knowledge files (typically: roadmap.md, workstreams.md, decisions-open.md, decisions.md, dependencies.md, team.md, watch-list.md)
   c. `log/INDEX.md` — scan Tags ([action], [decision], [risk]) and References (DEC-*, RISK-*, ACTION-*) for last 7 days
   d. Read ONLY matched daily logs + latest weekly (if exists)
   e. `knowledge/INDEX.md` — items with watch flag or trend [↑]
   f. `contributions/INDEX.md` — scan for pending signals tagged [risk] or [action]
   g. `.lore/inconsistencies.md` — open items older than 7 days
4. If no state file or >24h old → full load via steps 3a–3g

---

## Refs

- `.claude/refs/ai-inference.md` — label any AI-inferred items

---

## Relationship to /briefing leads

| Variant | Purpose | When | Focus |
|---------|---------|------|-------|
| `/briefing leads` | What do I do **today**? | Daily | Tactical — 3 actions, blockers, dependencies |
| `/briefing weekly` | What must happen **this week**? | Weekly | Strategic — decisions, escalations, watch list, deadlines |

---

## Output Template

```markdown
> **LORE** — Intelligence & Delivery Engine
> Project: {PROJECT_NAME} · Source: Lore Knowledge Graph
> Generated: [DATE] · Coverage: [X]% · Confidence: [High/Medium/Low]
> ───────────────────────────────────────────────────────────────

# {PROJECT_NAME} – Weekly Plan: [DATE] to [DATE+6]

## 1. Decisions Needed This Week

Items from decisions-open.md + log [decision] tags that have a deadline within 7 days
or are already overdue.

| # | Decision | Why this week | Workstream | Owner | Deadline | Action |
|---|----------|--------------|-----------|-------|----------|--------|
| 1 | [Title] | [if not decided by X then Y stalls] | [WS] | [name] | [date] | → /escalate [ID] |

If none: "No decisions due this week."

## 2. Escalations (overdue or worsening)

Items with trend [↑], actions overdue >7 days, or stalled >14 days.

| # | Item | Trend | Stalled since | Owner | Action |
|---|------|-------|--------------|-------|--------|
| 1 | [ID] [Title] | [↑] | [date] | [name] | → /escalate [ID] |

If none: "No escalations needed."

## 3. VP Watch List

Items from knowledge/watch-list.md — items VP will ask about. Prepare answers proactively.

| # | Item | Why VP cares | Current state | Prep needed |
|---|------|-------------|--------------|-------------|
| 1 | [Title] | [reason] | [state] | [what to prepare] |

If none: "Nothing on watch list."

## 4. Actions Due This Week

All open [action] tags with deadline within the next 7 days.

| # | Action | Owner | Due | Workstream | Status |
|---|--------|-------|-----|-----------|--------|
| 1 | [Title] | [name] | [date] | [WS] | [on track / at risk / overdue] |

If none: "No actions due this week."

## 5. Stale Inconsistencies

Open INC items older than 7 days — need resolution or snooze.

| # | INC-ID | Type | Age (days) | Action |
|---|--------|------|-----------|--------|
| 1 | INC-XXX | [type] | [N] | → /ask inconsistencies |

If none: "All inconsistencies current."

## 6. This Week's Milestones & Deadlines

Any milestone gates, external deadlines, or events within the next 14 days.

| # | Event | Date | Owner | Status |
|---|-------|------|-------|--------|
| 1 | [Title] | [date] | [name] | [ready / at risk / blocked] |

If none: "No milestones or deadlines in the next 14 days."
```

---

## Rules

- Maximum 1 page. If it takes more, you're including too much detail.
- Format: compact, one line per item, with `/command` suggestion for every actionable item.
- Every item must have an owner. If no owner: flag as "⚠ No owner — assign immediately."
- Items without deadlines: flag as "⚠ No deadline — set by end of week."
- If log data is thin (<5 days): say so, mark confidence as Low.
- Never include items that are on track with no action needed — only items that need attention.
- Sort within each section: most urgent first.
- If a section is empty: show "None" with one-line explanation — never omit the section header.
