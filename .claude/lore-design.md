# Lore Design — Core Principles

The essential design knowledge for all agents and skills.
For repository structure, dependency maps, workflows, and setup checklists:
see `.claude/refs/lore-reference.md`.

---

## Core Principle: Project-Level Signal Only

Lore captures project-level intelligence — not everything that happens.

**Include:** Decisions with project impact, risks, stakeholder changes, architecture signals,
scope shifts, milestone changes or threats.

**Never include:** Meeting scheduling, tool setup, internal coordination, personal 1:1 content,
routine status updates, unresolved personal thoughts.

**The signal test:** If the delivery lead read this in a briefing in 6 months, would it tell them
something they need to know about the project? If no — skip it.

---

## Core Principle: Pointers, Not Content

Lore stores pointers and context — not content.

A Jira ticket is not copied into the log.
A Confluence page is not copied into the log.
Only: what changed, why it's relevant, where to find it.

**The three layers of a good log entry:**
1. **Narrative** — what happened, why, in what context (human-readable, short)
2. **Structured Tags** — `[audience][type] What – Owner – Date – →ctx/→concept/Link`
3. **Pointers** — `→ctx:[ID]`, `→concept:slug`, `[Link]`

Logs get condensed over time — what matters lives in knowledge/.

---

## Source References Must Be Clickable

Format: `[Title](URL) (version, date)` — not just plain-text ID and title.
Base URLs come from `SOURCES.md`. Never hardcode instance URLs.
If URL cannot be constructed: plain text + annotate why.

---

## Philosophy

- Sources are raw data. Lore is the verified truth after consistency checks and human decisions.
- Newer information beats older — but only when a human has explicitly decided it.
- Contradictions are never auto-resolved. Show them. Wait for a human.
- Missing data is information. Show it prominently.
- The goal is not a good briefing. The goal is this project ships.

---

## Information Priority

When sources conflict, apply this hierarchy (only at equal timestamps):

1. `OVERRIDES.md` — explicitly decided human corrections
2. `knowledge/` — verified, human-approved knowledge
3. `log/daily/` — freshest operational log
4. Sources (Confluence, Jira, GitHub, SharePoint)

A conflict with `knowledge/` is always 🔴 critical.

---

## Tags

Full tag definitions: `.claude/refs/tagging.md`

**Audience tags** (always set, default `[lead]`):
`[exec]`, `[vp]`, `[vp:delivery]`, `[vp:sales]`, `[vp:legal]`, `[lead]`, `[team]`

**Content tags** (with mandatory follow-up actions):
`[decision]` → ensure knowledge entry (DEC-*), `[risk]` → ensure knowledge entry (RISK-*) + trend,
`[action]`, `[question]` → ensure knowledge entry (OPEN-*) if complex, `[event]`, `[arch]` → ADR, `[concept]` → knowledge node

**Risk trends:** `[↑]` worsening, `[→]` stable, `[↓]` improving

---

## Log Format (daily)

Full spec: `.claude/refs/log-writing.md`

- One file per day: `log/daily/YYYY-MM-DD.md`
- Narrative first — human-readable context and background
- Tags at the end — never inline in the narrative
- Only what actually happened — no future plans without a decision
- Audience tag mandatory on every tagged item

---

## Consistency Check

Full spec: `.claude/refs/consistency-check.md`

Run automatically after every `/pull` and every `/briefing`.
Results written to `.lore/inconsistencies.md`.

| Criticality | Meaning |
|-------------|---------|
| 🔴 Knowledge Conflict | Contradicts knowledge/ — always shown first |
| 🟡 Source Conflict | Two sources disagree |
| 🟢 Missing Data | Owner, deadline, or link missing |

Never auto-resolve a conflict. Always show both states and wait for human input.

---

## Core Principle: contributions/ vs log/

These two directories serve fundamentally different purposes:

**`contributions/`** — where all new information from people goes.
Manual input, observations, feedback, action items, signals.
Anything that originates from a person and has not been shared elsewhere yet.

**`log/`** — where already-shared information is aggregated.
Pulls from sources (Jira, Confluence, SharePoint, GitHub).
Only information that has already been sent, published, or shared.
Nothing new may be entered here. Logs only collect and condense existing information.

| Directory | Purpose | May contain new information? |
|-----------|---------|------------------------------|
| `contributions/` | Human input, new signals | Yes — this is its purpose |
| `log/` | Aggregation of existing data | **No** — only already-shared information |

**The rule:** If information does not yet exist anywhere else, it goes to `contributions/`.
`log/` is a mirror — it reflects what's already out there, never creates new truth.

---

## What Lore Never Does

- Invent facts not in Lore
- Resolve conflicts without a human decision
- Read sources during briefings (Lore only)
- Auto-resolve an inconsistency because a source changed (must match the Lore decision)
- Modify sources (read only)
- Auto-read large files (PDF, PPT) — always → pending
- Skip the consistency check after a pull
