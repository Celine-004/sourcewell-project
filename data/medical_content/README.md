# SourceWell Project Medical Content Repository

## Overview
This directory contains curated medical content for evidence-based risk assessment and prevention guidance. All content undergoes rigorous citation verification and medical accuracy review before integration into the knowledge base.

## Directory Structure

### Content Creation
- **`guidelines/`** - Clinical practice guidelines from major medical organizations (all files reside here: drafts and approved)
- **`research_abstracts/`** - Peer-reviewed research abstracts with complete citation metadata (all files reside here: drafts and approved)
- **`_TEMPLATE_*.md`** - Fill-in-the-blank templates for consistent content creation (files prefixed with `_` are not ingested)

### Quality Assurance & Audit Trail
- **`processed/archived/`** - Successfully ingested content moved here by ingestion script (audit trail and prevents re-ingestion)
- **`processed/validation_reports/`** - Quality assurance logs and error reports from ingestion process

## Content Standards

### Citation Requirements
- **Complete source attribution** with accessible URLs or PMIDs
- **Vancouver-style citation metadata** for academic compliance
- **Calculator relevance** explicitly documented
- **Original medical language preserved** without meaning alteration

### Quality Gates (Streamlined Workflow)
1. **Draft Creation** - Create files in `guidelines/` or `research_abstracts/` using templates, set `review_status: "draft"`
2. **Medical Review** - Verify citations, accuracy, calculator relevance, and YAML completeness
3. **Approval** - Change `review_status: "approved"` after human quality review
4. **Ingestion** - Automated script processes only files with `review_status: "approved"` from main folders
5. **Archival** - Successfully ingested content automatically moved to `processed/archived/`

**Note:** `review_status` in YAML frontmatter is the single source of truth for ingestion readiness. No file movement required during review process.

## Calculator Integration

### Supported Risk Calculators
- **`FINDRISC`** - Finnish Diabetes Risk Score
- **`ModifiedFramingham`** - Cardiovascular risk with BMI and BP
- **`ColorectalScreening`** - Age and family history-based screening
- **`[]` (empty)** - General medical content not tied to specific calculator scoring

### File Naming Convention
- **Guidelines:** `[organization]-[topic]-[year].md`
- **Research:** `[study-name]-[first-author]-[year].md`
- **Format:** lowercase, hyphens, descriptive keywords

### File Encoding
All Markdown files must be saved with **UTF-8 encoding**. This is critical for displaying non-ASCII medical symbols (e.g., ≥, ≤, °C) correctly.

### Inline Links
Used within content for immediate user reference and to guide AI attribution:
- **Priority:** PMC ID (for free full-text) > DOI (for publisher's authoritative version) > PMID (for PubMed abstract page)
- **Granularity:** Link as close as possible to the specific medical claim(s) without hindering readability. Link blocks of related claims from the same source once
- **Avoid Redundancy:** Do not include multiple inline links to the exact same source consecutively

## Legal and Compliance

### Medical Disclaimers
The medical content included in this repository (within `data/medical_content/`) is for **demonstration and educational purposes only** as part of an academic Capstone project. This content has been curated to showcase the application's functionality in processing and citing medical information. **It is not intended to provide medical advice or replace professional medical consultation.**

### Copyright Compliance
Users are advised that this content may be subject to copyright by its original publishers (e.g., medical organizations, journals). Any use of this content beyond the scope of academic demonstration, especially for commercial purposes, may require explicit permission from the copyright holders. All sources are meticulously cited within the application's output and where applicable, within the content files themselves.

- Brief excerpts for educational/research purposes under fair use
- Complete citation metadata for all sources
- No full text reproduction - summaries and key points only

---

**Maintain strict adherence to these guidelines for clinical-grade accuracy and regulatory preparation.**
