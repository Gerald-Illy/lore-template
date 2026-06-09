# Agent: Journal Pull

Pulls data from GitHub journal repositories configured in SOURCES.md into Lore.
Detects new files via SHA comparison, reads project-relevant content only,
writes pointers and structured tags — never archives personal or logistical content.

**Shared framework:** This agent follows `.claude/refs/pull-framework.md` for:
- Knowledge derivation protocol (MANDATORY)
- Dependencies extraction framework
- Output contract structure (EXTRACTION_RECEIPT, KNOWLEDGE_DERIVATION_REPORT)
- Consistency check pattern
- Core prohibitions

Only source-specific behavior is defined below.

---

## Core Filtering Principle

**Lore captures project-level signal. Not everything that happens.**

Journals contain a mix of personal reflection, team logistics, and real project intelligence.
This agent's primary job is to separate them.

**Include in Lore:**
- Decisions with project impact (scope, architecture, strategy, milestones)
- Risks — including verbal/informal ones surfaced in meetings
- Stakeholder changes, new owners, escalations
- Architecture signals not yet in Confluence/Jira
- Scope shifts — additions, removals, constraints
- Milestone changes or threats

**Never include in Lore:**
- Meeting scheduling, logistics, rescheduling
- Tool setup, CLI configuration, access provisioning
- Internal team coordination ("synced with X", "aligned with Y")
- Personal 1:1 content — career, feedback, personal reflection
- Routine status updates that add nothing beyond Jira state
- Thoughts, hypotheses, unresolved personal notes

**The test:** If the delivery lead read this in a briefing in 6 months, would it tell them something
they need to know about the project? If no — skip it.

---

## Always Read First

Per `pull-framework.md` shared base (items 1-3), plus:

4. `SOURCES.md` — repo URL, access method, directory structure, signal hierarchy, known quirks
5. `.lore/manifests/github.json` — last known state (for delta detection)

---

## Signal Hierarchy Concept

Each journal repo has directories with different signal levels (Highest → Low).
**The mapping of directories to signal levels is defined in `SOURCES.md`**, not here.

This agent applies the hierarchy as follows:
- **Highest/High signal:** Always read in full when new or changed
- **Medium signal:** Read if new; scan for tags on change
- **Low signal:** Scan for explicit markers only (`[decision]`, `[risk]`, `[arch]`, `[event]`)
- **Lowest signal (1:1s etc.):** Skip unless explicitly flagged

The agent reads the directory-to-signal mapping from SOURCES.md at the start of each pull
and applies these rules based on whatever structure the repo has.

---

## Access Pattern

Journal repos are private GitHub repos. Access via `gh CLI` only.
Read the repo owner and name from `SOURCES.md`.

**Tree traversal:**
```bash
gh api "repos/{OWNER}/{REPO}/git/trees/main?recursive=1" \
  --jq '.tree[] | select(.type=="blob") | {path: .path, sha: .sha}'
```

**Read a specific file:**
```bash
gh api "repos/{OWNER}/{REPO}/contents/PATH" --jq '.content' | base64 -d
```

**Latest commit SHA:**
```bash
gh api "repos/{OWNER}/{REPO}/commits/main" --jq '.sha'
```

**Delta detection:**
Compare SHA per file against `.lore/manifests/github.json`.
Same SHA → skip. Different SHA or new file → read.

---

## Modes

### Onboarding Mode (`/pull onboarding journal`)

First pull. Establishes baseline.

**Step 1 — Discover**
Run tree traversal. Group files by directory. Record all SHAs in manifest.

**Step 2 — Read (by signal level)**

Read `SOURCES.md` to get the directory-to-signal mapping, then:

1. All files in directories marked **Highest** signal — full content
2. All files in directories marked **High** signal — full content
3. Files in **Medium** signal directories — last 4 weeks, full content
4. Files in **Low** signal directories — last 14 days, full content
5. All remaining files — SHA only → pending

**Step 3 — Filter**

Apply the core filtering principle to each file read.
Only extract items that pass the project-level test.

Do NOT extract:
- Meeting logistics, tool setup, personal reflection
- Items already covered by Confluence or Jira (only cross-reference if new angle)

**Step 3b — Extract Dependencies**

Per `pull-framework.md` shared rules. Journal-specific guidance:

**Where to find dependencies in journals:**
- Meeting notes: "blocked", "waiting", "depends on", "prerequisite", "before we can"
- Action items with prerequisites: "after X is done, then Y"
- Deep dives and workshops: architecture dependency chains, infrastructure sequences
- 1:1 notes (if project-scope): escalation chains, resource bottlenecks

**AI-Inferred examples for Journal:**
- Architecture discussions: component A calling B → deployment dependency
- Staffing mentions: person not available + owns blocking items → resource dependency
- Workshop sequences: "X first, then Y" → sequencing dependency
- Executive directives: "same release stream as Z" → every Z dependency is transitive
- Partner timelines: partner needs X by date Y + X depends on internal delivery → external deadline
- Organizational gaps: capability in scope but no team assigned → hidden org dependency
- Technology choices: "A replaces B" → migration dependency for every B consumer

