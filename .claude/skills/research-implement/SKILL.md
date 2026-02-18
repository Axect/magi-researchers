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

### Step 0: Locate Research Plan

1. If a path is provided in `$ARGUMENTS`, use it directly.
2. Otherwise, find the most recent research plan:
   - Glob for `outputs/*/plan/research_plan.md`
   - Select the most recently modified one.
3. If no plan is found, inform the user and suggest running `/research-brainstorm` first, or creating a plan manually.
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

### Step 4: User Review

Present the implementation for user review:
- Highlight key design decisions
- Note any areas where alternative approaches were considered
- Ask if modifications are needed before proceeding to testing

## Notes
- Prefer simple, readable code over clever optimizations
- Match the coding style to the research domain conventions
- If the plan is ambiguous, make reasonable choices and document them
- Do not over-engineer — implement exactly what the plan specifies
