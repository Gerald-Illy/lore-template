---
name: ask
description: Query the Lore knowledge base — ask questions about project state, decisions, risks, dependencies, architecture. Includes traceback mode to trace claim origins and inconsistencies mode to review/resolve conflicts. Searches local knowledge first, then logs, then reaches into sources (Jira, Confluence, SharePoint) when needed.
---

# Skill: /ask [question] | /ask traceback "[claim]" | /ask inconsistencies [filter]

Interactive query assistant for the Lore knowledge base.
Answers questions about project state by searching through all layers of knowledge.
Traceback mode traces the origin of a specific claim back to its original source.
Inconsistencies mode shows and resolves open knowledge conflicts.

---

## --help

When invoked as `/ask --help` or `/ask -h` — print this and stop:

```
/ask — Query the Lore knowledge base

Usage:
  /ask [question]                    → knowledge query
  /ask traceback "[claim]"           → trace origin of a claim
  /ask traceback [file]:[section]    → trace origin of a file entry
  /ask inconsistencies [filter]      → show and resolve open conflicts

Examples:
  /ask what blocks milestone M3?
  /ask who owns the infrastructure workstream?
  /ask what was decided about multi-tenancy?
  /ask what is the current status of PROJ-1234?
  /ask traceback "Jane Smith is Engineering Lead"
  /ask traceback "M2 date is June 2027"
  /ask traceback knowledge/team.md:"Platform Services"
  /ask inconsistencies
  /ask inconsistencies knowledge

Layers searched (in order):
  1. knowledge/     — verified, human-approved facts
  2. log/daily/     — recent operational events
  3. Sources         — live Jira / Confluence / GitHub (when needed)

Tip: For live Jira/Confluence data use /atlassian. For a full status report use /briefing.
```

---

## Mode Detection

```
/ask traceback "[claim]"           → traceback mode (see below)
/ask traceback [file]:[section]    → traceback mode (see below)
/ask inconsistencies [filter]      → inconsistencies mode (see below)
/ask [anything else]               → standard query mode
```

If first word after `/ask` is `traceback` → switch to traceback mode.
If first word after `/ask` is `inconsistencies` → switch to inconsistencies mode.
Otherwise → standard query mode (existing behavior).

---

## How It Works (Standard Query Mode)

Three-layer search — stop as soon as the answer is complete:

### Layer 1: Knowledge (fast, verified)

Progressive loading — don't read everything:
1. `OVERRIDES.md` — check for corrections on the topic (already in context from session start)
2. `knowledge/INDEX.md` — scan Key Topics, Answers, and Contains to identify relevant files
3. Read ONLY the matched `knowledge/*.md` files (or specific sections via Section Index)

If the answer is fully covered here → respond. Done.

### Layer 1.5: Contributions (unprocessed signals)

If knowledge/ doesn't fully answer, or the question is about recent/pending signals:
1. `contributions/INDEX.md` — scan What, Tags, Status for pending signals matching the query
2. Read ONLY matched contribution files

Flag these as "unprocessed signal — not yet verified."

### Layer 2: Logs (recent, operational)

If knowledge/ and contributions don't fully answer:
1. `log/INDEX.md` — scan Signals, Entities, References to identify relevant logs
2. Read ONLY the matched log files (not "last 7 days" — only those that match)
3. `.lore/inconsistencies.md` — open contradictions

If the answer is covered between knowledge/ and logs → respond. Done.

### Layer 3: Sources (authoritative, live)

If local data is insufficient, stale, or the user asks for live data:
1. **Jira** — via `/atlassian` skill (acli CLI)
2. **Confluence** — via `/atlassian` skill (acli CLI)
3. **GitHub repos** — via `gh` CLI
4. **SharePoint** — local sync folder (OneDrive)

Always tell the user which layer you're pulling from and why.

---

## Behaviour

