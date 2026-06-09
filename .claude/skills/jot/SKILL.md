---
name: jot
description: Quickly capture anything from a session — notes, todos, feedback, recaps. Smart formatting, optional save to Lore.
---

# Skill: /jot

Quickly jot down whatever you need from this session.
One command for everything you want to capture, share, or remember.

## --help

When invoked as `/jot --help` or `/jot -h` — print this and stop:

```
/jot — Quickly capture anything from a session

Usage:
  /jot [text]             quick note or observation
  /jot todo [text]        action item
  /jot watch [text]       VP watch list item (strategic leadership attention)
  /jot watch list         show active watch items
  /jot watch resolve [ID] resolve a watch item
  /jot correct [text]     correct knowledge (updates knowledge/ directly)
  /jot resolve [INC-ID]   resolve an inconsistency
  /jot feedback [text]    session quality issue
  /jot recap [focus]      session summary (full or focused)

Examples:
  /jot team lead mentioned partner timeline is shifting
  /jot todo check with PM whether M2 date still holds
  /jot watch compliance gap risk — no equivalent capability before MVP
  /jot watch list
  /jot watch resolve WATCH-03 "confirmed in leadership sync"
  /jot correct M2 date moved from June to July — confirmed in standup
  /jot resolve INC-015 confirmed: network connectivity is via service mesh
  /jot feedback briefing missed a workstream completely
  /jot recap
  /jot recap focus on the infrastructure discussion

Output: formatted for copy/paste (Slack, email) or saved to Lore.
At the end you choose: Save? (git commit + push)
```

---

## Type Detection

If no explicit type keyword is given, detect from context:

| Signal | Type |
|--------|------|
| First word is `todo` or `task` | todo |
| First word is `watch` | watch |
| First word is `correct` or `fix` | correct |
| First word is `resolve` | resolve |
| First word is `feedback` or `bug` | feedback |
| First word is `recap` or `summary` | recap |
| No args at all | recap (interactive) |
| Anything else | note |

The user can always override: `/jot todo ...` forces todo regardless of content.

---

## Behavior by Type

### note

Quick observation, signal, or piece of informal intelligence.

1. Take text verbatim — no editing, no summarizing
2. Add 1-2 sentences of session context (what was being discussed)
3. Format for output
4. Offer to save

### todo

Action item for the delivery lead.

1. Take text verbatim
2. Add session context (what triggered this task)
3. Format for output
4. Offer to save

### watch

VP watch list item — strategic items requiring leadership attention.

**Sub-commands:**
- `/jot watch [text]` → add new item to watch list
- `/jot watch list` → show active items
- `/jot watch resolve [ID]` → mark item as resolved (ask reason if not inline)
- `/jot watch resolve [ID] "[why]"` → resolve with inline reason

**Add flow:**
1. Detect author (see `rules/author-detection.md`)
2. Read `knowledge/watch-list.md`, find highest `WATCH-XX`, increment
3. Add row to the Active table
4. Confirm: "Added WATCH-[XX]: [text] — watching."
5. No save prompt — writes to `knowledge/watch-list.md` directly (atomic)

**Resolve flow:**
1. Find the row in `knowledge/watch-list.md`
2. If no reason given: ask "Why is this resolved? (one sentence)"
3. Move to Resolved section with date and reason
4. Confirm: "WATCH-[XX] resolved: [reason]"

**List flow:**
Display all active items:
```
## VP Watch List — [N] active items

| ID | Item | Owner | Added | Days |
|----|------|-------|-------|------|
| WATCH-01 | [text] | [author] | [date] | [days since added] |

[Items > 14 days: flag with ⚠]
```

**What goes on the watch list:**
- Unresolved risks that could escalate
- People/team unknowns that affect delivery
- Dependencies on external decisions
- Timeline threats not yet reflected in milestones

**NOT for the watch list:**
- Tactical action items (use `/jot todo` instead)
- Already-decided things (use knowledge/decisions-open.md)
- Inconsistencies (use `/ask inconsistencies`)

**Watch list rules:**
- IDs are sequential (WATCH-01, WATCH-02, ...). Never reuse.
- Never auto-resolve. Only the user can resolve.
- Auto-detect duplicates before adding.
- File location: `knowledge/watch-list.md`

**Integration with /briefing:**
- VP briefing: shows active watch items (max 5, > 14 days get ⚠)
- Exec briefing: only items > 21 days AND exec-level (partner/budget/cross-solution)
- Weekly briefing: shows full watch list in section 3

### correct

Correct information in `knowledge/` directly.

1. Parse what the user says is wrong and what the new truth is
2. Find the relevant `knowledge/` file(s)
3. Show the current state vs. the correction
4. On save:
   - Edit the `knowledge/` file(s) directly
   - Write a `CHANGELOG.md` entry documenting the correction
   - `git add` + `git commit` + `git push`

No contributions/ file is created — this writes to knowledge/ directly.
The CHANGELOG entry is mandatory (documents what changed, why, and who said so).

### resolve

Document the resolution of an open inconsistency.

