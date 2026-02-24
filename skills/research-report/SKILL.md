# Research Report Skill

## Description
Generates a structured markdown research report from all previous phase outputs. Actively integrates existing plots, generates missing visualizations, and cross-verifies claim-evidence integrity. Requires at least some prior phase results to exist.

## Usage
```
/research-report [path/to/output/dir]
```

## Arguments
- `$ARGUMENTS` — Optional path to the research output directory. If not provided, uses the most recent `outputs/*/` directory.

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-3-pro-preview"` (fallback)
  3. `model: "gemini-2.5-pro"` (last resort)
- **Visualization**: Use `matplotlib` with `scienceplots` (`['science', 'nature']` style). Save plots as PNG (300 dpi) and PDF.

### Step 0: Gather Materials & Health Check

1. Find the active research output directory.
2. Inventory available materials by checking for:
   - `brainstorm/synthesis.md` (and other brainstorm files)
   - `plan/research_plan.md`
   - `src/` contents
   - `tests/` and test results
   - `plots/` visualizations
3. **Read the plot manifest** (`plots/plot_manifest.json`):
   - If the manifest exists, parse it as the primary source of plot information.
   - If the manifest does NOT exist but `plots/` contains files, create the manifest by inventorying all `.png`/`.pdf` files in `plots/` and generating metadata (description, section_hint, caption, markdown_snippet) for each.
   - If neither exists, note that no visualizations are available yet (they may be generated in the mini-loop).
4. **Plot health check**: For each plot listed in the manifest, verify:
   - The PNG file exists and is non-empty (file size > 0)
   - If any plot file is missing or corrupt, note it for re-generation in Step 2.
5. Read the report template from `${CLAUDE_PLUGIN_ROOT}/templates/report_template.md`.
6. Determine the domain and load the relevant domain template from `${CLAUDE_PLUGIN_ROOT}/templates/domains/` for tone/style guidance.

### Step 1: Content Assembly & Plot Mapping

Read all available materials:
- `brainstorm/synthesis.md` — for Research Background and Brainstorming Summary sections
- `plan/research_plan.md` — for Methodology section
- All files in `src/` — for Implementation section
- Test results and `tests/` — for Testing section
- `plots/plot_manifest.json` — for Results & Visualization section

**Plot-to-Section Mapping:**
Using the `section_hint` field from the manifest, assign each plot to a report section:
- `results` → Section 5 (Results & Visualization)
- `methodology` → Section 3 (Methodology)
- `validation` → Section 5 or Section 6 (Testing)
- `comparison` → Section 5 (Results & Visualization)
- `testing` → Section 6 (Testing)

### Step 2: Report Draft with Integrated Plots (Iteration 1)

Using the template structure from `${CLAUDE_PLUGIN_ROOT}/templates/report_template.md`, generate the report:

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
- Embed any `methodology`-tagged plots here with their captions

**Section 4 — Implementation:**
- Architecture overview
- Key components and their roles
- Notable implementation decisions

**Section 5 — Results & Visualization:**
- Key findings and observations
- **For each `results`/`comparison`-tagged plot from the manifest:**
  - Write a contextualizing paragraph with concrete quantitative observations (read from captions and source data if available)
  - Embed the plot using the manifest's `markdown_snippet`
  - Follow with interpretation of what the plot shows
- Do NOT use passive references like "see figure below" — actively discuss what the data shows with specific numbers

**Section 6 — Testing:**
- Test strategy overview
- Test results summary
- Validation against expected outcomes
- Embed any `validation`/`testing`-tagged plots with their captions

**Section 7 — Conclusion:**
- Summary of contributions
- Limitations and caveats
- Future work suggestions

**Appendix:**
- Links to all brainstorm documents
- Link to research plan
- Links to source and test directories
- **Plot manifest summary table** (plot_id, description, section)

### Step 3: Gap Detection & Plot Generation Loop

After completing the initial draft, perform a gap analysis:

1. **Identify missing visualizations**: Review the draft and ask:
   - Are there quantitative claims without supporting figures?
   - Are there comparisons described in text that would benefit from a chart?
   - Are there test results that lack visual representation?
   - Would a summary/overview figure help tie the narrative together?

