# Lore Reference — Structure, Workflows, Maintenance

Detailed reference for setup, maintenance, and skill creation.
Core principles: see `.claude/lore-design.md`.

Load this file when: creating new skills, running `/lore`, modifying Lore infrastructure,
or resolving dependency questions. NOT needed for daily operations (pull, briefing, ask).

---

## Repository Structure

```
project-root/
├── CLAUDE.md                    ← Entry point for Claude; role, startup, skill table
├── SOURCES.md                   ← What sources exist and where (human-maintained)
├── OVERRIDES.md                 ← Human corrections to source information (always wins)
├── CHANGELOG.md                 ← Session log of all Claude-made changes (auto-log rule)
├── .claude/
│   ├── lore-design.md           ← Core principles (pointer, signal, philosophy, tags)
│   ├── agents/
│   │   ├── loremaster/agent.md              ← The Loremaster (develops and guards the framework)
│   │   ├── pull-confluence/agent.md         ← Confluence pull agent (onboarding + daily)
│   │   ├── pull-jira/agent.md               ← Jira pull agent (onboarding + daily, full hierarchy)
│   │   ├── pull-journal/agent.md            ← Journal pull agent (GitHub private repo, project-level signal only)
│   │   ├── pull-sharepoint/agent.md         ← SharePoint pull agent (PPTX/DOCX extraction, multi-site, timestamp-based delta)
│   │   ├── crawl-coordinator-jira/agent.md  ← Jira crawl coordinator (tree assessment, batching, delegation)
│   │   ├── crawl-coordinator-confluence/agent.md ← Confluence crawl coordinator (size/type classification, volume batching)
│   │   └── crawl-reader/agent.md            ← Generic deep reader (source-agnostic, reads items, extracts by goal)
│   ├── rules/                         ← Always loaded (every session)
│   │   ├── never-invent.md      ← Core principle + priority hierarchy + role
│   │   ├── rag-light.md         ← Index-first retrieval law (RAG-light)
│   │   ├── session-end.md       ← Mandatory end-of-session checks (logging, watch, index completeness)
│   │   ├── output.md            ← Output standards (provenance footer, ID references, author detection)
│   │   └── privacy.md           ← Public / Confidential / Private section convention
│   ├── refs/                          ← Loaded on demand by skills/agents that need them
│   │   ├── tagging.md           ← Audience + content tags (single source of truth)
│   │   ├── condensing.md        ← Log lifecycle (daily → yearly)
│   │   ├── log-writing.md       ← How daily logs are written
│   │   ├── log-links.md         ← Clickable source references in all logs
│   │   ├── ai-inference.md      ← AI-inferred hypotheses: labeling, lifecycle, quality bar
│   │   ├── extraction-quality.md ← Pull extraction: inclusion checklists, thoroughness, receipts
│   │   ├── consistency-check.md ← Consistency check spec (what gets checked, format, resolution)
│   │   ├── decision-impact-scan.md ← Decision → knowledge state cross-check
│   │   ├── auto-log-format.md   ← CHANGELOG format reference
│   │   ├── pull-framework.md    ← Shared rules for all pull agents (derivation, dependencies, output contract)
│   │   └── lore-reference.md    ← THIS FILE — structure, workflows, maintenance
│   ├── skills/
│   │   ├── pull/SKILL.md               ← Pull from sources (includes retroactive mode)
│   │   ├── pull/retroactive.md         ← Retroactive sub-mode spec
│   │   ├── briefing/SKILL.md           ← /briefing shared base (routing + rules)
│   │   ├── briefing/exec.md            ← Executive variant template
│   │   ├── briefing/vp.md              ← VP variant template
│   │   ├── briefing/leads.md           ← Delivery lead variant template
│   │   ├── briefing/weekly.md          ← Weekly plan variant template
│   │   ├── ask/SKILL.md                ← Query the Lore knowledge base (three-layer search + traceback + inconsistencies)
│   │   ├── jot/SKILL.md                ← Capture anything — notes, todos, watch items, feedback, recaps
│   │   ├── escalate/SKILL.md           ← Draft escalation for stalled items
│   │   ├── override/SKILL.md           ← Correct wrong information (writes OVERRIDES.md)
│   │   ├── crawl/SKILL.md              ← Goal-driven crawl (Jira + Confluence, coordinator + reader pattern)
│   │   ├── publish/SKILL.md            ← Publish to Confluence (markdown + HTML embed via Forge)
│   │   ├── atlassian/SKILL.md          ← Query Jira/Confluence via acli CLI
│   │   ├── mc/SKILL.md                 ← Mission Control — in-flight delivery board
│   │   ├── artifact/SKILL.md           ← Create HTML slide decks and dashboards
│   │   ├── reasoning/SKILL.md          ← Deep multi-agent retrieval with semantic reasoning
│   │   └── lore/SKILL.md               ← Develop/test/fix the Lore framework
├── .lore/
│   ├── config.md                ← Lore instance settings: publishing defaults, global config
│   ├── pending.md               ← Items not yet read; loaded manually with /read
│   ├── inconsistencies.md       ← Open contradictions; updated after every pull
│   ├── agent-learning.md        ← Operational learnings not yet promoted to rules/skills
│   ├── loremaster-log.md        ← Loremaster session memory
│   └── manifests/
│       ├── jira.json            ← Last-known Jira state (for delta detection)
│       ├── confluence.json
│       ├── sharepoint.json      ← Last-known SharePoint state (timestamp-based delta)
│       └── github.json
├── log/
│   ├── INDEX.md                 ← Journal-format index (date, signals, entities, references)
│   ├── onboarding/              ← First pull baseline; readonly after creation
│   ├── daily/                   ← YYYY-MM-DD.md; kept for 14 days then condensed
│   ├── weekly/                  ← Kept for 3 months then condensed
│   ├── monthly/                 ← Kept for 6 months then condensed (quarterly/yearly created on demand)
│   └── archive/                 ← Condensed source logs; retained 120 days for traceback
│       ├── daily/
│       ├── weekly/
│       ├── monthly/
│       └── quarterly/
├── artifacts/
│   ├── *.html                   ← HTML slide decks and dashboards (reference only, not pulled)
│   ├── *.md                     ← Published markdown artifacts (moved here after external publish)
│   └── *.md.published           ← Sidecar files marking published artifacts (YAML metadata)
├── contributions/
│   ├── INDEX.md                 ← Signal-format index (type, what, from, status)
│   └── *.md                     ← Individual contribution files
└── knowledge/
    ├── INDEX.md                 ← Sachbuch-format index (what, contains, key topics, answers)
    ├── scope.md                 ← Project purpose, MVP scope, boundaries
    ├── roadmap.md               ← Milestones with dates
    ├── workstreams.md           ← Workstream structure, leads, capabilities
    ├── dependencies.md          ← Cross-workstream dependencies
    ├── decisions.md             ← All decided items (DEC-01 through DEC-nn)
    ├── decisions-open.md        ← Open DACIs and undecided items
    ├── assignments.md           ← Delivery ownership: capability → team → person → Jira
    ├── ai-patterns.md           ← AI-inferred patterns: hypotheses, risks, opportunities
    ├── architecture.md          ← Technology stack, patterns, ADRs
    ├── team.md                  ← Roles, stakeholders, assignments
    ├── principles.md            ← Non-negotiable project principles
    ├── watch-list.md            ← Strategic items requiring VP/exec attention
    └── context/                 ← Optional: org structure, domain context
```

