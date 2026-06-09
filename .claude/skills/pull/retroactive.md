---
description: Retroactively add missed content or new sources to Lore without breaking history. Two modes: missed (content existed in sources but wasn't captured during onboarding) and new-source (entirely new source added after initial onboarding).
---

## --help

When invoked as `/retroactive --help` or `/retroactive -h` — print this and stop:

```
/retroactive — Add missed content or new sources to Lore without breaking history

Usage:
  /retroactive missed "[description]"
  /retroactive new-source "[name]"

Modes:
  missed       content existed in source during onboarding but wasn't captured
  new-source   new source being connected to Lore for the first time

Examples:
  /retroactive missed "M2 scope decision from April Confluence page"
  /retroactive missed "RISK-03 was logged in Jira but not in our log"
  /retroactive new-source "Partner SharePoint — Telekom project docs"
  /retroactive new-source "Internal ADR repo for the project"

What happens (missed):
  knowledge/ updated → retroactive log entry at original date → inconsistency check → CHANGELOG

What happens (new-source):
  SOURCES.md updated → onboarding baseline pulled → knowledge/ merged → manifests created → CHANGELOG

Guarantee: audit trail always created. log/onboarding/ baselines are never modified.
```

# Skill: /retroactive [missed|new-source]

Adds content to Lore that was not captured during initial onboarding —
either because something was overlooked, or because a new source is being connected.

Never modifies `log/onboarding/` baselines.
Always creates an explicit audit trail of when and why content was added retroactively.

---

## Modes

```
/retroactive missed "[description]"    → missed content from existing source
/retroactive new-source "[name]"       → new source, never pulled before
```

---

## Mode A: /retroactive missed

Use when content existed in a source during onboarding but was not captured.

### Step 1 – Identify what was missed

Ask if not clear:
- What is the content? (decision, risk, action, dependency, concept, scope item)
- What source does it come from? (Confluence page, Jira item, Journal entry, SharePoint doc)
- What is the original date of that content?

### Step 2 – Classify the content

Determine which knowledge/ file(s) it belongs to:

| Content type | knowledge/ file |
|---|---|
| Scope change, constraint, MVP definition | knowledge/scope.md |
| Dependency, blocker, cross-team link | knowledge/dependencies.md |
| Team member, role, ownership | knowledge/team.md |
| Milestone, deadline, sequencing | knowledge/roadmap.md |
| Architecture choice, design decision | knowledge/architecture.md |
| Workstream definition, responsible team | knowledge/workstreams.md |
| Principle, non-negotiable, design rule | knowledge/principles.md |

If it spans multiple files: add to all relevant files.

### Step 3 – Add to knowledge/

Add the content to the appropriate knowledge/ file.
Follow the file's existing format exactly.
Add source link and original date.
Mark with: `<!-- retroactively added [TODAY] from [source] -->`

### Step 4 – Write retroactive log entry

Write a log entry dated to the **original content date** (not today).
File: `log/daily/[ORIGINAL-DATE].md`

If a log file for that date already exists → append at the end.
If no log file exists → create it as a minimal retroactive log.

Format:
```markdown
# Daily Log – [ORIGINAL-DATE] [retroactive]
<!-- Added retroactively on [TODAY] — missed during onboarding -->

## Retroactive Addition
Source: [source name + link]
Added on: [TODAY]
Reason: Missed during initial onboarding pull.

---

## [section: Decisions / Risks / Actions / etc.]
- [audience][tag] [Description] – Owner: [Name] – →ctx:[ID if applicable]
  `[retroactive][source: name, original date]`
```

### Step 5 – Check for inconsistencies

Does the newly added content contradict anything in knowledge/?
→ If yes: add entry to `.lore/inconsistencies.md` immediately.
→ If no: note explicitly in output "No new inconsistencies detected."

### Step 6 – Update CHANGELOG and loremaster-log

CHANGELOG entry (auto-log rule):
```
## [TODAY] – Retroactive addition: [brief description]

[One sentence: what was missed, which source, why it matters now.]

Files: `knowledge/[file].md`, `log/daily/[ORIGINAL-DATE].md`
```

No loremaster-log entry needed unless `.claude/` or `.lore/` files were changed.

---

## Mode B: /retroactive new-source

Use when a new source is being connected to Lore for the first time,
after the initial onboarding has already run.

The content in the new source is self-dating (its own timestamps).
What needs an explicit record is: **when this source was added to Lore**.

### Step 1 – Register the source

Add to `SOURCES.md`:
```
## [Source Name]
Type: [Confluence/Jira/SharePoint/GitHub/...]
URL/Path: [url or local path]
Added to Lore: [TODAY]
Status: Active
Key pages / entry point: [...]
Pull agent: [agent name or "manual"]
```

Note explicitly: `Added to Lore: [TODAY]` — this is the record of when Lore started tracking it.

### Step 2 – Run baseline pull

Pull the source in onboarding mode (same as `/pull onboarding` but for this source only).

Apply all onboarding extraction rules:
- Manifests first
- Key pages full content, everything else metadata + pending
- Apply Checklist A (relevance gate) and Checklist B (thoroughness)
- Produce EXTRACTION_RECEIPT

### Step 3 – Write baseline file

Write to `log/onboarding/[source-name]-baseline.md`.

Use the **standard onboarding baseline structure** (from pull skill).
Add header:
```markdown
<!-- SOURCE ADDED AFTER INITIAL ONBOARDING -->
<!-- Connected to Lore: [TODAY] -->
<!-- Source content dates: [date range of content pulled] -->
<!-- This is NOT a retroactive miss — this source did not exist in Lore at onboarding time -->
```

The date range in the header makes the relationship to the initial baseline clear:
- If source content predates onboarding → note it explicitly in the Noteworthy section
- If source content is newer → no special note needed (self-evident from dates)

### Step 4 – Derive knowledge/

Same as onboarding Step 5 (Derive knowledge/).
Merge new findings into existing knowledge/ files.
For each merged item: add source link + `[source added: TODAY]` annotation.

If new content contradicts existing knowledge/:
→ Surface as 🔴 Knowledge Conflict in `.lore/inconsistencies.md` immediately.
→ Do NOT silently overwrite existing knowledge.

### Step 5 – Update manifests

Create `.lore/manifests/[source-name].json` (or equivalent format for source type).
Update `knowledge/INDEX.md` to reflect newly added knowledge.

### Step 6 – CHANGELOG

```
## [TODAY] – New source connected: [source name]

[One sentence: what this source is, why it was added, what new knowledge it brought.]

Files: `SOURCES.md`, `log/onboarding/[source-name]-baseline.md`, `knowledge/[files].md`
```

---

## When to use which mode

| Situation | Mode |
|---|---|
| "I noticed during onboarding that X was not captured" | `missed` |
| "We have a SharePoint site / Confluence space that wasn't connected yet" | `new-source` |
| "A Jira project was missing from the initial pull" | `new-source` |
| "I found a decision in a Confluence page that wasn't logged" | `missed` |
| "A new team member created a doc that has relevant context" | `missed` |
| "We're connecting a new external source (partner docs, contract, etc.)" | `new-source` |

If unclear: ask before proceeding.

---

## Audit Trail Guarantee

After any `/retroactive` invocation, the following must exist:

| What | Where |
|---|---|
| The content itself | `knowledge/[file].md` |
| When it was added (for missed) | `log/daily/[ORIGINAL-DATE].md` with `[retroactive]` marker |
| When source was connected (for new-source) | `SOURCES.md` "Added to Lore" field + baseline header |
| CHANGELOG record | `CHANGELOG.md` top entry |
| Inconsistency check result | either new entry in `.lore/inconsistencies.md` or explicit "none found" in output |

---

## Rules

- Never modify existing `log/onboarding/` baseline files — they are readonly
- Retroactive log entries always use the **original content date**, not today
- New source baselines always state both: content date range AND Lore-connection date
- Never silently add content — always write CHANGELOG
- If knowledge entry is created retroactively: add `[retroactive]` comment in the file header

---

