# Version Log

All versions of the Lore template.

---

## [1.1.0] — 2026-06-10

### Added
- **Source Registry (`SOURCES.md`):** External source definitions via `source-registry` type. Teams can maintain their own sources (Confluence page, HTTP, local file) without touching the repo. Merge rules: local wins on ID collision, external adds only.
- **Web sources (`SOURCES.md`, `pull-framework.md`):** Live URL fetch with HTML→Markdown conversion, hash-based delta detection, Focus hints for section extraction, configurable schedule (every-pull/daily/weekly).
- **`/setup` skill (`.claude/skills/setup/SKILL.md`):** Interactive wizard for adding, editing, removing, and validating sources. Guided type-specific prompts, connectivity validation, manifest initialization.
- **Source Resolution in `/pull` (Phase 0):** Two-tier resolution — local SOURCES.md + external registries fetched and merged at runtime. Failure-tolerant (warn and proceed).
- **`/pull web` scope:** Dedicated scope for pulling only web sources.
- **`/setup update` subcommand:** Check for new or updated Lore skills, agents, rules, and refs against the plugin/template source. Presents a summary of what's new, what changed, and suggests safe updates to apply.

---

## [1.0.0] — 2026-06-09

### Added
- **Slack briefing variant (`.claude/skills/briefing/slack.md`):** Lightweight, conversational Slack catch-up messages for people returning from vacation or offsite. Full skill with argument parsing, interactive prompts, RAG-light compliance.
- **Merge resolution rules (`.claude/refs/merge-resolution.md`):** Deterministic conflict resolution for all Lore file types — manifests, CHANGELOG, indexes, inconsistencies, logs, knowledge files. Enables multi-session work without human bottlenecks.
- **Merge check in session-end (`.claude/rules/session-end.md`):** New priority-one step — resolve conflicts before any other session-end action.
- **`/lore check` Phase 2 + 3:** Recommended manual validation steps (Dry-Run Setup, Smoke-Test with Mock Data) output after structural lint passes. Not yet automated.
- **Plugin reference in README:** [lore-plugin](https://github.com/Gerald-Illy/lore-plugin) documented as standard setup path.
- **Full skill suite:** ask, briefing (exec, vp, weekly, slack, leads), escalate, override, jot, pull, crawl, atlassian, publish, mc, reasoning, artifact, lore, setup.
- **8 agents:** loremaster, pull-confluence, pull-jira, pull-journal, pull-sharepoint, crawl-coordinator-jira, crawl-coordinator-confluence, crawl-reader.
- **Rules:** never-invent, RAG-light, privacy, output standards, session-end, agent-learning.
- **Refs:** pull-framework, merge-resolution, tagging, consistency-check, extraction-quality, ai-inference, log-writing, log-links, auto-log-format, condensing, decision-impact-scan, lore-reference.
- **RAG-Light index system:** knowledge/, log/, contributions/ with structured INDEX.md formats (Sachbuch, Journal, Signal).
- **Privacy sections:** Public / Confidential / Private with read-access rules.
- **Plugin compatibility:** Works with [lore-plugin](https://github.com/Gerald-Illy/lore-plugin) v1.4.1+.
