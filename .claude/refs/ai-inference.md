# Rule: AI-Inferred Content — Pattern Recognition Mode

## Principle

Claude may use pattern recognition to surface dependencies, risks, and connections
that are NOT explicitly stated in any source — but ONLY under strict labeling rules.

The "never invent" rule remains absolute for FACTS.
AI inference is allowed for HYPOTHESES — things that logically follow from known facts.

---

## When AI Inference Is Allowed

1. **Dependency extraction** — inferring blocking relationships from architecture, team structure, business model, feature composition, compliance requirements, release models
2. **Risk identification** — surfacing risks that follow logically from known facts (e.g., "team X not engaged but owns capability Y" → integration risk)
3. **Gap detection** — identifying what SHOULD exist based on patterns but doesn't (e.g., missing owner, missing plan, missing engagement)

## When AI Inference Is NOT Allowed

1. **Decisions** — never infer that a decision was made without a source
2. **Status** — never infer the status of work without a source
3. **Timelines** — never infer deadlines that weren't stated
4. **People's opinions** — never infer what someone thinks or intends
5. **Facts** — never state something as fact that isn't in a source

---

## Mandatory Labeling

Every AI-inferred item MUST be labeled. No exceptions.

**In knowledge/ files:**
- Separate section: `## AI-Inferred [Type]`
- Each entry: `[AI-inferred] [Description] — Reasoning: [why]`
- Status column: always starts as `Unverified — check with [suggested owner]`

**In daily logs:**
- Tag: `[AI-inferred][risk]` or `[AI-inferred][dependency]`
- Always followed by: `Reasoning: [one sentence]`

**In baselines:**
- Separate subsection within the relevant section
- Clearly marked with ⚠ header

**In briefings:**
- AI-inferred items in a separate block at the end
- Introduced with: "The following are AI-inferred — not stated in sources:"

---

## Quality Bar for AI Inference

An inference is worth recording if:
1. It follows from 2+ known facts (not a single data point extrapolation)
2. It has a clear logical chain (A → B → therefore C)
3. It is actionable (someone can verify or act on it)
4. It matters for delivery (passes Checklist A: would a delivery lead care?)

An inference is NOT worth recording if:
- It's obvious to anyone reading the source
- It's speculative with no clear reasoning chain
- It's not actionable (no way to verify or respond)
- It's about feelings, moods, or opinions

---

## Lifecycle of AI-Inferred Items

1. **Created** — labeled `[AI-inferred]`, status: `Unverified`
2. **Verified** — if a source confirms it, remove `[AI-inferred]` label, move to main section, add source link
3. **Rejected** — if investigation shows it's wrong, delete it with note: `[AI-inferred] AI-X rejected [date] — [reason]`
4. **Stale** — if unverified for >30 days and no one has checked, flag for review

---

## Relationship to Never-Invent Rule

The never-invent rule (`.claude/rules/never-invent.md`) governs FACTS.
This rule governs HYPOTHESES.

They are complementary:
- A fact without a source → violation of never-invent
- A hypothesis clearly labeled as AI-inferred → permitted by this rule
- A hypothesis presented as fact → violation of BOTH rules

The test: if the `[AI-inferred]` label were removed, would it violate never-invent? If yes → the label is mandatory and must never be dropped until a source confirms it.
