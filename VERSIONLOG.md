# Version Log

All versions of the Lore template.

---

## [1.0.0] — 2026-06-09

### Added
- **Slack briefing variant (`.claude/skills/briefing/slack.md`):** Lightweight, conversational Slack catch-up messages for people returning from vacation or offsite. Full skill with argument parsing, interactive prompts, RAG-light compliance.
- **Merge resolution rules (`.claude/refs/merge-resolution.md`):** Deterministic conflict resolution for all Lore file types — manifests, CHANGELOG, indexes, inconsistencies, logs, knowledge files. Enables multi-session work without human bottlenecks.
- **Merge check in session-end (`.claude/rules/session-end.md`):** New priority-one step — resolve conflicts before any other session-end action.
- **`/lore check` Phase 2 + 3:** Recommended manual validation steps (Dry-Run Setup, Smoke-Test with Mock Data) output after structural lint passes. Not yet automated.
- **Plugin reference in README:** [lore-plugin](https://github.com/Gerald-Illy/lore-plugin) documented as standard setup path.
- **Full skill suite:** ask, briefing (exec, vp, weekly, slack, leads), escalate, override, jot, pull, crawl, atlassian, publish, mc, reasoning, artifact, lore.
- **8 agents:** loremaster, pull-confluence, pull-jira, pull-journal, pull-sharepoint, crawl-coordinator-jira, crawl-coordinator-confluence, crawl-reader.
- **Rules:** never-invent, RAG-light, privacy, output standards, session-end, agent-learning.
- **Refs:** pull-framework, merge-resolution, tagging, consistency-check, extraction-quality, ai-inference, log-writing, log-links, auto-log-format, condensing, decision-impact-scan, lore-reference.
- **RAG-Light index system:** knowledge/, log/, contributions/ with structured INDEX.md formats (Sachbuch, Journal, Signal).
- **Privacy sections:** Public / Confidential / Private with read-access rules.
- **Plugin compatibility:** Works with [lore-plugin](https://github.com/Gerald-Illy/lore-plugin) v1.4.1+.