2. **If gaps are found** (and iteration count < 2):
   a. For each needed plot, write a self-contained Python script using:
      ```python
      import matplotlib.pyplot as plt
      import scienceplots
      plt.style.use(['science', 'nature'])
      ```
   b. Execute the script with `uv run python {script_path}`
   c. Save plots to `plots/` as both PNG (300 dpi) and PDF
   d. Update `plots/plot_manifest.json` with the new plot entries
   e. Re-draft the affected report sections to integrate the new plots
   f. Increment the iteration counter

3. **If no gaps are found** (or iteration limit reached): Proceed to Step 4.

**Loop constraints:**
- Maximum 2 iterations of gap detection + generation
- Each iteration should generate at most 3 new plots
- New plots must use existing data from `src/` or test outputs — do NOT fabricate data

### Step 4: MAGI Traceability Review

Execute these two review calls **simultaneously** (in the same message):

**Gemini (BALTHASAR) — Scientific Rigor Review:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "You are a scientific reviewer. Analyze this research report for claim-evidence integrity. Identify:\n\n1. **Orphaned claims**: Text assertions that lack a supporting figure, table, or data reference\n2. **Orphaned plots**: Figures that are embedded but never discussed or interpreted in the text\n3. **Weak links**: Claims that reference a figure but the figure doesn't clearly support the claim\n4. **Caption quality**: Are figure captions precise, quantitative, and publication-ready?\n\nFor each issue found, specify the section, the problematic text or figure, and a concrete fix.\n\nReport draft:\n{report_content}\n\nPlot manifest:\n{manifest_content}",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-3-pro-preview" → "gemini-2.5-pro"
)
```

**Codex (CASPER) — Visualization Quality Review:**
```
mcp__codex-cli__ask-codex(
  prompt: "You are a data visualization reviewer. Analyze this research report for visualization quality and completeness. Identify:\n\n1. **Missing visualizations**: Quantitative results or comparisons described in text that would benefit from a chart/plot but have none\n2. **Plot-narrative mismatch**: Figures whose captions or surrounding text don't accurately describe what the plot shows\n3. **Visualization improvements**: Existing plots that could use better chart types, scales, or encodings for clarity\n4. **Reproducibility gaps**: Plots that lack source context or data references needed to regenerate them\n\nFor each issue found, specify the section, the problematic text or figure, and a concrete fix.\n\nReport draft:\n{report_content}\n\nPlot manifest:\n{manifest_content}"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__ask-gemini` with the Gemini fallback chain and visualization-focused framing.

**Claude (MELCHIOR) — Synthesis & Revision:**

After both reviews are received, synthesize the feedback:

1. Identify **consensus issues** (flagged by both models) — these are high-priority fixes
2. Identify **divergent suggestions** — evaluate each on merit and apply where appropriate
3. Apply revisions:
   - For each **orphaned claim**: Add a supporting visualization (if within loop budget) or add an explicit caveat ("This observation requires further visual analysis.")
   - For each **orphaned plot**: Add discussion text around the embedded figure
   - For each **weak link**: Strengthen the connecting narrative or replace with a more appropriate figure reference
   - For each **visualization improvement**: Generate updated plot code if the fix is straightforward (e.g., scale change, label fix)
4. Update the report draft with all revisions

### Step 5: Write Final Report

1. Save the completed report to `report.md` in the output directory root.
2. Present a summary to the user:
   - Report location
   - Word count / section breakdown
   - Number of plots integrated (from original manifest + newly generated)
   - Any sections that are thin due to missing phase data
   - Summary of traceability review findings and resolutions

### Step 6: User Review

- Ask if any sections need expansion or modification
- Offer to regenerate specific sections with different emphasis
- Offer to generate additional visualizations for specific findings

## Notes
- Write in clear, academic-but-accessible style
- Use markdown formatting effectively (headers, lists, code blocks, tables)
- Include all plot references as relative paths
- If some phases were skipped, note this in the report and mark sections as "Not Available"
- The report should stand alone as a complete document
- When writing about plots, always include concrete quantitative observations — never just "As shown in Figure X"
- The gap detection loop is optional: if all claims are well-supported and all plots are referenced, skip directly to traceability review
