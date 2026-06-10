---
name: setup
description: "Configure Lore sources and project settings interactively. Usage: /setup [action]"
---

# Skill: /setup [action]

Interactive configuration of Lore sources and project settings.
Guides through adding, editing, and validating sources without manual file editing.

## --help

When invoked as `/setup --help` or `/setup -h` — print this and stop:

```
/setup — Configure Lore sources and project settings

Usage:
  /setup [action]

Actions:
  (none)          show current setup status + what's missing
  add-source      add a new source (guided wizard)
  edit-source     modify an existing source
  remove-source   remove a source from SOURCES.md
  validate        test connectivity to all configured sources
  config          edit .lore/config.md settings (branding, email, etc.)

Examples:
  /setup
  /setup add-source
  /setup add-source jira
  /setup add-source web "https://status.example.com"
  /setup validate
  /setup config

Tip: After adding a source, run /pull onboarding (first time) or /pull (daily).
     Use /setup validate to check if all sources are reachable.
```

---

## /setup (status)

Show current configuration state:

```
Setup Status – YYYY-MM-DD

Sources configured:
  ✅ Jira — PROJ @ your-site.atlassian.net
  ✅ Confluence — SPACE @ your-site.atlassian.net/wiki
  ⚠  GitHub — configured but no journal pull yet
  ❌ Web — no web sources configured
  ❌ SharePoint — not configured

Config:
  ✅ .lore/config.md — complete
  ⚠  Email not set (needed for /publish)

Next step: [suggestion based on gaps]
```

---

## /setup add-source

Interactive wizard that guides through adding a source.

### Step 1 — Type Selection

If type not provided as argument, ask:

```
What type of source do you want to add?

1. Jira         — issue tracking (epics, stories, tasks)
2. Confluence   — wiki pages and documentation
3. GitHub       — repository, commits, PRs, issues
4. Web          — live website (public URL, fetched each pull)
5. SharePoint   — documents (PPTX, DOCX via OneDrive sync)
6. Registry     — pointer to external source definitions
```

### Step 2 — Type-Specific Prompts

#### Jira
```
Site URL?          → https://your-site.atlassian.net
Project key(s)?    → PROJ (comma-separated for multiple)
Entry points?      → top-level epics or VIs (optional, helps scope)
Signal hierarchy?  → e.g. "VI > Epic > Story" (optional)
```

#### Confluence
```
Site URL?          → https://your-site.atlassian.net/wiki
Space key?         → SPACE
Key pages?         → page IDs to monitor (optional)
```

#### GitHub
```
Repository URL?    → https://github.com/org/repo
Branch?            → main (default)
Signal type?       → commits, PRs, issues (default: all)
```

#### Web
```
URL?               → https://example.com/status
Name?              → (human-readable label)
Focus?             → what to extract (optional — "all" if blank)
Schedule?          → every-pull (default), daily, weekly
```

#### SharePoint
```
Site URL?          → https://company.sharepoint.com/sites/project
Local sync path?   → ~/OneDrive/project-folder
File types?        → .pptx, .docx (default)
```

#### Registry
```
URL?               → Confluence page URL, HTTP endpoint, or local path
Name?              → (human-readable label)
```

### Step 3 — Validation (optional but recommended)

After collecting info, offer to validate:

```
Validate connectivity? (y/n)
```

If yes:
- Jira/Confluence: attempt acli connection or API ping
- GitHub: check if repo is accessible
- Web: fetch URL, check for content
- SharePoint: check if local sync path exists
- Registry: fetch and attempt to parse

Report result:
```
✅ Connection successful — [details]
```
or:
```
⚠ Could not connect — [reason]. Add anyway? (y/n)
```

### Step 4 — Write to SOURCES.md

Append the new source section to SOURCES.md in the correct format.
If a section for that type already exists: add to it (don't duplicate the heading).

### Step 5 — Initialize Manifest

Create or update the corresponding manifest file in `.lore/manifests/`:
- Jira → `jira.json`
- Confluence → `confluence.json`
- GitHub → `github.json`
- Web → `web.json`
- SharePoint → `sharepoint.json`

Initialize with empty state (no items pulled yet).

### Step 6 — Suggest Next Step

```
✅ Source added: [name]

Next: run /pull onboarding to establish the baseline.
      or /pull [type] to pull just this source.
```

---

## /setup edit-source

1. List all configured sources with numbers
2. User picks which one to edit
3. Show current values, allow changing any field
4. Write back to SOURCES.md

---

## /setup remove-source

1. List all configured sources
2. User picks which one to remove
3. Confirm: "Remove [name]? Manifest will be preserved for history. (y/n)"
4. Remove section from SOURCES.md
5. Do NOT delete manifest (historical record)

---

## /setup validate

Test all configured sources for connectivity:

```
Source Validation – YYYY-MM-DD

Jira (PROJ):        ✅ reachable — 142 issues found
Confluence (SPACE): ✅ reachable — 38 pages in space
GitHub (org/repo):  ✅ reachable — last commit 2h ago
Web (Status Page):  ✅ reachable — 2.4KB content
SharePoint:         ⚠ sync path not found — check OneDrive
Registry (Alpha):   ✅ fetched — 3 additional sources parsed

Overall: 5/6 sources healthy
```

---

## /setup config

Interactive editor for `.lore/config.md`:

- Confluence publishing settings (base URL, space, email)
- Branding (colors, fonts for /artifact)
- Project metadata (name, team, stakeholders)

---

## References

Source format: `SOURCES.md`
Config: `.lore/config.md`
Pull framework: `.claude/refs/pull-framework.md` (source resolution)
Manifests: `.lore/manifests/`

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- None (operates on SOURCES.md and .lore/config.md directly — not indexed)

### Index Write
- None (SOURCES.md is human-maintained, not indexed; manifests are not indexed)
