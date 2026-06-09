---
description: Query Jira and Confluence via acli CLI. Use when the user mentions jira, confluence, or any Atlassian tool.
---

# Atlassian Agent

> **Requires setup** — `acli` must be installed and authenticated (`acli jira auth status --site {JIRA_HOST}` to check)

## --help

When invoked as `/atlassian --help` or `/atlassian -h` — print this and stop:

```
/atlassian — Query Jira and Confluence via acli CLI (instance from SOURCES.md)

Usage:
  /atlassian [query or item key]

Examples:
  /atlassian PROJ-1234
  /atlassian what epics are in milestone M3?
  /atlassian who is assigned to items in PROJ-5678?
  /atlassian JQL: project = MYPROJ AND status = "In Progress"

Requires: acli installed and authenticated (see SOURCES.md for site URL)
Tip: For knowledge-base queries use /ask. For deep tree traversal use /crawl.
     For writes to Confluence use /publish (acli is read-only for pages).
```

---

## Purpose

Specialist for querying the project's Atlassian instance (see SOURCES.md for base URL) — Jira and Confluence — via `acli`.
Looks up work items by key or JQL, resolves parent/child hierarchies, checks status and assignees.

Use when you need to answer:
- What is the status of PROJ-XXXXX?
- Which epics exist under a Value Increment?
- Who is assigned to items in a milestone?
- Are there stories under these epics?

> **Non-negotiable:** Never describe what you could query. Always **execute** acli commands and interpret the results.

> **Write operations:** To publish content or embed HTML on Confluence, use `/publish` — acli is read-only for Confluence pages.

---

## CLI

**Binary:** `acli` (must be in PATH and already authenticated)

### Common Commands

| Intent | Command |
|--------|---------|
| Check auth | `acli jira auth status --site {JIRA_HOST}` |
| View single item | `acli jira workitem view KEY --site {JIRA_HOST}` |
| Search by JQL (table) | `acli jira workitem search --jql '...' --fields 'key,summary,status,assignee,issuetype,parent' --site {JIRA_HOST}` |
| Search as JSON | add `--json` to search command |
| Find children | `--jql 'parent in (KEY1,KEY2,...)'` |
| Get all pages | add `--paginate` |

### Confluence Commands

| Intent | Command |
|--------|---------|
| List pages (table) | `acli confluence page list --space {SPACE}` |
| List pages (JSON with versions) | `acli confluence page list --space {SPACE} --json` |
| View single page | `acli confluence page view --id PAGE_ID` |
| View page as JSON | `acli confluence page view --id PAGE_ID --json` |

**Important:** The default table output does NOT include version numbers or timestamps.
Always use `--json` when you need delta detection (version comparison).
Parse JSON output with `python -c "..."` (use `python`, not `python3` — Windows convention).

**Note:** Replace `{JIRA_HOST}` and `{SPACE}` with values from SOURCES.md.

---

## Workflow

1. **Auth check** — run `acli jira auth status --site {JIRA_HOST}` first; if not authenticated, tell the user to run `acli jira auth login --site {JIRA_HOST}`
2. **Single item** — use `view` for detail; use `search --json` for structured data with parent/subtask fields
3. **Bulk query** — build JQL, use `--fields` to limit output, add `--paginate` for large sets
4. **Hierarchy** — for work packages, always check for children with `parent in (...)` unless the user asks for a single item only
5. **Summarise** — present as table with key, summary, status, assignee, parent; flag gaps

---

## Output Standards

- **Always use tables** for item lists — never raw JSON dumps
- **Clickable links** — format IDs as `[KEY]({JIRA_BASE}/browse/KEY)` — derive base URL from SOURCES.md
- **Flag unassigned items** — use `—` and note count at the end
- **Flag discrepancies** — if Jira data contradicts source documents, mark with warning
- **Write CHANGELOG.md entry** after producing any deliverable that modifies a file (see `.claude/refs/auto-log-format.md`)
