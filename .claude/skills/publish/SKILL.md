---
description: Publish workspace artifacts to Confluence via REST API. Use when user says "publish to confluence", "update confluence page", "push to confluence", or "embed HTML".
---

# Publish

## --help

When invoked as `/publish --help` or `/publish -h` — print this and stop:

```
/publish — Publish workspace artifacts to Confluence

Usage:
  /publish [mode] [artifact]

Modes:
  page     markdown content publishing — creates/updates a Confluence page
  html     embeds a full HTML artifact into a Confluence page via Forge macro

Examples:
  /publish page artifacts/briefing.md
  /publish html artifacts/dashboard.html
  /publish                → Claude asks which artifact and mode

Requires: Atlassian API token in system keyring (one-time setup)
  python -c "import keyring; keyring.set_password('confluencekit', 'you@company.com', 'TOKEN')"

After publish:
  - Page width is set automatically (wide for markdown, full-width for HTML)
  - Page is registered as watched in .lore/config.md
  - Source file is marked with a .published sidecar file
  - CHANGELOG.md entry is written to record the publish

Tip: acli is read-only for Confluence — use /publish for all writes.
```

---

> **Requires setup** — store Atlassian API token in system keyring (one-time):
> ```
> python -c "import keyring; keyring.set_password('confluencekit', 'you@company.com', 'YOUR_TOKEN')"
> ```

## Purpose

Publishes workspace artifacts (markdown + HTML) to Confluence pages via the Confluence REST API.
Two modes: **page** (markdown/content publishing) and **html** (embedded HTML artifact via Forge macro).

Use when the user wants to:
- Push a workspace artifact to a Confluence page
- Update an existing Confluence page with new content
- Embed a full HTML artifact into a Confluence page via Forge macro

> **Non-negotiable:** Always use confluencekit — never hand-edit Confluence content or use acli for writes.

---

## Build Kit: confluencekit

Reusable Confluence publishing engine at `.claude/skills/publish/confluencekit/`:

| Module | Purpose |
|--------|---------|
| `confluencekit.py` | Main entry point: `publish()`, `embed_html()`, `set_token()` |
| `converter.py` | Markdown to Confluence storage format (pure functions) |
| `api.py` | REST API helpers: publish, upload, create/delete pages, set width |

**Token resolution order:** system keyring -> `ATLASSIAN_API_TOKEN` env var -> interactive prompt

**Token management:**
```bash
# Store token (one-time, or when token expires)
python -c "import keyring; keyring.set_password('confluencekit', 'you@company.com', 'TOKEN')"
```

Get tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

---

## Mode 1 — Publish Markdown Artifact

Create a per-artifact `update-confluence.py` script:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

def _repo_root():
    d = Path(__file__).resolve().parent
    while d != d.parent:
        if (d / "CLAUDE.md").exists():
            return d
        d = d.parent

sys.path.insert(0, str(_repo_root() / ".claude" / "skills" / "publish" / "confluencekit"))
from confluencekit import publish, set_token

EMAIL       = "you@company.com"              # from .lore/config.md
PAGE_ID     = "123456"                       # target page ID
BASE_URL    = "https://your-site.atlassian.net"  # from SOURCES.md
TITLE       = "Page Title"
GITHUB_REPO = "https://github.com/org/repo"  # from .lore/config.md
SOURCE_FILE = "workspace/artifact/artifact.md"

if __name__ == "__main__":
    if "--set-token" in sys.argv:
        set_token(EMAIL)
    else:
        publish(
            page_id=PAGE_ID,
            title=TITLE,
            md_file=Path(__file__).parent / "artifact.md",
            html_file=Path(__file__).parent / "artifact.html",
            base_url=BASE_URL,
            email=EMAIL,
            github_repo=GITHUB_REPO,
            source_path=SOURCE_FILE,
        )
```

**Run:** `python update-confluence.py`

---

## Mode 2 — Embed HTML Artifact (Forge HTML Macro)

Embeds an entire HTML file into a Confluence page via a Forge macro.
The HTML is stored inline in the page body — no attachment needed.

```python
import sys
from pathlib import Path

