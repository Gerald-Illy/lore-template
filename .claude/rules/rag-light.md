# Rule: RAG-Light — Index-First Intelligence

---

## Law

All information in Lore MUST be indexed. Indexes ARE the retrieval layer.

1. **Read = Index First.** Every skill that reads information MUST consult the
   relevant index before opening any file. The index tells you which files
   contain what. Never scan directories. Never guess.

2. **Write = Index Update.** Every skill that creates or modifies a file MUST
   update the relevant index in the same operation. A write without an index
   update is incomplete — equivalent to writing a file with no name.

3. **Priority Hierarchy.** When retrieving information, consult indexes in this order:
   1. OVERRIDES.md (self-indexed — table IS the retrieval surface, always pre-loaded)
   2. knowledge/INDEX.md
   3. log/INDEX.md
   4. contributions/INDEX.md
   5. SOURCES.md (remote source registry)

   **Published files:** Files with a `.published` sidecar (e.g. `file.md.published`) live in
   `artifacts/` and are NOT in the retrieval hierarchy. They are excluded from `/ask` unless
   the user explicitly asks about publication history. The external page is the source of truth.

4. **Completeness.** If a file has no index entry, it effectively does not exist
   for retrieval. Surface missing entries as gaps.

---

## Index Locations

| Source | Index file | Format | Maintained by |
|--------|-----------|--------|---------------|
| knowledge/ | knowledge/INDEX.md | Sachbuch | /pull (Phase 5), /jot correct |
| log/ | log/INDEX.md | Journal | /pull (Phase 3), condensation |
| contributions/ | contributions/INDEX.md | Signal | /jot (all types), /publish |
| OVERRIDES.md | (self-indexed) | — | /override |
| Remote sources | SOURCES.md | — | human-maintained |

---

## Format: Sachbuch (knowledge/)

Knowledge files are reference material: compressed, structured, often table-based.
Retrieval question: **"Does this file cover my topic?"**

### Main Table

```
| File | What | Contains | Key Topics | Answers | Updated |
```

| Field | Purpose |
|-------|---------|
| File | Relative path (clickable link) |
| What | 1-sentence semantic summary |
| Contains | What TYPE of structured data + quantity (e.g. "30 DEC-*, 5 OPEN-*") — solves entity explosion for table-heavy files. Use `—` for narrative files. |
| Key Topics | Topic clusters the file covers (not individual entities) |
| Answers | Questions this file can answer — maps directly to /ask queries |
| Updated | Date of last meaningful change |

### Section Sub-Table (large files with 3+ major sections)

```
| File | Section | Answers | Key Topics |
```

Section entries enable targeted reading of specific parts without loading the full file.

**No "Entities" field.** For reference files, "Contains" + "Key Topics" is the right
abstraction. Individual entity listing would explode.

---

## Format: Journal (log/)

Log files are narrative: context-rich, timestamped, with concrete events.
Retrieval question: **"Did something relevant happen on this day?"**

### Table

```
| File | Date | Sources | Signals | Tags | Entities | References |
```

| Field | Purpose |
|-------|---------|
| File | Relative path |
| Date | YYYY-MM-DD |
| Sources | Which sources were pulled (Journal, Jira, Confluence, etc.) |
| Signals | 3-5 key things that happened — the semantic retrieval hook |
| Tags | Content tags from tagging.md ([decision], [risk], [event], etc.) |
| Entities | Concrete names mentioned (3-8 per entry — dailies don't explode) |
| References | Which knowledge-IDs (DEC-*, RISK-*, OPEN-*) are referenced — enables cross-retrieval |

### Sections

Separate tables for: Daily, Weekly, Monthly, Onboarding Baselines.
Each follows the same column structure adapted to its lifecycle stage.

**Entities ARE appropriate here** — a daily log has 3-8 concrete names, not 55.

---

## Format: Signal (contributions/)

Contributions are single signals: short, typed, unprocessed.
Retrieval question: **"Are there unprocessed signals about my topic?"**

### Table

```
| File | Type | What | From | Tags | Date | Status |
```

| Field | Purpose |
|-------|---------|
| File | Relative path |
| Type | Matches /jot types: note, todo, correct, resolve, feedback, recap, watch |
| What | 1-sentence description of the signal |
| From | Attribution (who contributed this) |
| Tags | Content tags from tagging.md |
| Date | When contributed |
| Status | Lifecycle: pending → reviewed → promoted → published → archived |

**No "Answers", no "Contains".** A signal is a signal — simple and direct.

---

## Published Files — `.published` Sidecar Convention

A file is marked as published by creating a companion sidecar file with the same name and a `.published` extension.

**Example:**
```
artifacts/2026-05-05-workstream-redesign.md           ← source file (moved to artifacts/ on publish)
artifacts/2026-05-05-workstream-redesign.md.published ← sidecar with publish metadata
```

**Sidecar format (YAML):**
```yaml
published_to: https://{CONFLUENCE_BASE}/wiki/spaces/{SPACE}/pages/PAGE_ID
published_date: YYYY-MM-DD
published_title: "Actual Page Title"
page_id: "PAGE_ID"
space: SPACE
original_source: contributions/
```

**Retrieval rule:** When a `.published` sidecar exists for a file, that file is excluded from
standard retrieval (the external page is the source of truth). Include it only when the user
explicitly asks about publication history or already-published content.

**Duplicate check:** Before publishing, check `contributions/INDEX.md` → Published table for an
existing `.published` sidecar on the candidate file.

---

## Retrieval Pattern

When a skill needs information, it follows this pattern:

```
1. State the retrieval need (what am I looking for?)
2. Scan relevant index(es) in priority order
3. Match: Key Topics / Answers / Signals / Entities against the need
4. Load ONLY the matched files (or sections)
5. If nothing matches: state "not indexed" — do not scan directories
```

### Example: /ask "What's blocking Platform Services?"

```
OVERRIDES.md → pre-loaded, check for PS corrections
knowledge/INDEX.md:
  → Key Topics contain "Platform Services"? → workstreams.md ✓, dependencies.md ✓
  → Answers contain "blocking"? → dependencies.md ✓, decisions-open.md ✓
log/INDEX.md:
  → Entities contain "Platform Services"? → daily/2026-05-20.md ✓
  → Tags contain [risk]? → filter further
contributions/INDEX.md:
  → Status=pending, Tags contain [risk]? → check for unprocessed signals

Result: Load 3 knowledge files + 1 daily instead of everything.
```

---

## Enforcement

### On Write

If a skill writes a file without updating the corresponding index:
- Session-end check flags it as incomplete
- The missing index entry MUST be added before the session ends

### On Read

If a skill reads a file without first consulting the index:
- This is a rule violation (same severity as a never-invent violation)
- Exception: files explicitly listed in CLAUDE.md "Always read first" (OVERRIDES.md, knowledge/INDEX.md, .lore/agent-learning.md)

### Skill Compliance

Every skill MUST declare in its SKILL.md:
- Which indexes it reads (## Index Read)
- Which indexes it writes (## Index Write)
- The compliance statement: "This skill is RAG-light compliant."

---

## Exceptions

1. **Always-loaded files** (per CLAUDE.md) bypass index-first: OVERRIDES.md,
   knowledge/INDEX.md itself, .lore/agent-learning.md
2. **Index files themselves** are never indexed (no meta-index)
3. **SOURCES.md** is human-maintained and serves as the remote source index —
   no parallel index needed
4. **Small config files** (.lore/config.md, .lore/inconsistencies.md) are loaded
   directly by skills that need them — too small and too stable to benefit from indexing
