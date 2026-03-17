# Research Test & Visualization Skill

## Description
Creates tests for research code and generates publication-quality visualizations. Requires
implemented code in `src/` of an active research output directory.

This skill does **not** execute the main research pipeline — that is Phase 3.5's responsibility
(`/research-execute`). If `results/` is already populated, tests and visualizations use those
artifacts. If not, tests use mocks/fixtures and visualizations use inline-computed values.

**Tool selection**: Claude autonomously chooses testing and visualization tools to match the
languages and ecosystems already present in `src/`. No specific framework is mandated.

## Usage
```
/research-test [path/to/output/dir]
```

## Arguments
- `$ARGUMENTS` — Optional path to the research output directory. If not provided, uses the most recent `outputs/*/` directory.

## Instructions

> **Shared rules**: Read `${CLAUDE_PLUGIN_ROOT}/shared/rules.md` before starting. §MCP, §Claude-Only, §Visualization apply to this skill.
> **Inline fallback** (if shared rules unavailable): Gemini models: gemini-3.1-pro-preview → gemini-2.5-pro → Claude. Codex: gpt-5.4. scienceplots `['science','nature']`, 300dpi PNG+PDF, Nature widths (3.5/7.2in). Subagents use `Read` tool.

### Claude-Only Mode
See §Claude-Only in shared rules.

### MCP Tool Rules
See §MCP in shared rules. Additionally:
- **When to search**: testing best practices, benchmark references, visualization techniques, domain-specific test patterns

---

## Common Restrictions

Regardless of tool choices, all outputs **must** satisfy the following contracts. These are the
interface between Phase 4 and Phase 5 (Report) — violating them breaks the pipeline.

| Restriction | Requirement | Rationale |
|:------------|:------------|:----------|
| **Plot Manifest** | All visualizations must be registered in `plots/plot_manifest.json` using the fixed schema below | Phase 5 (Report) reads this file to assemble the report |
| **Dual Format** | Every plot must be saved as both **PNG** (300 dpi) and **PDF or SVG** | PNG for preview, PDF/SVG for publication |
| **Execution Evidence** | At least one test or verification must confirm the code runs without error | Validates implementation correctness |
| **Dependency Spec** | Any new test/viz dependencies must be added to the appropriate manifest (`pyproject.toml`, `Cargo.toml`, `DESCRIPTION`, etc.) | Reproducibility |

---

### Step 0: Locate Implementation & Detect Workspace

1. Find the active research output directory (from `$ARGUMENTS` or most recent `outputs/*/`).
2. Verify `src/` exists and contains implementation code.
3. Read `plan/research_plan.md` for research context, test strategy guidance, and the YAML
   frontmatter's `languages`/`ecosystem` fields.
4. Read all source files in `src/` to understand what needs testing.
5. **Workspace Detection** — scan for languages and ecosystems actually present:

   **1st signal — Package manager files** (scan project root and `src/`):
   | File | Ecosystem |
   |:-----|:----------|
   | `Cargo.toml` | Rust / cargo |
   | `pyproject.toml`, `requirements.txt`, `uv.lock` | Python / uv or pip |
   | `Project.toml` | Julia |
   | `DESCRIPTION` | R |
   | `CMakeLists.txt`, `Makefile` | C/C++ |
   | `package.json` | Node.js |

   **2nd signal — File extension distribution** in `src/`:
   Glob for `src/**/*.rs`, `src/**/*.py`, `src/**/*.r`, `src/**/*.jl`, `src/**/*.cpp`, etc.
   Note the count and dominant extension.

   **Priority rule**: If `research_plan.md` frontmatter says `languages: ["python"]` but `src/`
   contains `Cargo.toml` and `.rs` files, **the actual files win**. Announce the discrepancy.

6. **Check execution results**:
   - Glob for `results/pre_execution_status.json`. If present, parse JSON and check the `state` field.
   - If `pre_execution_status.json` does not exist but `pre_execution_status.md` does (legacy workspace), read the `.md` and infer state from its content (look for SUCCESS/FAILED/PARTIAL/EXISTING).
   - State `SUCCESS` or `EXISTING` → integration tests and visualizations may use `results/` data.
   - State `FAILED`, `PARTIAL`, or file absent → integration tests must be skipped; use mocks/inline data.

### Step 1: Test Strategy Discussion

1. Prepare a workspace summary:
   - Detected languages and ecosystems
   - Key functions/modules and their expected behaviors
   - Whether `results/` data is available

2. Consult Gemini for test suggestions, providing the workspace context:
   ```
   mcp__gemini-cli__ask-gemini(
     prompt: "Given the following research implementation, suggest a comprehensive test strategy.\n\nWorkspace context:\n- Detected languages/ecosystems: {detected}\n- results/ status: {SUCCESS|FAILED|ABSENT}\n\nResearch plan:\n@{output_dir}/plan/research_plan.md\n\nSource files:\n@{output_dir}/src/*\n\nPre-execution status (if available):\n@{output_dir}/results/pre_execution_status.json\n\nSuggest tests in two tiers:\n1. Unit tests (no results/ dependency — use mocks/fixtures; must run even without pre-execution)\n2. Integration/validation tests (may depend on results/ artifacts; mark as skippable if results/ absent)\n\nRecommend appropriate testing tools for the detected languages. Do not prescribe a single framework — choose what fits the codebase.",
     model: "gemini-3.1-pro-preview"
   )
   ```

   > **If `--claude-only`**: Per §SubagentExec — **A** (CD, test strategist): Read research plan, source files, pre_execution_status. Suggest 2-tier test strategy (unit + integration) with appropriate tools for detected languages. Return structured text.

