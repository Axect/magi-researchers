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

### Claude-Only Mode
When `--claude-only` is active (passed from the parent `/research` pipeline), all Gemini/Codex MCP calls in this skill are replaced with Claude Agent subagents (`subagent_type: general-purpose`). Subagents use the `Read` tool to access files instead of `@filepath`. Output filenames remain unchanged; each output starts with `> Source: Claude Agent subagent (claude-only mode, {style})`.

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-2.5-pro"` (fallback)
  3. Claude (last resort — skip Gemini MCP tool, use Claude directly)
- **Visualization**: Use `matplotlib` with `scienceplots` (`['science', 'nature']` style). Save plots as PNG (300 dpi) and PDF.
- **File References**: Use `@filepath` in the prompt parameter to pass saved artifacts (e.g., `@report.md`)
  instead of pasting file content inline. The CLI tools read files directly, preventing context truncation.
- **Web Search**: Use web search freely whenever report writing requires citation verification, related work context, or factual accuracy checks:
  - **Claude**: Use the `WebSearch` tool directly
  - **Gemini**: Add `search: true` to `mcp__gemini-cli__ask-gemini` calls
  - **Codex**: Add `search: true` to `mcp__codex-cli__ask-codex` calls
  - **When to search**: citation verification, related work references, fact-checking claims, confirming state-of-the-art results

### Step 0: Gather Materials & Health Check

1. Find the active research output directory.
2. Inventory available materials by checking for:
   - `brainstorm/synthesis.md` (and other brainstorm files)
   - `brainstorm/weights.json` (scoring weights)
   - `brainstorm/personas.md` (assigned expert personas)
   - `brainstorm/debate_round2_gemini.md` (adversarial debate, if `--depth high` was used)
   - `brainstorm/debate_round2_codex.md` (adversarial debate, if `--depth high` was used)
   - `plan/research_plan.md`
   - `plan/murder_board.md` (plan stress-testing results)
   - `plan/mitigations.md` (murder board mitigations)
   - `plan/phase_gate.md` (plan phase gate report)
   - `src/` contents
   - `src/phase_gate.md` (implementation phase gate report)
   - `tests/` and test results
   - `tests/phase_gate.md` (test phase gate report)
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
- `brainstorm/weights.json` — for Brainstorming Summary (scoring weights used)
- `brainstorm/personas.md` — for Brainstorming Summary (expert personas assigned)
- `brainstorm/debate_round2_*.md` — for Brainstorming Summary (debate resolution, if available)
- `plan/research_plan.md` — for Methodology section
- `plan/murder_board.md` — for Methodology section (Plan Stress Testing subsection)
- `plan/mitigations.md` — for Methodology section (mitigation strategies)
- `plan/phase_gate.md` — for Appendix F (Quality Assurance)
- All files in `src/` — for Implementation section
- `src/phase_gate.md` — for Appendix F
- Test results and `tests/` — for Testing section
- `tests/phase_gate.md` — for Appendix F
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
- **Expert Personas**: Summarize the Gemini and Codex personas assigned and their influence on ideation (from `personas.md`)
- **Scoring Weights**: Show the weights used for direction ranking (from `weights.json`)
- Notable points from cross-check reviews
- **Debate Resolution** (if `debate_round2_*.md` exists): Summarize key disagreements and their resolutions
- Final chosen direction and rationale (with weighted score breakdown)