def _repo_root():
    d = Path(__file__).resolve().parent
    while d != d.parent:
        if (d / "CLAUDE.md").exists():
            return d
        d = d.parent

sys.path.insert(0, str(_repo_root() / ".claude" / "skills" / "publish" / "confluencekit"))
from confluencekit import embed_html

embed_html("PAGE_ID", "path/to/dashboard.html")
```

Or via CLI:
```bash
cd .claude/skills/publish/confluencekit
python confluencekit.py --embed <page_id> <html_file>
```

**Forge app details** — configure in `.lore/config.md` under Confluence publishing:
- Extension key, instance cloud-id, and space-id are instance-specific
- Parameter name for HTML content: `embed-h-t-m-l` (for bobswift Forge app)

---

## Constraints

| Constraint | Detail |
|-----------|--------|
| HTML macro | May be blocked by Confluence org policy — use Forge extension (Mode 2) |
| acli Confluence | Read-only (list/view only) — cannot write pages |
| MCP Atlassian | May be blocked by org policy (admin allowlist required) |
| Attachment access | Controlled by Confluence page permissions |

---

## Page Width

Automatically set by confluencekit after publish/embed.

| Mode | Width | UI label |
|------|-------|----------|
| Markdown publish | `wide` | Wide |
| HTML embed | `full-width` | Max |

---

## Workflow

1. **Determine mode** — markdown content or HTML embed?
2. **Check script** — verify per-artifact `update-confluence.py` exists (Mode 1) or call `embed_html()` (Mode 2)
3. **Prepare content** — strip YAML frontmatter before conversion. Add attribution (see below).
4. **Run** — publish and confirm URL
5. **Register as watched** — add/update the page in `.lore/config.md` → "Watched Pages" table with current version.
6. **Report** — print the live page URL on success
7. **Mark source** — if the source file is in `contributions/`:
   - Move source file to `artifacts/` (same filename)
   - Create a `.published` sidecar file in `artifacts/`
   - Sidecar contains YAML publish metadata (see "Publish Metadata" below)
   - Update `contributions/INDEX.md` — update Promoted entry to point to `artifacts/` path
8. **Log** — write CHANGELOG.md entry after a successful publish

---

## Rules

- Never hardcode version numbers — always GET first
- Always XML-escape HTML content before inserting into storage format
- Full-width should always be set for HTML embed pages
- After publish: log the change in CHANGELOG.md
- **Read `.lore/config.md` "Confluence — Publishing Defaults"** section for default parent pages and title format
- **No first-person language:** Published pages are public-facing. Rewrite in neutral/third-person or imperative form.
- **Strip frontmatter:** YAML frontmatter is internal metadata. Always strip before converting to Confluence storage format.

---

## Confluence Attribution

Every page published from Lore MUST include both an info panel at the top and a footer at the bottom.

**Top — Info panel (Confluence storage format):**
```xml
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>This page is maintained by <strong>{PROJECT_NAME}</strong> (Lore Project Intelligence).
    Content is AI-generated and human-reviewed. Source: <a href="GITHUB_REPO_URL">GitHub repository</a></p>
  </ac:rich-text-body>
</ac:structured-macro>
```

Replace `{PROJECT_NAME}` and `GITHUB_REPO_URL` from `.lore/config.md`.

**Bottom — Footer:**
```xml
<p><em>Published: YYYY-MM-DD via Claude ({PROJECT_NAME}) | AI-generated content | Source of truth: <a href="GITHUB_REPO_URL">GitHub repository</a></em></p>
```

---

## Publish Metadata

After a successful publish, create a `.published` sidecar file:

```yaml
published_to: https://your-site.atlassian.net/wiki/spaces/{SPACE}/pages/{PAGE_ID}
published_date: YYYY-MM-DD
published_title: "Actual Page Title on Confluence"
page_id: "PAGE_ID"
space: SPACE
original_source: contributions/
```

This sidecar tells Lore where the file was published so it can:
- Exclude this file from standard retrieval
- Avoid re-publishing the same content
- Know which Confluence page corresponds to this file

**Never include this metadata in Confluence output.**
