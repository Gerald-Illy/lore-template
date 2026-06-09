# Skill: /crawl

Goal-driven crawler for Jira and Confluence.
Unlike `/pull` (ingest everything new), `/crawl` answers a specific question
by intelligently navigating a source tree.

---

## --help

When invoked as `/crawl --help` or `/crawl -h` — print this and stop:

```
/crawl — Goal-driven crawler for Jira and Confluence

Usage:
  /crawl jira <entry-point> [goal] [depth]
  /crawl confluence <entry-point> [goal] [depth]

Arguments:
  entry-point   Jira key (e.g. PROJ-1000) or Confluence page ID
  goal          Optional: question to answer (quoted string)
  depth         Optional: tree | overview | full (default: tree → present & ask)

Examples:
  /crawl jira PROJ-1000
  /crawl jira PROJ-1000 "what blocks Q3?"
  /crawl jira PROJ-1000 "status overview" overview
  /crawl confluence 12345678 "what decisions were made?"

Tip: Unlike /pull (ingest everything new), /crawl answers a specific question.
     Use /atlassian for quick lookups; /crawl for tree traversal with a goal.
     Default stops after tree discovery — you decide what to read next.
```

---

## Usage

```
/crawl jira <entry-point> [goal] [depth]
/crawl confluence <entry-point> [goal] [depth]
```

**Examples:**
```
/crawl jira PROJ-1000
/crawl jira PROJ-1000 "what blocks Q3?"
/crawl jira PROJ-1000 "status overview" overview
/crawl confluence 12345678 "architecture decisions" full
```

---

## Parameters

| Parameter | Required | Values | Default |
|-----------|----------|--------|---------|
| `source` | yes | `jira` or `confluence` | — |
| `entry_point` | yes | Jira key or Confluence page ID | — |
| `goal` | no | Free text describing what to find | — |
| `depth` | no | `tree`, `overview`, `full` | `tree` |

### Depth behavior

| Depth | What happens | Content read |
|-------|-------------|--------------|
| `tree` | **Scripts only.** Discover full hierarchy + external deps. Show tree (down to Epic level — stories as counts). Ask user what to do next. | Nothing (metadata only) |
| `overview` | Read entry point + all items down to Epic level (descriptions + comments). Stories/Tasks/Bugs only as counts. | Down to Epic |
| `full` | Read everything including Stories, Tasks, Bugs. Follow blocking links one hop. | All levels |

### Default behavior (no depth specified)

**Just run the scripts.** The script traverses the full hierarchy (unlimited depth) and resolves all external dependencies. Show the user:
1. Tree structure (visual, compact — full depth)
2. External dependencies (resolved: type, summary, status)
3. Delta summary (new/changed/unchanged)
4. Suggestions for what to investigate

Then **ask the user** what to do next. Don't spawn agents, don't read content, don't write files.

The user can then say:
- "Read all delta items"
- "Look at PROJ-1001 in detail"
- "Only the blockers"
- "Give me the full overview"
- "Save this" (→ creates artifact)

---

## Output

**Default: session only.** Everything stays in conversation. No files written.

Files are ONLY created when the user explicitly asks ("save this", "write it down", "artifact").
When writing is requested, write to: `artifacts/crawl-<source>-<date>-<goal-slug>.md`

**No writes to:** `log/`, `knowledge/`, `contributions/` — this is experimental.

---

## Prerequisites

- `acli` must be in PATH and authenticated (see `/atlassian` skill)
- Python 3.10+ available

---

## Workflow

### Phase 1 — Tree Discovery (always runs, deterministic)

```bash
python .claude/skills/crawl/scripts/jira_tree.py <entry-point>
python .claude/skills/crawl/scripts/confluence_tree.py <space-key>
```

**Jira script:**
1. Traverses the full hierarchy (unlimited depth — follows children until there are none)
2. Resolves all external dependencies (fetches type, summary, status for linked items outside the tree)
3. Merges into existing manifest (extends/updates, never removes)
4. Computes delta against previous manifest state
5. Ensures bidirectional dependency consistency

**Confluence script:**
1. Fetches ALL pages in a space in a single API call (`page list --space`)
2. Builds parent/child tree from `parentId` relationships
3. Classifies pages by type (meeting-log, decision, reference, requirements, planning, operational)
4. Merges into existing manifest (extends/updates, never removes)
5. Computes delta via version number comparison

