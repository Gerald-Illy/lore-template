# .lore/recipes/

Retrieval recipes for the `/reasoning` skill.
Recipes capture successful retrieval strategies for reuse on similar future queries.

---

## Format

Each recipe is a single markdown file:

```markdown
# .lore/recipes/[pattern-name].md
---
pattern: "natural language description of queries this recipe matches"
strategy: |
  1. Primary files: [which knowledge files to start with]
  2. Graph walk: [what aspects to explore, what connections to follow]
  3. Temporal: yes/no (depth: recent/14d/30d/full)
  4. Live sources: [which, if any]
  5. Consistency: [which files to cross-validate]
confidence: high/medium/low
last_used: YYYY-MM-DD
hits: N
created_from: "original query that produced this recipe"
---
```

---

## Lifecycle

| Stage | Trigger |
|-------|---------|
| Created | After a complex query succeeds and user confirms "save as recipe" |
| Used | Matched by pattern on future `/reasoning` queries |
| Refined | If a recipe-guided answer still needs corrections |
| Decayed | Not used in 14 days → flagged for review |
| Pruned | Maximum 20 recipes — oldest/lowest-hit archived on overflow |

---

## Rules

- Recipes accelerate retrieval — they don't bypass quality gates
- A recipe match gives the reasoning a head start, not a shortcut
- Never auto-create recipes — always require explicit user confirmation
- Recipe saves require commit + push (persistent artifact)
- Stale recipes (decayed) are flagged, not auto-deleted