3. Synthesize the test plan, keeping two tiers explicit:
   - **Tier 1 — Unit tests** (always run):
     - Individual function/module correctness
     - Edge cases and boundary conditions
     - Error path handling
     - Use mocks/fixtures — never depend on `results/`
   - **Tier 2 — Integration / validation tests** (run only if `results/` is available):
     - Data artifact loading and schema validation
     - End-to-end result correctness against known values
     - Marked skippable when `results/` is absent

4. Present the test plan to the user for approval/modifications.

### Step 2: Test Implementation

1. Choose test tooling based on detected workspace (not prescribed):
   - Use the native test framework for each detected language
   - For multi-language projects, run each language's tests independently and aggregate results
   - Recommended defaults (use if nothing more fitting exists):
     | Language | Test Framework |
     |:---------|:---------------|
     | Python | `pytest` |
     | Rust | `cargo test` |
     | R | `testthat` |
     | Julia | `Test.jl` |
     | C/C++ | `ctest` / `Catch2` |

2. Write Tier 1 unit tests:
   - Clear test names describing what's being tested
   - Mocks/fixtures for any external data or expensive computation
   - Informative assertion messages on failure

3. Write Tier 2 integration tests, guarded by availability of `results/`:
   - Python example:
     ```python
     import pytest, pathlib, json
     _status_json = pathlib.Path("results/pre_execution_status.json")
     _status_md = pathlib.Path("results/pre_execution_status.md")  # legacy fallback
     RESULTS_AVAILABLE = _status_json.exists() or _status_md.exists()

     @pytest.mark.skipif(not RESULTS_AVAILABLE, reason="results/ not available — run /research-execute first")
     def test_output_schema():
         ...
     ```
   - For other languages, use the equivalent conditional skip mechanism.

4. Run all tests and report results:
   - Tier 1 failures are **blocking** — fix before proceeding.
   - Tier 2 skips (due to absent `results/`) are **expected and acceptable**.
   - Tier 2 failures (results/ present but tests fail) should be investigated.

5. Fix failing Tier 1 tests or flag them for user attention if the fix requires code changes in `src/`.

### Step 3: Visualization

1. Create `plots/` directory if it doesn't exist.

2. **Choose visualization tooling** based on detected workspace:
   - Use the visualization library native to the dominant scripting language.
   - For mixed high-performance + scripting language projects (e.g., Rust + Python):
     - High-performance code generates data → saves to `results/*.csv` / `*.json`
     - Scripting language reads and plots the data
   - Recommended defaults:
     | Language | Visualization |
     |:---------|:--------------|
     | Python | `matplotlib` + `scienceplots` (`['science', 'nature']` style) |
     | R | `ggplot2` |
     | Julia | `Plots.jl` or `Makie.jl` |

   > **IMPORTANT:** For Python visualizations, `scienceplots` with `['science', 'nature']` style is **required**, not optional. Do NOT use manual `plt.rcParams` overrides — they conflict with scienceplots defaults.
   >
   > **Technical note (`text.usetex`):** The `['science', 'nature']` style enables `text.usetex=True`. All text in plots (axis labels, annotations, titles, legends) must be ASCII or LaTeX-escaped. Unicode characters like `π`, `²`, `⁴`, `≈` will cause `RuntimeError`. Use `r'$\pi$'`, `r'$^2$'`, `r'$^4$'`, `r'$\approx$'` instead.
   >
   > **Figure sizing:** Use Nature column widths — single column: 3.5 in, double column: 7.2 in.

3. **Data source selection**:
   - `results/` status `SUCCESS` or `EXISTING`: load data from `results/` for plots
   - `results/` status `FAILED` or `PARTIAL`: use available partial data; note incomplete sections in captions
   - `results/` absent: compute all plot data inline within the visualization script

4. Generate visualizations appropriate to the research:
   - Design plots that best reveal the core findings (Claude decides what to plot)
   - Apply domain-appropriate plot types, scales, and styles
   - Every plot **must** satisfy the Common Restrictions:
     - Axes labeled with quantities and units
     - Legend present if multiple series
     - Saved as both PNG (300 dpi) and PDF or SVG:
       ```python
       # Python example
       fig.savefig('plots/{name}.png', dpi=300, bbox_inches='tight')
       fig.savefig('plots/{name}.pdf', bbox_inches='tight')
       ```

### Step 4: Plot Manifest Generation

After all plots are generated, create or update `plots/plot_manifest.json`. This file is the
**mandatory interface** to Phase 5 (Report). Its schema is fixed regardless of what tool generated
the plots.

