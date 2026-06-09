# Rule: Extraction Quality — Resolution Level, Inclusion & Thoroughness

## Purpose

This rule ensures that pull agents extract all project-delivery-critical content
without over-extracting trivia or under-extracting important items.
It defines the resolution level, inclusion criteria, and verification protocol.

---

## Resolution Level: Value Increment

Lore operates at **Value Increment level** — not every detail, but enough to reach everything below.

| Source | Lore Level | Include | Aggregate | Skip |
|--------|-----------|---------|-----------|------|
| Jira | Value Increment + Epic | VI status, blocking chains, milestone mapping | Stories/bugs as counts ("5 bugs fixed in Module X") | Individual story acceptance criteria |
| Confluence | Decision + Requirement + Milestone + Dependency | DACI outcomes, scope definitions, architecture choices | Minor page edits as "page X updated" | Formatting changes, link fixes |
| Journal | Directive + Decision + Risk + Dependency + Scope change | CTO directives, workshop outcomes, blocking relationships | Multiple related small items as one entry | Meeting scheduling, tool setup, personal reflection |

**The test:** Can the delivery lead, reading only Lore, understand what blocks delivery,
what was decided, who owns what, and what the critical path is?
If yes → resolution level is correct.
If no → something was missed at VI level.

---

## Aggregation Rules

Aggregation is allowed. Interpretation is not.

| Allowed | Not Allowed |
|---------|-------------|
| "5 Module X bugs resolved this week" | "Module X quality is improving" |
| "3 of 5 M1 items unassigned" | "M1 staffing is insufficient" |
| "Network connectivity blocked since March 23" | "Team is too slow on networking" |
| "Load test: 37TB ingested on 3-node cluster" | "Performance is good enough" |

**Rule:** State the facts at aggregate level. Never add adjectives, judgments, or conclusions
that aren't explicitly stated in a source. The delivery lead draws conclusions — not the tool.

---

## Checklist A: Inclusion — "Is this important enough for Lore?"

Applied to every item encountered during extraction. Two gates: relevance AND currency.

**Gate 1 — Relevance (any box checked = include):**
```
□ 1. Does it affect project delivery timeline? (milestone, deadline, blocker)
□ 2. Does it create or resolve a dependency?
□ 3. Does it change who is responsible for what? (ownership, staffing)
□ 4. Does it change scope? (add, remove, constrain, defer)
□ 5. Is it a decision with architectural or strategic impact?
□ 6. Is it a risk that could delay delivery?
□ 7. Is it needed to understand any of the above? (supporting context for D/R/A/Q)

→ ANY box checked: passes relevance gate, proceed to Gate 2
→ NO box checked: skip or aggregate with related items
```

**Gate 2 — Currency (must pass before including):**
```
□ Is there a NEWER source that supersedes this item?
   - Decision overridden by a later decision? → include the later one, mark this as superseded
   - Risk resolved in a subsequent meeting or Jira item? → record as resolved, not as open
   - Action item completed (Jira Done/Closed, or meeting note "resolved")? → skip or note as done
   - Dependency unblocked since this source was written? → update status, don't create new entry

□ Is the date of this item OLDER than the current known state in knowledge/?
   - If knowledge/ already has a newer version of this item: do NOT overwrite with older data
   - If the newer state was explicitly decided (OVERRIDES.md): that wins

→ PASS: item is current, include it
→ FAIL: item is superseded — see "Handling Superseded Items" below
```

**Explicit exclusions (never include regardless of checklist):**
- Meeting logistics, scheduling, rescheduling
- Tool setup, CLI configuration, access provisioning
- Personal reflection, career topics, 1:1 feedback
- Routine status with zero change from last known state
- Items already captured at the same level from another source (cross-reference only)
- Content that is verbatim in another source (link only)

---

## Handling Superseded Items

Superseded items are NOT silently dropped. They are recorded as resolved/overridden.

| Item type | Was superseded by | How to record |
|-----------|------------------|---------------|
| Decision | Later decision in same or newer source | Note in decisions-open.md: "Superseded by [D-ID] — [date]" |
| Risk | Resolved: fix deployed, blocker removed | Move to resolved with date + how resolved |
| Action | Completed: Jira Done, meeting "resolved" | Record as done — do NOT carry forward as open |
| Dependency | Blocker resolved, link removed in Jira | Update status in dependencies.md: "Resolved [date]" |
| Scope item | Explicitly removed from MVP, deferred | Note deferral with source and date |

