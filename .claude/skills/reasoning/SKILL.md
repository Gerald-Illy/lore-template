---
name: reasoning
description: Deep multi-agent retrieval with semantic reasoning for complex queries. Spawns subagents for broad knowledge graph walks, runs mandatory quality gates at each phase, and offers to save successful strategies as recipes.
---

# Skill: /reasoning [question]

Deep retrieval and reasoning skill for complex queries that can't be answered
by standard RAG-Light index lookups. Uses subagents to read broadly across
knowledge, runs mandatory quality gates at every phase transition, and builds
a recipe library from successful strategies.

Standalone skill. Later integrable into `/ask` and `/briefing`.

---

## --help

When invoked as `/reasoning --help` or `/reasoning -h` — print this and stop:

```
/reasoning — Deep multi-agent retrieval with semantic reasoning

Usage:
  /reasoning [question]          → full reasoning flow with quality gates
  /reasoning --help              → this help text

Examples:
  /reasoning what's actually blocking launch readiness?
  /reasoning how do the IAM dependencies affect all workstreams?
  /reasoning what changed about the architecture since the kickoff?
  /reasoning is the current team allocation consistent with the roadmap priorities?

When to use:
  - Question needs cross-file synthesis (connects multiple knowledge areas)
  - Question requires understanding HOW things connect, not just WHAT they are
  - Answer has high impact (decision basis, escalation, stakeholder communication)
  - Previous /ask answer was insufficient (follow-up indicates depth needed)
  - Question requires temporal reasoning (evolution, changes, "since when")
  - Standard briefing templates don't cover the question

When NOT to use:
  - Simple factual lookup → use /ask
  - Standard status report → use /briefing
  - Live Jira/Confluence data → use /atlassian
  - Known format with defined scope → use the specific skill

Cost: Higher than /ask — spawns multiple subagents. Use when depth matters.
```

---

## Flow

```
/reasoning "complex question"

Phase 0: Complexity & Recipe Check
├── Run Gate 0 (complexity decision)
├── If simple → redirect to /ask with note
├── Check .lore/recipes/ for pattern match
└── Match found → use recipe strategy, adapt parameters to current query

Phase 1: Primary Retrieval (RAG-Light)
├── OVERRIDES.md (already in context)
├── knowledge/INDEX.md → identify primary files via Key Topics, Answers, Contains
├── contributions/INDEX.md → pending signals
├── log/INDEX.md → recent relevant entries
├── Load primary matched files
└── Run Gate 1 (before deep reading)

Phase 2: Semantic Graph Walk
├── Full LLM reasoning over primary files — unconstrained:
│   "What in these files could connect to something elsewhere?
│    Think about every aspect: concepts, relationships, dependencies,
│    constraints, decisions, risks, people, systems, timelines,
│    assumptions, implications, prerequisites, side effects,
│    or ANYTHING else that might be relevant."
├── No predefined categories. No artificial scope limits.
├── For each significant connection identified:
│   └── Spawn subagent (Knowledge Walker):
│       "Read broadly across knowledge/. Find everything related to
│        {aspect}. Report: what you found, how it connects to the query,
│        what contradicts or complicates the picture, what's missing."
├── After each subagent returns → run Gate 2 (during reading)
└── Main agent receives enriched picture from all subagent reports

Phase 3: Completeness Decision
├── Run Gate 3 (before answering — first pass)
├── Full reasoning: "Given everything I now know, what's STILL
│   missing for a reliable, complete answer?"
├── Gap types (non-exhaustive, reason freely):
│   ├── Context gap → spawn another Knowledge Walker
│   ├── Data gap → query live source (atlassian CLI, crawl)
│   │   (confirm with user if non-trivial call)
│   ├── Temporal gap → Phase 4
│   ├── Relationship gap → another graph walk iteration
│   └── Verification gap → need second source to confirm
└── If complete → Phase 5. If temporal needed → Phase 4.

Phase 4: Temporal Context (only if query needs it)
├── Spawn subagent (Log Scanner):
│   "Navigate the log hierarchy for temporal context on {topic}.
│    Hierarchy (most current first):
│    state+daily → older dailies → weekly → monthly → quarterly → yearly → onboarding
│    Read at appropriate depth. Report what changed, when, provenance."
├── Depth determined by query:
│   ├── "What's happening now?" → state + recent dailies
│   ├── "What changed recently?" → dailies + current weekly
│   ├── "How did this evolve?" → full chain to relevant depth
│   └── "Complete history" → all levels down to onboarding
├── Each level compresses the one below (not losslessly)
├── Never just "last daily" — that skips too much
└── Subagent reports with provenance (which log level info came from)

Phase 5: Consistency Check & Synthesis
├── Run Gate 4 (consistency)
├── Run Gate 5 (confidence meta-check)
├── Synthesize answer from full picture
├── Format output (see Output Format below)
└── If query was complex + answer succeeded → ask user: "Save as recipe?"
```

