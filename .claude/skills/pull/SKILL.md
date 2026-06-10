---
name: pull
description: "Pull fresh data from all active sources into Lore. Includes retroactive mode for missed content or new sources. Usage: /pull [scope]"
---

# Skill: /pull [scope]

Pulls fresh data from all active sources into Lore.
Runs consistency checks after every pull.
Never modifies sources – only reads.

## --help

When invoked as `/pull --help` or `/pull -h` — print this and stop:

```
/pull — Pull fresh data from all sources into Lore

Usage:
  /pull [scope]

Scopes:
  (none)               all active sources — standard daily pull
  journal              only GitHub Journal
  jira                 only Jira
  confluence           only Confluence
  github               only GitHub repos
  web                  only web sources (live URL fetch)
  onboarding           first pull — establishes the baseline (run once)
  on-demand [name]     single on-demand source from SOURCES.md
  retroactive missed "[desc]"       add missed content from existing source
  retroactive new-source "[name]"   connect a new source after initial onboarding

Examples:
  /pull
  /pull jira
  /pull confluence
  /pull on-demand sharepoint
  /pull onboarding      ← first time only
  /pull retroactive missed "M2 scope decision from April Confluence page"
  /pull retroactive new-source "Partner SharePoint — Telekom project docs"

Phases: source resolution → manifest check → read changes → write log → decision scan → consistency check → update manifests → condensation check → state file
Tip: Sources are pulled in parallel. Consistency check always runs after.
     Source registries (external) are fetched first — teams can maintain their own sources.
     Use /ask inconsistencies after pull to review any new conflicts.
```

## Repo
Path: read from SOURCES.md — use the configured repository path.
If not found: stop and say "No repository path found in SOURCES.md."

## Scopes
/pull                  → all active sources (daily pull)
/pull journal          → only journal
/pull jira             → only jira
/pull confluence       → only confluence
/pull github           → only github repos
/pull web              → only web sources
/pull onboarding       → first pull – baseline mode
/pull on-demand [name] → single on-demand source from SOURCES.md
/pull retroactive missed "[desc]"     → add missed content (see retroactive mode below)
/pull retroactive new-source "[name]" → connect new source (see retroactive mode below)

---

## Refs (load before pull)
- `.claude/refs/pull-framework.md` — source resolution, knowledge derivation, output contract
- `.claude/refs/extraction-quality.md` — inclusion checklists, thoroughness, receipts
- `.claude/refs/log-writing.md` — daily log format and template
- `.claude/refs/log-links.md` — clickable source references
- `.claude/refs/tagging.md` — audience + content tags
- `.claude/refs/ai-inference.md` — AI pattern recognition rules
- `.claude/refs/consistency-check.md` — consistency check spec (Phase 4)
- `.claude/refs/decision-impact-scan.md` — decision → knowledge state cross-check (Phase 3b)

---

## Phase 0 – Source Resolution

Before any pull agent starts, resolve the full source set:

1. Read SOURCES.md (local baseline — always present)
2. Find `source-registry` entries (Type = `source-registry`)
3. Fetch each registry (Confluence API, HTTP, local file)
4. Parse content (auto-detect: markdown table, YAML, JSON, free-form)
5. Merge: local sources + external sources → runtime source list
6. Report: which registries consulted, what was found, warnings

**Rules:**
- Local sources win on ID collision
- External registries add sources, never override or remove local ones
- If a registry is unreachable or unparseable: warn and proceed with local sources
- Warnings go into pull output — never silently swallowed

The merged runtime source list is used by all subsequent phases.
Pull agents cannot distinguish local from external sources — they treat all identically.

---

## Phase 1 – Read Manifests (no tokens)
Load .lore/manifests/ for the active scope only:

| Scope | Manifests loaded |
|-------|-----------------|
| `/pull` (all) | All manifests |
| `/pull journal` | github.json only |
| `/pull jira` | jira.json only |
| `/pull confluence` | confluence.json only |
| `/pull github` | github.json only |
| `/pull on-demand [name]` | Manifest matching source type |

Compare against current source state. Build change list.
A moved or copied file with same hash = not new. Skip.

Report before Phase 2:
"Found [N] changes across [sources]:
 Journal: [N] / Jira: [N] / Confluence: [N] / GitHub: [N]
 Proceeding with pull."

---

