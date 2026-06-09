# Manual Setup Guide

Use this guide if you're setting up Lore without the plugin.

---

## Prerequisites

- [ ] Claude Code installed (VS Code extension, CLI, or Desktop app)
- [ ] Git repository initialized
- [ ] Access to your project's Jira, Confluence, and GitHub
- [ ] (Optional) Atlassian CLI installed: `brew install atlassian/tap/acli`

---

## Step 1: Clone Template

```bash
git clone <template-repo-url> <your-project-name>
cd <your-project-name>
rm -rf .git
git init
git add .
git commit -m "Initial Lore setup from template"
```

---

## Step 2: Replace Placeholders

### 2.1 Project Name

Replace `{PROJECT_NAME}` in these files:
- `CLAUDE.md` (lines 1, 3, 13)
- `.lore/config.md` (line 11)
- `.claude/skills/briefing/*.md` (all briefing variants)

**Find & replace:**
```bash
# macOS/Linux:
find . -type f -name "*.md" -exec sed -i '' 's/{PROJECT_NAME}/YourProjectName/g' {} +

# Windows (PowerShell):
Get-ChildItem -Recurse -Include *.md | ForEach-Object {
    (Get-Content $_.FullName) -replace '\{PROJECT_NAME\}', 'YourProjectName' | Set-Content $_.FullName
}
```

### 2.2 Repository URL

Update `.lore/config.md`:
```markdown
| Repository | `https://github.com/your-org/your-repo` |
```

---

## Step 3: Configure Sources

Edit `SOURCES.md` with your real URLs:

### Jira
```markdown
| Site | `https://your-company.atlassian.net` |
| Project(s) | `PROJ, OTHER` |
| Entry Points | VI-123, EPIC-456 |
```

**Set up acli auth:**
```bash
acli jira auth login --site your-company.atlassian.net
```

### Confluence
```markdown
| Site | `https://your-company.atlassian.net/wiki` |
| Space | `YOURSPACE` |
| Key Pages | 123456789, 987654321 |
```

### GitHub
```markdown
| Repository | `https://github.com/your-org/your-repo` |
| Branch | `main` |
| Signal | Commits, PRs, issues |
```

Ensure GitHub CLI is authenticated:
```bash
gh auth status
# If not: gh auth login
```

### SharePoint (optional)
```markdown
| Site | `https://yourcompany.sharepoint.com/sites/project` |
| Local sync | `~/OneDrive/project-folder` |
| File types | `.pptx`, `.docx` |
```

---

## Step 4: Configure Publishing (optional)

If you want to publish briefings to Confluence, update `.lore/config.md`:

```markdown
## Confluence — Publishing Defaults

| Base URL | `https://your-company.atlassian.net` |
| Space | `YOURSPACE` |
| Default parent page | "Project Documentation" |
| Default parent ID | 123456789 |
| Email | `you@company.com` |
```

---

## Step 5: First Pull (Onboarding)

This establishes your baseline knowledge:

```bash
# In Claude Code:
/pull onboarding
```

**What happens:**
1. Reads your configured sources (Jira, Confluence, GitHub)
2. Extracts project structure, decisions, and key information
3. Creates initial knowledge files in `knowledge/`
4. Writes first log entry in `log/onboarding/`

**Duration:** 5-15 minutes depending on source size.

---

## Step 6: Verify Setup

Check that these files now have content:

```bash
# Should have entries:
cat knowledge/INDEX.md
cat log/INDEX.md

# Should have a baseline log:
ls -la log/onboarding/

# Should have initial knowledge:
ls -la knowledge/
```

---

## Step 7: First Briefing

```bash
/briefing
```

You should see:
- Current project state
- Open decisions
- Tracked risks
- Recent changes

If the output says "no data" → check `SOURCES.md` configuration.

---

## Common Issues

### "No sources configured"
→ Check `SOURCES.md` has real URLs, not template placeholders.

### "acli not found"
→ Install: `brew install atlassian/tap/acli` or `npm install -g @atlassian/acli`

### "GitHub auth failed"
→ Run: `gh auth login`

### "Confluence pages empty"
→ Check page IDs are correct (view page → look at URL)
→ Verify your Confluence user has read access

### "First pull takes forever"
→ Normal for large Confluence spaces. Check progress in logs.
→ Consider limiting to specific pages in `SOURCES.md` → Key Pages.

---

## Next Steps

Once setup is complete:

1. **Daily routine:** `/pull` every morning
2. **Before standups:** `/briefing`
3. **Capture signals:** `/jot` for notes, todos, feedback
4. **Query knowledge:** `/ask` any question about project state
5. **Track decisions:** Use `/override` when sources are wrong

---

## Advanced Configuration

### Custom Branding (for `/artifact`)

Edit `.lore/config.md` → Branding section with your brand colors.

### Confluence HTML Publishing

Requires Forge app setup. See `.lore/config.md` → Forge Macro section.

### Signal Hierarchy Tuning

Define which issue types matter in `SOURCES.md` → Jira → Signal Hierarchy:

```markdown
### Signal Hierarchy
VP > VI > Epic > Story
(Tasks and subtasks = noise, don't pull)
```

---

## Getting Help

- Check `CLAUDE.md` for all available commands
- Run `/lore check` to validate your setup
- See `.claude/rules/` for framework behavior rules