Scripts produce:
- `crawl-jira-manifest.json` — single persistent Jira manifest
- `crawl-confluence-manifest.json` — single persistent Confluence manifest

### Phase 2 — Present & Ask (default stop point)

Render the tree using the appropriate render script:

```bash
python .claude/skills/crawl/scripts/render_jira_tree.py [--manifest PATH] [--entry-point KEY]
python .claude/skills/crawl/scripts/render_confluence_tree.py [--manifest PATH] [--entry-point SPACE:KEY]
```

**Jira render** reads `crawl-jira-manifest.json` and outputs a fixed-width column-aligned tree:
```
Key              | Summary          | Status      | @Assignee       | [Location]  | Stories
VP  PROJ-123    Project MVP…       In Progress                      [PROJ]
├─ VI  PROJ-456  Some feature…     Open          @Person           [PROJ]
│   ├─ Epic X-1  Epic title…       In Progress   @Person           [PROJ/team]   ← 5 stories (2 closed)
│   └─ Epic X-2  Another epic…     Open          @Person           [PROJ/team]   ← 3 stories
└─ VI  PROJ-789  Another VI…       Open                            [OTHER]
```

**Format rules (hardcoded in script):**
- VP/VI show `[OwningProgram]` short name
- Epics show `[PROJECT/team]` (project from key prefix, team short name)
- Only blocking dependencies shown (below epic, with resolution status)
- Stories collapsed as counts: `← N stories (X closed)`
- Summary truncated with `…` + 2-char gap before status column
- No blank lines between childless VIs

After rendering, show:
1. **Tree output** (from render script)
2. **Delta summary** — what's new, what changed, what's unchanged
3. **Suggestions** — based on tree structure and delta

**STOP HERE unless depth is `overview` or `full`, or user gives explicit instruction.**

### Phase 3 — Coordinate (only when user requests content reading)

Spawn the appropriate coordinator agent:

**Jira:** `.claude/agents/crawl-coordinator-jira/agent.md`
**Confluence:** `.claude/agents/crawl-coordinator-confluence/agent.md`

Pass to coordinator **in the prompt** (not as a file to read):
```
goal:          <the user's goal>
depth:         <overview | full>
root:          <key, type, summary, status>
children:      <summary — key, type, status, child count, blocking deps>
delta:         <list of new/changed keys>
total_items:   <number>
```

**Agents never read manifest or tree files.** Everything is in the prompt.

### Phase 4 — Synthesize

Present findings in conversation (session mode). Structured by theme, not by tree position.

If user asks to save: write artifact following the template below.

---

## Artifact Template (when writing is requested)

Organized by **signal urgency and theme**, not by tree position.
Every Jira key is a link: `[KEY]({jira_base}/browse/KEY)` — derive `jira_base` from SOURCES.md (see `.lore/config.md` — Jira section).

```markdown
# <Goal> — <Entry Point> — <Date>

**Goal:** <what was asked>
**Entry point:** [KEY](link) (<type>)
**Scope:** <N> items across <N> levels
**Items read:** <N>
**Reads used:** <N> / 200 limit

---

## Tree Structure

<Visual tree. Compact. Signals inline.
 Show: type, [KEY](link), summary, status, owner, child count.
 Mark: ⚡ blocking deps, ⚠ risks/gaps.
 Collapse stories: "← N stories (X done, Y open)">

---

## Critical Signals

### 1. <SIGNAL TITLE>
<What's wrong, who owns it, impact, what's needed.>

---

## <Thematic Sections>
<Compact tables: Key | Summary | Status | Owner | Signal>

---

## Dependencies
<Sequential chains + active external deps>

---

## Ownership & Gaps
<Concentration risks. Unowned critical items.>
```

**Key rules:**
- **Signals first.** Most important at the top.
- **Group by theme/urgency**, not tree hierarchy.
- **Tables for data**, prose for analysis. Never dump descriptions verbatim.
- **No per-item sections.** Items appear in tables or signal discussions.

---

## Agents

| Agent | Role |
|-------|------|
| `crawl-coordinator-jira` | Jira tree assessment + delegation |
| `crawl-coordinator-confluence` | Confluence tree assessment + delegation |
| `crawl-reader` | Generic deep reader (source-agnostic) |