## Phase 2 – Read Changes (by priority)

Read in this order, stop if budget exceeded:

| Prio | What | How |
|------|------|-----|
| 1 | Journal – all new entries | Full content |
| 2 | Confluence Key Pages (.lore/config.md) | Full content |
| 3 | Jira High/Critical items | Full content |
| 4 | Jira other changes | Title + status + owner only |
| 5 | Confluence other changes | Title + author + one-line summary |
| 6 | GitHub /docs and /adr changes | Full content |
| 7 | GitHub other commits | Commit message + author only |
| 8 | SharePoint/OneDrive Key-Docs | Full content |
| 9 | SharePoint/OneDrive other new files | Metadata only → pending |

Large files (PDF, PPT, large MD) → never auto-read → `.lore/pending.md`.

---

## Phase 3 – Write Log

Write to `log/daily/[TODAY].md` following `.claude/refs/log-writing.md` exactly.
The full template and tagging rules are in that ref — do not duplicate here.

Key rules:
- Audience tag mandatory on every tagged item — default: `[lead]`
- Narrative first, tags at end
- Only what actually happened
- For substantial topics (e.g. entire workshop on one theme): write extended
  narrative directly in the log — no separate files. Keep it compact but complete
  enough for a delivery lead who wasn't in the meeting.

**Contributions integration (mandatory):**
After writing pull data, before finalizing the log:

1. Read `contributions/INDEX.md` — filter for `Status=pending`
2. For each pending contribution:
   - If Type=note → integrate into "Context & Narrative" section
   - If Type=todo OR Type=correct OR Type=resolve → integrate into relevant source section with [action] tag
   - If Type=feedback → integrate into "Context & Narrative" with attribution
   - If Type=recap → integrate into "Context & Narrative" as standalone paragraph
   - If Type=watch → integrate into corresponding tagged section (Decisions/Risks/Actions/Questions)
3. Preserve From attribution in the log entry
4. Update `contributions/INDEX.md` → Status: promoted (for integrated items)
5. If contribution references a knowledge ID (DEC-*, RISK-*, OPEN-*) → add →ctx: link

Contributions without clear integration point: leave as pending — do not force.

**Index update (mandatory):** After writing the daily log, add or update the entry
in `log/INDEX.md` → Daily section. Extract: Date, Sources, Signals (3-5 key events),
Tags, Entities (3-8 names), References (DEC-*, RISK-*, OPEN-* IDs mentioned).

---

## Internal Consistency (applies to all write phases)

When adding new information to a knowledge file, ALL sections referencing the same
structure must be updated in the same operation. After writing structural information,
scan ALL sections in that file for lists, tables, counts, and overviews that reference
the same structure — update them all. A file with conflicting internal counts or
lists is a bug equivalent to missing data.

---

## Phase 3a – Decision Impact Scan

Full spec: `.claude/refs/decision-impact-scan.md`

