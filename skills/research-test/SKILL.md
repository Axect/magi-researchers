# Research Test & Visualization Skill

## Description
Creates tests for research code and generates publication-quality visualizations. Requires implemented code in `src/` of an active research output directory.

## Usage
```
/research-test [path/to/output/dir]
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
- **File References**: Use `@filepath` in the prompt parameter to pass saved artifacts (e.g., `@plan/research_plan.md`)
  instead of pasting file content inline. The CLI tools read files directly, preventing context truncation.

### Step 0: Locate Implementation

1. Find the active research output directory (from `$ARGUMENTS` or most recent).
2. Verify `src/` exists and contains implementation code.
3. Read the research plan (`plan/research_plan.md`) for test strategy guidance.
4. Read all source files to understand what needs testing.

### Step 1: Test Strategy Discussion

1. Prepare a summary of the implemented code (key functions, expected behaviors, edge cases).

2. Consult Gemini for test suggestions:
```
mcp__gemini-cli__ask-gemini(
  prompt: "Given the following research plan and implementation, suggest comprehensive test cases. Include unit tests, integration tests, and validation tests against known results.\n\nResearch plan:\n@{output_dir}/plan/research_plan.md\n\nSource files:\n@{output_dir}/src/*.py",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-3-pro-preview" → "gemini-2.5-pro"
)
```

3. Synthesize the test suggestions into a test plan:
   - **Unit tests**: Individual function correctness
   - **Integration tests**: Component interaction
   - **Validation tests**: Results match known/expected values
   - **Edge cases**: Boundary conditions, degenerate inputs

4. Present the test plan to the user for approval/modifications.

### Step 2: Test Implementation

1. Create `tests/` directory if it doesn't exist.
2. Write test code using `pytest`:
   - `tests/test_*.py` files matching source modules
   - Clear test names describing what's being tested
   - Appropriate assertions with informative failure messages
3. Run tests with `uv run pytest tests/ -v` and report results.
4. Fix any failing tests (or flag them for user attention if the fix isn't clear).

### Step 3: Visualization

1. Create `plots/` directory if it doesn't exist.
2. Generate visualizations using matplotlib + scienceplots:

```python
import matplotlib.pyplot as plt
import scienceplots

plt.style.use(['science', 'nature'])
```

3. For each visualization:
   - Create the figure with appropriate size for the content
   - Use proper labels, titles, and legends
   - Apply domain-appropriate plot types (see domain template)
   - Save in both formats:
     ```python
     fig.savefig('plots/{name}.png', dpi=300, bbox_inches='tight')
     fig.savefig('plots/{name}.pdf', bbox_inches='tight')
     ```

4. Visualization checklist:
   - [ ] Axes labeled with quantities and units
   - [ ] Legend present if multiple series
   - [ ] Appropriate scale (linear, log, etc.)
   - [ ] Color-blind friendly palette (scienceplots default handles this)
   - [ ] Saved as both PNG and PDF

### Step 4: Plot Manifest Generation

After all plots are generated, create `plots/plot_manifest.json` — a structured registry of every plot for use by the report phase.

1. For **each** plot generated in Step 3, collect the following metadata:
   ```json
   {
     "plot_id": "descriptive_snake_case_name",
     "files": {
       "png": "plots/{name}.png",
       "pdf": "plots/{name}.pdf"
     },
     "description": "One-sentence description of what the plot shows",
     "section_hint": "results | methodology | validation | comparison | testing",
     "caption": "Publication-ready figure caption (2-3 sentences). Include key quantitative findings visible in the plot.",
     "markdown_snippet": "![Caption text](plots/{name}.png)",
     "source_context": "Brief note on what code/data generated this plot"
   }
   ```

2. Write the complete manifest as a JSON array to `plots/plot_manifest.json`:
   ```json
   {
     "generated_at": "YYYY-MM-DD HH:MM",
     "total_plots": N,
     "plots": [ ...entries... ]
   }
   ```

3. **Section hint values** (controlled vocabulary):
   - `results` — Key findings, main experimental outcomes
   - `methodology` — Algorithmic diagrams, data pipeline illustrations
   - `validation` — Comparison with known/expected values, error analysis
   - `comparison` — Baseline vs. proposed method, ablation studies
   - `testing` — Test coverage, pass/fail distributions, edge case behavior

4. **Caption guidelines**:
   - First sentence: what the plot shows (e.g., "Training loss over 100 epochs for three model variants.")
   - Second sentence: key observation (e.g., "The proposed method converges 2.3x faster than the baseline.")
   - Third sentence (optional): implication or context.

### Step 5: Phase Gate

Before presenting to the user, execute a lightweight quality checkpoint:

1. **Self-assessment**: Evaluate the test and visualization outputs against the following checklist and assign a confidence level (`High`, `Medium`, or `Low`):

| Checklist Item | Criteria |
|:---------------|:---------|
| Coverage adequacy | Key functions and components have corresponding tests; no major gaps |
| Edge case handling | Boundary conditions, degenerate inputs, and error paths are tested |
| Visualization quality | Plots follow scienceplots style, axes labeled, legends present, saved as PNG+PDF |
| Result reproducibility | Tests are deterministic or use fixed seeds; results are consistent across runs |

2. **Conditional MAGI mini-review** (if confidence is `Medium` or `Low`):
   - Send the test results + plot summaries to Codex for a focused review targeting the low-scoring checklist items:
   ```
   mcp__codex-cli__ask-codex(
     prompt: "Review these research tests and visualizations for coverage, edge cases, visualization quality, and reproducibility. Focus on: {low_scoring_items}\n\n@{output_dir}/plots/plot_manifest.json\n@{output_dir}/tests/test_*.py"
   )
   ```

3. **Go/No-Go synthesis**: Write a brief gate report with:
   - Confidence level and justification
   - Checklist scores (pass/partial/fail for each item)
   - Issues found (if any) and applied fixes
   - Go/No-Go decision

4. Save to `tests/phase_gate.md`.

> If the gate returns **No-Go**, fix the identified issues before presenting to the user. Maximum 1 fix iteration.

### Step 6: Summary

Present to the user:
- Test results summary (passed/failed/skipped)
- List of generated plots with descriptions
- Phase gate result summary
- Any issues found during testing
- Suggestions for additional tests or visualizations

## Notes
- If scienceplots is not installed, run `uv add SciencePlots` first.
- For physics: include comparison with analytical/theoretical results in plots.
- For AI/ML: include learning curves, comparison charts, and metric tables.
- For statistics: include residual diagnostics, Q-Q plots, forest plots, and posterior densities.
- For mathematics: include proof dependency DAGs, phase portraits, and parameter space plots.
- For paper: include argument maps, figure placement plans, and citation network diagrams.
