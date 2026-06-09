---
name: override
description: Correct wrong information in Lore — writes to OVERRIDES.md. Usage: /override "[What's wrong]" "[What's correct]"
---

## --help

When invoked as `/override --help` or `/override -h` — print this and stop:

```
/override — Correct wrong information in Lore (writes to OVERRIDES.md)

Usage:
  /override "[what's wrong]" "[what's correct]"

Examples:
  /override "M3 target is 2026-Q3" "M3 target is 2026-Q4"
  /override "Owner of workstream X is Alice" "Owner of workstream X is Bob"
  /override "Feature Y not resolved" "Feature Y resolved as of 2026-05-15"

What happens:
  1. Entry written to OVERRIDES.md immediately
  2. Claude asks: correct directly in source or notify owner?
  3. Option A: shows exact change needed in the source file
  4. Option B: drafts notification message to source owner (waits for approval)

Tip: For session quality issues use /feedback.
     For tasks use /todo. For observations use /note.
```

# Skill: /override "[What's wrong]" "[What's correct]"

1. Create entry in OVERRIDES.md (immediately)
2. Ask: "Correct directly in source or notify owner?"

## Option A: Correct directly
→ Open source if access available
→ Show exactly where the change needs to be made

## Option B: Notify owner
→ Load knowledge/team.md → find source owner
→ Create message draft:

---
To: [Owner]
Subject: Correction needed – [Source]

In [Source/Link] it currently states:
"[Wrong info]"

Correct is:
"[Correct info]"

Please update. Thank you.
[Suggested fix as copy-paste]
---

→ Wait for approval. Never send without confirmation.

## After correction in source
→ Set override entry status to "Corrected"
→ On next pull, override automatically becomes obsolete

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- `knowledge/INDEX.md` — for Option A (correct directly): identify which knowledge file contains the wrong information via Key Topics and Answers
- `knowledge/INDEX.md` — for Option B (notify owner): locate team.md for source owner lookup

### Index Write
- None (OVERRIDES.md is self-indexed — the table IS the retrieval surface)
