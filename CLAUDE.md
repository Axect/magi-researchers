# Claude Researchers — Project Conventions

## Overview

This project provides a research agent workflow powered by Claude Code skills and agents.
Use `/research` to run the full pipeline, or individual phase skills (`/research-brainstorm`, `/research-implement`, `/research-test`, `/research-report`) independently.

## Research Workflow

### Full Pipeline
```
/research "연구 주제" [--domain physics|ai_ml]
```

### Individual Phases
```
/research-brainstorm "주제"    # Phase 1: Brainstorming (Gemini + Codex cross-check)
/research-implement            # Phase 3: Implementation (requires research_plan.md)
/research-test                 # Phase 4: Testing & Visualization
/research-report               # Phase 5: Final Report
```

## MCP Tool Rules

- **Gemini**: Always pass `model: "gemini-3-pro-preview"` explicitly. Never omit or use other model IDs.
- **Codex**: Use `mcp__codex-cli__ask-codex` for analysis, `mcp__codex-cli__brainstorm` for ideation.
- **Context7**: Use for library documentation lookups during implementation.

## Output Directory Structure

All research outputs go under `outputs/{topic_YYYYMMDD}/`:
```
outputs/{topic_YYYYMMDD}/
├── brainstorm/          # Phase 1 outputs (5 files)
├── plan/                # Phase 2 research plan
├── src/                 # Phase 3 implementation code
├── tests/               # Phase 4 test code
├── plots/               # Phase 4 visualizations (PNG + PDF)
└── report.md            # Phase 5 final report
```

## Visualization Rules

- Always use `matplotlib` with `scienceplots` package.
- Apply `plt.style.use(['science', 'nature'])` for all plots.
- Save plots in both PNG (300 dpi) and PDF formats.
- Place all plots in `plots/` subdirectory of the output.

## Code Conventions

- Use `uv` for Python dependency management and script execution.
- Implementation language/framework is flexible per research needs.
- Modularize code in `src/` with clear separation of concerns.
- Tests go in `tests/` with descriptive names.

## Domain Templates

Domain-specific prompts are in `templates/domains/`:
- `physics.md` — Physical intuition, dimensional analysis, conservation laws
- `ai_ml.md` — Benchmarks, ablation studies, reproducibility

## Cross-Check Protocol

During brainstorming (Phase 1):
1. Gemini and Codex brainstorm independently (parallel)
2. Each reviews the other's output (cross-check)
3. Claude synthesizes all 4 documents into a unified direction
4. User confirms/adjusts before proceeding
