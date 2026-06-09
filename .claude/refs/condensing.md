# Rule: Condensation & Log Lifecycle

## Principle
Logs are ephemeral. Knowledge is permanent.
What matters lives in knowledge/.
Logs are condensed and then archived.

## What is never deleted
- log/onboarding/        ← Baseline, readonly, forever
- knowledge/             ← ADRs, concepts, principles
- OVERRIDES.md

## Archive

Condensed source logs are NOT deleted — they move to `log/archive/`.

```
log/archive/
├── daily/       ← Dailies condensed into weeklies
├── weekly/      ← Weeklies condensed into monthlies
├── monthly/     ← Monthlies condensed into quarterlies
└── quarterly/   ← Quarterlies condensed into yearlies
```

**Purpose:** Traceback. When `/ask traceback` needs the original detail
behind a condensed entry, it reads from archive.

**Retention:** 120 days after archival. On session start, if the oldest
archived file is >120 days old, surface once:

```
⚠ Archive contains logs older than 120 days (oldest: YYYY-MM-DD).
  Consider clearing: log/archive/daily/ (N files)
  Clear now? [yes / no]
```

No auto-delete. Only on explicit confirmation.

**Not indexed.** Archive files are not in `log/INDEX.md`. They are only
accessed by traceback queries that follow →ctx: links (knowledge IDs like
DEC-*, RISK-*) back to their original filename.

---

## How Condensation Is Triggered

Condensation is checked automatically at the end of every `/pull` (Phase 6).
The pull reports what's eligible — the delivery lead confirms before anything is condensed.

| Level | Threshold | What happens |
|-------|-----------|-------------|
| daily → weekly | Dailies older than 14 days | Suggested at end of pull |
| weekly → monthly | Weeklies older than 3 months | Suggested at end of pull |
| monthly → quarterly | Monthlies older than 6 months | Suggested at end of pull |
| quarterly → yearly | Quarterlies older than 6 quarters | Suggested at end of pull |

Implementation: see `/pull` SKILL.md Phase 6.

### Weekly Log Format

File: `log/weekly/YYYY-WXX.md` (e.g., `log/weekly/2026-W20.md`)

```markdown
# Weekly Log – YYYY-WXX ([start date] to [end date])

## What happened this week
[3-5 paragraphs: narrative telling the story of the week. What moved, what didn't,
what surprised, what blocked. Written like a daily "Context & Narrative" but spanning
the full week. This is the primary reading experience — make it readable.]

## New decisions this week
[Table: Decision | Owner | Level — only NEW decisions, not repeats from dailies]

## Active risks (end of week)
[Table: Risk | Owner | Trend — snapshot of risk state at week end]

## Open actions (carry-forward)
[Table: Action | Owner | Due — only actions still open at week end]

## Source changes
[1-2 sentences: what changed in Confluence/Jira/GitHub/SharePoint — aggregated]

---

## Condensed from
[List of archived dailies with relative links + 1-line summary each]
```

**Tone:** The "What happened" section is the heart of the weekly. It must be
readable as a standalone narrative — someone skipping dailies should understand
the week from this section alone. Tables below are reference/lookup only.

**Links:** All Jira items and Confluence pages mentioned in the narrative MUST
be hyperlinked. Key topics and achievements are **bold**-highlighted as paragraph
openers. The "Condensed from" footer links back to the archived dailies for
full detail retrieval.

---

## Daily → Weekly (after 14 days)
Then: move daily to `log/archive/daily/`.

- [decision][exec/vp/lead]: complete + →ctx: link (knowledge ID)
- [decision][team]:          title + date + owner + →ctx: link (knowledge ID)
- [risk] open:               complete + trend
- [risk] closed:             omit
- [action] open:             preserve
- [action] done:             omit
- [question] open:           preserve
- [concept]:                 term + →concept: link
- Jira/Confluence changes:   aggregated only ("X items changed")

## Weekly → Monthly (after 3 months)
Then: move weekly to `log/archive/weekly/`.

- Only [exec] and [vp] complete
- Everything else: one sentence + →ctx: / →concept: links
- Jira/Confluence changes: omit

## Monthly → Quarterly (after 6 months)
Then: move monthly to `log/archive/monthly/`.

- Only decisions, risk changes, milestones
- One sentence per entry + links
- Preserve trend history for risks

## Quarterly → Yearly (after 6 quarters)
Then: move quarterly to `log/archive/quarterly/`.

- Only turning points, strategic decisions
- What shaped this project this year?
- Preserve all →ctx: and →concept: links

## Yearly
Stays forever. Never condensed.

---

## Setup Log (`.lore/loremaster-log.md`)

The setup log is NOT a project log — it is the Lore infrastructure's memory.
Different lifecycle rules apply.

### Condensation (after 3 months)

Entries older than 3 months are condensed into a summary block:

```markdown
## Archive: [YYYY-MM] to [YYYY-MM]

[N] sessions. Key changes:
- [one-line summary per significant change]
- [design principles established — preserve these]

Full entries archived to `.lore/archive/`. Design principles survive in the rules they created.
```

### What is always preserved (never condensed)

- Design principles established (these ARE the rules — if they were written into rule files, the loremaster-log entry is the only record of WHY)
- Breaking changes to agents or skills
- Entries that document "Still open" items not yet resolved

### What is safe to condense

- Routine fixes ("fixed typo in X", "added missing field Y")
- Entries where the "What changed" is fully reflected in the changed files themselves
- Entries where "Still open" was resolved in a later entry
