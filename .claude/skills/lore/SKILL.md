---
name: lore
description: "Develop, test, fix, or improve the Lore framework. Usage: /lore [check|test|fix|log|plugin]"
---

# Skill: /lore [action]

Invokes the Loremaster to develop and improve the framework.

## --help

When invoked as `/lore --help` or `/lore -h` — print this and stop:

```
/lore — Develop, test, fix, or improve the Lore framework

Usage:
  /lore [action]

Actions:
  (none)     quick health check — infrastructure + consistency + quality
  check      full setup checklist — presence, consistency, quality of all files
  test       walk through a workflow step by step
  fix        something is broken — agent diagnoses and fixes
  log        show .lore/loremaster-log.md (session history)
  plugin     check plugin integration health (/{project}:* command coverage)

Examples:
  /lore
  /lore check
  /lore fix
  /lore plugin

Tip: /lore check is more thorough than /lore (plain).
     Changes to .claude/ or .lore/ always require a loremaster-log entry.
     Plugin coverage: /{project}:* wraps ask, briefing, escalate, todo, note, recap, feedback.
```

## Scopes

```
/lore          → Show current setup status (quick health check)
/lore check    → Full setup checklist — completeness + consistency + quality
/lore test     → Walk through a workflow step by step
/lore fix      → Something is broken — agent diagnoses and fixes
/lore log      → Show .lore/loremaster-log.md (session history)
/lore plugin   → Check plugin integration health
```

---

## What the agent does

The agent always reads `.lore/loremaster-log.md` first, then `.claude/lore-design.md`
and `.claude/refs/lore-reference.md`. Do not carry structure knowledge internally —
read it fresh every time.

---

### /lore (quick status)

One-pass health check. Reads actual files, surfaces problems:

```
Setup Health – YYYY-MM-DD

✅ Complete | ⚠ Partial | ❌ Missing

Infrastructure:
  [per-file status]

Consistency gaps:
  [CLAUDE.md vs actual files, lore-reference.md currency, etc.]

Quality flags:
  [bloated skills, missing refs, agents duplicating skill content]

Blocking /pull: Yes/No → [what to fix first]
Next step: [one concrete action]
```

---

### /lore check

Systematic walk through the full checklist in `.claude/refs/lore-reference.md`
(Setup Minimum Viable State + Dependency Map).

For each item: ✅ present and correct / ⚠ exists but stale or partial / ❌ missing.

**Also checks quality, not just presence:**
- Are SKILL.md files well-structured? (frontmatter, refs section, clear steps)
- Does every SKILL.md have a `## --help` section? (mandatory — every command must respond to `--help` / `-h` with usage, subcommands, examples, and a cross-skill tip)
- Are agents lean, or duplicating content that belongs in skills?
- Are refs loaded only where needed, or everywhere by default?
- Is `.lore/config.md` complete for every source in `SOURCES.md`?
- Does `knowledge/INDEX.md` match actual files in `knowledge/`?
- Are there skills in `skills-todo/` that should be promoted to `skills/`?

**Compliance sub-check (template-only):**

Scans all tracked files for information that must not leak into the public template:

| Category | Pattern | Allowed |
|----------|---------|---------|
| Company names | Employer names, internal project codenames | ❌ Replace with `{PROJECT_NAME}` |
| Personal names | Real team member names in examples | ❌ Replace with generic names (Alex, Sam, Jordan) |
| Emails | Real `@company.com` addresses | ❌ Use `you@company.com` placeholder |
| Internal URLs | Intranet, Jira, Confluence instances | ❌ Use `{CONFLUENCE_BASE}`, `{JIRA_BASE}` |
| GitHub owner links | Links to plugin/template repos | ✅ Public repos — owner name is intentional |
| Placeholder tokens | `{PROJECT_NAME}`, `{OWNER}`, `{SPACE}` | ✅ Must remain as-is |

**Scan command (grep-based):**
```
grep -rni "<list of known company/personal patterns>" --include="*.md" --include="*.json" --include="*.py"
```

Exclude: `.git/`, `node_modules/`, paths that are clearly placeholder examples (`you@company.com`).

**On failure:** List all matches with file + line number. Do not auto-fix — show to user for decision (some may be intentional).

---

### /lore check — Phase 2: Dry-Run Setup (manual, recommended)

> **Status:** Not yet automated. Output as recommendation after Phase 1.

After the structural lint passes, recommend:

```
──────────────────────────────────────────────
📋 Recommended: Dry-Run Setup Test

Validates that the template works end-to-end when freshly set up.

Steps:
1. Clone template into a fresh temp directory
2. Replace all {PROJECT_NAME} placeholders with "test-project"
3. Run /lore check — should pass without errors
4. Run /ask "test" — should follow RAG-Light path, report "not indexed"
5. Run /briefing — should report missing data gracefully (not crash)
6. Run /pull onboarding — should detect empty SOURCES.md and report

Pass criteria:
- No crashes or unhandled errors
- Missing data surfaces as explicit "no data" messages (never-invent rule)
- All index files exist and are structurally valid (even if empty)

Not yet automated. Run manually after template changes.
──────────────────────────────────────────────
```

