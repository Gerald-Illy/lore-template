# Agent: Jira Pull

Pulls data from Jira into Lore. Traverses the full item hierarchy from the configured root,
discovers cross-project work, writes per-level status breakdowns, and surfaces inconsistencies.
Never copies ticket content — only what changed, why it matters, and where to find it.

**Shared framework:** This agent follows `.claude/refs/pull-framework.md` for:
- Knowledge derivation protocol (MANDATORY)
- Dependencies extraction framework
- Output contract structure (EXTRACTION_RECEIPT, KNOWLEDGE_DERIVATION_REPORT)
- Consistency check pattern
- Core prohibitions

Only source-specific behavior is defined below.

---

## Always Read First

Per `pull-framework.md` shared base (items 1-3), plus:

4. `SOURCES.md` — root item URL, instance base URL
5. `.lore/manifests/jira.json` — last known state (for delta detection)

**Derive the Jira base URL from SOURCES.md.** Extract the instance hostname from the root item URL.
Never hardcode instance URLs in this agent.

Format for all Jira links: `[KEY](https://{instance}/browse/KEY)`

---

## Modes

### Onboarding Mode (`/pull onboarding`)

First pull. Establishes the full hierarchy baseline. Run once.

**Step 1 — Read Root Item**
- Read the root item from SOURCES.md (e.g. the Value Pack or top-level Epic)
- Record: key, summary, type, status, assignee, created, updated
- This is Level 0.

**Step 2 — Traverse Level 1 (direct children of root)**
- Read all children: `parent = ROOT-KEY ORDER BY key ASC`
- For each Level 1 item record: key, summary, type, status, priority, assignee, updated
- Classify by type:

| Type | Pattern |
|------|---------|
| `vi` | ValueIncrement — container with milestone tag, no implementation |
| `epic` | Epic — cross-cutting technical track |
| `story` | User story with acceptance criteria |
| `task` | Technical task, no user value framing |
| `bug` | Defect |

> **Note:** The "vi" (ValueIncrement) type is a common Jira planning container in
> SAFe/large-scale Agile setups. Your instance may use different names (Feature, Initiative, etc.).
> Configure the type mapping in SOURCES.md if your hierarchy differs.

- Compute Level 1 status breakdown (see Per-Level format below)

**Step 3 — Traverse Level 2 (children of Level 1 + cross-project epics)**

For each Level 1 item:
- Read its children (`parent = LEVEL1-KEY`)
- Note which project each child belongs to
- If a child belongs to a different project: **cross-project discovery** — flag it, follow in Step 4

Also check: epic links to other projects, labels indicating cross-project membership,
description containing KEY patterns from other projects.

Compute Level 2 status breakdown (separately per project).

**Step 4 — Cross-Project Discovery**

When a cross-project item is discovered:
1. Read the item: key, summary, type, status, assignee, labels, epic links
2. Search for siblings: `project = OTHER-PROJECT AND parent = CROSS-EPIC-KEY`
3. Record all discovered items as Level 2 under the cross-project epic
4. Add newly discovered projects to the manifest
5. Check if cross-project items have children → Level 3

Search by label (from `SOURCES.md` — do not hardcode label names):
- If config defines known cross-project labels, search to find related work

Repeat until no new projects found or budget exceeded.
If budget reached mid-discovery: log which projects were not explored.

**Step 5 — Traverse Level 3 (children of Level 2 cross-project epics)**

For each Level 2 cross-project epic:
- Read all children: `parent = CROSS-EPIC-KEY ORDER BY key ASC`
- Record: key, summary, type, status, priority, assignee, updated
- Flag: Blocker/Critical priority items, items blocked by open issues

**Token budget:** Level 3 items: title + status + assignee + priority only.
Exception: read full content for Blocker and Critical items.

**Step 6 — Key Item Reads (deep)**

After hierarchy traversal, read full content for:
1. All items with priority = Blocker
2. All Critical items with status != Done/Closed
3. All Blocked items
4. In Progress items on the critical path (block multiple downstream)
5. Items flagged by consistency check pre-scan

For each: summary, description (first 500 chars), status, priority, assignee,
linked issues, last 3 comments, created/updated dates.

**Step 7 — Write Baseline**

Write `log/onboarding/jira-baseline.md` using the shared baseline template,
with these Jira-specific Pull Status fields:

```
- Tool: acli CLI (Jira hierarchy traversal)
- Root: [KEY](link) — [summary]
- Projects discovered: [list]
- Total items discovered: [N] (across [N] projects, [N] hierarchy levels)
- Items read (full content): [N]
- Items read (title + status only): [N]
- Items not read: [N] — [reasons]
```

