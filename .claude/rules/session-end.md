# Rule: Session End

What must happen before any session ends.

---

## Merge Check (before any other action)

If `git status` shows "have diverged" or unmerged paths at session start or before commit:

1. Run `git pull` (or continue an in-progress merge)
2. If conflicts: apply `.claude/refs/merge-resolution.md` rules
3. Stage resolved files, verify no conflict markers remain
4. Report briefly what was merged from the other side

This takes priority over all other session-end steps. A session must not
commit on top of unresolved conflicts.

---

## Logging

Two logs, different scopes:

| Log | Scope | When |
|-----|-------|------|
| `CHANGELOG.md` | Project content | `knowledge/`, `OVERRIDES.md`, `SOURCES.md` |
| `.lore/loremaster-log.md` | Framework infrastructure | `.claude/` (rules, skills, agents, refs) |

No silent edits. No exceptions.

**CHANGELOG format** (newest first):
```
## [YYYY-MM-DD] – [Title]

[One sentence: what changed and why.]

Files: `path/to/file`, `path/to/file`
```

**When to log:**
- Content changed → CHANGELOG
- Infrastructure changed → loremaster-log
- Both changed → both
- Read-only session → neither

**Retroactive:** if missed, backfill next session with `[retroactive]` marker.

---

## The Loremaster's Watch

Any session that creates, modifies, renames, or deletes files in `.claude/` must run this checklist before ending:

1. CLAUDE.md skill table matches actual `.claude/skills/` directories
2. CLAUDE.md agent table matches actual `.claude/agents/` directories
3. `lore-reference.md` structure tree matches actual files
4. Cross-references between skills, agents, and rules are consistent
5. No orphans — no file references a path that doesn't exist
6. Loremaster-log entry written

This applies to every skill and agent — not just `/lore`.

Infrastructure drift is silent and cumulative. The Loremaster's watch makes every actor responsible for consistency.

**Exceptions:** read-only operations, content-only changes (knowledge/, log/).

---

## RAG-Light Index Completeness Check

Any session that creates or modifies files in `knowledge/`, `log/`, or `contributions/` must verify index completeness before ending:

| Area modified | Index to check | What to verify |
|---------------|---------------|----------------|
| `knowledge/*.md` | `knowledge/INDEX.md` | File has an entry with current Updated date, Key Topics, Answers |
| `log/daily/*.md` | `log/INDEX.md` → Daily | File has an entry with Date, Sources, Signals, Tags, Entities, References |
| `log/weekly/*.md` | `log/INDEX.md` → Weekly | File has an entry |
| `contributions/*.md` | `contributions/INDEX.md` | File has an entry with Type, What, From, Tags, Date, Status |
| `artifacts/*.md.published` | `contributions/INDEX.md` → Promoted table | Promoted entry updated to point to `artifacts/` path |

**Procedure:**
1. List all files written to indexed areas during this session
2. For each file: confirm corresponding index entry exists and is current
3. If missing: add the entry before session ends
4. If stale (e.g. Updated date wrong, Key Topics outdated): refresh

**Exceptions:**
- Index files themselves (INDEX.md) — never self-indexed
- `.lore/inconsistencies.md` — not indexed (config file, loaded directly)
- `OVERRIDES.md` — self-indexed (table IS the index)
- Read-only sessions — nothing to check
