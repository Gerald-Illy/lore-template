# Rule: Output Standards

How all user-facing output must look.

---

## Provenance Footer

Every output from `/briefing`, `/ask`, or any synthesized answer MUST end with:

```
---
**Data provenance**
Last pull: YYYY-MM-DD HH:MM (Europe/Vienna) | Sources used: [list] | Freshness: [indicator]
```

**Freshness:** `current` (0–4h) · `recent (Xh ago)` (4–24h) · `stale (N days) — consider /pull` (1–3d) · `outdated (N days) — /pull recommended` (>3d)

Rules:
- Never omit. Even if the answer is short.
- Be specific about sources — not "all sources" but what was actually read.
- If an override influenced the answer: mention it.
- Stale = quality warning, not just metadata.

---

## ID References

| Prefix | Meaning |
|--------|---------|
| `DEC-##` | Decided (closed) |
| `OPEN-##` | Open decision |
| `INC-###` | Inconsistency |
| `RISK-##` | Tracked risk |
| `ACTION-##` | Tracked action |
| `QUESTION-##` | Open question |

**In prose:** first mention includes short title — `DEC-07 ("Selected Availability")`. Subsequent mentions: bare ID.

**In tables:** no inline title needed when an adjacent column explains it.

**Footer legend:** only when 5+ different IDs appear across multiple types.

**Never expand:** inside tables with description columns, in internal logs, in "see also" lists.

---

## Author Detection

When attributing input to a person (e.g. `from:` in /jot, author in /override):

1. `git config user.name` — primary
2. OS username — fallback
3. Ask — if neither works

Use the name as-is. Never guess. Never normalize.