1. For **each** plot, collect:
   ```json
   {
     "plot_id": "descriptive_snake_case_name",
     "files": {
       "png": "plots/{name}.png",
       "pdf": "plots/{name}.pdf"
     },
     "description": "One-sentence description of what the plot shows",
     "section_hint": "results | methodology | validation | comparison | testing",
     "caption": "Publication-ready figure caption (2-3 sentences). Include key quantitative findings.",
     "markdown_snippet": "![Caption text](plots/{name}.png)",
     "source_context": "What code/data generated this plot (include results/ file path if applicable)",
     "style": ["science", "nature"],
     "dpi": 300,
     "source_script": "plots/plot_{name}.py",
     "source_function": "plot_{name}",
     "generation_date": "YYYY-MM-DDTHH:MM:SS+00:00"
   }
   ```

   The `style`, `dpi`, `source_script`, `source_function`, and `generation_date` fields are required for downstream report generation (Phase 5). `source_script` must be an actual file path to the Python script that generated the plot.

   > **Note:** The `source_context` field provides a human-readable description. The `source_script` and `source_function` fields provide machine-readable paths for automated style validation by the Report phase (Step 0.5). Both must be populated.

2. Write the complete manifest to `plots/plot_manifest.json`:
   ```json
   {
     "generated_at": "YYYY-MM-DD HH:MM",
     "total_plots": N,
     "plots": [ ...entries... ]
   }
   ```

3. **Section hint vocabulary** (controlled — Phase 5 uses this for placement):
   - `results` — Key findings, main experimental outcomes
   - `methodology` — Algorithmic diagrams, data pipeline illustrations
   - `validation` — Comparison with known/expected values, error analysis
   - `comparison` — Baseline vs. proposed, ablation studies
   - `testing` — Test coverage, pass/fail distributions, edge case behavior

4. **Caption guidelines**:
   - Sentence 1: what the plot shows
   - Sentence 2: key quantitative observation
   - Sentence 3 (optional): implication or context

### Step 5: Phase Gate

Before presenting to the user, execute a lightweight quality checkpoint:

1. **Self-assessment** against the checklist:

| Checklist Item | Criteria |
|:---------------|:---------|
| Tier 1 coverage | All major functions have unit tests; no significant gaps |
| Edge case handling | Boundary conditions, degenerate inputs, and error paths are tested |
| Tier 2 status | Integration tests present; skipped with clear reason if `results/` absent |
| Common Restrictions | plot_manifest.json present with all required fields (including `style`, `dpi`, `source_script`, `source_function`, `generation_date`), all plots in PNG + PDF/SVG, dependency spec updated |
| Style compliance (Python) | All Python-generated plots use `scienceplots` `['science', 'nature']` style; no Unicode in labels; Nature column widths |
| Result reproducibility | Tests are deterministic or use fixed seeds |

2. **Conditional MAGI mini-review** (if confidence is `Medium` or `Low`):
   ```
   mcp__codex-cli__ask-codex(
     prompt: "Review these research tests and visualizations. Focus on: {low_scoring_items}\n\n@{output_dir}/plots/plot_manifest.json\n@{output_dir}/tests/ (or equivalent test directory)\n@{output_dir}/results/pre_execution_status.json",
     model: "gpt-5.4"
   )
   ```

   > **If `--claude-only`**: Per §SubagentExec — **B** (AC, test reviewer): Read plot manifest, test files, pre_execution_status. Review focusing on {low_scoring_items}. Return structured text.

3. Write gate report to `tests/phase_gate.md`.

> If the gate returns **No-Go**, fix identified issues before presenting. Maximum 1 fix iteration.

### Step 6: Summary

Present to the user:
- **Detected workspace**: languages, ecosystems, tools chosen for testing and visualization
- **results/ status**: SUCCESS / FAILED / PARTIAL / SKIPPED / EXISTING
- **Tier 1 tests**: passed / failed count
- **Tier 2 tests**: passed / skipped count (with reason)
- **Plots generated**: list with section hints and descriptions
- **Phase gate result**
- **Any issues** found, with recommended next steps

## Notes
- The choice of testing and visualization tools is Claude's judgment call — match the workspace.
- If a new dependency is needed for testing/visualization, add it to the appropriate package manager
  file (`uv add`, `cargo add`, etc.) before using it.
- For mixed-language projects: aggregate all test results into a single summary; maintain a single
  `plot_manifest.json` regardless of which language generated the plots.
- If scienceplots is not installed for Python: `uv add SciencePlots`.
- For non-Python plots (R/ggplot2, Julia/Makie, etc.): the `style` field in the manifest should describe the equivalent style used (e.g., `["ggplot2-publication"]`). Report-level scienceplots enforcement applies only to matplotlib-generated plots; non-Python plots are exempt from scienceplots but must still meet the Common Restrictions (dual format, 300 dpi, proper labeling).
- **Domain visualization hints** (guidelines, not rules):
  - Physics: comparison with analytical/theoretical results
  - AI/ML: learning curves, metric tables, comparison charts
  - Statistics: residual diagnostics, Q-Q plots, posterior densities
  - Mathematics: phase portraits, parameter space plots, proof dependency DAGs
  - Paper: argument maps, figure placement plans