---

## rules/ vs refs/ — when to load what

`rules/` files are auto-loaded into every session by Claude Code. Only foundational rules belong here.
`refs/` files are loaded on demand — skills and agents that need them must list them explicitly.

**When creating a new skill:** Check this table. If the skill writes logs, reads sources,
tags content, or uses AI inference — it needs refs. Add a `## Refs` section to the SKILL.md.

| Ref | Load when the skill… | Currently used by |
|-----|---------------------|-------------------|
| `tagging.md` | …tags items with audience/content tags | `/pull` |
| `log-writing.md` | …writes daily log entries | `/pull` |
| `log-links.md` | …adds clickable source links to logs | `/pull` |
| `condensing.md` | …condenses or references log lifecycle | `/pull` (Phase 6) |
| `ai-inference.md` | …uses AI pattern recognition (inferred risks, deps) | `/pull`, `/briefing` |
| `extraction-quality.md` | …extracts content from sources (checklists, receipts) | `/pull` agents |
| `pull-framework.md` | …is a pull agent (shared derivation, deps, output contract) | all pull agents |
| `consistency-check.md` | …runs or references the consistency check | `/pull`, `/ask inconsistencies` |
| `lore-reference.md` | …needs repo structure, dependency map, or setup checklist | `/lore`, loremaster agent |