The reader is source-agnostic. Coordinators pass it the right acli commands.

---

## Manifests

One file per source. Only read/written by Python scripts — never by Claude or agents.

- Always extended or updated, never reduced
- Supports multiple entry points in one file
- Overlapping trees merge automatically

### Jira: `.lore/manifests/crawl-jira-manifest.json`

Trees = parent/child hierarchy only, dependencies are cross-references.

```json
{
  "format_version": 1,
  "last_updated": "ISO timestamp",
  "entry_points": ["PROJ-1000", "PROJ-1001"],
  "nodes": {
    "KEY": {
      "type": "...", "summary": "...", "status": "...",
      "updated": "...", "assignee": "...", "comment_count": N,
      "parent": "KEY"|null, "children": ["KEY"],
      "deps_out": ["KEY"], "deps_in": ["KEY"],
      "owning_program": "...", "team": "..."
    }
  }
}
```

### Confluence: `.lore/manifests/crawl-confluence-manifest.json`

Tree derived from `parentId` relationships. No body content stored (only fetched during overview/full reads).

```json
{
  "format_version": 1,
  "last_updated": "ISO timestamp",
  "entry_points": ["space:{SPACE}"],
  "nodes": {
    "PAGE_ID": {
      "title": "...", "status": "current",
      "parent_id": "PAGE_ID"|null, "children": ["PAGE_ID"],
      "version": N, "updated": "ISO timestamp",
      "type_class": "decision|meeting-log|reference|requirements|planning|operational|unknown"
    }
  }
}
```

**Agents never read these files.** The skill pre-digests tree data into the coordinator prompt.

---

## Constraints

- Default = scripts only, then ask. Never auto-read content.
- Never write files unless explicitly asked.
- Never modify `/pull` manifests
- Scripts are deterministic — no LLM involvement in tree discovery
- Coordinator decides what to read — reader executes
- Reader never spawns further agents
- If acli fails for an item: mark as gap, continue
- Every Jira key in output MUST be a markdown link

---

## References

- `.claude/refs/extraction-quality.md` — inclusion checklist + thoroughness checklist (applied by crawl-reader during content extraction)
- `.claude/refs/log-links.md` — clickable source reference format (all output links must follow this)
- `.claude/refs/tagging.md` — audience + content tags (applied when findings are saved as artifacts)

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- `knowledge/INDEX.md` — when synthesizing findings, consult Key Topics to identify related knowledge context
- `log/INDEX.md` — when checking for prior crawls of the same entry point, scan References

### Index Write
- None (session-only by default — artifacts/ is not indexed. If crawl findings are later promoted to knowledge/ or log/ by another skill, that skill handles the index update)

---

## Known Behaviors

| Behavior | Verified | Impact |
|----------|----------|--------|
| VIs have long descriptions (500-2000 words) | 2026-05-18 | Max 3-5 VIs per reader batch |
| Epics have medium descriptions (~100-500 words) | 2026-05-18 | 8-12 Epics per reader batch |
| Stories/Tasks are short (1-3 sentences) | 2026-05-18 | 15-20 per reader batch |
| Bugs are variable (often detailed) | 2026-05-18 | 8-12 per reader batch |
| JQL batch is 17x more efficient | 2026-05-18 | `search --jql "key in (...)"` fetches 20 items/call |
| Comments come FREE in search response | 2026-05-18 | `--fields "...,comment"` returns full content |
| ADF descriptions need parsing | 2026-05-18 | Extract `content[].content[].text` recursively |
| Windows encoding issues | 2026-05-18 | Use `encoding="utf-8", errors="replace"` |
| Confluence `page list` returns all pages in one call | 2026-05-20 | Single API call for entire space (~1.3s for 56 pages) |
| Confluence body not in `page list` response | 2026-05-20 | Body only via individual `page view` — tree discovery stays metadata-only |
| Confluence type classifiable from title patterns | 2026-05-20 | meeting-log, decision, reference, requirements, planning, operational |

---

## Read Budget

Each crawl has a **200-read limit** (acli calls total across all agents).
A JQL batch of 20 items = 1 read. Individual `view` = 1 read.

If the crawl needs more than 200 reads:
- Stop and report what has been covered
- Explain what remains and why it matters
- Ask for extension
