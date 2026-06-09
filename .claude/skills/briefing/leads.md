# Briefing Variant: Leads

Target: Delivery Lead, Stream Leads
Presented by: Lore (self-serve)
Tone: Operational. What to do today. Per workstream if filtered.

---

## Load (index-driven)

1. Check `log/state/` for most recent state file (≤24h)
2. If fresh → **use directly as output** (add Lore header + provenance footer with current timestamp)
3. If stale/missing → fall back to full synthesis:
   a. `knowledge/INDEX.md` — scan Key Topics and Answers for: milestones, workstreams, dependencies, ownership, open decisions
   b. Read ONLY matched knowledge files (typically: roadmap.md, workstreams.md, dependencies.md, team.md, decisions-open.md, decisions.md)
   c. `log/INDEX.md` — scan Signals, Tags ([action], [risk], [decision]), and Entities for last 7 days
   d. Read ONLY matched daily logs + latest weekly (if exists)
   e. `contributions/INDEX.md` — scan for pending signals tagged [risk] or [action]
   f. Read ONLY matched contribution files
   g. `.lore/inconsistencies.md` — all levels (🔴, 🟡, 🟢)

Only load `knowledge/architecture.md` if knowledge/INDEX.md Key Topics indicate a cross-solution escalation or dependency is relevant.

---

## Refs

- `.claude/refs/ai-inference.md` — label any AI-inferred items

---

## Output Template — All Workstreams

```markdown
> **LORE** — Intelligence & Delivery Engine
> Project: {PROJECT_NAME} · Source: Lore Knowledge Graph
> Generated: [DATE] · Coverage: [X]% · Confidence: [High/Medium/Low]
> ───────────────────────────────────────────────────────────────

# {PROJECT_NAME} – Delivery Briefing

## Today's Focus

[2-3 bullets: what needs attention today — blockers, overdue actions, expiring decisions.]

## Milestones

| Milestone | Date | Status | Owner | Days left | Note |
|-----------|------|--------|-------|-----------|------|
| [M] | [Date] | [🟢/🟡/🔴] | [Name] | [N] | [One sentence] |

## Workstream Status

### [Workstream 1]
- **Status:** [🟢/🟡/🔴]
- **Progress:** [What moved]
- **Blockers:** [What's stuck + since when + owner]
- **Actions due:** [Open actions with deadlines]
- **Dependencies:** [Inbound/outbound + status]
- **Stalled items:** [Items with no change in 7+ days] — suggest /escalate [ID]

### [Workstream 2]
[Same structure]

## Open Actions (by deadline)

| # | Action | Owner | Due | Status | Workstream |
|---|--------|-------|-----|--------|------------|
| 1 | [What] | [Who] | [When] | [On track/Overdue] | [WS] |

## Open Decisions

| # | Decision | Owner | Deadline | Days open | Impact |
|---|----------|-------|----------|-----------|--------|
| 1 | [What] | [Who] | [When] | [N] | [What's blocked] |

## Risks

| # | Risk | Owner | Trend | Last update | Action |
|---|------|-------|-------|-------------|--------|
| 1 | [Risk] | [Who] | [↑→↓] | [Date] | [Next step or /escalate] |

## Open Questions

- [Question] — owner: [name] — open since: [date]

## Inconsistencies

| ID | Criticality | Type | Description | Status |
|----|-------------|------|-------------|--------|
| [INC-ID] | [🔴/🟡/🟢] | [Type] | [One sentence] | [Status] |

## Stalled Items (no update 7+ days)

- [Item] — last update: [date] — owner: [name] — suggest /escalate [ID] or /ask "[question]"

---

Context coverage: [X]% · Sources not pulled: [list with days since last pull]
```

Max: 2 pages. If more: summarize, link to /context [ID].
Suggest /escalate or /ask for every stalled item.

---

## Output Template — Filtered to Workstream

```markdown
> **LORE** — Intelligence & Delivery Engine
> Project: {PROJECT_NAME} · Source: Lore Knowledge Graph
> Generated: [DATE] · Coverage: [X]% · Confidence: [High/Medium/Low]
> ───────────────────────────────────────────────────────────────

# {PROJECT_NAME} – Delivery Briefing: [Workstream]

## Today's Focus

[2-3 bullets: what needs attention in this workstream today.]

## Status: [🟢/🟡/🔴]

[2-3 sentences: workstream health, progress, blockers.]

## Milestone

| Milestone | Date | Status | Owner | Days left |
|-----------|------|--------|-------|-----------|
| [M] | [Date] | [🟢/🟡/🔴] | [Name] | [N] |

## Progress

[What moved — bullet points with dates.]

## Blockers

- [Blocker] — since [date] — owner: [name] — suggest /escalate [ID]

## Actions Due

| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| 1 | [What] | [Who] | [When] | [On track/Overdue] |

## Open Decisions

| # | Decision | Owner | Deadline | Days open |
|---|----------|-------|----------|-----------|
| 1 | [What] | [Who] | [When] | [N] |

## Dependencies

- [Dep] — direction: [inbound/outbound] — status: [blocked/clear] — owner: [name]

## Risks

| # | Risk | Owner | Trend | Action |
|---|------|-------|-------|--------|
| 1 | [Risk] | [Who] | [↑→↓] | [Next step] |

---

Context coverage: [X]% · Sources not pulled: [list with days since last pull]
```

Max: 1 page.