---

## Quality Gates

Mandatory self-checks at each phase transition. Hard gates — not suggestions.
If a gate fails, loop back or spawn additional work. Maximum 2 loops per gate.

### Gate 0: Complexity Decision (Phase 0)

Run immediately on query arrival.

| # | Question | Simple (→ /ask) | Complex (→ continue) |
|---|----------|-----------------|----------------------|
| A | Is this answerable by a single standard briefing template? | Yes — exec, vp, weekly, operational have defined scopes | No — doesn't fit any template |
| B | Does the answer require information from more than 2 knowledge files? | Probably not — one or two targeted reads | Yes — needs cross-file synthesis |
| C | Does this require understanding HOW things connect, not just WHAT they are? | No — factual lookup | Yes — relationships, implications, dependencies |
| D | Would a wrong or incomplete answer here have consequences? | Low impact | High impact — decision basis, escalation, stakeholder communication |
| E | Is this a follow-up to a previous insufficient answer? | N/A | Yes — prior answer didn't satisfy |
| F | Does this require temporal reasoning (evolution, changes, "since when")? | No — current state is enough | Yes — needs log chain or change history |

**Decision rule:** 2+ "Complex" → proceed with /reasoning. Otherwise redirect to /ask.

**Override:** Direct invocation of `/reasoning` bypasses Gate 0 — user decided.

### Gate 1: Before Deep Reading (Phase 1 → Phase 2)

Run after primary retrieval, before starting the semantic graph walk.

| # | Question | Purpose | Fail action |
|---|----------|---------|-------------|
| 1 | Can I restate the question in my own words? Does my restatement capture ALL dimensions? | Prevents drift from the start | Restate until clear |
| 2 | What would a COMPLETE answer need to contain? What dimensions does this question touch? | Defines the target space | List dimensions explicitly |
| 3 | Who would be affected by this answer or have an opinion on it? | Opens perspectives you'd otherwise miss | List stakeholders/roles |
| 4 | What assumptions am I already making before I've read deeply? | Makes implicit bias explicit | List and flag each assumption |

### Gate 2: During Reading (within Phase 2, after each subagent returns)

Run after receiving each subagent report.

| # | Check | Signal | Fail action |
|---|-------|--------|-------------|
| 5 | What surprised me in what I just read? | Surprise = important signal | Follow the surprise — it needs more context |
| 6 | What did I EXPECT to find but didn't? | Absence is information | Flag as gap, investigate or note as missing |
| 7 | Am I still answering the original question or following a side path? | Drift detection | Return to Gate 1 restatement, re-anchor |
| 8 | Whose perspective is still missing from my picture? | One-sidedness check | Spawn subagent for that perspective |
| 9 | If what I just read is true — what else MUST also be true? | Follow logical implications | Verify the implication |
| 10 | If what I just read is NOT true — what would that change? | Criticality assessment | If high impact: verify from second source |

