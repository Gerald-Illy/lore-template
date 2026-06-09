# Briefing Variant: VP

Target: Solution Lead (VP), Solution Engineering Lead (Sr Dir)
Presented by: Stream Leads / Delivery Lead
Tone: Workstream-based. Status, blockers, decisions needed.

---

## Load (index-driven)

1. `knowledge/INDEX.md` — scan Key Topics and Answers for: milestones, workstreams, dependencies, ownership, watch list
2. Read ONLY matched knowledge files (typically: roadmap.md, workstreams.md, dependencies.md, team.md, watch-list.md)
3. `log/INDEX.md` — scan Signals, Tags ([decision], [risk], [action]), and Entities for last 7 days
4. Read ONLY matched daily logs
5. `contributions/INDEX.md` — scan for pending signals tagged [risk] or [vp]
6. Read ONLY matched contribution files
7. `.lore/inconsistencies.md` — 🔴 and 🟡

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

# {PROJECT_NAME} – VP Briefing

## Program Health: [🟢/🟡/🔴]

[2-3 sentences: overall status, what moved, what's blocked.]

## Milestones

| Milestone | Date | Status | Owner | Note |
|-----------|------|--------|-------|------|
| [M] | [Date] | [🟢/🟡/🔴] | [Name] | [One sentence] |

## Workstream Status

### [Workstream 1]
- **Status:** [🟢/🟡/🔴]
- **Progress:** [What moved this week]
- **Blockers:** [What's stuck + since when]
- **Dependencies:** [Cross-workstream or external]
- **Next:** [What's expected next]

### [Workstream 2]
[Same structure]

## Decisions Needed

| # | Decision | Owner | Deadline | Impact if delayed |
|---|----------|-------|----------|-------------------|
| 1 | [What] | [Who] | [When] | [What happens] |

## Open Risks

| # | Risk | Owner | Trend | Action |
|---|------|-------|-------|--------|
| 1 | [Risk] | [Who] | [↑→↓] | [Suggested next step or /escalate] |

## Watch List

| ID | Item | Days | Trend |
|----|------|------|-------|
| WATCH-XX | [short description] | [N] | [new/aging ⚠] |

Only show items with status=watching. Items > 14 days get ⚠. Items > 30 days: "Consider /escalate or /watch resolve".
Maximum 5 items — if more, show top 5 by age + "[N] more — /watch list for full".
If watch list is empty: omit this section entirely.

## Escalation Candidates

- [Item] — stalled [N] days — suggest /escalate [ID]

## Inconsistencies (🔴 and 🟡)

| ID | Type | Description | Status |
|----|------|-------------|--------|
| [INC-ID] | [Type] | [One sentence] | [Status] |

---

Context coverage: [X]% · Sources not pulled: [list with days since last pull]
```

Max: 2 pages. Suggest /escalate or /ask for stalled items.

---

## Output Template — Filtered to Workstream

```markdown
> **LORE** — Intelligence & Delivery Engine
> Project: {PROJECT_NAME} · Source: Lore Knowledge Graph
> Generated: [DATE] · Coverage: [X]% · Confidence: [High/Medium/Low]
> ───────────────────────────────────────────────────────────────

# {PROJECT_NAME} – VP Briefing: [Workstream]

## Status: [🟢/🟡/🔴]

[2-3 sentences: workstream health, what moved, what's stuck.]

## Milestone

| Milestone | Date | Status | Owner | Note |
|-----------|------|--------|-------|------|
| [M] | [Date] | [🟢/🟡/🔴] | [Name] | [One sentence] |

## Progress

[What moved this period — bullet points.]

## Blockers

- [Blocker] — since [date] — owner: [name] — suggest /escalate [ID]

## Dependencies

- [Dep] — status: [blocked/clear] — owner: [name]

## Decisions Needed

| # | Decision | Owner | Deadline |
|---|----------|-------|----------|
| 1 | [What] | [Who] | [When] |

## Risks

| # | Risk | Owner | Trend |
|---|------|-------|-------|
| 1 | [Risk] | [Who] | [↑→↓] |

---

Context coverage: [X]% · Sources not pulled: [list with days since last pull]
```

Max: 1 page.