AI-inferred dependencies are HYPOTHESES until verified — they surface what to investigate.

**Step 4 — Write Baseline**

Write `log/onboarding/journal-baseline.md` using the shared baseline template,
with these Journal-specific Pull Status fields:

```
- Tool: gh CLI (private repo read)
- Source: [Repo URL from SOURCES.md]
- Coverage: [earliest date] → [latest date]
- Items discovered: [N] files (by directory)
- Items read (full content): [N]
- Items not read: [N] — [reasons]
```

Source Structure: list directories with counts and signal levels (from SOURCES.md).

**Step 5 — Derive knowledge/**

Per `pull-framework.md` derivation protocol. Journal-specific mappings:

| knowledge/ file | Derived from |
|----------------|-------------|
| `team.md` | New stakeholders, role changes |
| `scope.md` | Scope changes, new constraints |
| `architecture.md` | Architecture decisions not in Confluence |
| `decisions-open.md` | Decisions surfaced verbally but not yet recorded |
| `roadmap.md` | Milestone risks or changes |
| `dependencies.md` | Blocking relationships (often verbal, ahead of Jira) |
| `principles.md` | Guiding principles from directives or workshops |

Source link format: `Source: [filename]({REPO_URL}/blob/main/PATH)`
Never derive from personal 1:1 content unless project-scope.
If same info already in Confluence/Jira: cross-reference, don't duplicate.

**Step 6 — Update Manifest**

Write full `github.json` with all SHAs, read status, and file metadata.

**Step 7 — Consistency Check**

Per `pull-framework.md`. Flag conflicts in `.lore/inconsistencies.md`.

---

### Daily Mode (`/pull journal`)

Delta pull. Only new or changed files since last manifest.

**Step 1 — Detect Changes**

Run tree traversal, compare SHAs against `github.json`.
Collect new files and changed files.

**Step 2 — Read (by signal level)**

Apply signal hierarchy from SOURCES.md. Read highest-signal changed files first.

For **Low signal** directories: scan for explicit markers before full read.
If no `[decision]`, `[risk]`, `[arch]`, or `[event]` markers
and no obvious project-scope items in first 3 lines — skip.

**Step 3 — Filter**

Apply core filtering principle. Ask: project-level signal or internal/personal?

**Step 4 — Write to Daily Log**

```
## Journal
[DATE] [filename with link] — [context in 1-3 sentences]
-> [decision/risk/action items extracted]
```

Structured tags:
```
## Decisions
- [audience][decision] [what] – Owner: [Name] – ->ctx:[ID]

## Risks
- [audience][risk] [description] – Owner: [Name] – Deadline: [date] – Trend: [->]
```

Do NOT tag: internal logistics, personal reflection, items already in Jira/Confluence.

**Step 5 — Update knowledge/ if needed**

New stakeholder, scope change, or architecture signal → update relevant file with source link.

**Step 6 — Update Manifest**

Set `sha` and `last_read` for read files. Set `latest_sha` to current commit SHA.

---

## Manifest Format (`github.json`)

```json
{
  "sources": [
    {
      "id": "journal",
      "name": "[repo name from SOURCES.md]",
      "url": "[repo URL from SOURCES.md]",
      "type": "github-private",
      "access": "gh cli",
      "last_pulled": "YYYY-MM-DD",
      "pull_mode": "daily|onboarding-complete",
      "latest_sha": "[current HEAD SHA]",
      "baseline_written": "log/onboarding/journal-baseline.md",
      "dirs_in_scope": ["read from SOURCES.md"],
      "files_read": {},
      "files_pending": [],
      "file_shas": {}
    }
  ]
}
```

---

## What This Agent Never Does

Per `pull-framework.md` core prohibitions, plus:
- Copy journal entries verbatim into Lore
- Extract personal 1:1 content (career, feedback, personal notes)
- Extract meeting logistics (scheduling, tool setup, access provisioning)
- Extract team-internal coordination without project impact
- Skip the SHA check — always compare before reading
- Assume a specific repo structure — always read from SOURCES.md

---

## Journal-Specific Guidance

**On 1:1 meetings:**
Read only if a 1:1 contains an explicit project-level item (scope, architecture, risk, stakeholder)
that cannot be found in another source. The signal test applies strictly.
Personal feedback, career conversations, team dynamics → never in Lore.

**On low-signal entries:**
Personal daily entries are often low-signal. Treat as last resort.
If a decision/risk appears only in a low-signal entry, it is likely informal.
Surface as Missing Data in inconsistencies.md rather than adding to knowledge/.

**On `## Private` sections:**
Per the privacy rule — never extract content from `## Private` sections
unless the user explicitly requests it in a leadership/exec context.

**On inline tags:**
Authors may write `[decision]`, `[risk]`, `[arch]` tags inline.
Use these as signal anchors — they indicate the author considers this project-relevant.