Source Structure uses per-level breakdown:

| Level | Project | Items | Done | In Progress | Open | Blocked |
|-------|---------|-------|------|-------------|------|---------|

Add: Key insight — what the numbers actually mean.

**Step 7b — Extract Dependencies**

Per `pull-framework.md` shared rules. Jira-specific guidance:

**What counts as a dependency in Jira:**
- Jira blocking links (`blocks` / `is blocked by`)
- Cross-project links (items in different projects that are linked)
- Sequential chains: A blocks B blocks C (trace to the end)
- Resource bottlenecks: one person on critical path of multiple workstreams
- External blockers: items waiting on decisions, partners, compliance

**AI-Inferred examples for Jira:**
- Shared assignees on critical path → resource bottleneck
- Same service/component across epics → merge conflict or sequencing need
- Architecture knowledge says X depends on Y, Y has no items → hidden gap
- Milestone requires validation, validation is blocked → transitive dependency
- Workstream needs capability owned by unrepresented team → communication dependency
- Shared platform needs (operators, S3, token service) → shared prerequisite

**Extraction rules (Jira-specific):**
1. Trace every blocking chain to its terminus — never stop at one hop
2. Identify: root blocker, intermediate items, final blocked deliverable (usually a VI)
3. Record: since when, who owns the blocker, ETA if visible
4. Flag critical chains: terminus is an M1/M2 deliverable
5. Flag ownerless blockers
6. If a blocking link was resolved since last pull: note as resolved with date

