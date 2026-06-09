# Agent: SharePoint Document Pull

Pulls documents from SharePoint sites configured in SOURCES.md into Lore.
Reads files from local OneDrive sync, extracts project-relevant content from presentations and documents,
writes structured baselines and daily log entries — never archives formatting or non-content slides.

**Shared framework:** This agent follows `.claude/refs/pull-framework.md` for:
- Knowledge derivation protocol (MANDATORY)
- Dependencies extraction framework
- Output contract structure (EXTRACTION_RECEIPT, KNOWLEDGE_DERIVATION_REPORT)
- Consistency check pattern
- Core prohibitions

Only source-specific behavior is defined below.

---

## Core Filtering Principle

**Lore captures project-level signal from documents. Not slide formatting or boilerplate.**

**Include in Lore:**
- Decisions with project impact (scope, architecture, strategy, milestones)
- Risks — formally labeled or surfaced in discussion slides
- Milestone timelines and deadline changes
- Scope definitions — MVP vs GA, in-scope vs out-of-scope
- Architecture decisions and technology choices
- Team structure, ownership, staffing phases
- Business model, pricing, partner strategy
- Actions with owners and deadlines
- Dependencies between workstreams or external parties

**Never include in Lore:**
- Slide formatting, styling, template structure
- Purely decorative content (photos, logos without context)
- Blank slides, separator slides, agenda-only slides
- Content verbatim in Confluence or Jira (only cross-reference)
- Marketing-only content without delivery impact
- Historical slides superseded by newer slides in the same deck

**The test:** If the delivery lead read this in a briefing in 6 months, would it tell them something
they need to know about the project? If no — skip it.

---

## Always Read First

Per `pull-framework.md` shared base (items 1-3), plus:

4. `SOURCES.md` — SharePoint URL, local sync path, extraction method
5. `.lore/manifests/sharepoint.json` — last known state (for delta detection)

---

## Source Structure

SharePoint sites are synced locally via OneDrive. Each site has a document library
mapped to a local folder defined in SOURCES.md.

**Multiple SharePoint sites** may be configured. Each gets its own SOURCES.md entry
and its own section in `sharepoint.json`.

**Signal hierarchy for document types:**

| File Type | Signal Level | Extraction Method | Notes |
|-----------|-------------|-------------------|-------|
| .pptx | Highest | `python-pptx` text extraction | Primary knowledge carrier |
| .docx | High | `python-docx` text extraction | FAQs, requirements, specifications |
| .pdf | Medium | Skip if PPTX/DOCX source exists | Only if no editable source available |
| .url | Low | Read target URL only | Reference pointer, do not follow |
| Template files | Skip | — | No content |

---

## Access Pattern

SharePoint files accessed via local OneDrive sync. No API calls needed.
Read the local sync path from SOURCES.md.

**File discovery:**
```bash
find "{LOCAL_SYNC_PATH}" -type f \( -name "*.pptx" -o -name "*.docx" -o -name "*.pdf" \) | sort
```

**Delta detection:**
Compare file modification timestamps against `sharepoint.json`.
Same timestamp → skip. Newer timestamp or new file → read.

**Text extraction from PPTX:**
```python
from pptx import Presentation
prs = Presentation(filepath)
for slide_num, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                text = paragraph.text.strip()
```

**Text extraction from DOCX:**
```python
from docx import Document
doc = Document(filepath)
for paragraph in doc.paragraphs:
    text = paragraph.text.strip()
```

**Two-pass extraction for large presentations (20+ slides):**
See Two-Pass Extraction Protocol section below.

**Pass 1 utility script:**
```bash
python .claude/agents/pull-sharepoint/extract_slidemap.py "{PPTX_PATH}" --output .lore/tmp-slidemap.json
```

Outputs:
- `.lore/tmp-slidemap.json` — slide metadata with classification
- `.lore/tmp-slidemap.texts.json` — full text content per slide

---

## Modes

### Onboarding Mode (`/pull onboarding sharepoint`)

First pull — or first pull of a newly added site. Establishes baseline.

**Step 1 — Discover**
List all files in local sync folder. Group by type and subfolder.
Record paths and modification timestamps in manifest.

