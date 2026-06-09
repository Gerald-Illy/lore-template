# Briefing Variant: Executive

Target: CTO, CPO, SVP Engineering
Presented by: Solution Lead (VP) / Solution Engineering Lead (Sr Dir)
Tone: Anchors they recognize. No action items for them.

---

## Load (index-driven)

1. Check `log/state/` for most recent state file (≤24h) → use as primary summary
2. If the state provides enough for exec format (milestones, strategic risks, key decisions) → condense to half page
3. If exec needs deeper context (watch-list escalation history, partner/budget specifics) → load additional:
   a. `knowledge/INDEX.md` — scan Key Topics for: milestones, scope, watch list, strategic risks
   b. Read ONLY matched knowledge files (typically: roadmap.md, scope.md, watch-list.md, decisions.md)
   c. `log/INDEX.md` — scan Signals and Tags ([decision], [risk]) for last 3 days
   d. Read ONLY matched daily logs
   e. `.lore/inconsistencies.md` — only 🔴 knowledge conflicts
4. If no state file or >24h old → full load via steps 3a–3e

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

# {PROJECT_NAME} – Executive Status

## Program Health: [🟢/🟡/🔴]

[One sentence: what moved, what's at risk, what's on track.]

## Milestones

| Milestone | Date | Status | Note |
|-----------|------|--------|------|
| [M] | [Date] | [🟢/🟡/🔴] | [One sentence] |

## Strategic Risks (exec-level only)

- [Risk] — [One sentence impact + trend]

Only include risks where:
- Partner/sales is stuck
- Budget is insufficient
- Cross-solution priority conflict can't be resolved at VP/Sr Dir level

## Key Decisions Made

- [Decision] — [One sentence context]

## Outlook

[One sentence: what happens next week / what to watch.]

Include watch items from knowledge/watch-list.md ONLY if:
- Item is > 21 days old AND
- Item is exec-level (partner/budget/cross-solution)
Phrasing: "Watching: [item] ([N] days)"
Maximum 2 items. If none qualify: omit.
```

Max: half a page. No action items. No /escalate suggestions.
If more content exists: summarize, do not extend.

---

## Output Template — Filtered to Workstream

```markdown
> **LORE** — Intelligence & Delivery Engine
> Project: {PROJECT_NAME} · Source: Lore Knowledge Graph
> Generated: [DATE] · Coverage: [X]% · Confidence: [High/Medium/Low]
> ───────────────────────────────────────────────────────────────

# {PROJECT_NAME} – Executive Status: [Workstream]

## Status: [🟢/🟡/🔴]

[One sentence: workstream health.]

## Milestone

| Milestone | Date | Status | Note |
|-----------|------|--------|------|
| [M] | [Date] | [🟢/🟡/🔴] | [One sentence] |

## Strategic Risks

- [Risk] — [One sentence impact + trend]

## Key Decision

- [Decision] — [One sentence]
```

Max: quarter page. Same exec rules apply.