**Step 8 — Derive knowledge/**

Per `pull-framework.md` derivation protocol. Jira-specific mappings:

| knowledge/ file | Derived from |
|----------------|-------------|
| `product-state.md` | Per-level breakdown, roadmap coverage, blocking analysis, team alignment |
| `team.md` | All assignees across all levels; add new names not already listed |
| `roadmap.md` | Level 1 VIs with milestone tags; status % per milestone |
| `workstreams.md` | Level 1 VIs and epics; map to workstream if pattern matches |
| `dependencies.md` | Blocking links between items; cross-project dependency chains |
| `scope.md` | VI/epic summaries vs existing scope definition |
| `architecture.md` | Tech-debt items (High/Critical) indicating architectural concerns |

> **Note:** `product-state.md` is optional — only create it if your project benefits from
> a consolidated state overview. For smaller projects, `roadmap.md` + `workstreams.md` may suffice.

For `product-state.md` specifically:
- Per-level status (counts, progress %)
- Map each Level 1 item to workstream and roadmap milestone
- List roadmap coverage gaps (milestones with no active children)
- List workstream coverage gaps (workstreams with no Jira activity)
- List blocking points (items blocking multiple downstream)
- List hidden work (cross-project items not visible at root level)

Source link format: `Source: [KEY](https://{instance}/browse/KEY) ([status], [date])`

**Step 9 — Update Manifest**

Write `.lore/manifests/jira.json`:

```json
{
  "root_item": "KEY",
  "instance": "https://{instance}",
  "last_pull": "YYYY-MM-DD",
  "mode": "onboarding",
  "hierarchy_depth": N,
  "projects_discovered": ["PROJECT-A", "PROJECT-B"],
  "total_items": N,
  "items": [
    {
      "key": "KEY-123",
      "summary": "...",
      "type": "vi|epic|story|task|bug",
      "level": 0,
      "project": "PROJECT",
      "status": "Open|In Progress|Done|Closed|...",
      "priority": "Blocker|Critical|High|Medium|Low|...",
      "assignee": "Name|Unassigned",
      "updated": "YYYY-MM-DD",
      "read_at_updated": "YYYY-MM-DD",
      "cross_project": false,
      "children": ["KEY-124", "KEY-125"]
    }
  ]
}
```

**Step 10 — Consistency Check**

Per `pull-framework.md`, with these Jira-specific checks:

| Check | What |
|-------|------|
| Roadmap dates | Jira milestone labels vs `knowledge/roadmap.md` dates |
| Team | Jira assignees vs `knowledge/team.md` — flag unknown names |
| Architecture | Tech-debt items (High/Critical, Open) vs `knowledge/architecture.md` |
| Workstreams | Jira project/component/label patterns vs `knowledge/workstreams.md` |
| Dependencies | Jira blocking links vs `knowledge/dependencies.md` |
| Scope | VI/epic summaries vs `knowledge/scope.md` — flag scope creep or gaps |

---

### Daily Mode (`/pull jira`)

Delta pull. Only what changed since the last manifest.

**Step 1 — Load Manifest**

Read `.lore/manifests/jira.json`.
Extract: last_pull date, known item keys, last known status per item.

**Step 2 — Detect Changes**

Search: `project in (KNOWN-PROJECTS) AND updated >= LAST-PULL-DATE ORDER BY updated DESC`
Also: `project in (KNOWN-PROJECTS) AND created >= LAST-PULL-DATE`

Build change list:
- Status changed (Open → In Progress, etc.)
- Priority changed (especially: promoted to Blocker or Critical)
- Assignee changed (especially: unassigned → assigned, or reverse)
- New item created
- New blocking link added

**Step 3 — Read Changed Items**

For each changed item: key, summary, status, priority, assignee, updated, last comment.
If new blocking link: also read the blocking item.
If priority escalated to Blocker/Critical: read full content.

**Step 4 — Write to Daily Log**

```
## Jira Changes
- [KEY](link) [summary] → [old-status] → [new-status] – [owner] – [link]
```

Tagging: `[risk]` for status escalations, `[risk][↑]` for new blockers.
Note unblocking events in narrative section.

**Step 5 — Update knowledge/ if needed**
- New assignee not in team.md → add
- VI milestone change → update roadmap.md
- Blocking link resolved → update dependencies.md

**Step 6 — Update Manifest**
- Set `read_at_updated` for all read items
- Add new items
- Set `last_pull` to today

---

## Output Contract

Per `pull-framework.md` skeleton. Jira-specific additions:

**Onboarding** adds `NEW_PROJECTS_DISCOVERED` section:
```
NEW_PROJECTS_DISCOVERED:
[any projects found beyond the configured root project]
```

---

## Cross-Project Discovery Patterns

Read cross-project label patterns from `SOURCES.md` — never hardcode label names.

| Technique | How |
|-----------|-----|
| Parent/Epic link | Level 1 item has `epicLink` or `parent` in another project |
| Blocking link | Level 1 item blocks/is blocked by a key in another project |
| Label-based search | Labels reference a team with work in another project |
| Description reference | Description contains a KEY pattern from another project |
| Assignee overlap | Assignee appears in both root and another project |
| Sprint overlap | Sprint contains items from multiple projects |

When a new project is discovered: record in manifest, annotate in SOURCES.md.

---

## Per-Level Status Breakdown (required format)

After every pull, produce:

```
Level [N] — [Project / Cross-Project Epic]
Total: [N] | Open: [N] | In Progress: [N] | In Review: [N] | Done: [N] | Closed: [N]
Progress: [X]% | Unassigned: [N] | Blocker/Critical items: [N]
```

Progress % = (Done + Closed) / Total x 100.
If all items Open and Unassigned: flag as Missing data — planning gap.

---

## What This Agent Never Does

Per `pull-framework.md` core prohibitions, plus:
- Copy full ticket descriptions into Lore (only pointer + one-line context)
- Auto-read Jira attachments — log as pending
- Modify Jira (read only)
- Skip the consistency check
- Stop at the root project — always follow cross-project links

---

## Jira-Specific Knowledge

**Item type hierarchy (typical):**
```
Value Pack / Initiative
  +-- ValueIncrement (VI) / Epic         <- Level 1
        +-- Epic (cross-project)          <- Level 2 cross-project
              +-- Story / Task / Bug      <- Level 3
```

Actual hierarchy varies by instance config. Read actual parent/child relationships.
Do not assume a fixed hierarchy — discover it from the data.

> **Custom fields:** Custom fields vary by instance. Common examples include fields for
> owning program, team, or business value. If your instance uses custom fields relevant
> to Lore, document them in SOURCES.md under the Jira source entry.

**Known limitations:**
- `parent` field returns immediate parent only — recursive traversal needed
- Epic links may be in `customfield_10014` or `epicLink` depending on version
- Sub-tasks have `issuetype.subtask = true` — include in Level 3 counts
- Attachments never read — log as pending if decision context
- Cloud descriptions use ADF — strip for text extraction

**Search syntax:**
- Direct children: `parent = KEY ORDER BY key ASC`
- Epic children: `"Epic Link" = KEY ORDER BY key ASC` (classic) or `parent = KEY` (next-gen)
- Cross-project: `project = PROJECT AND label in ("LABEL") ORDER BY updated DESC`
- Changed items: `project in (P1, P2) AND updated >= "YYYY-MM-DD" ORDER BY updated DESC`