### Gate 3: Before Answering (Phase 3/4 → Phase 5)

Run after all retrieval is complete, before synthesis.

| # | Check | Criterion | Fail action |
|---|-------|-----------|-------------|
| 11 | Could I explain this to someone who knows the project — and they'd say "yes, that's the full picture"? | Completeness gut-check | Identify what's missing, loop back |
| 12 | What would a critic ask me FIRST about this answer? | Find weak spots | Address or acknowledge the gap |
| 13 | Is there a perspective I've CONSCIOUSLY excluded? Why? | "not found" vs. "deliberately omitted" | Document exclusion and reason |
| 14 | Where am I being vague or hand-waving? | Vagueness = often lack of understanding | Get specific or acknowledge uncertainty |
| 15 | If I look at this answer in a week — what would bother me? | Temporal distance simulation | Fix what would bother future-you |

### Gate 4: Consistency (within Phase 5)

| # | Check | Fail action |
|---|-------|-------------|
| 16 | Do my sources agree on key claims? | Surface contradiction with both sources + timestamps |
| 17 | Am I treating all areas with equal depth, or biased toward what I read first? | Re-read under-explored areas — recency/primacy bias |
| 18 | Does my answer align with OVERRIDES.md? | Override has absolute priority — adjust answer |
| 19 | Is anything I'm treating as current actually outdated? | Check temporal validity — flag stale info |

### Gate 5: Confidence Meta-Check (final gate before output)

| # | Question | Action |
|---|----------|--------|
| 20 | On a scale 1-5: how confident am I in this answer? | Report confidence to user |
| 21 | What would I need to read/verify to move from current confidence to 5? | If achievable: do it. If not: state what's missing. |
| 22 | Is there anything I'm stating as fact that is actually an inference? | Mark inferences explicitly |

### Gate Behavior

- Gates are NOT optional. Every phase transition runs its gate.
- Gate failures loop back — force one more iteration.
- Maximum 2 loops per gate (prevents infinite recursion).
- If a gate still fails after 2 loops: proceed but **flag explicitly** in output:
  "Note: [gate name] did not fully pass — answer may be incomplete regarding [X]."
- Gate reasoning is internal. Only failures affecting answer quality are surfaced to user.

---

## Subagent Dispatch

Subagents are spawned dynamically via the Agent tool. No predefined agent definitions —
the /reasoning skill formulates prompts based on its Phase 2 reasoning.

### Subagent Types

| Role | When spawned | Prompt pattern |
|------|-------------|----------------|
| Knowledge Walker | Phase 2: for each connection identified | "Read broadly across knowledge/. Find everything related to {aspect}. Report: what you found, how it connects, contradictions, what's missing." |
| Log Scanner | Phase 4: when temporal context needed | "Navigate the log hierarchy for {topic}. Hierarchy: state+daily → dailies → weekly → monthly → quarterly → yearly → onboarding. Read at depth appropriate for: {query type}. Report changes with provenance." |
| Consistency Checker | Phase 5: when multiple claims need cross-validation | "Compare these claims across {file list}. Report: consistent / conflict at [file:claim]." |
| Source Querier | Phase 3: when knowledge is insufficient | "Query {source} for {specific data point}. Use atlassian CLI / crawl as appropriate." |

### Dispatch Rules