---

### /lore check — Phase 3: Smoke-Test with Mock Data (manual, recommended)

> **Status:** Not yet automated. Output as recommendation after Phase 2.

After dry-run passes, recommend:

```
──────────────────────────────────────────────
📋 Recommended: Smoke-Test with Mock Data

Validates that RAG-Light retrieval, briefings, and /ask work with minimal data.

Setup:
1. Add minimal SOURCES.md entry (e.g. fake Confluence space)
2. Create knowledge/test-workstreams.md with 3 dummy workstreams
3. Create log/daily/2026-01-01.md with a sample daily log
4. Update knowledge/INDEX.md and log/INDEX.md with entries

Test matrix:
| Command                        | Expected behavior                                    |
|--------------------------------|------------------------------------------------------|
| /ask "What workstreams exist?" | Finds test-workstreams.md via INDEX, returns content  |
| /ask "What happened Jan 1?"   | Finds daily log via INDEX, returns signals            |
| /ask "unknown topic"           | Reports "not indexed" — does NOT hallucinate          |
| /briefing                      | Produces structured output using available data       |
| /jot "test note"               | Creates contribution, updates contributions/INDEX.md  |
| /override "A" "B"             | Creates entry in OVERRIDES.md                         |

Pass criteria:
- RAG-Light path is followed (index first, then load)
- Never-invent rule holds (no fabricated content)
- Index updates happen on write
- Provenance footer is present on all outputs

Not yet automated. Run manually after significant template changes.
──────────────────────────────────────────────
```

---

### /lore test

Walk through a workflow step by step. Agent asks which workflow if not specified.

For each step: check preconditions → execute or simulate → note result.
Document what worked and what did not. Write to loremaster-log.

---

### /lore fix

User reports something broken or wrong.

1. Identify which files are involved
2. Identify all downstream dependencies via the Dependency Map
3. Make the change
4. Resolve every dependency — no inconsistencies left behind
5. Verify: does CLAUDE.md match actual skill/agent files?
6. Verify: does `lore-reference.md` match actual skill/agent files?
7. Write CHANGELOG entry + loremaster-log entry

---

### /lore log

Show `.lore/loremaster-log.md` — session history and open items.

---

### /lore plugin

Check that the plugin integration is healthy. The plugin repo is at
`https://github.com/{OWNER}/lore-plugin` — read it if you need to understand
template structure or what's configurable.

Runtime layout:
```
~/.lore/
  .plugin/              ← generic framework (cloned by setup, updated via /lore:update --all)
    commands/           ← source of /lore:* commands
    templates/          ← *.tpl files that generate /{project}:* commands
  config.json           ← registry of connected projects
  {project}/                  ← this repo (cloned by /lore:setup)

~/.claude/commands/
  lore/                 ← installed /lore:* commands (copied from ~/.lore/.plugin/commands/)
  {project}/                  ← installed /{project}:* commands (generated from templates)
```

Templates (in `~/.lore/.plugin/templates/`):
```
_preamble.md.tpl   ← shared runtime context (Steps 0–2.5), generates _preamble.md
ask.md.tpl         ← generates commands/ask.md
briefing.md.tpl    ← generates commands/briefing.md
escalate.md.tpl    ← generates commands/escalate.md
overwrite.md.tpl   ← generates commands/overwrite.md
jot.md.tpl         ← generates commands/jot.md
help.md.tpl        ← generates commands/help.md (self-contained)
plugin.json.tpl    ← generates commands/plugin.json
settings.json.tpl  ← generates commands/settings.json
```

Check:
1. Which skills in `.claude/skills/` are covered by a template → accessible as `/{project}:*`
2. Which production skills have no template → users must invoke directly in Claude
3. Are template references pointing to valid SKILL.md files in this repo?
4. Are generated commands in `~/.claude/commands/{project}/` stale vs current skill files?
   → Flag if `/lore:update {project}` needs to be run

Current coverage (v1.4.1):
```
Plugin health (YYYY-MM-DD):
✅ ask, briefing, escalate, overwrite, jot, help — template + generated command
❌ pull, inconsistencies, atlassian, publish, crawl, etc. — no template, direct invocation only
```

---

## References

Agent definition: `.claude/agents/loremaster/agent.md`
Lore design: `.claude/lore-design.md` (principles) + `.claude/refs/lore-reference.md` (structure, checklists)
Session memory: `.lore/loremaster-log.md`
Plugin repo: `https://github.com/{OWNER}/lore-plugin`
