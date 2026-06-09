# Rule: Tagging

## Audience Tags
Tags are set by humans. Claude only filters by them.

| Tag | For whom | When |
|-----|----------|------|
| [exec] | C-Level, Board | Only what truly matters |
| [vp] | All VPs | Standard for strategic topics |
| [vp:delivery] | VP Delivery | Only when specifically relevant |
| [vp:sales] | VP Sales | Only when specifically relevant |
| [vp:legal] | VP Legal | Only when specifically relevant |
| [lead] | Project leads | Cross-functional, dependencies |
| [team] | Internal | Operational, technical |

Default when unclear: [lead]
Specific VP tags only when truly relevant for that role only.

## Content Tags
Set by humans. Claude suggests when it detects something.

| Tag | What | Automatic follow-up action |
|-----|------|---------------------------|
| [decision] | Decision made | Ensure knowledge entry (DEC-*) |
| [risk] | Identified risk | Ensure knowledge entry (RISK-*) + trend |
| [action] | Task with owner+date | – |
| [question] | Open question | Ensure knowledge entry (OPEN-*) if complex |
| [event] | Milestone, external | Ensure knowledge entry if important |
| [arch] | Architecture-relevant | ADR draft |
| [concept] | New concept | Check/create knowledge node |

## Trend Tags for Risks
Claude derives trend from time progression – always as suggestion.

| Tag | Meaning |
|-----|---------|
| [↑] | Worsening |
| [→] | Stable |
| [↓] | Improving |
