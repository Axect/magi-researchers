# Research Implement Skill

## Description
Implements research code based on an existing research plan. Requires a `research_plan.md` to be present in the active research output directory.

## Usage
```
/research-implement [path/to/research_plan.md]
```

## Arguments
- `$ARGUMENTS` — Optional path to the research plan. If not provided, searches for the most recent `outputs/*/plan/research_plan.md`.

## Instructions

### MCP Tool Rules
- **Context7**: Use `mcp__plugin_context7_context7__query-docs` for library documentation lookups. Call `resolve-library-id` first to get the library ID.
- **File References**: Use `@filepath` in the prompt parameter to pass saved artifacts (e.g., `@plan/research_plan.md`)
  instead of pasting file content inline. The CLI tools read files directly, preventing context truncation.

### Step 0: Locate Research Plan

1. If a path is provided in `$ARGUMENTS`, use it directly.
2. Otherwise, find the most recent research plan:
   - Glob for `outputs/*/plan/research_plan.md`
   - Select the most recently modified one.
3. If no plan is found, inform the user and suggest running `/magi-researchers:research-brainstorm` first, or creating a plan manually.
4. Read the research plan and identify:
   - The output base directory (parent of `plan/`)
   - Required algorithms/models to implement
   - Programming language and framework choices
   - Expected inputs and outputs
   - Dependencies needed

### Step 1: Environment Setup

1. Create the `src/` directory under the output base if it doesn't exist.
2. Check if any additional Python dependencies are needed beyond what's in `pyproject.toml`.
   - If so, inform the user and suggest adding them via `uv add`.

### Step 2: Implementation

1. Follow the research plan's implementation section strictly.
2. Write modular, well-structured code in `src/`:
   - Main entry point (e.g., `src/main.py`)
   - Separate modules for distinct components (e.g., `src/model.py`, `src/data.py`, `src/utils.py`)
3. Use Context7 (`mcp__plugin_context7_context7__query-docs`) to look up library APIs when needed.
4. Include docstrings for all public functions explaining:
   - Purpose
   - Parameters and return values
   - Any assumptions or limitations

### Step 3: Validation

1. After implementation, do a basic sanity check:
   - Ensure all files are syntactically valid (e.g., `uv run python -c "import src.main"` or equivalent)
   - Check for obvious issues (unused imports, undefined variables)
2. Present the implementation summary to the user:
   - List of files created with brief descriptions
   - Any deviations from the research plan and why
   - Known limitations or TODOs

### Step 4: Phase Gate

Before presenting to the user, execute a lightweight quality checkpoint:

1. **Self-assessment**: Evaluate the implementation against the following checklist and assign a confidence level (`High`, `Medium`, or `Low`):

| Checklist Item | Criteria |
|:---------------|:---------|
| Code correctness | All files are syntactically valid; key functions produce expected output types |
| Alignment with plan | Implementation matches the research plan's specification; deviations are documented |
| Error handling | Edge cases and invalid inputs are handled gracefully |
| Dependency management | All required libraries are listed; no undeclared imports |

2. **Conditional MAGI mini-review** (if confidence is `Medium` or `Low`):
   - Send the implementation summary + source code to Codex for a focused review targeting the low-scoring checklist items:
   ```
   mcp__codex-cli__ask-codex(
     prompt: "Review this research implementation for correctness, plan alignment, error handling, and dependency management. Focus on: {low_scoring_items}\n\n@{output_dir}/plan/research_plan.md\n@{output_dir}/src/*.py"
   )
   ```

3. **Go/No-Go synthesis**: Write a brief gate report with:
   - Confidence level and justification
   - Checklist scores (pass/partial/fail for each item)
   - Issues found (if any) and applied fixes
   - Go/No-Go decision

4. Save to `src/phase_gate.md`.

> If the gate returns **No-Go**, fix the identified issues before presenting to the user. Maximum 1 fix iteration.

### Step 5: User Review

Present the implementation for user review:
- Highlight key design decisions
- Note any areas where alternative approaches were considered
- Include the phase gate result summary
- Ask if modifications are needed before proceeding to testing

## Notes
- Prefer simple, readable code over clever optimizations
- Match the coding style to the research domain conventions
- If the plan is ambiguous, make reasonable choices and document them
- Do not over-engineer — implement exactly what the plan specifies
