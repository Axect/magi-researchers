# MAGI Researchers

**Three AI models. One synthesis.**

> *Like the MAGI system in Evangelion — three supercomputers cross-verifying each other to reach a unified decision — this plugin orchestrates Claude, Gemini, and Codex to conduct rigorous, multi-perspective research.*

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Claude Code](https://img.shields.io/badge/claude--code-plugin-blueviolet)

---

## Why MAGI?

- **Cross-verification by design** — Three independent AI models brainstorm, review each other's work, and synthesize results. No single-model blind spots.
- **Publication-ready outputs** — Structured reports, test suites, and `scienceplots`-styled figures in one pipeline.
- **Domain-aware** — Built-in templates for physics, AI/ML, statistics, mathematics, and paper writing — extensible to any scientific domain.

## Architecture

![MAGI Architecture](MAGI.drawio.png)

## Installation

### Option 1: Marketplace Install (Recommended)

Run these commands inside Claude Code (no manual clone needed):

```
/plugin marketplace add Axect/magi-researchers
/plugin install magi-researchers@magi-researchers-marketplace
```

### Option 2: Local Plugin Directory (Development)

For plugin development or testing:

```bash
git clone https://github.com/Axect/magi-researchers.git
claude --plugin-dir /path/to/magi-researchers
```

## Prerequisites

- **Python >= 3.11**
- **[uv](https://docs.astral.sh/uv/)** — Python package manager
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** — Anthropic CLI

### MCP Servers (Required)

This plugin requires three MCP servers configured in your Claude Code environment.

#### Project Scope (default)

Servers are stored in the current project's `.mcp.json` and available only within that project:

```bash
# Gemini CLI — cross-model brainstorming and review
claude mcp add gemini-cli -- npx -y gemini-mcp-tool

# Codex CLI — independent analysis and ideation
claude mcp add codex-cli -- npx -y @cexll/codex-mcp-server

# Context7 — library documentation lookup
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

#### User Scope

Servers are stored in `~/.claude/settings.json` and available across **all** your projects:

```bash
# Gemini CLI — cross-model brainstorming and review
claude mcp add -s user gemini-cli -- npx -y gemini-mcp-tool

# Codex CLI — independent analysis and ideation
claude mcp add -s user codex-cli -- npx -y @cexll/codex-mcp-server

# Context7 — library documentation lookup
claude mcp add -s user context7 -- npx -y @upstash/context7-mcp@latest
```

> **Tip:** Use user scope (`-s user`) if you plan to use MAGI across multiple projects. Use project scope (default) if you want to keep MCP configurations isolated per project.

### Python Dependencies

```bash
uv add matplotlib SciencePlots numpy
```

## Usage

### Full Research Pipeline

```
/magi-researchers:research "your research topic" --domain physics
```

This runs the complete pipeline:
1. **Brainstorming** — Gemini and Codex independently generate ideas, then cross-check each other
2. **Planning** — Claude synthesizes inputs into a concrete research plan
3. **Implementation** — Claude Code writes the research code
4. **Testing & Visualization** — Tests designed collaboratively; publication-quality plots
5. **Reporting** — Structured markdown report of the entire process

### Individual Phase Skills

```
/magi-researchers:research-brainstorm "topic"   # Brainstorming only
/magi-researchers:research-implement             # Implementation (needs existing plan)
/magi-researchers:research-test                  # Testing & visualization
/magi-researchers:research-report                # Report generation
```

## Output Structure

All outputs are saved to `outputs/{topic_YYYYMMDD_vN}/`:

```
outputs/{topic_YYYYMMDD_vN}/
├── brainstorm/          # Phase 1: 5 brainstorm documents
├── plan/                # Phase 2: research plan
├── src/                 # Phase 3: implementation code
├── tests/               # Phase 4: test code
├── plots/               # Phase 4: PNG (300 dpi) + PDF plots
└── report.md            # Phase 5: final report
```

## Visualization

Plots use `matplotlib` with `scienceplots` for publication-quality styling (`science` + `nature` themes). All plots are saved as both PNG (300 dpi) and PDF.

## Domain Templates

Domain-specific context templates guide the AI models:
- `templates/domains/physics.md` — Physical intuition, dimensional analysis, conservation laws
- `templates/domains/ai_ml.md` — Benchmarks, ablation studies, reproducibility
- `templates/domains/statistics.md` — Statistical inference, assumption checking, effect sizes
- `templates/domains/mathematics.md` — Logical rigor, proof structure, symbolic computation
- `templates/domains/paper.md` — Academic writing, claim-evidence structure, citation integrity

## Recommended Permissions

Add to your project's `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(uv:*)",
      "Bash(uv run:*)",
      "Bash(uv run python3:*)",
      "Bash(uv add:*)",
      "Bash(uv sync:*)",
      "Bash(mkdir:*)",
      "mcp__gemini-cli__ask-gemini",
      "mcp__gemini-cli__brainstorm",
      "mcp__codex-cli__ask-codex",
      "mcp__codex-cli__brainstorm",
      "mcp__plugin_context7_context7__resolve-library-id",
      "mcp__plugin_context7_context7__query-docs"
    ]
  }
}
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing domain templates, reporting bugs, and submitting pull requests.

## License

MIT