After writing the log, for every new decision (DEC-##) found in this pull:
1. Consult `knowledge/INDEX.md` — identify files whose Key Topics or Answers relate to the decision's subject
2. Read ONLY those matched knowledge files
3. Check for activation triggers, conditional states, "benched" items
4. If a decision changes existing knowledge state → update the knowledge file immediately
5. Update `knowledge/INDEX.md` entry for any modified file (refresh Updated date, Key Topics, Answers)
6. Report: decisions scanned, state changes applied, potential impacts flagged

**This phase is mandatory.** A decision is not fully processed until its downstream
impact on knowledge/ has been verified. Skipping this phase = knowledge drift.

---

## Phase 4 – Consistency Check

Full spec: `.claude/refs/consistency-check.md`

**Handoff:** Pull writes results directly to `.lore/inconsistencies.md`.
Pull does NOT invoke `/ask inconsistencies` — it only writes the raw findings.

Report after pull:
"Consistency check complete:
 🔴 [N] Knowledge Conflicts (new)
 🟡 [N] Source Conflicts (new)
 🟢 [N] Missing Data (new)
 ✅ [N] Auto-resolved
 ⚠ [N] Stale (>14 days unresolved)
 → /ask inconsistencies to review"

---

## Phase 5 – Update Manifests

Update .lore/manifests/ with new state.

**Index updates (mandatory):**
- `knowledge/INDEX.md` — add or update entries for any new or modified knowledge files.
  Use Sachbuch format: File, What, Contains, Key Topics, Answers, Updated.
  Add Section sub-entries for files with 3+ major sections.
- `contributions/INDEX.md` — update Status for all contributions handled in this pull:
  - Integrated into log (Phase 3) → Status: promoted
  - Promoted to knowledge/ (Phase 3b decision scan or separate promotion) → Status: knowledge

---

## Phase 6 – Condensation Check

Full rules: `.claude/refs/condensing.md`

After manifests are updated, check if any logs are past their condensation threshold:

| Level | Threshold | Action |
|-------|-----------|--------|
| daily → weekly | Daily logs older than 14 days | Suggest condensing into `log/weekly/YYYY-WXX.md` |
| weekly → monthly | Weekly logs older than 3 months | Suggest condensing into `log/monthly/YYYY-MM.md` |
| monthly → quarterly | Monthly logs older than 6 months | Suggest condensing into `log/quarterly/YYYY-QX.md` |
| quarterly → yearly | Quarterly logs older than 6 quarters | Suggest condensing into `log/yearly/YYYY.md` |

### Behavior

1. **Check only** — never auto-condense. Only suggest.
2. List what's eligible:
   ```
   📦 Condensation candidates:
    • 3 daily logs (2026-05-06, 2026-05-08, 2026-05-11) → log/weekly/2026-W19.md, 2026-W20.md
    • (no weekly/monthly/quarterly candidates)
   Condense now? [yes / no / pick specific]
   ```
3. If user says **yes** → condense all candidates per `refs/condensing.md` format rules, then move source logs to `log/archive/<level>/`.
4. If user says **no** → skip, no further action.
5. If user picks specific → condense only those, archive those, leave the rest.
6. If nothing is eligible → show nothing (no "all clear" noise).

**Index update (mandatory):** When condensation happens:
- Remove condensed daily entries from `log/INDEX.md` → Daily section
- Add new weekly/monthly entry to the corresponding section in `log/INDEX.md`

### Skip conditions

- `/pull onboarding` → never suggest condensation
- If pull failed or was partial → skip condensation check
- If no daily logs exist yet → skip silently

---

## Phase 7 – State File (Leads Briefing)

After condensation check, generate a full leads-level briefing as the state file.

**Output:** `log/state/YYYY-MM-DD.md` (using today's date)
**Format:** Follows the output template defined in `.claude/skills/briefing/leads.md`

### Sources

Synthesize from everything loaded during phases 1–6, plus stable knowledge:

| Source | Used for |
|--------|----------|
| `knowledge/roadmap.md` | Milestones with days-left calculation |
| `knowledge/workstreams.md` | Per-workstream status, progress, leads |
| `knowledge/dependencies.md` | Dependencies, blockers, stalled items |
| `knowledge/decisions-open.md` | Open decisions with days-open counter |
| `knowledge/team.md` | Ownership, team changes |
| `knowledge/assignments.md` | Ownership gaps |
| `.lore/inconsistencies.md` | All severity levels (🔴, 🟡, 🟢) |
| `contributions/INDEX.md` | Pending signals tagged [risk] or [action] |
| Last 7 days of daily logs | Actions, trends, stalled detection (7+ days no change) |

### Content

All sections from the leads output template:

- **Today's Focus** — 2-3 bullets: blockers, overdue actions, expiring decisions
- **Milestones** — with date, status, owner, days left, note
- **Workstream Status** — per WS: status, progress, blockers (since when + owner), actions due, dependencies, stalled items
- **Open Actions** — by deadline, with owner and status
- **Open Decisions** — with owner, deadline, days open, impact
- **Risks** — with owner, trend (↑→↓), last update, action
- **Open Questions** — with owner and open-since date
- **Inconsistencies** — all levels with ID, type, description, status
- **Stalled Items** — items with no update 7+ days, with /escalate suggestions
- **Data Provenance** — timestamp, sources read, freshness, context coverage %

### Rules

- Write ONLY what was found in this pull + stable knowledge. Never invent.
- If a section has no data: write "No data this period." — never omit the section.
- State file does NOT update knowledge/ — it is a synthesis snapshot only.
- One state file per day. If pulled multiple times: overwrite same-day file.
- Max 2 pages. If data is thin, reduce — don't pad.
- Stalled = no log entry change in 7 days. Calculate from log dates.
- If milestone date has passed with no completion logged: mark 🔴 automatically.
- Suggest /escalate or /ask for every stalled item.

### Refinement Loop

After writing the initial state file, review it critically:

1. **Check completeness** — for each workstream: is there a concrete progress statement, a blocker with owner and date, and actions due? If any section says only "No data" but sources exist that weren't consulted: go get them.
2. **Check actionability** — can a delivery lead read this and know what to do today? If not, identify what's missing (e.g. deadlines, owners, trend direction).
3. **Fill gaps** — if gaps are found, load the specific source that would fill them:
   - Missing progress details → re-read relevant daily logs or Jira changes
   - Missing ownership → check `knowledge/team.md` or `knowledge/assignments.md`
   - Missing dependencies → check `knowledge/dependencies.md`
   - Missing risk context → check `.lore/inconsistencies.md` or `contributions/`
4. **Update the state file** with the retrieved details.
5. **Repeat** until either:
   - All sections are filled with concrete, actionable content, OR
   - The data genuinely doesn't exist (then "No data" is correct — but name what's missing)

Max 3 iterations. If still incomplete after 3: write as-is and note gaps in Data Provenance.

### Skip conditions

- `/pull onboarding` → no state file (baselines serve this purpose)
- Partial/failed pull → no state file (incomplete data = misleading)

---

## Onboarding Mode (/pull onboarding)

First pull only. Run once. Establishes the baseline.

### Steps
Step 1: Build manifests — Claude knows what exists
Step 2: Read Confluence Key Pages (from .lore/config.md) — full content
Step 3: Read Jira – Open + High/Critical items only — title + status + owner + link
Step 4: Read Journal – last 14 days — full content
Step 5: Read GitHub /docs and /adr only — full content
Step 6: Everything else → manifest + pending only

### Write Baselines
Write to `log/onboarding/` (not `log/daily/`). Mark as readonly after writing.
Baseline structure: see `.claude/refs/lore-reference.md` → "Onboarding Baseline Structure".

### Derive knowledge/
Each agent derives knowledge/ content from its source. Rules:
- Only write what is verifiable — never invent
- Mark confidence with clickable link from SOURCES.md base URL
- If a field cannot be determined: "No data — [which source would have this]"
- Update knowledge/INDEX.md

### Consistency Check
Run after onboarding. Inconsistencies are expected — flag them, don't resolve.

---

## Rules

- Never modify sources – read only
- Never read a file that hasn't changed (hash check first)
- Large files always go to pending – never auto-read
- Consistency check is mandatory – never skip
- If pull fails for a source: log it, continue with others
- If budget exceeded mid-pull: stop, write partial log, note what's missing
- Always report coverage % at end

## Parallel Pull

When pulling multiple sources (`/pull` without scope), use the Agent tool to pull
sources simultaneously instead of sequentially:

```
Agent(pull-journal) ─┐
Agent(pull-jira)    ─┤─→ collect results → write single daily log
Agent(pull-confluence)┘
```

- Each agent loads only its own refs and manifests
- Results merged into one daily log (Phase 3)
- Consistency check (Phase 4) runs AFTER all agents complete

---

## Retroactive Mode

When scope starts with `retroactive`, this is a special mode that adds content
that was missed during onboarding or connects a new source after initial setup.

Full specification: `.claude/skills/pull/retroactive.md`

Two sub-modes:
- `/pull retroactive missed "[desc]"` — content existed in source but wasn't captured
- `/pull retroactive new-source "[name]"` — entirely new source being connected

Key guarantees:
- Never modifies `log/onboarding/` baselines (they are readonly)
- Always creates explicit audit trail
- Always runs consistency check after adding content
- Always writes CHANGELOG entry
- If one agent fails: others continue, failure is logged

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- `knowledge/INDEX.md` — Phase 3b: identify knowledge files affected by new decisions
- `knowledge/assignments.md` — Phase 7: ownership gaps for state file
- `knowledge/ai-patterns.md` — Phase 7: risks and new patterns for state file

### Index Write
- `log/INDEX.md` — Phase 3: add entry for new daily log
- `knowledge/INDEX.md` — Phase 5: add/update entries for changed knowledge files
- `log/INDEX.md` — Phase 6: update on condensation (remove dailies, add weekly/monthly)
- `contributions/INDEX.md` — Phase 5: update status if contributions were promoted