- Subagent scope is determined by the main agent's reasoning — never predefined
- Each subagent gets full context about the original query + what's already known
- Subagents report compressed — main agent synthesizes
- No limit on number of subagents (Lore won't grow complex enough to be prohibitive)
- For live source queries (atlassian, crawl): confirm with user if non-trivial
  (single Jira item or single Confluence page is fine without confirmation)

### Subagent Prompt Template

```
You are a research subagent for the Lore /reasoning skill.

Original query: "{user's question}"
What's already known: {summary of findings so far}
Your assignment: {specific aspect to investigate}

Instructions:
- Read broadly across the specified scope
- Report EVERYTHING relevant, even tangentially
- Flag contradictions or inconsistencies
- Flag what you expected to find but didn't
- Compress your findings into a structured report
- Do not synthesize an answer — report raw findings

Scope: {knowledge/ | log/ hierarchy | specific files | live source}
```

---

## Recipe Integration

### On Entry (Phase 0)

1. Check if `.lore/recipes/` exists and has files
2. If yes: scan recipe patterns against current query
3. If match found: use recipe strategy as a starting point for Phase 1-2
   (don't skip gates — recipe accelerates, doesn't bypass)

### On Success (end of Phase 5)

If the query was complex and the answer passed all gates:

```
→ This reasoning strategy worked well. Save as recipe for future similar queries?
  Pattern: "[suggested pattern]"
  (Saving requires commit + push)
```

Only save on explicit user confirmation.

### Recipe Format

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

### Recipe Lifecycle

- **Created:** after successful complex query (user confirms)
- **Used:** matched by pattern on future queries (accelerates, doesn't bypass gates)
- **Refined:** if a recipe-guided answer still needs corrections → update recipe
- **Decayed:** not used in 14 days → flagged for review next time recipes are scanned
- **Pruned:** maximum 20 recipes — oldest/lowest-hit get archived on overflow

---

## Output Format

### Answer Structure

```markdown
## [Answer title — derived from question]

[Comprehensive answer — structured with headers, tables, lists as needed.
 Each claim attributed to source. Inferences explicitly marked.]

### Sources Used
| Source | File/Location | Relevance |
|--------|--------------|-----------|
| ... | ... | ... |

### Gate Flags (only if any gate didn't fully pass)
- [Gate X] did not fully pass: [what's potentially incomplete]

---
#### 🤖 AI Reasoning

**My read:** [Assessment — what does this mean for delivery?]
**What concerns me:** [Risks, gaps, dynamics that follow from the facts]
**What I'd recommend:** [Concrete next step]
**Confidence:** [1-5] — [reason for confidence level]

---
**Data provenance**
Last pull: YYYY-MM-DD HH:MM (Europe/Vienna) | Sources used: [list] | Freshness: [indicator]
```

### Confidence Levels

| Level | Meaning |
|-------|---------|
| 5 | Full picture, all gates passed, multiple sources confirm |
| 4 | Strong answer, minor gaps acknowledged |
| 3 | Good answer but some areas couldn't be fully verified |
| 2 | Partial answer — significant gaps remain |
| 1 | Best effort — major data missing, answer is tentative |

---

## Rules

1. **Never invent.** If you don't know: say "This is not documented in {PROJECT_NAME}."
2. **Never resolve contradictions.** Surface both sides with timestamps. Human decides.
3. **Never auto-commit recipes.** Always ask. Recipe save requires explicit confirmation + push.
4. **Privacy.** Never read `## Confidential` or `## Private` sections unless explicitly asked.
5. **OVERRIDES.md has absolute priority.** If an override exists, it supersedes everything.
6. **Live sources need confirmation for non-trivial calls.** A single Jira item or Confluence page is fine. A broad search or crawl: ask first.
7. **Completeness over speed.** Read broadly first, optimize later. A fast wrong answer is worse than a slow right one.
8. **Flag inferences.** Anything derived rather than directly stated must be marked `[inferred]`.
9. **Gate failures must be surfaced.** Never silently swallow a failed gate check.
10. **Subagent scope is unlimited.** The reasoning determines what to read — never artificially constrain it.

---

## RAG-Light Compliance

This skill is RAG-light compliant.

### Index Read
- `knowledge/INDEX.md` — Phase 1: identify primary files via Key Topics, Answers, Contains
- `contributions/INDEX.md` — Phase 1: find pending signals via What, Tags, Status
- `log/INDEX.md` — Phase 1 + Phase 4: identify relevant logs via Signals, Entities, References, Tags

### Index Write
- None (read-only skill — recipes live in `.lore/recipes/`, not indexed areas)

---

