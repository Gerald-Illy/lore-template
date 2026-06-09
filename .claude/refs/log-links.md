# Rule: Clickable Links in Daily Logs

## Principle

Every reference to an external source in the **Context & Narrative** section of a daily log
MUST include a clickable markdown link so the reader can navigate directly to the source.

---

## What Gets Linked

| Reference type | Link format | Example |
|----------------|-------------|---------|
| Confluence page | `[Title]({CONFLUENCE_BASE}/wiki/spaces/{SPACE}/pages/PAGE_ID)` | `[IAM decision record]({CONFLUENCE_BASE}/wiki/spaces/{SPACE}/pages/2113241179)` |
| Jira item | `[KEY]({JIRA_BASE}/browse/KEY)` | `[PROJ-1234]({JIRA_BASE}/browse/PROJ-1234)` |
| GitHub file | `[filename](https://github.com/OWNER/REPO/blob/main/PATH)` | `[meeting-notes.md](https://github.com/OWNER/REPO/blob/main/meetings/2026-04-30.md)` |
| Miro board | `[Board name](URL)` | `[Project Plan](https://miro.com/app/board/BOARD_ID=/)` |

---

## Where Links Are Required

1. **Context & Narrative** — every named Confluence page, Jira item, or external reference
2. **Journal section** — link to the Journal file (GitHub URL) if the item is noteworthy
3. **Jira/Confluence/GitHub Changes** — every page/item MUST be a clickable link
4. **Confluence Changes section** — every page listed MUST include its full Confluence link:
   `[Title]({CONFLUENCE_BASE}/wiki/spaces/{SPACE}/pages/PAGE_ID)`

---

## Where Links Are NOT Required

- Tags section (decisions, risks, actions) — these use `→ctx:` references instead
- Pending section — these are internal references to `.lore/pending.md`
- People names — no links to profiles

---

## How to Construct Links

Base URLs are defined in `SOURCES.md`. Use these patterns:

| Source | Pattern |
|--------|---------|
| Confluence | `{CONFLUENCE_BASE}/wiki/spaces/{SPACE}/pages/{PAGE_ID}` |
| Jira | `{JIRA_BASE}/browse/{KEY}` |
| GitHub | `https://github.com/{OWNER}/{REPO}/blob/main/{PATH}` |
| Miro | Use the URL directly from the source |

Page IDs are available from `.lore/manifests/confluence.json` and from pull agent output.
Jira keys are available from Jira pull output.
GitHub owner/repo pairs are listed in `SOURCES.md`.

---

## Applies To

- All daily log files (`log/daily/YYYY-MM-DD.md`)
- Weekly/monthly condensation: preserve links from narrative sections
