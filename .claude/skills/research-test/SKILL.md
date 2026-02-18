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

### Step 0: Locate Implementation

1. Find the active research output directory (from `$ARGUMENTS` or most recent).
2. Verify `src/` exists and contains implementation code.
3. Read the research plan (`plan/research_plan.md`) for test strategy guidance.
4. Read all source files to understand what needs testing.

### Step 4a: Test Strategy Discussion

1. Prepare a summary of the implemented code (key functions, expected behaviors, edge cases).

2. Consult Gemini for test suggestions:
```
mcp__gemini-cli__ask-gemini(
  prompt: "Given the following research implementation, suggest comprehensive test cases. Include unit tests, integration tests, and validation tests against known results.\n\n{code summary and key functions}",
  model: "gemini-3-pro-preview"
)
```

3. Synthesize the test suggestions into a test plan:
   - **Unit tests**: Individual function correctness
   - **Integration tests**: Component interaction
   - **Validation tests**: Results match known/expected values
   - **Edge cases**: Boundary conditions, degenerate inputs

4. Present the test plan to the user for approval/modifications.

### Step 4b: Test Implementation

1. Create `tests/` directory if it doesn't exist.
2. Write test code using `pytest`:
   - `tests/test_*.py` files matching source modules
   - Clear test names describing what's being tested
   - Appropriate assertions with informative failure messages
3. Run tests with `uv run pytest tests/ -v` and report results.
4. Fix any failing tests (or flag them for user attention if the fix isn't clear).

### Step 4c: Visualization

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

### Step 5: Summary

Present to the user:
- Test results summary (passed/failed/skipped)
- List of generated plots with descriptions
- Any issues found during testing
- Suggestions for additional tests or visualizations

## Notes
- If scienceplots is not installed, run `uv add SciencePlots` first.
- For physics: include comparison with analytical/theoretical results in plots.
- For AI/ML: include learning curves, comparison charts, and metric tables.