1. **Start with knowledge/** — always. It's the verified, condensed truth.
2. **Go to sources only when needed** — if knowledge/ is stale, incomplete, or the user explicitly asks for live/fresh data.
5. **Never invent** — if the answer isn't in any layer, say: "This is not documented in Lore."
6. **Flag staleness** — if knowledge/ data is old and no recent log confirms it, say so.
7. **Flag contradictions** — if sources disagree, show both with timestamps (per never-invent rule).
8. **AI inference allowed** — for dependencies/risks/gaps, clearly labeled `[AI-inferred]`.

---

## Output Format

**Short answers** — for factual queries (who owns X, what's the status of Y):
- Direct answer, one to three sentences
- Source citation: `[Source: knowledge/roadmap.md]` or `[Source: Jira PROJ-1234]`

**Deep answers** — for complex queries (what blocks M3, explain the dependency chain):
- Brief summary (2-3 sentences)
- Detail section with structured data (tables, lists)
- Source citations for each claim
- AI-inferred items labeled and separated

**"I don't know" answers** — when data is missing:
- State what's missing
- Suggest where to look or who to ask
- Offer to pull from source if applicable: "Shall I check Jira/Confluence for this?"

---

## 🤖 AI Reasoning (mandatory, always at the end)

Every answer ends with a reasoning block. This is where the Co-Delivery-Lead gives its assessment — pattern recognition, concerns, and recommendations that go beyond what's explicitly in the data.

*Interpretation by Claude. Not ground truth. Clearly separated from facts above.*

Format:

```
---
#### 🤖 AI Reasoning

**My read:** [One sentence assessment — what does this mean for delivery?]
**What concerns me:** [Risks, gaps, or dynamics that follow logically from the facts above]
**What I'd recommend:** [Concrete next step — a /command, a person to talk to, an action to take]

*Confidence: [High / Medium / Low] — based on [data quality note]*
```

### When to say more vs. less

| Answer type | AI Reasoning depth |
|-------------|-------------------|
| Simple factual query ("who owns X?") | One sentence: "No concerns — this is clear." |
| Status query ("what's the state of Y?") | 2-3 sentences: assessment + recommendation if stale/at-risk |
| Complex query ("what blocks M3?") | Full block: read + concerns + recommendation |
| Missing data | Full block: what's missing, why it matters, how to fix it |

### Rules for AI Reasoning

- **Always give your honest assessment** — no diplomatic padding
- **Disagree if warranted** — if the data suggests something the user might not want to hear, say it
- **Be concrete** — "talk to the owner" not "consider stakeholder alignment"
- **Flag what you can't see** — if your assessment is limited by missing data, say so
- **Never present reasoning as fact** — the section header makes this clear, but never blur the line

---

## Example Queries

| Query | Expected layer |
|-------|---------------|
| "What are the M3 milestones?" | Layer 1 (knowledge/roadmap.md) |
| "Who owns the infrastructure workstream?" | Layer 1 (knowledge/workstreams.md) |
| "What was decided about multi-tenancy?" | Layer 1+2 (knowledge/decisions-open.md, knowledge/decisions.md + daily logs) |
| "What's blocking the network capability?" | Layer 1+2 (knowledge/dependencies.md + recent logs) |
| "What's the current status of PROJ-1234?" | Layer 3 (Jira live query) |
| "What changed in Confluence this week?" | Layer 3 (Confluence live query) |

---

## Rules

- Respect privacy rules — never read `## Confidential` or `## Private` sections unless explicitly asked
- Follow extraction quality rules — cite sources, flag gaps
- If answer requires multiple sources: show which parts come from where
- If user asks a follow-up: remember the context from the previous answer
- If knowledge/ contradicts a source: surface it as inconsistency, don't silently pick one

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- `knowledge/INDEX.md` — Layer 1: identify relevant knowledge files via Key Topics, Answers, Contains
- `contributions/INDEX.md` — Layer 1.5: find pending signals via What, Tags
- `log/INDEX.md` — Layer 2: identify relevant logs via Signals, Entities, References

### Index Write
- None (read-only skill)

---

## Traceback Mode: /ask traceback "[claim]"

Find where a piece of information originally came from.
Not "which pull brought it in" — but "who said it first, and based on what?"

### Search Strategy

Search in this order, stop when origin is found:

1. **Git blame on the file** — `git log -p --all -S "[search term]"` and `git blame` on the relevant file. Find the commit that introduced the claim.
2. **Pull logs** — search `log/daily/` for the date the claim was introduced.
3. **Daily logs** — search `log/daily/` for related decisions or discussions.
4. **Contributions** — search `contributions/` for manual input that introduced the claim.
5. **OVERRIDES.md history** — if the claim is an override, `git log OVERRIDES.md` shows when/by whom.

### Output Format

```
## Traceback: "[claim]"

### 1. Current State
| Location | Line/Section | Last modified |
|----------|-------------|---------------|
| `knowledge/team.md` | line 42, section "Core Team" | 2026-05-13 |

### 2. Introduction
| Date | Commit | Action |
|------|--------|--------|
| 2026-05-13 | [`abc1234`](link) | Confluence pull — knowledge derivation |

### 3. Origin Source
| Source | Link | Author | Date |
|--------|------|--------|------|
| Confluence: "Team Structure" | [page](url) | Author Name | 2026-05-10 |

### 4. Chain (oldest → newest)
[Source] (date, author)
  → [Pull/Action] (date, commit)
    → [Current location] (date)

### 5. All Sources (clickable)
| # | Source | Link | Date | Context |
|---|--------|------|------|---------|
| 1 | ... | [link](url) | ... | ... |
```

**Confidence:** high | medium | low

### Link Requirements

- Confluence: `{CONFLUENCE_BASE}/wiki/spaces/{SPACE}/pages/{pageId}`
- Jira: `{JIRA_BASE}/browse/{key}`
- GitHub: `https://github.com/{OWNER}/{REPO}/blob/main/{path}`
- Git commits: relative reference acceptable
- Base URLs from `SOURCES.md`. Never hardcode without checking.

### Confidence Levels

| Level | Meaning |
|-------|---------|
| **high** | Full chain found: original source → pull → current location |
| **medium** | Source identified but chain has gaps |
| **low** | Best guess based on timing and context — origin not definitively proven |

### Traceback Rules

1. **Never invent a source** — if you can't find it, say so
2. **Git is the ground truth** — git blame/log is the most reliable starting point
3. **Show your work** — always list what was checked, even if nothing was found
4. **One claim at a time** — keep it focused
5. **No judgment** — traceback shows where something came from, not whether it's correct
6. **Suggest next steps** — if origin is unclear, suggest how to verify

---

## Inconsistencies Mode: /ask inconsistencies [filter]

Show and resolve open inconsistencies.
Fast. One at a time. Human decides. Claude executes.

### Refs
- `.claude/refs/consistency-check.md` — what gets checked, format, resolution rules

### Load
1. `.lore/inconsistencies.md`
2. Referenced sources per inconsistency (only what's needed)

### Filters

```
/ask inconsistencies              → all open, sorted by criticality then age
/ask inconsistencies knowledge    → 🔴 only knowledge conflicts – highest priority
/ask inconsistencies milestone    → only milestone conflicts
/ask inconsistencies decision     → only decision gaps
/ask inconsistencies risk         → only risk gaps
/ask inconsistencies action       → only overdue actions
/ask inconsistencies ownership    → only missing owners
```

### Severity

| Level | Meaning |
|-------|---------|
| 🔴 Knowledge Conflict | contradicts a decision or principle in knowledge/ |
| 🟡 Source Conflict | two sources disagree |
| 🟢 Missing Data | gap with no source |

### Output Structure

```
### Open Inconsistencies – [DATE]
[X] open / [Y] in clarification / [Z] resolved this week

🔴 Knowledge Conflicts: [N] ← always shown first, always
🟡 Source Conflicts: [N]
🟢 Missing Data: [N]
```

Then show items (max 5 at once):

#### 🔴 Knowledge Conflict

```
#### 🔴 [INC-ID] Knowledge Conflict – [Title]
**Why critical:** This contradicts a documented decision or principle
in knowledge/. Either the knowledge is outdated or someone is
working against an established direction.

**Conflict:**
- knowledge/[file] ([Date]) → [State A]
- [Source B] ([Date]) → [State B]

**This means one of:**
1. A new decision was made but not documented → create ADR
2. Someone is working against the architecture → needs immediate attention
3. The knowledge entry is outdated → update knowledge/

**Proposed resolution:**
→ A) Knowledge is correct – source is wrong → /override "[old]" "[correct]"
→ B) New decision supersedes knowledge → /override "[old]" "[correct]" + ADR draft
→ C) Escalate immediately → /escalate INC-[ID]
→ D) Document resolution → /jot resolve INC-[ID] "[what's correct and why]"
```

#### 🟡 Source Conflict

```
#### 🟡 [INC-ID] Source Conflict – [Title]
**Conflict:**
- [Source A] ([Date]) → [State A]
- [Source B] ([Date]) → [State B]

**Context:** [one sentence why this matters]

**Proposed resolution:**
→ A) Accept [State A] → /override "[State B]" "[State A]"
→ B) Accept [State B] → /override "[State A]" "[State B]"
→ C) Escalate to owner → /escalate INC-[ID]
→ D) Document resolution → /jot resolve INC-[ID] "[what's correct and why]"
```

#### 🟢 Missing Data

```
#### 🟢 [INC-ID] Missing Data – [Title]
**What's missing:** [what data or source is absent]

**Why it matters:** [one sentence impact]

**Proposed resolution:**
→ A) Track down the missing data → /jot todo "[who should provide what]"
→ B) Escalate to owner → /escalate INC-[ID]
→ C) Accept as known gap → /jot resolve INC-[ID] "Known gap: [what and why]"
```

### Resolution Sub-Commands

| Action | Use when… |
|--------|-----------|
| `/override "[wrong]" "[correct]"` | "This must be actively enforced until sources catch up" |
| `/jot resolve INC-[ID] "[reason]"` | "I know what's correct — documenting it for the record" |
| `/escalate INC-[ID]` | "Someone else needs to act on this" |

### Inconsistencies Rules

- Show maximum 5 inconsistencies at once – not a wall of text
- Always show proposed resolutions – never just the problem
- Never resolve automatically – always wait for human input
- A source update after a conflict was logged does NOT resolve it.
  Claude checks if the update actually addresses the conflict.
  If not: conflict stays open, note added: "Source updated [date]
  but conflict unresolved – value still shows old state"
- After /override: run consistency check on affected area
- Track resolution time – flag if INC older than 14 days unresolved
- If same type of inconsistency repeats: flag as systemic issue
  "⚠ 3rd milestone conflict this week – systemic source update problem"
- After working through multiple inconsistencies in one session: suggest /jot recap
