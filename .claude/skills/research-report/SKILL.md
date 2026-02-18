# Research Report Skill

## Description
Generates a structured markdown research report from all previous phase outputs. Requires at least some prior phase results to exist.

## Usage
```
/research-report [path/to/output/dir]
```

## Arguments
- `$ARGUMENTS` — Optional path to the research output directory. If not provided, uses the most recent `outputs/*/` directory.

## Instructions

### Step 0: Gather Materials

1. Find the active research output directory.
2. Inventory available materials by checking for:
   - `brainstorm/synthesis.md` (and other brainstorm files)
   - `plan/research_plan.md`
   - `src/` contents
   - `tests/` and test results
   - `plots/` visualizations
3. Read the report template from `templates/report_template.md`.
4. Determine the domain and load the relevant domain template for tone/style guidance.

### Step 1: Content Assembly

Read all available materials:
- `brainstorm/synthesis.md` — for Research Background and Brainstorming Summary sections
- `plan/research_plan.md` — for Methodology section
- All files in `src/` — for Implementation section
- Test results and `tests/` — for Testing section
- List of plots in `plots/` — for Results & Visualization section

### Step 2: Report Generation

Using the template structure from `templates/report_template.md`, generate the report:

**Section 1 — Research Background:**
- Problem statement and motivation
- Relevant prior work and context
- Research questions or hypotheses

**Section 2 — Brainstorming Summary:**
- Key ideas generated during brainstorming
- Notable points from cross-check reviews
- Final chosen direction and rationale

**Section 3 — Methodology:**
- Approach description from the research plan
- Key algorithms or techniques used
- Assumptions and their justifications

**Section 4 — Implementation:**
- Architecture overview
- Key components and their roles
- Notable implementation decisions

**Section 5 — Results & Visualization:**
- Key findings and observations
- Embed plot references: `![Description](plots/filename.png)`
- Quantitative results with proper formatting

**Section 6 — Testing:**
- Test strategy overview
- Test results summary
- Validation against expected outcomes

**Section 7 — Conclusion:**
- Summary of contributions
- Limitations and caveats
- Future work suggestions

**Appendix:**
- Links to all brainstorm documents
- Link to research plan
- Links to source and test directories

### Step 3: Write Report

1. Save the completed report to `report.md` in the output directory root.
2. Present a summary to the user:
   - Report location
   - Word count / section breakdown
   - Any sections that are thin due to missing phase data

### Step 4: User Review

- Ask if any sections need expansion or modification
- Offer to regenerate specific sections with different emphasis

## Notes
- Write in clear, academic-but-accessible style
- Use markdown formatting effectively (headers, lists, code blocks, tables)
- Include all plot references as relative paths
- If some phases were skipped, note this in the report and mark sections as "Not Available"
- The report should stand alone as a complete document