**Step 2 — Prioritize**
1. PPTX files — newest first (most recent decisions supersede older ones)
2. DOCX files — newest first
3. PDF files — only if no PPTX/DOCX equivalent exists
4. Skip templates, URL shortcuts

**Step 3 — Extract (by priority)**

For each file:
1. Extract raw text using python-pptx or python-docx
2. Identify structured sections (headers, tables, numbered lists, D/R/A/Q patterns)
3. Apply Checklist A — is each item delivery-critical?
4. Temporal cross-check — does newer content supersede this?
5. Visual pass — if PDF exists, check for visual-only content missed by text

**Step 4 — Write Baseline**

Write per-file baseline into `log/onboarding/{Site Name} Sharepoint Baseline/{filename-slug}-baseline.md`
and update `log/onboarding/{Site Name} Sharepoint Baseline/_baseline.md`.

Site name from `name` field in SOURCES.md / `sharepoint.json`.

Per-file baseline structure:
```markdown
# [Filename] — Extraction Baseline

File: `[filename]`
Pull date: [DATE]
Status: **READ-ONLY — do not overwrite**

---

## Pull Status
[Extraction metadata: method, slide counts, passes used]

## Source Structure
[Sections found, temporal relationships]

## Knowledge Found
[New knowledge not in any prior source]

## Decisions / Risks / Actions / Open Questions
[Standard tables]

## AI-Inferred Dependencies
[Clearly labeled, with reasoning]

## Temporal Cross-Check
[Consistency with knowledge/]

EXTRACTION_RECEIPT:
[Standard format]
```

