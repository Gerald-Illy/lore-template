# Ref: Consistency Check – After Every Pull & Update

Full spec for consistency checks. Run automatically after every pull and after every /briefing.
Log results in `.lore/inconsistencies.md`.

Core principles for contradiction handling: see `.claude/rules/never-invent.md`.

---

## What gets checked:

**Milestones:**
- Does one source show a different date than another?
- Are there milestones without associated tasks in a source?
- Are there tasks without milestone assignment?

**Decisions:**
- Are there decisions without implementation in a source?
- Are there status changes in sources without a decision log?
- Are there open decisions older than 14 days?

**Risks:**
- Are there blocked items in sources without a tracked risk entry?
- Are there risk entries without an owner?
- Are there risks without a trend tag?

**Actions:**
- Are there actions without an owner?
- Are there actions without a deadline?
- Are there actions overdue > 7 days without an update?

**Ownership:**
- Are there items in sources without an assigned owner?
- Are there milestones without an owner in knowledge/milestones.md?

**Knowledge Conflicts (highest priority):**
Contradictions between knowledge/ and external sources are
more critical than normal source-to-source conflicts.
They indicate undocumented decisions or
deviations from decided architecture/principles.

- Does a source contradict an ADR in knowledge/architecture.md?
  → Was the architecture decision silently revised?
  → Is someone working against the decided direction?

- Does a source contradict an entry in knowledge/principles.md?
  → Principle violated or principle outdated?

- Does a source contradict a knowledge file in knowledge/?
  → New knowledge that requires updating the file?
  → Or error in the source?

- Does a source contradict knowledge/team.md (roles, owners)?
  → Has the team structure changed without an update?

---

## ID Schema

All tracked items use self-explanatory prefixes:

| Prefix | Meaning | Sequence |
|--------|---------|----------|
| `DEC-##` | Decided (closed decision) | Unified sequence across all sources |
| `OPEN-##` | Open decision (needs resolution) | Separate sequence |
| `INC-###` | Inconsistency / contradiction | Separate sequence |
| `RISK-##` | Tracked risk | Separate sequence |
| `ACTION-##` | Tracked action | Separate sequence |
| `QUESTION-##` | Open question | Separate sequence |

The source where an item was first identified (Journal, Workshop, Confluence, etc.) is NOT encoded in the ID. It belongs in the Source column of the respective table.

---

## Format in .lore/inconsistencies.md

Additional required field:
| INC-ID | ... | Criticality | ... |
Criticality: 🔴 Knowledge conflict / 🟡 Source conflict / 🟢 Missing data

Knowledge conflicts always shown first – regardless of age.

| ID | Date | Type | Description | Source A | Source B | Status |
|----|------|------|-------------|----------|----------|--------|
| INC-001 | [DATE] | Milestone | M3: July (log entry) vs June (Source B) | log/daily/YYYY-MM-DD.md | [Source B] | Open |
| INC-002 | [DATE] | Decision | No implementation in sources for [D-ID] | log/daily/YYYY-MM-DD.md | – | Open |
| INC-003 | [DATE] | Action | [A-ID] overdue for 7 days, no update | log/daily/YYYY-MM-DD.md | – | Open |

Status: Open / In Clarification / Resolved [DATE] by [Person]

---

## When to mark as resolved:

**Automatically resolved when:**
Sources agree after pull AND
the new state reflects the Lore decision.
Note: "Auto-resolved [DATE]: [Source] now matches [Lore state]"

**Manually resolved when:**
Human decides that a different state applies than in Lore.
Use /overwrite or /escalate — always with person + date.

**Never resolved when:**
Source changes but still doesn't show the Lore state.
Not even when source changes multiple times without resolving the conflict.

Example:
- INC-007: M3 → July (Lore) vs June (Confluence)
- Confluence changes: different section – M3 still June → stays open
- Confluence changes: M3 now July → Auto-resolved ✓
