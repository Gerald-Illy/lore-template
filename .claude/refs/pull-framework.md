# Pull Framework — Shared Rules for All Pull Agents

This file defines behavior shared across all pull agents (Confluence, Jira, Journal, SharePoint).
Each agent references this framework and adds only its source-specific logic.

---

## Always Read First (shared base)

Every pull agent MUST read these before any operation:

1. `.claude/refs/extraction-quality.md` — resolution level, inclusion checklist, thoroughness checklist
2. `.claude/refs/ai-inference.md` — when and how to use AI pattern recognition
3. `.claude/lore-design.md` — how Lore works (pointer principle, log format, tags)

Each agent adds its own source-specific items (SOURCES.md entries, config, manifest).

---

## Knowledge Derivation (MANDATORY — never skip)

This step applies to EVERY pull — onboarding or daily. No exceptions.

### Warning

> **This step is NOT optional.** Every pull must evaluate what knowledge/ files
> need creating or updating. Skipping this step means the pull is incomplete.
> If token budget is exhausted, stop and report "knowledge derivation pending"
> rather than silently skipping.

### Derivation Checklist

For each knowledge/ file listed in the agent's mapping table:

1. Read the current file (or note it doesn't exist yet)
2. Compare against what was just pulled
3. Decide: create / update / no change needed
4. If update: make the edit with source link
5. If no change: explicitly state why (e.g., "already captured from Journal source")

### KNOWLEDGE_DERIVATION_REPORT Format

```
KNOWLEDGE_DERIVATION_REPORT:
- knowledge/[file].md: [created|updated|unchanged — reason]
```

Each agent lists its own specific knowledge/ files in this report.
This report is part of the output contract. A pull without this report is incomplete.

### Rules

- Only write what is verifiable from the source
- Mark derived content with clickable link to the source
- If conflicting info across sources: flag as inconsistency, don't resolve
- If info cannot be determined: leave field blank with explanation
- If the same information is already in knowledge/ from another source: do not duplicate — cross-reference

---

## Dependencies Extraction (MANDATORY)

Dependencies are critical delivery intelligence. Every pull must actively search for them.
Use BOTH explicit source extraction AND AI pattern recognition.

### What Counts as a Dependency

- Workstream A blocked by Workstream B (explicit or implicit)
- Decisions that gate other work ("X cannot start until Y is decided")
- External dependencies (partners, vendors, compliance, other R&D teams)
- Resource dependencies (person needed but not available, skill gap)
- Technical dependencies (service X requires service Y, migration prerequisite)
- Timeline dependencies (event A must happen before event B)

Each agent defines its own "Where to find dependencies" section with source-specific guidance.

### AI-Inferred Dependencies

Beyond what is explicitly stated, actively look for dependencies that FOLLOW LOGICALLY
from architecture, team structure, feature composition, business model, infrastructure,
compliance, and release model.

Each agent defines its own source-specific AI-inference examples.

### MANDATORY LABELING

> Every AI-inferred dependency MUST be marked with `[AI-inferred]`.
> Format: `[AI-inferred] [Description] — Reasoning: [why this likely exists]`

This is non-negotiable. The delivery lead must always know what came from a source
vs. what was pattern-matched by AI. Never mix inferred and source-verified dependencies.

### Extraction Rules

- Record: what depends on what, who owns the blocking side, current status, since when
- If a dependency has no owner: flag it — ownerless dependencies are invisible risks
- If a dependency has been open >14 days: mark as potential escalation
- Cross-reference with `knowledge/dependencies.md` — add new, verify existing
- AI-inferred dependencies go into a SEPARATE subsection in `knowledge/dependencies.md`

---

## Output Contract Structure

Every pull agent returns structured output to the main session.
Agents never write files directly unless explicitly told to.

### Onboarding Output Skeleton

```
BASELINE:
[full baseline content]

KNOWLEDGE_DERIVED:
[for each knowledge/ file: what was derived and from which source item]

KNOWLEDGE_DERIVATION_REPORT:
[agent-specific file list]

MANIFEST:
[full JSON for the agent's manifest]

EXTRACTION_RECEIPT:
[see format below]

INCONSISTENCIES:
[any conflicts found against knowledge/]
```

### Daily Output Skeleton

```
CHANGES:
[list of changed items with summaries]

LOG_ENTRIES:
[formatted entries for the daily log]

KNOWLEDGE_UPDATES:
[any knowledge/ files that need updating]

KNOWLEDGE_DERIVATION_REPORT:
[agent-specific file list]

MANIFEST_UPDATE:
[updated entries for the manifest]

EXTRACTION_RECEIPT:
[see format below]
```

### EXTRACTION_RECEIPT Format

```
EXTRACTION_RECEIPT:
- Sources processed: [N] [source-specific unit]
- Structured sections found: [N]
- Items at VI level extracted: [N]
- Items aggregated (below VI level): [N] — [summary]
- Items skipped (exclusion criteria): [N] — [which criteria]
- Dependencies found: [N] source-verified + [N] AI-inferred
- Checklist A applications: [N] evaluated, [N] included, [N] excluded
- Checklist B score: [N]/10
- Checklist B gaps: [any unchecked items]
```

Daily mode may omit Checklist A line if no new items were evaluated.

---

## Consistency Check

After every pull, compare derived knowledge/ against what was found in the source.
Flag any inconsistencies in `.lore/inconsistencies.md`.

**At onboarding:** flag everything, resolve nothing. Inconsistencies are expected.

**Criticality rules:**
- 🔴 Knowledge Conflict — source state contradicts a verified knowledge/ statement
- 🟡 Source Conflict — two items within the same source contradict each other
- 🟢 Missing Data — item missing owner, deadline, or milestone link

---

## Core Prohibitions (all pull agents)

No pull agent ever:
- Resolves inconsistencies (only surfaces them)
- Skips the manifest update
- Invents information not found in the source
- Reads items/pages/files that haven't changed (delta check first)
- Skips knowledge derivation — a pull without KNOWLEDGE_DERIVATION_REPORT is incomplete and must not be committed
- Hardcodes instance URLs, project keys, file paths, or label names — always reads from SOURCES.md and config.md
- Auto-reads attachments/images by default — logs as pending

Each agent adds its own source-specific prohibitions.

---

## Onboarding Baseline Template (shared structure)

All baselines follow this section structure (agents customize content):

```markdown
# [Source] Baseline – [Identifier]
<!-- READONLY: Written [DATE]. Do not modify. -->

## Pull Status
[Pull date, mode, tool, source identifiers, counts]

## Source Structure
[Compact overview — types/categories with counts, not item-by-item]

## Knowledge Found
[Table: knowledge/ file | New from this source | Already known | Source items]

## Decisions
[Table: # | Decision | Owner | Status | Source]

## Risks
[Table: # | Risk | Severity | Owner | Source]

## Actions
[Table: # | Action | Owner | ETA | Status | Source]

## Open Questions
[Table: # | Question | Owner | Source]

## Noteworthy
[Cross-source inconsistencies, partners, patterns, anything delivery-relevant]
```

Agents may add source-specific sections (e.g., Milestones & Team, Per-Level Breakdown).
