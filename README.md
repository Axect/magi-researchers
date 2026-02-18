# Claude Researchers

A research agent workflow for Physics, AI/ML, and other scientific domains, powered by Claude Code's native skill and agent system.

## How It Works

This workflow orchestrates multiple AI models (Claude, Gemini, Codex) through a structured research pipeline:

1. **Brainstorming** — Gemini and Codex independently generate ideas, then cross-check each other's work
2. **Planning** — Claude synthesizes all inputs into a concrete research plan
3. **Implementation** — Claude Code writes the research code
4. **Testing & Visualization** — Tests are designed collaboratively; plots use publication-quality styling
5. **Reporting** — A structured markdown report captures the entire research process

## Quick Start

### Setup
```bash
# Install dependencies
uv sync
```

### Run Full Pipeline
```
/research "your research topic" --domain physics
```

### Run Individual Phases
```
/research-brainstorm "topic"   # Brainstorming only
/research-implement            # Implementation (needs existing plan)
/research-test                 # Testing & visualization
/research-report               # Report generation
```

## Output

All outputs are saved to `outputs/{topic_YYYYMMDD}/` with structured subdirectories for brainstorming records, plans, source code, tests, plots, and the final report.

## Visualization

Plots use `matplotlib` with `scienceplots` for publication-quality styling (`science` + `nature` themes). All plots are saved as both PNG (300 dpi) and PDF.

## Domain Templates

Domain-specific context templates guide the AI models:
- `templates/domains/physics.md` — Physical intuition, dimensional analysis, conservation laws
- `templates/domains/ai_ml.md` — Benchmarks, ablation studies, reproducibility

## Requirements

- Python >= 3.11
- Claude Code with MCP servers configured (Gemini, Codex, Context7)
