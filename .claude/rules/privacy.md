# Rule: Privacy

This rule always applies – when writing, reading, and summarizing files.

---

## Section Hierarchy

Files have three clearly separated sections, always in this order:

```markdown
## Public
[Project knowledge, meetings, decisions, action items]

## Confidential
[Only for leadership, VP, and exec briefings]

## Private
[Personal, 1:1s, sensitive assessments, unfinished thoughts]
```

`## Confidential` and `## Private` always go at the end – in this order.

---

## When Writing Files

Automatically separate into the corresponding sections.
For borderline cases, show a preview and ask – do not decide alone.

---

## When Reading Sources

| Section | Default | With explicit request |
|---|---|---|
| `## Public` | ✅ read | ✅ |
| `## Confidential` | ❌ do not read | ✅ only in leadership/VP/exec context |
| `## Private` | ❌ do not read | ✅ only when user explicitly requests |

---

## Important Security Note

**These sections are not a technical security solution.**
They only prevent standard commands and normal briefings from accessing this content.
Anyone with repo access who specifically looks for it can read `## Confidential` and `## Private` at any time.

The sections serve to:
- Create awareness of what is sensitive
- Prevent accidental access
- Provide a clear foundation for adding real protection later

---

## Recommendations for Real Protection

**Low sensitivity** (accidental access should be prevented)
→ Section convention is sufficient. This is the default here.

**Medium sensitivity** (only specific people should have access)
→ Separate GitHub repo with explicit collaborators.
Anyone not invited sees nothing – regardless of Claude.

**High sensitivity** (encrypted, even repo owner should not easily access)
→ `git-crypt` or `age` encryption.
File is stored encrypted in the repo, only key holders can open it.