**Section 3 — Methodology:**
- Approach description from the research plan
- Key algorithms or techniques used
- Assumptions and their justifications
- **Plan Stress Testing** (if `murder_board.md` exists): Summarize the murder board's critical findings and the mitigations applied (from `mitigations.md`). This demonstrates that the methodology was adversarially tested before implementation.
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
  prompt: "You are a scientific reviewer. Analyze this research report for claim-evidence integrity. Identify:\n\n1. **Orphaned claims**: Text assertions that lack a supporting figure, table, or data reference\n2. **Orphaned plots**: Figures that are embedded but never discussed or interpreted in the text\n3. **Weak links**: Claims that reference a figure but the figure doesn't clearly support the claim\n4. **Caption quality**: Are figure captions precise, quantitative, and publication-ready?\n\nFor each issue found, specify the section, the problematic text or figure, and a concrete fix.\n\nReport draft:\n@{output_dir}/report.md\n\nPlot manifest:\n@{output_dir}/plots/plot_manifest.json",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-2.5-pro" → Claude
)
```

**Codex (CASPER) — Visualization Quality Review:**
```
mcp__codex-cli__ask-codex(
  prompt: "You are a data visualization reviewer. Analyze this research report for visualization quality and completeness. Identify:\n\n1. **Missing visualizations**: Quantitative results or comparisons described in text that would benefit from a chart/plot but have none\n2. **Plot-narrative mismatch**: Figures whose captions or surrounding text don't accurately describe what the plot shows\n3. **Visualization improvements**: Existing plots that could use better chart types, scales, or encodings for clarity\n4. **Reproducibility gaps**: Plots that lack source context or data references needed to regenerate them\n\nFor each issue found, specify the section, the problematic text or figure, and a concrete fix.\n\nReport draft:\n@{output_dir}/report.md\n\nPlot manifest:\n@{output_dir}/plots/plot_manifest.json",
  model: "gpt-5.4"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__ask-gemini` with the Gemini fallback chain and visualization-focused framing.

> **If `--claude-only`**: Replace both BALTHASAR and CASPER calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent, BALTHASAR — Scientific Rigor Review):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are BALTHASAR, a Creative-Divergent scientific reviewer. You look for gaps in reasoning, missed connections, and opportunities for deeper analysis.
>
> Use the Read tool to read:
> - {output_dir}/report.md
> - {output_dir}/plots/plot_manifest.json
> - {output_dir}/brainstorm/personas.md (if it exists, adopt the Gemini/Subagent A persona for continuity)
>
> Analyze this research report for claim-evidence integrity. Identify:
> 1. **Orphaned claims**: Text assertions lacking a supporting figure, table, or data reference
> 2. **Orphaned plots**: Figures embedded but never discussed or interpreted
> 3. **Weak links**: Claims that reference a figure but the figure doesn't clearly support the claim
> 4. **Caption quality**: Are figure captions precise, quantitative, and publication-ready?
>
> For each issue, specify the section, problematic text/figure, and a concrete fix.
>
> Return your review as structured text (do not save to a file)."
> )
> ```
>
> **Subagent B (Analytical-Convergent, CASPER — Visualization Quality Review):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are CASPER, an Analytical-Convergent visualization reviewer. You focus on data presentation quality, reproducibility, and practical completeness.
>
> Use the Read tool to read:
> - {output_dir}/report.md
> - {output_dir}/plots/plot_manifest.json
> - {output_dir}/brainstorm/personas.md (if it exists, adopt the Codex/Subagent B persona for continuity)
>
> Analyze this research report for visualization quality and completeness. Identify:
> 1. **Missing visualizations**: Quantitative results described in text that need a chart/plot
> 2. **Plot-narrative mismatch**: Figures whose captions don't match what the plot shows
> 3. **Visualization improvements**: Better chart types, scales, or encodings for clarity
> 4. **Reproducibility gaps**: Plots lacking source context or data references
>
> For each issue, specify the section, problematic text/figure, and a concrete fix.
>
> Return your review as structured text (do not save to a file)."
> )
> ```

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

1. Determine the version number:
   - If `report_versions.json` exists, read `current_version` and increment.
   - Otherwise, this is version 1.
2. If version > 1: archive current `report.md` → `report_v{N-1}.md`
3. Save the completed report to `report.md`.
4. Write/update `report_versions.json`:
   ```json
   {
     "schema_version": "1.0.0",
     "current_version": 1,
     "versions": [{
       "version": 1,
       "file": "report.md",
       "created_at": "ISO-8601",
       "feedback_tier": null,
       "feedback_summary": "Initial report"
     }]
   }
   ```
5. Present summary: location, word count, plot count, thin sections, traceability review findings.

### Step 6: User Feedback Loop

Maximum 3 feedback iterations per entry into this step.

**Step 6a: Solicit Feedback**

Present the report and ask:
"Report v{N} is ready at `report.md`. Please review and provide feedback, or say **approve** to finalize."

**Step 6b: Classify Feedback**

When user provides feedback (not "approve"):

1. Classify into one of three tiers:
   - **Tier 1 (Cosmetic)** — wording, tone, structure, formatting, caption rewording
   - **Tier 2 (Visualization)** — new/modified plots, chart type changes, scale changes, plot-narrative linkage
   - **Tier 3 (Substantive)** — code changes, re-execution, different methodology, new experiments

2. Present classification: "I classify this as **Tier {N} ({name})**. Planned action: {description}. Proceed?"

3. If user disagrees, re-classify.

4. Mixed-tier feedback: decompose and apply Tier 1/2 first, then escalate Tier 3.

**Step 6c: Apply — Tier 1 (Cosmetic)**

1. Archive: `report.md` → `report_v{N}.md`
2. Apply text changes directly to report
3. Write updated `report.md`
4. Update `report_versions.json` (increment version, tier=1, summary)
5. Present diff summary → return to Step 6a

**Step 6d: Apply — Tier 2 (Visualization)**

1. Archive: `report.md` → `report_v{N}.md`
2. For each visualization change:
   a. Write matplotlib+scienceplots script
   b. Execute with `uv run python {script_path}`
   c. Save to `plots/` (PNG 300dpi + PDF)
   d. Update `plots/plot_manifest.json`
3. Re-draft affected report sections with updated plots
4. Scoped MAGI traceability review (Step 4 procedure, but only modified sections + new plots):
   - Gemini: scientific rigor on changed sections only
   - Codex: visualization quality on new/modified plots only
   - Claude: synthesize and apply
5. Write updated `report.md`
6. Update `report_versions.json` (increment version, tier=2, summary)
7. Present changes summary → return to Step 6a

**Step 6e: Apply — Tier 3 (Substantive / Escalation)**

This skill cannot handle substantive changes alone.

- **Standalone** (`/research-report`): Inform user which phase needs re-running. Suggest `/research --resume {output_dir}`. Exit loop.
- **Pipeline** (`/research`): Return control to orchestrator for outer-loop handling (see orchestrator Step R2).

**Step 6f: Finalize**

When user approves or iteration limit reached:
- Announce final version number and version history summary.

### LaTeX Formatting Rules
When writing the report, use LaTeX for all mathematical expressions:
- **Inline math**: Use `$...$` for short expressions within a sentence (e.g., `$\alpha = 0.05$`, `$O(n \log n)$`)
- **Display equations**: Use `$$` on its own line, with the equation on a separate line:
  ```
  $$
  \hat{\theta}_{\text{MLE}} = \arg\max_\theta \prod_{i=1}^{n} f(x_i \mid \theta)
  $$
  ```
- Never write display equations inline as `$$..equation..$$` on a single line — always use line breaks between `$$` and the equation
- Use display equations for: key formulas, derivations, loss functions, objective functions, main results
- Use inline math for: variable names, parameter values, complexity notation, short expressions in running text

## Output Files
```
report.md                          # Final report (always latest version)
report_v{N}.md                     # Archived report versions (created on feedback)
report_versions.json               # Version manifest with feedback history
plots/
├── *.png                          # Plot images (300 dpi)
├── *.pdf                          # Plot vector versions
└── plot_manifest.json             # Plot registry
```

## Notes
- Write in clear, academic-but-accessible style
- Use markdown formatting effectively (headers, lists, code blocks, tables)
- Include all plot references as relative paths
- If some phases were skipped, note this in the report and mark sections as "Not Available"
- The report should stand alone as a complete document
- When writing about plots, always include concrete quantitative observations — never just "As shown in Figure X"
- The gap detection loop is optional: if all claims are well-supported and all plots are referenced, skip directly to traceability review
