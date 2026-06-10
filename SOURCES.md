# Sources

Where all project data lives. Human-maintained.

Sources can be defined here directly, or delegated to an external registry
that teams maintain independently.

---

## Source Registry (optional)

A source registry is a pointer to an external location (e.g. a Confluence page,
a shared document, a JSON file) that contains additional source definitions.
This allows teams to maintain their own sources without touching this repo.

| Field | Value |
|-------|-------|
| Type | `source-registry` |
| URL | `https://your-site.atlassian.net/wiki/spaces/TEAM/pages/12345` |
| Name | (human-readable label, e.g. "Alpha Team Sources") |
| Format | (auto-detected — markdown table, YAML, JSON, or free-form text) |

### How it works

1. `/pull` reads SOURCES.md first (local sources always present)
2. Finds `source-registry` entries
3. Fetches each registry URL (via Confluence API, HTTP, or local file)
4. Parses found source definitions (format is flexible — see below)
5. Merges into runtime source list (local wins on ID collision)
6. Pull agents work with the merged set

### Format flexibility

External registries can use **any readable format** — Lore will attempt to parse:

- Markdown tables (same columns as SOURCES.md sections)
- YAML blocks
- JSON arrays/objects
- Free-form text with recognizable structure (headings + key-value pairs)

If Lore cannot parse a registry: **warn and skip** — never block the pull.
The warning appears in the pull output and daily log.

### Merge rules

| Situation | Rule |
|-----------|------|
| Local source + external source with same ID | Local wins |
| External source not in SOURCES.md | Added to runtime set |
| External source removed from registry | Dropped from runtime (manifests preserved) |
| Registry unreachable | Warn, proceed with local sources only |
| Registry format unreadable | Warn, skip that registry, proceed |

### Example

```markdown
## Source Registry

| Field | Value |
|-------|-------|
| Type | `source-registry` |
| URL | `https://company.atlassian.net/wiki/spaces/ALPHA/pages/98765` |
| Name | Alpha Team Sources |
```

On that Confluence page, the team maintains:

```markdown
## Jira

| Field | Value |
|-------|-------|
| Site | `https://company.atlassian.net` |
| Project(s) | `ALPHA` |
| Entry Points | ALPHA-100, ALPHA-200 |

## Confluence

| Field | Value |
|-------|-------|
| Site | `https://company.atlassian.net/wiki` |
| Space | `ALPHA` |
| Key Pages | 11111, 22222 |
```

---

## Jira

| Field | Value |
|-------|-------|
| Site | `https://your-site.atlassian.net` |
| Project(s) | `PROJ` |
| Entry Points | Top-level epics or VIs |
| acli auth | `acli jira auth login --site your-site.atlassian.net` |

### Signal Hierarchy
<!-- Define which issue types contain meaningful signal for your project -->
<!-- Example: VP > VI > Epic > Story -->

### Key Pages
<!-- List the most important Jira items to monitor -->

---

## Confluence

| Field | Value |
|-------|-------|
| Site | `https://your-site.atlassian.net/wiki` |
| Space | `SPACE` |
| Key Pages | (list important page IDs) |

### Navigation
<!-- List the main page trees and their purpose -->

---

## GitHub

| Field | Value |
|-------|-------|
| Repository | `https://github.com/org/repo` |
| Branch | `main` |
| Signal | Commits, PRs, issues |

### Signal Hierarchy
<!-- What counts as project-level signal vs noise? -->

---

## SharePoint (optional)

| Field | Value |
|-------|-------|
| Site | `https://company.sharepoint.com/sites/project` |
| Local sync | `~/OneDrive/project-folder` |
| File types | `.pptx`, `.docx` |

---

## Web (optional)

Live web sources — public URLs fetched on each pull.
Use for status pages, documentation sites, roadmaps, release notes, or any live content.

| Field | Value |
|-------|-------|
| URL | `https://example.com/status` |
| Name | (human-readable label) |
| Focus | (optional — what to extract: "status table", "release notes section", "all") |
| Schedule | (optional — `every-pull`, `daily`, `weekly`. Default: `every-pull`) |

### How it works

1. `/pull` fetches the URL (HTML → Markdown conversion)
2. Extracts content based on Focus hint (or takes full page)
3. Compares against last-known content (hash-based delta check)
4. If changed: creates log entry with what changed
5. Knowledge derivation applies as with any other source

### Multiple URLs

Add multiple web sources as separate entries:

```markdown
## Web

| URL | Name | Focus |
|-----|------|-------|
| `https://status.cloud.example.com` | Platform Status | Current incidents |
| `https://docs.partner.io/changelog` | Partner API Changelog | Latest entries |
| `https://roadmap.example.com/public` | Public Roadmap | Q3 milestones |
```

### Signal Hierarchy
<!-- What's high signal vs noise on these pages? -->
<!-- Example: Incident = high, maintenance = low -->
