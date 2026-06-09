# Lore Template

A ready-to-use template for **Lore** — a living project intelligence framework that connects distributed sources (Jira, Confluence, GitHub, SharePoint) into a single queryable memory.

**Not an archive. A memory.**

---

## What is Lore?

Lore is an AI-powered co-delivery framework that:
- Keeps full transparency on project state
- Surfaces problems before they become blockers
- Makes inconsistencies visible and trackable
- Prepares decisions, escalations, and briefings
- Never invents. Never interprets beyond the data.

Think of it as your project's **always-on delivery lead** — it knows what happened, what's planned, what's at risk, and what needs a decision.

---

## What's in this template?

```
.claude/          ← AI instructions (rules, skills, agents)
.lore/            ← Intelligence layer (config, manifests, learning)
artifacts/        ← Published HTML artifacts
log/              ← Aggregated daily/weekly project logs
knowledge/        ← Verified, structured project knowledge
contributions/    ← New human input (notes, todos, feedback)
SOURCES.md        ← Where your data sources live (Jira, Confluence, GitHub)
OVERRIDES.md      ← Human corrections to source data
CLAUDE.md         ← Main AI briefing and command reference
```

---

## How to use this template

### Option 1: Via Lore Plugin (recommended)

The **[Lore Plugin](https://github.com/Gerald-Illy/lore-plugin)** is the standard way to install and set up Lore.

```bash
# Install the plugin
git clone https://github.com/Gerald-Illy/lore-plugin.git
cd lore-plugin
# Follow the plugin's README for installation steps

# Then scaffold a new Lore project
lore setup <project-name>
```

The plugin will:
1. Clone this template into your project
2. Replace all `{PROJECT_NAME}` placeholders
3. Guide you through source configuration
4. Run the first data pull

### Option 2: Manual setup

See [SETUP.md](SETUP.md) for step-by-step instructions.

---

## Quick Start (after setup)

```bash
# Pull fresh data from all sources
/pull

# Get an operational briefing
/briefing

# Ask the knowledge base anything
/ask "What's blocking Platform Services?"

# Capture a quick note or todo
/jot "API migration needs decision on auth strategy"

# Draft an escalation
/escalate OPEN-05
```

Full command reference: See `CLAUDE.md` after setup.

---

## Requirements

- **Claude Code** (VS Code extension, CLI, or Desktop app)
- **Git** repository for your project
- **Source access:** Jira, Confluence, GitHub (minimum)
- **Optional:** SharePoint for document extraction

---

## Philosophy

Lore is designed around three core principles:

**1. Never invent**  
If it doesn't know something, it says so. Explicitly. No diplomatic padding.

**2. Timestamp beats authority**  
Newer information wins — but only when a human consciously decided it.

**3. Contradictions are information**  
When sources disagree, both states are surfaced. No silent resolution.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Support

- **Plugin (recommended setup path):** [github.com/Gerald-Illy/lore-plugin](https://github.com/Gerald-Illy/lore-plugin)
- **Template issues:** Open an issue on this repository
- **Documentation:** See `CLAUDE.md` and `.claude/` after setup
