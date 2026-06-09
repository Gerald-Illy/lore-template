---
name: escalate
description: Draft an escalation for a stalled item, risk, or decision. Usage: /escalate "[ID or description]"
---

# Skill: /escalate "[ID or description]"

Drafts an escalation message for a stalled item, risk, or decision.
Never sends without explicit user confirmation.

---

## --help

When invoked as `/escalate --help` or `/escalate -h` — print this and stop:

```
/escalate — Draft an escalation for a stalled item, risk, or decision

Usage:
  /escalate "[ID or description]"

Examples:
  /escalate RISK-03
  /escalate OPEN-04
  /escalate "Component X decision stalled since April — blocking M2"
  /escalate "owner of ACTION-12 has not responded in 2 weeks"

When to use:
  - Item is stalled and owner is not responding
  - Risk is trending up and deadline is approaching
  - Decision is overdue >14 days with no movement

Escalation levels:
  Stream Lead    action overdue 7+ days, owner known
  VP             risk [↑] with no mitigation plan, decision blocked >14 days
  Exec           partner/sales blocked, budget insufficient, cross-solution conflict

Tip: Never sends without your explicit confirmation.
     For information about an item, use /ask instead.
```

---

## When to Escalate (vs. other skills)

| Situation | Use |
|-----------|-----|
| Item is stalled, owner is not responding | `/escalate` |
| Risk trend is [↑] and deadline is approaching | `/escalate` |
| Decision is overdue >14 days with no movement | `/escalate` |
| You need information about an item | `/ask` |
| Two sources disagree on a fact | `/ask inconsistencies` |
| Something is wrong in Lore's knowledge | `/override` |

**Escalation thresholds** (from briefing/SKILL.md):
- **To VP level:** No status change in 7+ days, owner not confirmed, blocker with no mitigation plan, trend [↑] with no action logged, cross-workstream dependency stuck
- **To exec level:** Partner/sales stuck without exec involvement, budget insufficient, cross-solution priority conflicts that VP/Sr Dir can't resolve

---

## Load (index-driven)

1. `knowledge/INDEX.md` — find knowledge entry for the ID (DEC-*, RISK-*, OPEN-*)
2. If no knowledge entry: `log/INDEX.md` → Daily section — scan References and Signals for the item by ID or description
3. Read ONLY matched files
4. `knowledge/INDEX.md` — scan Key Topics and Answers for: ownership, workstream context
5. Read ONLY matched knowledge files (typically: team.md, workstreams.md)
6. `log/INDEX.md` — scan last 5 daily entries by date, derive trend for this item
7. `.lore/inconsistencies.md` — check if item has related open INCs

---

## Derive Escalation Level

Based on the item and its context, determine the right level:

| Signal | Level | Recipient |
|--------|-------|-----------|
| Action overdue 7+ days, owner known | Stream Lead / Workstream | Owner + stream lead |
| Risk trend [↑], no mitigation plan | VP | Owner + VP Delivery |
| Decision blocked >14 days, cross-workstream | VP | Decision owner + affected stream leads |
| Blocker involves external partner or budget | Exec | VP + Solution Lead |
| Cross-solution priority conflict | Exec | VP + CTO office |

If unclear: default to VP level and let the user adjust.

---

## Output

```
---
### Escalation Draft – [ID or Title]

**Level:** [Stream Lead / VP / Exec]
**To:** [Owner from team.md]
**CC:** [Relevant stakeholders per audience tag and escalation level]
**Subject:** [ESCALATION] [ID] – [Title]

---

**Context** (3-4 sentences)
[What the item is. When it was created. What milestone/workstream it belongs to.]

**Why now**
[Trend data: how long stalled, trend direction, what deadline is approaching.]
[What happens if this isn't resolved by [date].]

**What is needed**
[Concrete ask: decision, unblock, staffing, alignment — one specific action.]

**Source**
[Link to knowledge entry, Jira item, or Confluence page]

---
```

---

## After Escalation

1. **Show draft — wait for explicit approval.** Never send without confirmation.
2. After approval, suggest:
   - "Add `[action]` tag to today's log? → /pull will track it"
4. If the user modifies the draft: apply changes, show updated version, wait for confirmation again.

---

## Rules

- Never send an escalation automatically — always draft + confirm.
- Always include a concrete "What is needed" — never escalate without a specific ask.
- If the item has no owner in team.md: flag this as part of the escalation ("⚠ No owner assigned — this is part of the problem").
- If the item has related open INCs: mention them ("Note: related inconsistency INC-XXX is also open").
- Tone: direct, factual, no diplomatic padding. State the problem and the ask.
- If the user provides a description instead of an ID: search log/INDEX.md References and Signals for matching items. If ambiguous: show matches and ask which one.

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- `log/INDEX.md` — identify daily logs referencing the escalation target (via References, Signals)
- `knowledge/INDEX.md` — identify knowledge entries for the ID + team.md and workstreams.md for ownership context (via Key Topics)

### Index Write
- None (drafts only — does not write to indexed areas)
