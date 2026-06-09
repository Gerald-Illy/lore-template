# Ref: Auto-Log Format

Format specification for CHANGELOG.md and .lore/loremaster-log.md entries.
These are written automatically at session end — not a user-invocable command.

See `.claude/rules/auto-log.md` for when to write which log.

---

## CHANGELOG.md Format

One section per logical change. Prepend at the top (newest first).

```
## [YYYY-MM-DD] – [Session title]

[One sentence describing what was done and why.]

Files: `path/to/file`, `path/to/file`
```

Rules:
- Every file created, modified, or deleted must be listed
- Never overwrite existing entries – only prepend
- Retroactive entries marked as `[retroactive]` after the timestamp

---

## .lore/loremaster-log.md Format

```
## [YYYY-MM-DD] – [Session title]

[One sentence describing what infrastructure changed and why.]

Files: `path/to/file`, `path/to/file`
```

Same rules as CHANGELOG — newest first, list all files, never overwrite.

---

## Backfill

If a session ended without a log entry: backfill on next session.
Mark as `[retroactive]` after the timestamp.

---

## Scoping Rules

| Content changed | Write to |
|----------------|----------|
| `knowledge/`, `OVERRIDES.md`, `SOURCES.md` | CHANGELOG.md |
| `.claude/`, `.lore/` (rules, skills, agents, config) | .lore/loremaster-log.md |
| Both types in one session | Both logs |
| Read-only operations | Neither |
