# Rule: Log Writing

Logs are the memory of the project.
They are written daily — from pull data and manual entries.
They must be readable for humans and processable by Claude.

---

## Core Principles

1. **Context stays in context.**
   Decisions, Risks, and Actions are never isolated.
   Always anchored in the narrative — then additionally tagged.

2. **Only what actually happened.**
   No wishful future thinking. No "will be done".
   What is documented is documented. What is not — is not.

3. **One log entry per day.**
   All sources in one file. Connections remain visible.

4. **Tags at the end — never inline in the narrative.**
   The narrative is for humans.
   The tags are for Claude.

---

## File & Path

```
log/daily/YYYY-MM-DD.md     ← daily, deltas only
log/onboarding/             ← first pull only, read-only after
```

---

## Daily Log Structure

```markdown
# Daily Log – YYYY-MM-DD

## Pull Metadata
Pull timestamp:     YYYY-MM-DD HH:MM (Europe/Vienna)
Sources pulled:     [list]
Items read:         [N]
Items pending:      [N] → .lore/pending.md
Tokens used:        [N] / [BUDGET]
Coverage:           [X]%
Sources not pulled: [list with days since last pull]

---

## Context & Narrative
Free text. What happened today.
Background of decisions. Team mood.
What triggered it. What surprised.
No structure — just write.
This is the human-readable layer.
Mention Decisions, Risks, Actions in context —
they will be additionally tagged below.

---

## Journal
[New journal entries, full content]

## Jira Changes
[Changed items with status change and owner]
Format: - [KEY] [Title] → [Old Status] → [New Status] – [Owner] – [Link]

## Confluence Changes
[Changed pages with author and one-sentence summary]
Format: - [Title] – [Author] – [what changed] – [Link]

## GitHub Changes
[New commits with message and author]
Format: - [repo] [sha] [message] – [author]

## Pending
[Items not yet read — from .lore/pending.md]

---

## Decisions
- [audience][decision] [Description] – Owner: [Name] – →ctx:[ID if available]
- [audience][decision][arch] [Description] – Owner: [Name] – →ctx:[ID]

## Risks
- [audience][risk] [Description] – Owner: [Name] – Deadline: [Date] – Trend: [↑→↓] – →ctx:[ID if available]

## Actions
- [audience][action] [What] – Owner: [Name] – by: [Date]

## Open Questions
- [audience][question] [Question] – Owner: [Name] – →ctx:[ID if complex]

## Concepts
- [concept] [Term] – →concept:[slug] (new/extended)

---

## Tagging Review
- [ ] All decisions tagged?
- [ ] All risks tagged?
- [ ] All actions with owner and date?
- [ ] All open questions tagged?
- [ ] [concept] tags where new terms appear?
- [ ] [arch] tags checked → ADR needed?
- [ ] →ctx: links set for decisions and risks (pointing to knowledge IDs)?
```

---

## Tag Reference

Full tag definitions: `.claude/refs/tagging.md`

Audience tags (always set, never omit): `[exec]`, `[vp]`, `[vp:delivery]`, `[vp:sales]`, `[vp:legal]`, `[lead]`, `[team]`. Default: `[lead]`.
Content tags: `[decision]`, `[risk]`, `[action]`, `[question]`, `[event]`, `[arch]`, `[concept]`.
Risk trends: `[↑]` worsening, `[→]` stable, `[↓]` improving.

---

## References

```
→ctx:DEC-07           ← link to knowledge entry (Decision)
→ctx:RISK-03          ← link to knowledge entry (Risk)
→ctx:OPEN-12          ← link to knowledge entry (Open Question)
→concept:service-mesh ← link to knowledge node
→log:2026-05-01       ← back-reference to another log entry
→roadmap:M3           ← link to milestone
```

`→ctx:[ID]` is an alias for "see the corresponding knowledge entry".
The ID must match an entry in `knowledge/decisions.md`, `knowledge/risks.md`,
or `knowledge/decisions-open.md`.

---

## What Goes in the Log

**YES:**
- Decisions with reasoning and context
- Status changes with background (why blocked — not just that it is)
- New risks with origin
- What was completed and what it means
- Open questions no one has yet answered
- New terms or concepts that appeared

**NO:**
- Complete documents (only link + one-sentence context)
- Routine updates without change
- Content that is verbatim in sources (reference + link only)
- Technical details only an engineer needs (→ team tag or omit)
- Future plans without a decision

---

## Condensation Rules

Full spec: `.claude/refs/condensing.md`

Condensation lifecycle: daily (14d) → weekly (3mo) → monthly (6mo) → quarterly (6Q) → yearly (forever).
See `.claude/refs/condensing.md` for the complete rules per tag type and level.
