# Research Workflow — Full Pipeline

## Description
Runs the complete research pipeline: Brainstorming → Planning → Implementation → Testing & Visualization → Reporting. Orchestrates all phases with user checkpoints between each.

## Usage
```
/research "research topic" [--domain physics|ai_ml|statistics|mathematics|paper]
```

## Arguments
- `$ARGUMENTS` — The research topic (required) and optional `--domain` flag.

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-3-pro-preview"` (fallback)
  3. `model: "gemini-2.5-pro"` (last resort)
- **Codex**: Use `mcp__codex-cli__brainstorm` for ideation, `mcp__codex-cli__ask-codex` for analysis/review.
- **Context7**: Use `mcp__plugin_context7_context7__query-docs` for library documentation lookups during implementation.
- **Visualization**: Use `matplotlib` with `scienceplots` (`['science', 'nature']` style). Save plots as PNG (300 dpi) and PDF.

When this skill is invoked, execute the full research pipeline below. **Always pause for user confirmation between phases.**

---

### Phase 0: Initialization

1. Parse `$ARGUMENTS`:
   - Extract the research topic (everything before `--domain` or the entire string)
   - Extract domain if `--domain` is specified; otherwise infer from topic keywords
2. Create the output directory structure:
   ```
   outputs/{sanitized_topic}_{YYYYMMDD}_v{N}/
   ├── brainstorm/
   ├── plan/
   ├── src/
   ├── tests/
   └── plots/
   ```
   - Sanitize topic: lowercase, spaces→underscores, remove special chars, max 50 chars
   - Date format: YYYYMMDD (today's date)
   - Version: Glob for `outputs/{sanitized_topic}_{YYYYMMDD}_v*/` and set N = max existing + 1 (start at v1)
3. If the domain has a template in `${CLAUDE_PLUGIN_ROOT}/templates/domains/`, read it as context.
4. Announce to the user: topic, domain, output directory.

---

### Phase 1: Brainstorming

Execute the `/magi-researchers:research-brainstorm` workflow:

**Step 1a — Parallel Brainstorming:**
- Call `mcp__gemini-cli__brainstorm` with `model: "gemini-3.1-pro-preview"` (apply fallback chain if it fails) for creative/theoretical ideas
- Simultaneously call a second brainstorm (Codex or Gemini with implementation focus) for practical ideas
- Save to `brainstorm/gemini_ideas.md` and `brainstorm/codex_ideas.md`

**Step 1b — Cross-Check:**
- Gemini reviews Codex ideas → `brainstorm/gemini_review_of_codex.md`
- Codex reviews Gemini ideas → `brainstorm/codex_review_of_gemini.md`

**Step 1c — Synthesis:**
- Claude reads all 4 documents and creates `brainstorm/synthesis.md`
- Present top research directions to user

**>>> USER CHECKPOINT: Confirm research direction <<<**

---

### Phase 2: Research Planning

1. Based on user-confirmed direction from Phase 1:
   - Define specific research objectives
   - Outline the technical approach (algorithms, models, data)
   - Specify implementation requirements (language, libraries, compute)
   - Design the test strategy
   - Plan visualizations
2. Save to `plan/research_plan.md`
3. Present plan summary to user

**>>> USER CHECKPOINT: Approve research plan <<<**

---

### Phase 3: Implementation

Execute the `/magi-researchers:research-implement` workflow:

1. Follow `research_plan.md` to implement code in `src/`
2. Use Context7 for library documentation as needed
3. Validate basic functionality
4. Present implementation summary to user

**>>> USER CHECKPOINT: Review implementation <<<**

---

### Phase 4: Testing & Visualization

Execute the `/magi-researchers:research-test` workflow:

**Step 4a — Test Design:**
- Consult Gemini for test case suggestions
- Claude synthesizes test strategy
- Present to user for approval

**Step 4b — Test Execution:**
- Write tests in `tests/`
- Run with `uv run pytest tests/ -v`
- Report results

**Step 4c — Visualization:**
- Generate plots using matplotlib + scienceplots (`['science', 'nature']` style)
- Save as PNG (300 dpi) and PDF in `plots/`

**Step 4d — Plot Manifest:**
- Generate `plots/plot_manifest.json` with metadata for every plot: plot_id, file paths, description, section_hint, publication-ready caption, and markdown snippet
- This manifest is the primary input for Phase 5's plot integration

**>>> USER CHECKPOINT: Review test results and visualizations <<<**

---

### Phase 5: Reporting

Execute the `/magi-researchers:research-report` workflow:

**Step 0 — Gather & Health Check:**
- Inventory all phase outputs
- Read `plots/plot_manifest.json` (create if missing but plots exist)
- Verify all plot files are present and valid

**Step 1 — Content Assembly & Plot Mapping:**
- Read all phase artifacts
- Map manifest plots to report sections using `section_hint` tags

**Step 2 — Report Draft with Integrated Plots:**
- Generate `report.md` using `${CLAUDE_PLUGIN_ROOT}/templates/report_template.md` structure
- Actively embed plots from the manifest with contextualizing paragraphs and quantitative observations
- Include all sections: Background, Brainstorming, Methodology, Implementation, Results, Testing, Conclusion

**Step 3 — Gap Detection & Plot Generation Loop (max 2 iterations):**
- Identify claims without supporting figures or results needing visualization
- Generate new plots (write matplotlib code → execute → save to `plots/` → update manifest)
- Re-draft affected sections with newly generated plots

**Step 4 — MAGI Traceability Review:**
- Gemini (BALTHASAR) reviews the draft for orphaned claims (text without supporting figures), orphaned plots (figures without discussion), and weak claim-evidence links
- Claude revises the report based on review feedback

**Step 5 — Write Final Report:**
- Save finalized `report.md`
- Present summary with plot integration statistics

**>>> USER CHECKPOINT: Review and finalize report <<<**

---

### Completion

Announce completion with:
- Output directory location
- Summary of all generated artifacts
- Any follow-up suggestions (e.g., expand implementation, add more tests, explore alternative directions)

## Notes
- If any phase fails, stop and inform the user with clear error context
- User can skip phases by saying "skip" at any checkpoint
- The workflow state is maintained through files — it can be resumed if interrupted
- Each phase skill can also be run independently outside this pipeline
