# Briefing Variant: Slack

Lightweight catch-up message for Slack — written for a specific person
who missed context (vacation, sick, offsite).

---

## When to use

- Someone was away and needs a quick catch-up
- You want to inform a team member via Slack about project state
- Any situation where a formatted briefing would be too heavy

---

## Argument Parsing

```
/briefing slack                    → ask: who, how long away, focus?
/briefing slack [person]           → ask: how long away, focus?
/briefing slack [person] [Nd|Nw]  → generate with timeframe (d=days, w=weeks)
```

Examples:
```
/briefing slack Alex 1w
/briefing slack Sam 3d
/briefing slack Jordan
```

---

## Interactive Prompts (if not provided)

1. **Who?** — Name of the recipient (used for tone, not filtering)
2. **How long away?** — Timeframe to cover (e.g. "1 week", "3 days", "since May 28")
3. **Focus?** — Optional. "risiken + next actions", "alles", "nur decisions" etc. Default: balanced overview.
4. **Language?** — Detect from user's prompt language. If unclear: ask.
5. **Additional context?** — "Anything not in Lore that should be included? (meetings, calls, decisions you made this week)" — user can add free text that gets woven in naturally.

---

## Data Loading

1. Determine date range from timeframe
2. Load daily logs within that range (log/INDEX.md → filter by date)
3. Load state file if ≤24h old (log/state/)
4. Skim knowledge files only for items that CHANGED in the timeframe (check Updated dates in knowledge/INDEX.md)
5. Check contributions/INDEX.md for pending signals in timeframe

Keep it light — this is NOT a full briefing. Load only what's needed for a conversational summary.

---

## Output Format

**3-4 natural paragraphs.** Written as if you're typing a Slack message to a colleague.

Structure (implicit, NOT as headers):
1. **Opening + Biggest News** — welcome back, here's what moved. Lead with the most impactful thing.
2. **Status & Good News** — what's working, what got achieved, positive momentum
3. **Risks & Open Items** — what's still risky or unresolved (brief, not alarmist)
4. **This Week & Next Actions** — what's happening now, what the person should know about

Rules:
- NO markdown headers (##)
- NO bullet lists (unless user explicitly asks)
- Bold (**text**) sparingly for emphasis — only key terms
- Casual but precise tone — like writing to a senior colleague
- Maximum 300 words (aim for 200)
- End with an offer ("Fragen? Sonst im Call.")
- Language matches the user's prompt language
- Include greeting and sign-off appropriate for Slack

---

## What to include

| Include | Don't include |
|---------|--------------|
| Milestone status changes | Routine Jira updates |
| New decisions (DEC-*) | Full decision rationale |
| Active risks (summarized) | INC-* details |
| Forward motion / achievements | Historical context |
| This week's key meetings/actions | Actions already completed |
| User-provided additional context | Provenance footer |
| People/team changes | Full team mapping |

---

## What NOT to do

- No LORE header block (this is a Slack message, not a report)
- No provenance footer (casual channel, not auditable output)
- No blockquotes or formatting-heavy structures
- No diplomatic padding — direct and honest, but not alarmist
- Don't list every single Jira ticket — only mention if it's significant
- Don't over-explain context the recipient already knows (they work here)

---

## User Review Flow

After generating:

```
---
Ready to paste. Adjustments? (kürzer / mehr detail / anderer fokus / passt)
```

- **passt** / **gut** → done
- Adjustment request → regenerate with feedback
- User provides additional info → weave in and regenerate

No save prompt. This is ephemeral output for Slack — not a Lore artifact.

---

## Example Output (German, 1 week vacation)

```
Hey [Name], welcome back! Quick update from last week: **M1** won't close all items
completely, but the **key goals are achievable** — core validation is running, main
service works on the target platform. Things like lifecycle support will only be
minimal and need to be followed up by M2. The operator track is moving well (12 new
stories after bootstrap close), PoC is validated.

For **M2** we don't have owners everywhere yet, but the big **topics are addressed**:
Auth is running, licensing is running, other topics are in our own hands. Kickoffs all
completed successfully, next steps landed well. Two streams already have Jira tickets.

This week: Today workshop on licensing, Thursday auth planning. We have about 6 people
from another team in prospect — onboarding prepared, one staffing decision still open.
Support topics identified, alignment in progress.

Questions? Otherwise in the call.
```

---

## RAG-Light Compliance

This skill variant is RAG-light compliant.

### Index Read
- `log/INDEX.md` — identify daily logs within the specified timeframe
- `knowledge/INDEX.md` — identify knowledge files with Updated date within timeframe
- `contributions/INDEX.md` — pending signals within timeframe

### Index Write
- None (ephemeral output, not saved to Lore)
