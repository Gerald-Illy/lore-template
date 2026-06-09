# Sources

Where all project data lives. Human-maintained.

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
