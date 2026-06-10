---
name: setup
description: "Configure Lore sources, project settings, and framework updates. Usage: /setup [action]"
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
  update          check for new or updated Lore skills/agents/rules

Examples:
  /setup
  /setup add-source
  /setup add-source jira
  /setup add-source web "https://status.example.com"
  /setup validate
  /setup config
  /setup update

Tip: After adding a source, run /pull onboarding (first time) or /pull (daily).
     Use /setup validate to check if all sources are reachable.
     Use /setup update periodically to stay current with Lore improvements.
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

## /setup update

Check if the Lore framework has new skills, extended existing ones, or updated rules/agents.
Compares the installed state against the plugin/template source and presents a summary.

### Step 1 — Determine Source

Resolve the Lore framework source (in priority order):

1. **Plugin installed** — check if `lore-plugin` is registered in `.claude/settings.json` or `.claude/settings.local.json` (command group or hook referencing `lore-plugin`). If yes: use the plugin's installed path as source.
2. **Template repo** — fetch from `https://github.com/Gerald-Illy/lore-template.git` (always the canonical source for the Lore framework).
3. **Manual** — if the template repo is unreachable: ask the user for an alternative path or URL.

### Step 2 — Compare

Compare the following areas between source (template/plugin) and local project:

| Area | Compare | What to check |
|------|---------|---------------|
| `.claude/skills/` | Directories | New skills not present locally |
| `.claude/skills/*/SKILL.md` | Content hash | Skills that have been extended or modified |
| `.claude/agents/` | Directories | New agents not present locally |
| `.claude/agents/*/AGENT.md` | Content hash | Agents that have been updated |
| `.claude/rules/` | Files | New rules not present locally |
| `.claude/rules/*.md` | Content hash | Rules that have been modified |
| `.claude/refs/` | Files | New refs not present locally |
| `.claude/refs/*.md` | Content hash | Refs that have been updated |

**Ignore:**
- `.lore/` (instance-specific state)
- `knowledge/`, `log/`, `contributions/` (project content)
- `SOURCES.md`, `OVERRIDES.md`, `CHANGELOG.md` (project-specific)
- Any file with `{PROJECT_NAME}` placeholders vs filled-in values (template vs instance)

### Step 3 — Summary

Present findings grouped by category:

```
Lore Update Check – YYYY-MM-DD
Source: lore-plugin v1.5.0 (or: lore-template @ abc1234)

🆕 New (not installed locally):
  • skill: /foo — [1-line description from SKILL.md frontmatter]
  • agent: bar-agent — [1-line description from AGENT.md frontmatter]
  • rule: baz.md — [1-line description or first heading]

📝 Updated (source is newer):
  • skill: /pull — [what changed: +2 phases, new retroactive mode, ...]
  • rule: session-end.md — [what changed: added merge check section]
  • ref: pull-framework.md — [what changed: added web source handling]

✅ Up to date:
  • 12 skills, 8 agents, 5 rules, 9 refs — no changes

Summary: 2 new, 3 updated, 34 unchanged
```

### Step 4 — Suggest Actions

For each new or updated item, suggest an action:

```
Suggested updates:

1. [new] Install skill /foo
   → Copy .claude/skills/foo/ from source
   → Add to CLAUDE.md command table

2. [updated] Update /pull skill
   → Changes: added Phase 0 (source resolution), new /pull web scope
   → ⚠ You have local modifications — review diff before applying

3. [updated] Update session-end.md rule
   → Changes: added merge check section
   → Safe to apply (no local modifications)

Apply all safe updates? [yes / pick specific / no]
```

### Step 5 — Apply (if user confirms)

For each accepted update:

1. **New items:** Copy from source to local project
2. **Updated items (no local mods):** Replace with source version
3. **Updated items (with local mods):** Show diff, ask user to confirm or merge manually
4. **CLAUDE.md:** Update command/agent tables if new skills or agents were installed
5. **VERSIONLOG.md:** Do NOT auto-update (user decides versioning)

### Rules

- Never auto-apply. Always show summary first, always ask.
- Never overwrite local modifications without explicit confirmation.
- If an updated skill has sections the user customized (e.g. project-specific signal hierarchy): warn before replacing.
- If the source is unreachable: report and stop. Do not guess.
- Show concrete diffs for updated files when the user asks "what changed?"

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
