# Ref: Merge Resolution Rules

When multiple sessions work on the same Lore repo, merge conflicts are inevitable.
This ref codifies how to resolve them — deterministically, without human intervention
for structural conflicts.

---

## When to Apply

1. **Session start:** If `git status` shows "have diverged" → `git pull` → if conflicts, apply these rules.
2. **Before commit:** If pushing would fail → `git pull --rebase` or `git pull` → if conflicts, apply these rules.
3. **User request:** When explicitly asked to merge or resolve conflicts.

---

## Resolution Rules by File Type

### Manifests (`.lore/manifests/*.json`)

| Field | Rule | Rationale |
|-------|------|-----------|
| `last_pull` / `last_pulled` | Take the **newer** date | Later pull has more data |
| `total_pages` / `total_items` | Take the **higher** number | Totals only grow (pages aren't deleted) |
| `summary.*` counts | Take **ours** if our `last_pull` is newer, else theirs | Counts reflect pull state |
| Item status changes | Take the **later** status in lifecycle (Open→In Progress→Closed→Cancelled) | Status only moves forward |
| New items (added in one side only) | Keep both | Additive — no information loss |
| `read_at_updated` field | Optional metadata — drop if causes conflict | Not load-bearing |

### CHANGELOG.md

| Situation | Rule |
|-----------|------|
| Both sides add entries at top | Keep **both**, sort newest-first by date |
| Same-date entries | Order: our entry first, then theirs (or alphabetical by title) |
| Identical entries | Deduplicate — keep one |

### contributions/INDEX.md

| Situation | Rule |
|-----------|------|
| Status conflict (pending vs promoted) | **promoted** wins (later state in lifecycle: pending → promoted → knowledge) |
| New entries added by other side | Keep — additive |
| Both sides add entries | Merge both into the table, preserve chronological order by date |

### .lore/inconsistencies.md

| Situation | Rule |
|-----------|------|
| New INC-### entries on one side | Keep all — additive (never discard inconsistencies) |
| Same INC-### modified on both sides | Take the version with more content / later date |
| Both sides add at same position | Keep both, order by INC number (higher = newer) |

### log/INDEX.md

| Situation | Rule |
|-----------|------|
| New daily/weekly entries | Keep both — additive |
| Same entry modified (e.g., signals updated) | Take the version with more content |

### knowledge/*.md

| Situation | Rule |
|-----------|------|
| **Cannot auto-resolve.** | Content changes require human review |
| Exception: metadata-only (Updated date, INDEX entry) | Take newer date |
| Exception: additive table rows | Keep both |

### .lore/loremaster-log.md

| Situation | Rule |
|-----------|------|
| Both sides add entries | Keep both, chronological order |

---

## Resolution Process

1. **Identify** — `git status` shows "both modified" files
2. **Classify** — match each file to a rule category above
3. **Resolve** — apply the rule mechanically
4. **Stage** — `git add` each resolved file
5. **Verify** — `grep -r "<<<<<<" .` to confirm no markers remain
6. **Report** — brief summary of what was kept from each side

---

## What Requires Human Decision

- knowledge/ content conflicts (meaning changed, not just metadata)
- OVERRIDES.md conflicts (human-decided corrections must not be auto-resolved)
- Any conflict where both sides change the SAME fact to DIFFERENT values

When in doubt: keep both versions visible and ask.

---

## Prevention (Conventions)

- **Pull before push:** Every session that commits should `git pull` first
- **Small commits:** Commit frequently to reduce conflict surface
- **Avoid long-running sessions:** The longer a session runs without syncing, the more conflicts accumulate
- **Manifests are expendable:** If a manifest conflict is complex, the newer pull's version is always safe (it reflects the latest source state)