**The rule:** If something is resolved or overridden, it is MORE important to record THAT FACT
than the original item. A resolved risk tells the delivery lead the project is unblocked.
A quietly dropped action tells them nothing — and may hide that it was ever tracked.

**Temporal priority** (from `never-invent.md`):
When sources conflict, newer beats older — but only when a human has consciously decided it.
Without explicit human decision: surface the contradiction, do not resolve it.

---

## Checklist B: Thoroughness — "Did I catch everything delivery-critical?"

Applied AFTER extraction is complete. A verification pass over the source material.

```
□ 1. STRUCTURED SECTIONS: Did I read ALL structured sections completely?
     (tables, numbered lists, "Key Directives", "Actions", "Decisions", "Risks")
     → If a section has N items, I must account for all N (include, aggregate, or skip with reason)

□ 2. DEPENDENCIES: Did I trace every dependency chain to its end?
     → Explicit + AI-inferred (per ai-inference.md rule)

□ 3. GATES: Did I identify all items that GATE other work?
     → Prerequisites, blockers, sequencing, approvals needed

□ 4. PEOPLE: Did I identify all persons with delivery responsibility?
     → New names, ownership changes, people leaving/joining

□ 5. DEADLINES: Did I capture all timeline references?
     → Dates, "by end of [month]", "before [event]", deadline changes

□ 6. SCOPE: Did I check for scope changes?
     → Additions, removals, constraints, deferrals, "not in MVP"

□ 7. RISKS: Did I look for risks — explicit AND implicit?
     → Explicit: "risk", "blocker", "concern"
     → Implicit: "not clear", "waiting", "no decision yet", "not started"

□ 8. WORKSTREAMS: Do my findings cover all workstreams mentioned in the source?
     → If a workstream is discussed but I extracted nothing from it → re-scan

□ 9. COUNT VERIFICATION: For structured sections with N items, did I account for all N?
     → Extracted: [count] | Aggregated: [count] | Skipped: [count] | Total: must equal N

□ 10. TEMPORAL CROSS-CHECK: Did I verify currency against newer sources?
     → For every open risk found: is there a Jira item, later meeting, or context doc that resolves it?
     → For every open action: is there a Jira item marked Done/Closed? A meeting note saying "resolved"?
     → For every decision: was it subsequently overridden in a later deep dive, workshop, or CTO directive?
     → For every dependency: does Jira show the blocking link as resolved?
     → If knowledge/ already has a NEWER state for this item: do NOT overwrite it with older data
     → If superseded: record the resolution, not the stale state (see "Handling Superseded Items")
```

**If ANY box is unchecked:** Go back and re-scan that category before finalizing.
Item 10 failure is especially serious — it means Lore may carry stale risks or closed actions as open.

---

## Extraction Receipt

Every pull produces an EXTRACTION_RECEIPT as part of its output. This is mandatory.

```
EXTRACTION_RECEIPT:
- Source: [filename/page/item identifier]
- Structured sections found: [N] (list them)
- Items at VI level extracted: [N]
- Items aggregated (below VI level): [N] — [summary of what]
- Items skipped (exclusion criteria): [N] — [which exclusion applied]
- Items found superseded (temporal cross-check): [N] — [what was resolved/overridden]
- Dependencies found: [N] source-verified + [N] AI-inferred
- Checklist A applications: [N] items evaluated, [N] included, [N] excluded, [N] superseded
- Checklist B score: [N]/10 checks passed
- Checklist B gaps: [list any unchecked items and why]
```

If Checklist B score < 10/10: explain what could not be verified and why.
A score of 7/10 or below should trigger a re-scan before finalizing.

---

## When Token Budget Forces Prioritization

If the token budget is exhausted before all sources are processed:

1. **Never silently skip** — report what was not processed
2. **Prioritize by Checklist A** — items that check more boxes get read first
3. **Always complete Checklist B for what WAS processed** — partial coverage with verification is better than broad coverage without
4. **Report pending items** — add to `.lore/pending.md` with reason and priority

---

## Relationship to Other Rules

- **never-invent.md** — This rule doesn't override it. Facts must have sources.
- **ai-inference.md** — AI-inferred items found during extraction follow that rule's labeling protocol.
- **log-writing.md** — Extracted items flow into daily logs following the log-writing tag system.
- **condensing.md** — Extraction receipts are ephemeral (live in output, not in permanent files). Only the extracted CONTENT persists.