---

## Workflows

### Workflow 1 — First Setup
1. Scaffold repo structure
2. Create CLAUDE.md, SOURCES.md, OVERRIDES.md
3. Fill all rules in .claude/rules/
4. Fill skills/pull/ and skills/briefing/ in .claude/skills/
5. Create .lore/ shells
6. Add at least one real source to SOURCES.md
7. Add navigation details for that source to `SOURCES.md` (key pages, signal hierarchy, watched pages)
8. Run `/pull onboarding` — derives knowledge/ from sources
9. Review derived knowledge/ — verify, correct, enrich
10. Run `/briefing leads` — test the system

### Workflow 2 — Daily
1. `/pull journal` (morning)
2. Tagging review in the new log entry
3. Check `/ask inconsistencies`
4. Run `/briefing leads`

### Workflow 3 — Weekly
1. `/pull` (all sources)
2. `/briefing vp` for the VP
3. Check `/ask inconsistencies knowledge`
4. Condense daily logs into weekly log
5. `/briefing weekly` for next week

### Workflow 4 — Improve Lore
1. What did not work?
2. Which rule or skill needs updating?
3. Make the change — resolve all dependencies (see Dependency Map below)
4. Document in loremaster-log.md
5. Test at next briefing

---

## Dependency Map

When any file changes, these downstream dependencies must also be updated:

| Changed file | Must also update |
|---|---|
| New skill added to `.claude/skills/` | `CLAUDE.md` skill table, `lore-reference.md` skill listing, `CHANGELOG.md`, check refs/ table (does the skill need any refs?), check plugin templates if skill should be VP-accessible |
| Skill removed | `CLAUDE.md` skill table, `lore-reference.md` skill listing, `CHANGELOG.md` |
| New rule added to `.claude/rules/` | `CHANGELOG.md` |
| New agent added to `.claude/agents/` | `CLAUDE.md` agents table, `lore-reference.md` agent listing, `CHANGELOG.md` |
| `skills/pull/SKILL.md` format changed | `log-writing.md` (if log format changes), `condensing.md` (if lifecycle changes) |
| `log-writing.md` changed | `skills/pull/SKILL.md` (must stay in sync with log format) |
| `condensing.md` changed | `skills/pull/SKILL.md` (Phase 6 references condensation), `log-writing.md` (pointer to condensing.md) |
| `knowledge/INDEX.md` | Must reflect all files in `knowledge/` |
| `log/INDEX.md` | Must reflect all files in `log/daily/`, `log/weekly/` |
| `contributions/INDEX.md` | Must reflect all files in `contributions/` |
| `SOURCES.md` structure changed | `log-links.md` (URL patterns) — source navigation lives within `SOURCES.md` itself |
| `.lore/config.md` changed | Verify publish skill and any skill using publishing defaults still works |
| Tag system changed (`tagging.md`) | `log-writing.md` (pointer), `lore-design.md` (pointer), `skills/pull/SKILL.md` |
| `CLAUDE.md` skill table changed | Must match actual files in `.claude/skills/` |
| `briefing/SKILL.md` escalation thresholds changed | `escalate/SKILL.md` (references briefing thresholds — must stay in sync) |
| `never-invent.md` priority hierarchy changed | `lore-design.md` Information Priority section (summary must match) |
| `rag-light.md` index formats changed | All skill compliance sections must stay in sync |
| Any file created/modified/deleted | `CHANGELOG.md` — session-end rule, no exceptions |

