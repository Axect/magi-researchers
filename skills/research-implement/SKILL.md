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

> **Shared rules**: Read `${CLAUDE_PLUGIN_ROOT}/shared/rules.md` before starting. §MCP, §Claude-Only apply to this skill.
> **Inline fallback** (if shared rules unavailable): Gemini models: gemini-3.1-pro-preview → gemini-2.5-pro → Claude. Codex: gpt-5.4. Use `@filepath` for MCP file refs; subagents use `Read` tool.

### Claude-Only Mode
See §Claude-Only in shared rules.

### MCP Tool Rules
See §MCP in shared rules. Additionally:
- **Context7**: Primary tool for library documentation lookups during implementation.
- **When to search**: library API changes, implementation examples, algorithm details, dependency compatibility, debugging known issues

### Step 0: Locate Research Plan

1. If a path is provided in `$ARGUMENTS`, use it directly.
2. Otherwise, find the most recent research plan:
   - Glob for `outputs/*/plan/research_plan.md`
   - Select the most recently modified one.
3. If no plan is found, inform the user and suggest running `/magi-researchers:research-brainstorm` first, or creating a plan manually.
4. Read the research plan and identify:
   - The output base directory (parent of `plan/`)
   - Required algorithms/models to implement
   - Programming language and framework choices (from frontmatter `languages`/`ecosystem` fields)
   - Expected inputs and outputs
   - Dependencies needed
5. **Parse mode flags from `$ARGUMENTS`**: If invoked standalone (not from the `/research` pipeline), check `$ARGUMENTS` for `--claude-only` and `--substitute` flags. When present, all Gemini/Codex MCP calls in this skill are replaced per the Claude-Only Mode rules above.
6. **Resolve output directory**: If `.workspace.json` exists at the output directory root, read `output_dir` from it and use as the base for all file operations. If absent (standalone invocation), derive the absolute output path from the location of `research_plan.md`.

### Step 1: Workspace Detection & Environment Setup

1. **Check if `src/` already has code** (Glob `src/**/*`):
   - If files exist, read them to understand the current ecosystem before adding anything new.
   - If `src/` is empty or absent, proceed with initialization.

2. **Determine language and ecosystem** using the following priority:

   | Priority | Source | How |
   |:---------|:-------|:----|
   | **1st** | Existing `src/` files | Detect package managers (`Cargo.toml`, `pyproject.toml`, `Project.toml`, `DESCRIPTION`) and dominant file extensions |
   | **2nd** | `research_plan.md` frontmatter | Read `languages` and `ecosystem` fields |
   | **3rd** | Domain + topic inference | Autonomous selection based on research domain and algorithms |

   If 1st and 2nd conflict (e.g., plan says Python but `src/` has Rust code), **the actual files win**.
   Announce the discrepancy and proceed with the detected ecosystem.

3. **Initialize the ecosystem** (only if `src/` is empty):
   - Run the appropriate setup commands for the chosen language:
     - Python: `uv init` (if no `pyproject.toml` exists) or `uv add {deps}`
     - Rust: If `src/` already exists (pre-created by the pipeline), run `cargo init` in the output directory root (not inside `src/`) to avoid double-nesting (`src/src/`). The resulting `src/main.rs` is the correct layout.
     - R: create `DESCRIPTION` and `R/` subdirectory
     - Julia: `julia --project=src/ -e 'import Pkg; Pkg.init()'`
     - C/C++: create `CMakeLists.txt` or `Makefile`
   - If the chosen language/tool is not available on the host system, inform the user with the
     install command and stop. Do NOT attempt to install system-level tools without user approval.

4. **Language selection principles** (when choosing freely):
   - Match the dominant language of the research domain and algorithms
   - Prefer languages/libraries the research plan explicitly mentions
   - Python + uv is the safe fallback when no other preference is clear
   - The implementation must be runnable on a standard Ubuntu Linux system via a scripted command
     (no interactive install steps, no GUI-only tools, no proprietary licenses required)

### Step 2: Implementation

1. Follow the research plan's implementation section strictly.
2. Write modular, well-structured code in `src/`:
   - Follow the ecosystem's idiomatic project layout (e.g., `src/main.py` for Python, `src/main.rs`
     + `src/lib.rs` for Rust, `R/` for R packages)
   - Separate modules for distinct components (data loading, model, utilities, etc.)
3. **Implement a dry-run / fast-mode flag** in the main entry point:
   - The flag should reduce runtime to seconds (e.g., 1 epoch, 10 samples, minimal iterations)
   - This is used by Phase 3.5 (`/research-execute`) for a quick sanity check before the full run
   - Examples: `--dry-run`, `--fast`, `--epochs 1 --samples 10`
