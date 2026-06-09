# Ref: Decision Impact Scan

## Purpose

Every new decision (DEC-##) detected during a pull MUST be checked against existing
knowledge/ files for structural implications. A decision is not fully processed until
its downstream impact on knowledge state has been verified.

This prevents the failure mode where a decision is correctly logged and tagged but
its structural effect on existing knowledge goes undetected.

---

## When to Run

After Phase 3 (Write Log), before Phase 5 (Update Manifests).
Runs as part of knowledge derivation — not a separate phase.

---

## Procedure

For EVERY new decision found in the current pull:

```
1. READ the decision text
2. SCAN knowledge/ for files that reference the decision's SUBJECT:
   - workstreams.md → any structural/reporting changes?
   - dependencies.md → any new/resolved dependencies?
   - decisions-open.md → supersedes an existing open decision?
   - team.md → ownership/staffing changes?
   - milestones.md → timeline/scope changes?
   - Any other knowledge file with activation triggers, conditional states, or "benched" items
3. CHECK: Does this decision CHANGE the state described in any knowledge file?
   - Activation triggers fired?
   - "Benched" → "Active"?
   - Ownership changed?
   - Scope added/removed?
   - Dependency created/resolved?
4. If YES → update the knowledge file immediately
5. If UNCLEAR → add to consistency check as potential impact (🟡)
```

---

## Activation Trigger Pattern

Knowledge files may contain conditional states like:
- "Activation trigger: if [condition]"
- "Benched — will activate when [condition]"
- "Blocked until [condition]"
- "Contingent on [decision]"

When a decision matches any such condition → the trigger has fired.
Update the file to reflect the new active state.

---

## Reporting

After the scan, report in the pull output:

```
DECISION IMPACT SCAN:
- Decisions scanned: [N]
- Knowledge files checked: [list]
- State changes applied: [N] — [brief description]
- Potential impacts flagged: [N] — [brief description]
```

If zero state changes and zero flags: report "No downstream impact detected."

---

## Failure Mode This Prevents

Without this scan:
- DEC-28 "FedRAMP = separate workstream" gets logged correctly
- But knowledge/workstreams.md still says "Legal & Compliance: Benched"
- The explicit activation trigger ("if FedRAMP track accelerates") goes unnoticed
- Knowledge state drifts from reality

This scan closes the loop between decisions and their structural effects.