1. Parse the INC-ID and the user's resolution statement
2. Find the inconsistency in `.lore/inconsistencies.md`
3. Show the conflicting states and the proposed resolution
4. On save:
   - Write a contributions/ file: `contributions/YYYY-MM-DD-resolve-INC-XXX.md`
   - The file documents: what's correct, why, and who decided (author)
   - `git add` + `git commit` + `git push`

**Important distinctions:**
- `/jot resolve` creates a **contribution** that documents what is correct. It does NOT:
  - Fix the inconsistency in the sources
  - Communicate the resolution to anyone
  - Remove the inconsistency from `.lore/inconsistencies.md`
- The inconsistency status changes to `resolved` but with a note that source resolution and communication are still pending.
- `/override` is the stronger mechanism: it writes to OVERRIDES.md, gets actively checked on every pull, and disappears automatically once sources match.
- An override can also be resolved by a `/jot resolve` contribution that unambiguously clarifies the correct state.

**When to use which:**
- `/jot resolve` — "I know what's correct, documenting it for the record"
- `/override` — "This must be actively enforced until sources catch up"

### feedback

Something was wrong or off in this session.

1. Take text verbatim
2. Capture session context:
   - Which skills were invoked
   - The trigger prompt
   - Relevant excerpt of Claude's response
   - Sources consulted
3. Format for output
4. Offer to save

### recap

Session summary — the most interactive mode.

1. If no focus given: summarize the full session
2. If focus given: extract only what's relevant to that topic
3. Show structured summary:
   - Key signals
   - Decisions / direction
   - Open questions
   - What should go into Lore (if anything)
4. Ask: save / adjust / copy & go / discard

---

## Output Formatting

Always format output so it's immediately usable — whether copied to Slack, pasted into an email, or saved to Lore.

### For note / todo / feedback:

```
**[Type]: [title or first words]**

[content]

_Context: [1-2 sentences what was being discussed]_
```

### For recap:

```
## Session Recap — YYYY-MM-DD

### Key Signals
- [signal]

### Decisions / Direction
- [decision]

### Open Questions
- [question]

### For Lore
[what should be incorporated — or "nothing new" if session was routine]
```

---

## End-of-Jot Flow

After showing the formatted output, ask:

```
→ Save? (git commit + push)
```

- **Yes / Save** → write to `contributions/YYYY-MM-DD-[type]-[slug].md`, then `git add` + `git commit` + `git push`
- **No** → done, nothing saved

One question. No other options.

---

## Smart Hints

Contextually show ONE short hint when it helps — not every time.

When to hint:
- User invokes `/jot` for the first time in a session → show available types
- Session had significant content but user only jots a note → "Tip: /jot recap captures the full session"
- User writes a long note that looks like a task → "This reads like a todo — want me to tag it as one?"

When NOT to hint:
- User already used `/jot` multiple times
- Small, obvious task
- User is clearly in a hurry (short message, no context)

Format: one line, italic, at the end. Never before the content.

---

## AI Reasoning (optional)

For recaps and complex notes, briefly surface your reasoning when it adds value:

- What you included and why
- What you deliberately left out
- Confidence level if data was thin

Format: short italic block after the main content, before the save prompt.

```
_I focused on the infrastructure discussion because that's where new information surfaced.
Left out the standard status updates — nothing changed there._
```

When NOT to include reasoning:
- Simple todo or note (the content speaks for itself)
- User is clearly just dropping something quick
- Session was short and straightforward

---

## File Format (when saving to Lore)

```markdown
---
type: [note|todo|correct|resolve|feedback|recap]
from: [author per .claude/rules/author-detection.md]
date: YYYY-MM-DD
status: pending
---

[formatted content as shown above]
```

Filename: `contributions/YYYY-MM-DD-[type]-[slug].md`
Slug: first 3 meaningful words, kebab-case.

---

## References

- `.claude/refs/tagging.md` — canonical audience + content tags (apply when tagging contributions)

---

## Rules

1. **Verbatim for notes/todos/feedback** — never rephrase what the user said
2. **Never auto-save** — always ask, always one prompt
3. **Privacy** — never include content from ## Confidential or ## Private sections in recaps
4. **Context-adaptive** — match output length to session complexity. Small session = small recap. Big session = structured recap.
5. **No fluff** — no "great question!", no "here's what I captured:", no filler
6. **One confirmation line** — for note/todo/feedback. Recap gets the full interactive flow.
7. **Internal consistency** — when `/jot correct` modifies a knowledge file, scan ALL sections in that file for lists, tables, counts, and overviews that reference the same structure. Update them all in the same operation. A file with conflicting internal counts is a bug.
8. **Tag consistency** — when setting tags on contributions, use only tags defined in `.claude/refs/tagging.md`. Suggest new tags when content doesn't fit existing ones.

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- `knowledge/INDEX.md` — for `/jot correct`: identify which knowledge file to update via Key Topics and Answers
- `knowledge/INDEX.md` — for `/jot watch`: locate watch-list.md
- `contributions/INDEX.md` — for `/jot resolve`: verify INC-ID context

### Index Write
- `contributions/INDEX.md` — after saving any contribution file (note, todo, resolve, feedback, recap): add entry with File, Type, What, From, Tags, Date, Status=pending
- `knowledge/INDEX.md` — after `/jot correct` modifies a knowledge file: update the entry's Updated date and refresh Key Topics/Answers if content changed significantly