---

## Setup Minimum Viable State

The system is ready for `/pull onboarding` when all of these are true:

- [ ] All rules present and filled: rules/ (never-invent, rag-light, session-end, output, privacy) + refs/ (tagging, condensing, log-writing, log-links, ai-inference, extraction-quality, consistency-check, decision-impact-scan, pull-framework)
- [ ] skills/pull/, skills/briefing/, skills/ask/, skills/escalate/, skills/override/, skills/jot/ present and filled
- [ ] SOURCES.md has at least one real source URL/path (no placeholders)
- [ ] `SOURCES.md` has navigation details (key pages, signal hierarchy) configured for that source
- [ ] knowledge/ files exist as templates (content is derived by onboarding, not manual)

Note: knowledge/ is NOT a prerequisite to fill manually.
The onboarding pull reads sources and derives knowledge/ content automatically.
After onboarding, knowledge/ becomes the verified truth — updated by subsequent pulls.

---

## Onboarding Baseline Structure (mandatory for all sources)

Every onboarding baseline in `log/onboarding/` follows this standard structure.
This applies regardless of source type (Confluence, Jira, Journal, GitHub, etc.).

Baselines are compressed operational intelligence — not inventories.
Leadership-grade accuracy to derive actions, find details, and resolve dependencies.

```
## Pull Status          ← How the pull proceeded, what was indexed/read/reconciled
## Source Structure     ← Compact inventory: types with counts, NOT item-by-item
## Knowledge Found      ← What was new per knowledge/ file vs already known
## Decisions            ← Table: Decision | Owner | Status | Source
## Risks                ← Table: Risk | Severity | Owner | Source
## Actions              ← Table: Action | Owner | ETA | Status | Source
## Open Questions       ← Table: Question | Owner | Source
## Noteworthy           ← Partners, people, links, patterns, inconsistencies
## Milestones & Team    ← Only if this source is authoritative
```

What does NOT belong in baselines:
- Content Sensitivity Assessments (separate analysis if needed)
- Full page/ticket content or verbatim copies
- Page-by-page or item-by-item inventory listings
- Content that can be found by following the source links

Every pull must also produce a `KNOWLEDGE_DERIVATION_REPORT` — a per-file
assessment of what was created, updated, or unchanged. A pull without this
report is incomplete.

See `skills/pull/SKILL.md` → "Write Baselines" for the full template.
See each pull agent's Step 3/4/7 for source-specific details.

---

## Structural Rules

Rules that govern Lore's own consistency — not project content but the framework itself.

**Single source of truth:** Every piece of information lives in exactly one file.
Other files reference it, never duplicate it. If you find the same content in two files,
one must become a pointer to the other.

| Information | Source of truth | Others reference it |
|-------------|----------------|---------------------|
| Tags (audience + content) | `refs/tagging.md` | `refs/log-writing.md`, `lore-design.md` |
| Condensation lifecycle | `refs/condensing.md` | `refs/log-writing.md` |
| Information priority hierarchy | `rules/never-invent.md` | `lore-design.md` |
| Consistency check spec | `refs/consistency-check.md` | `rules/never-invent.md` (pointer) |
| URL patterns for sources | `SOURCES.md` | `refs/log-links.md` |
| Index formats (Sachbuch/Journal/Signal) | `rules/rag-light.md` | skill SKILL.md files (compliance sections) |

**Every source needs navigation details:** When a source is added to `SOURCES.md`,
add navigation sub-sections (key pages, signal hierarchy, delta detection) directly below
the source block. No separate config.md entry needed.
