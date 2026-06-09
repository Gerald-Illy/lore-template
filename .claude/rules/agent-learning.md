# Rule: Agent Learning

How skills and agents capture operational learnings.

---

## No Local Memory

**Never write to local memory files** (outside the repo).

All operational knowledge belongs in the repo — in `.lore/agent-learning.md`,
rules, skills, or agents. This ensures every Lore user has the same experience
regardless of their local Claude configuration.

Local memory (`~/.claude/projects/.../memory/`) is not used for this project.

---

## When to Write a Learning

After a skill or agent execution that produced a suboptimal result:
- Wrong output format
- Missed data that should have been caught
- Unnecessary steps or token waste
- Edge case not covered by the skill spec
- User had to correct or redirect

Write a learning entry to `.lore/agent-learning.md`.

---

## Environment Gate

**Only write learnings in VS Code sessions.**

Do NOT write learnings in CLI sessions (Claude Code terminal).
CLI is used by Lore consumers — learnings there would be noise.

Detection: if the session environment indicates VS Code (IDE extensions,
MCP servers like `pylance_mcp_server`, `ide` tools present), learnings
are allowed. Otherwise: skip silently.

---

## Format

```markdown
## L-XXX: [Short title] (YYYY-MM-DD)

[What went wrong or could be improved — one paragraph max.]

**Skill/Agent:** [which skill or agent this applies to]
**Rule:** [the concrete improvement — what should be done differently]
```

Increment the L-XXX number sequentially.

---

## Promotion

Learnings stay in `agent-learning.md` until explicitly promoted to the
corresponding skill, agent, or rule file. Promotion means:

1. Integrate the learning into the target file (rule, constraint, or step)
2. Remove the entry from `agent-learning.md`
3. Log in loremaster-log

---

## Size Guard

When `agent-learning.md` exceeds **10 entries**: surface a notice to the user:

```
⚠ Agent learning file has [N] entries. Consider promoting learnings
  into their target skills/agents/rules. Run: /lore promote-learnings
```

This is a suggestion, not a blocker. Do not auto-promote.

---

## What NOT to Learn

- Correct behavior (only capture deviations)
- One-off situations that won't recur
- Things already covered by existing rules

---

## Git Operations

Never auto-commit or auto-push without explicit user confirmation.
Skills that offer a save flow (like `/jot`) ask the user first:

```
→ Save? (git commit + push)
```

Only on explicit "yes", "commit", "push", or equivalent → execute `git add` + `git commit` + `git push`.
Never infer commit intent from content approval ("passt", "sauber") alone.