4. Use Context7 (`mcp__plugin_context7_context7__query-docs`) to look up library APIs when needed.
5. Include docstrings/comments for all public functions explaining purpose, parameters, return values.

### Step 3: Update research_plan.md Frontmatter

After implementation, update the YAML frontmatter in `plan/research_plan.md` to reflect the actual
execution commands. This information is consumed by Phase 3.5 (`/research-execute`).

Read the current frontmatter and update or add these fields:
```yaml
---
title: "..."
domain: "..."
languages: ["rust", "python"]        # actual languages used in src/
ecosystem: ["cargo", "uv"]           # actual package managers
execution_cmd: "bash run_all.sh"     # command to run the full pipeline
dry_run_cmd: "bash run_all.sh --dry-run"  # fast sanity-check command (seconds)
expected_outputs:                    # key files that should appear in results/
  - "results/metrics.csv"
  - "results/model.pt"
estimated_runtime: "~30 minutes"     # rough estimate for user awareness
---
```

If a `run_all.sh` (or equivalent) script does not yet exist, create it in the **output directory root** (not inside `src/`). The `cwd` field in `execution_manifest.json` should be set accordingly. Always verify that `execution_cmd` can be run from the directory specified by `cwd`.

### Step 3b: Emit Execution Manifest

After updating the YAML frontmatter, also emit a structured `execution_manifest.json` in the output directory root. This file is the machine-readable execution contract consumed by Phase 3.5 (`/research-execute`).

```json
{
  "schema_version": "1.0.0",
  "languages": ["rust", "python"],
  "ecosystem": ["cargo", "uv"],
  "execution_cmd": "bash run_all.sh",
  "dry_run_cmd": "bash run_all.sh --dry-run",
  "expected_outputs": [
    {"path": "results/metrics.csv", "required": true},
    {"path": "results/model.pt", "required": false}
  ],
  "estimated_runtime": "~30 minutes",
  "cwd": "."
}
```

Fields:
- `schema_version`: Always `"1.0.0"` for this release
- `languages`, `ecosystem`: Actual languages/tools used in `src/`
- `execution_cmd`: Single command to run the full pipeline
- `dry_run_cmd`: Fast sanity-check command (seconds, not minutes)
- `expected_outputs`: Files that should appear in `results/` after execution. `required: true` means the pipeline should warn if absent; `required: false` means optional.
- `estimated_runtime`: Rough estimate for user awareness
- `cwd`: Working directory relative to the output directory (optional, defaults to output directory root)

> The YAML frontmatter in `research_plan.md` is retained for backward compatibility and human readability, but `execution_manifest.json` is the authoritative machine contract.

**Pre-validation**: Before proceeding to Step 4, verify that the file or command referenced by `execution_cmd` exists at the expected path (e.g., `Glob` for `run_all.sh` or check that the binary is available). If the target does not exist, fix the manifest/frontmatter before running validation.

> **Note**: If Step 4 (Validation) discovers issues that require changing the execution command, re-update the frontmatter (Step 3) and manifest (Step 3b) after the fix to keep them consistent.

### Step 4: Validation

1. Run the dry-run command to confirm basic executability:
   ```bash
   {dry_run_cmd}
   ```
   - Exit 0: validation passed.
   - Non-zero: fix the issue before presenting to the user.
   Maximum 1 auto-fix attempt. If the fix still results in a non-zero exit, halt, present the full error to the user, and recommend returning to Step 2 for code revision. Do not loop.

2. Present the implementation summary to the user:
   - List of files created with brief descriptions
   - Detected/chosen ecosystem and rationale
   - Execution commands (`execution_cmd`, `dry_run_cmd`)
   - Any deviations from the research plan and why
   - Known limitations or TODOs

### Step 5: Phase Gate

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
   Skill(
     skill: "codex:rescue",
     args: "--wait --model gpt-5.4 Review this research implementation for correctness, plan alignment, error handling, and dependency management. Focus on: {low_scoring_items}. Read and analyze the files at {output_dir}/plan/research_plan.md and all source files in {output_dir}/src/ matching the detected language (*.py, *.rs, *.jl, *.r, *.cpp, etc.)"
   )
   ```
   > **If `--claude-only`**: Per §SubagentExec — **B** (AC, code reviewer): Read research plan + source files. Review correctness, plan alignment, error handling, dependency management focusing on {low_scoring_items}. Return structured text.

3. **Go/No-Go synthesis**: Write a brief gate report with:
   - Confidence level and justification
   - Checklist scores (pass/partial/fail for each item)
   - Issues found (if any) and applied fixes
   - Go/No-Go decision

4. Save to `src/phase_gate.md`.

> If the gate returns **No-Go**, fix the identified issues before presenting to the user. Maximum 1 fix iteration.

### Step 6: User Review

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