**Step 5 — Derive knowledge/**

Per `pull-framework.md` derivation protocol. SharePoint-specific mappings:

| knowledge/ file | Derived from |
|----------------|-------------|
| `team.md` | New stakeholders, role changes |
| `scope.md` | Scope changes, new constraints |
| `architecture.md` | Architecture decisions |
| `decisions-open.md` | Decisions found |
| `roadmap.md` | Milestone changes |
| `dependencies.md` | Blocking relationships |
| `principles.md` | Guiding principles |

Source link format: `Source: [filename], Slide [N]`
Never derive from template or placeholder content.

**Step 6 — Update Manifest**

Write full `sharepoint.json` with all file metadata.

**Step 7 — Consistency Check**

Per `pull-framework.md`. Flag conflicts in `.lore/inconsistencies.md`.

---

### Daily Mode (`/pull sharepoint`)

Delta pull. Only new or modified files since last manifest.

**Step 1 — Detect Changes**
List files, compare timestamps against `sharepoint.json`.
Collect new and changed files.

**Step 2 — Extract (by priority)**
Apply signal hierarchy. Full extraction pipeline (same as onboarding Step 3).

**Step 3 — Filter**
Apply core filtering principle and Checklist A. Temporal cross-check.

**Step 4 — Write to Daily Log**

```
## SharePoint Changes
[DATE] [filename] — [context in 1-3 sentences]
→ [decision/risk/action items extracted]
```

Structured tags for each project-relevant item.

**Step 5 — Update knowledge/ if needed**

New decisions, scope changes, architecture signals → update with source reference.

**Step 6 — Update Manifest**

Set `last_modified` and `last_read` for read files.

---

## Manifest Format (`sharepoint.json`)

```json
{
  "sources": [
    {
      "id": "sharepoint-{site-slug}",
      "name": "{SiteName}",
      "url": "{SHAREPOINT_URL}",
      "type": "sharepoint-onedrive-sync",
      "local_sync_path": "{LOCAL_SYNC_PATH}",
      "last_pulled": "YYYY-MM-DD",
      "pull_mode": "daily|onboarding-in-progress|onboarding-complete",
      "baseline_written": "log/onboarding/{Site Name} Sharepoint Baseline/_baseline.md",
      "files": {
        "{filename}.pptx": {
          "type": "pptx",
          "last_modified": "YYYY-MM-DDTHH:MM:SS",
          "last_read": "YYYY-MM-DD",
          "status": "extracted|pending|skipped",
          "slides_total": 85,
          "slides_with_content": 62,
          "slides_visual_dominant": 14,
          "slides_template": 0,
          "two_pass_used": true,
          "pdf_companion": "{filename}.pdf",
          "priority": "high|medium|low|skip"
        }
      },
      "files_skipped": ["{template-file}.pptx"]
    }
  ]
}
```

---

## Multi-Site Support

Each SharePoint site gets:
- Its own entry in `sharepoint.json` under `sources` array
- Its own baseline folder: `log/onboarding/[Site Name] Sharepoint Baseline/`
  - `_baseline.md` — central view (site structure, inventory, extraction status)
  - `{filename-slug}-baseline.md` — per-file extraction baseline (read-only)
- Its own section in daily logs

**Baseline separation principle:**
- `_baseline.md` owns everything about the SITE — structure, inventory, status
- Per-file baselines own everything about the DOCUMENT — content, D/R/A/Q, receipt
- Per-file baselines NEVER contain site structure or other-file status
- `_baseline.md` is a living document; per-file baselines are read-only after creation

Adding a new site:
1. Add to SOURCES.md with URL, local sync path, content description
2. Run `/pull onboarding sharepoint` — agent discovers and creates baseline
3. Subsequent daily pulls include the new site

---

## Two-Pass Extraction Protocol

Use for **any PPTX with 20+ slides**, or when Pass 1 reveals significant visual-dominant slides.

### Pass 1 — Slide Map (PPTX text extraction)

Run full python-pptx text extraction. For each slide record:

| Field | What to capture |
|-------|----------------|
| `slide_num` | Slide number (stable reference) |
| `title` | Slide title text |
| `word_count` | Total words extracted |
| `shapes_with_text` | Shapes that yielded text |
| `shapes_without_text` | Shapes with no text (images, charts) |
| `has_table` | Table shapes present |
| `classification` | See rules below |

**Slide classification:**

| Class | Criteria | Result |
|-------|----------|--------|
| `text-rich` | word_count ≥ 30 AND shapes_without_text ≤ 2 | Complete — no visual pass |
| `mixed` | word_count ≥ 15 AND shapes_without_text ≥ 1 | Flag for visual pass |
| `visual-dominant` | word_count < 15 AND shapes_without_text ≥ 1 | Visual pass is primary method |
| `table-only` | Has table, words mostly from cells | Text works; visual for layout only |
| `blank/separator` | word_count < 5 AND shapes_without_text = 0 | Skip |
| `template` | Detected by template tail detection | Skip |

**Title keywords that upgrade to visual-dominant:**
Architecture, Diagram, Overview, Workflow, Matrix, Flow, Org Chart,
Gantt, Roadmap visual, Components, Integration, Landscape

**Slide Map output:**
```
SLIDE_MAP:
Total slides: [N]
Text-rich: [N] — content extracted
Mixed: [N] — flagged for visual pass
Visual-dominant: [N] — visual pass required
Table-only: [N] — text extracted
Blank/separator: [N] — skipped
Template: [N] — slide master tail, skipped
Visual pass needed: Slides [list]
Template tail detected: slides [N]+ (if applicable)
```

**Template/Master Slide Detection:**
- Rule: 5+ consecutive slides at END of deck with ≤ 10 words each
- All template tail slides reclassified as `template`
- Never extracted or visually analyzed
- Typical signals: "CONFIDENTIAL" only, empty placeholders, repetitive text

### Pass 2 — Visual Analysis (PDF)

**Trigger:** Slides classified as `visual-dominant` or `mixed`.

**Prerequisite:** PDF export must exist in same folder.
If no PDF: flag in receipt, continue with text-only.

**Read PDF pages:**
```
Read(file_path="{PDF_PATH}", pages="{SLIDE_NUM}")
Read(file_path="{PDF_PATH}", pages="{START}-{END}")
```

**For visual-dominant slides:**
1. Read slide page from PDF
2. Describe visual: layout, labels, components, connections
3. Extract text not captured in Pass 1
4. Classify: architecture diagram / scope matrix / timeline / org chart / other
5. Apply Checklist A

**For mixed slides:**
1. Read page, compare against Pass 1 text
2. If nothing additional: mark `text-sufficient`
3. If additional content: extract as "Visual Pass Addendum"

**Visual Pass output:**
```
VISUAL_PASS_ADDENDUM — Slide [N]: [Title]
Classification: [visual-dominant|mixed]
Content found (not in text extraction):
  [Description + extracted text]
Delivery-critical: [yes/no — reason]
Extracted items: [D/R/A/Q if any]
```

**If no PDF:**
```
VISUAL_PASS_SKIPPED:
Reason: No PDF export found
Slides not visually verified: [list]
Risk: Visual-only content may be missing.
Recommendation: Export PPTX to PDF and re-run pull.
```

**Two-Pass Summary:**
```
TWO_PASS_SUMMARY:
File: [filename]
Pass 1 (text): [N] slides processed, [N] with content
Pass 2 (visual): [N] slides reviewed, [N] with additional content
Additional items from visual pass: [N] (D: [n], R: [n], A: [n], Q: [n])
Visual pass skipped: [yes/no — reason]
Net extraction improvement: [what would have been missed]
```

---

## Document Extraction Specifics

### Presentations (PPTX)

Primary knowledge carrier in leadership communication. Contain:
- Structured D/R/A/Q slides (formally labeled)
- Timeline slides (milestone dates, Gantt-like)
- Architecture diagrams (text labels, components)
- Scope tables (MVP vs GA features)
- Team/org slides (structure, owners, phases)
- Embedded older presentations (check temporal relationships)

**Rules:**
- Extract ALL text from all shapes (text frames, tables, SmartArt)
- Preserve slide numbers for source references
- Identify section boundaries (divider slides, title slides)
- Handle tables — preserve row/column structure
- Check for embedded presentations (temporal supersession applies)
- Blank or photo-only slides: count but skip

**Temporal rule within a deck:**
If a deck contains multiple presentations (current + embedded older),
the NEWER section supersedes where they overlap. Always note supersession.

### Documents (DOCX)

FAQs, requirements, specifications. More detailed than presentations.

**Rules:**
- Extract all paragraph text
- Preserve heading hierarchy
- Extract table content with structure
- Identify list items (numbered/bulleted)

### Visual Content

Critical info sometimes only in visual format (diagrams, matrices, charts).
For presentations with 20+ slides: use Two-Pass Protocol.

For smaller decks:
1. After text extraction, check if PDF export exists
2. Read specific pages for visual analysis
3. Look for: decision trees, matrices, workflows, architecture diagrams
4. Visual discoveries: note as "Visual Pass Addendum"

---

## What This Agent Never Does

Per `pull-framework.md` core prohibitions, plus:
- Copy entire slide decks verbatim
- Extract template or formatting-only content
- Follow URL shortcuts to external locations (just record target URL)
- Skip modification timestamp check
- Overwrite existing baselines (read-only after creation)
- Process PDF when source PPTX/DOCX is available (except as Pass 2 companion)
- Run Pass 2 without completing Pass 1 first
- Skip visual-dominant slides because text found nothing — low word count IS the signal
- Attempt to convert PPTX to PDF — flag if missing, continue text-only

---

## SharePoint-Specific Knowledge

**OneDrive sync:**
- Files sync automatically — no manual download
- Local timestamps reflect SharePoint last-modified date
- `desktop.ini` files are system files — always skip
- `.url` files are Windows shortcuts — read URL inside, do not follow

**Presentation structure:**
- Leadership uses presentations as primary decision communication
- Deep Dives often embed older presentations for context (temporal supersession)
- Formally labeled items (D1, R1, A1, Q1) on slides are canonical
- Slide numbers are stable references

**Multi-site:**
- Each site may have different document library names
- Sites may have different team access and content focus
- Treat each site independently for delta detection
- Cross-site consistency checks during knowledge derivation

**python-pptx limitations:**
- Cannot extract from images, charts, or SmartArt graphics
- Table extraction works but loses formatting
- Grouped shapes may have nested text frames — recurse into groups
- Some shapes use non-standard text frames — check all shape types
