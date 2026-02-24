<p align="center">
  <img src="MAGI.drawio.png" width="600" alt="MAGI Architecture" />
</p>

<h1 align="center">MAGI Researchers</h1>

<p align="center">
  <strong>Three AI models. One synthesis.</strong><br/>
  <em>Multi-model research pipeline for Claude Code — orchestrating Claude, Gemini, and Codex</em>
</p>

<p align="center">
  <a href="https://github.com/Axect/magi-researchers/stargazers"><img src="https://img.shields.io/github/stars/Axect/magi-researchers?style=social" alt="GitHub Stars" /></a>&nbsp;
  <img src="https://img.shields.io/badge/claude--code-plugin-blueviolet" alt="Claude Code Plugin" />&nbsp;
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+" />&nbsp;
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT" />&nbsp;
  <a href="https://github.com/Axect/magi-researchers/issues"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome" /></a>
</p>

<p align="center">
  <a href="#get-started">Get Started</a> &bull;
  <a href="#why-magi">Why MAGI?</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#usage">Usage</a> &bull;
  <a href="#roadmap">Roadmap</a>
</p>

---

> *Like the MAGI system in Evangelion — three supercomputers cross-verifying each other — this plugin orchestrates Claude, Gemini, and Codex for rigorous, multi-perspective research.*

## Get Started

**Prerequisites:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) + Python 3.11+ with [uv](https://docs.astral.sh/uv/)

**1. Install the plugin** (inside Claude Code):
```
/plugin marketplace add Axect/magi-researchers
/plugin install magi-researchers@magi-researchers-marketplace
```

**2. Set up MCP servers** (one-time):
```bash
claude mcp add -s user gemini-cli -- npx -y gemini-mcp-tool
claude mcp add -s user codex-cli -- npx -y @cexll/codex-mcp-server
claude mcp add -s user context7 -- npx -y @upstash/context7-mcp@latest
```

**3. Run your first research:**
```
/magi-researchers:research "your research topic" --domain physics
```

MAGI generates cross-verified hypotheses, writes implementation code, renders publication-quality plots, and synthesizes a structured report — all saved to `outputs/{topic}/`.

<details>
<summary><strong>Alternative: Local Development</strong></summary>

```bash
git clone https://github.com/Axect/magi-researchers.git
claude --plugin-dir /path/to/magi-researchers
uv add matplotlib SciencePlots numpy
```
</details>

## Why MAGI?

Single-model research has blind spots. One model hallucinates a citation or misses a critical constraint — and nobody catches it.

| | **Single Model** | **MAGI (3 Models)** |
|:---|:---|:---|
| **Brainstorming** | One perspective | Three independent perspectives |
| **Verification** | Self-review (unreliable) | Cross-model peer review |
| **Blind spots** | Undetected | Caught by competing models |
| **Output** | Raw text | Structured report with consensus & divergence analysis |

- **Claude (MELCHIOR)** — *The Scientist.* Synthesis, planning, implementation, report generation.
- **Gemini (BALTHASAR)** — *The Critic.* Creative brainstorming, cross-verification, broad knowledge.
- **Codex (CASPER)** — *The Builder.* Feasibility analysis, code review, implementation focus.

## Features

### Research Pipeline

| Phase | What Happens | Output |
|:---|:---|:---|
| **1. Brainstorm** | Gemini + Codex independently generate ideas, then cross-review | 5 brainstorm documents |
| **2. Plan** | Claude synthesizes into a concrete research plan | `research_plan.md` |
| **3. Implement** | Claude writes code with Context7 library lookups | `src/` |
| **4. Test & Visualize** | Collaborative test design + publication-quality plots | `tests/` + `plots/` |
| **5. Report** | Manifest-driven report with MAGI traceability review | `report.md` |

### Key Capabilities

- **Publication-quality plots** — `matplotlib` + `scienceplots` (`science` + `nature` themes), saved as PNG (300 dpi) + vector PDF
- **LaTeX math formatting** — Proper inline `$...$` and display equations in all output documents
- **Report gap detection** — Identifies claims without supporting figures, generates new plots on the fly
- **MAGI traceability review** — All three models cross-verify the final report for orphaned claims/plots
- **Domain templates** — Built-in context for Physics, AI/ML, Statistics, Mathematics, and Paper Writing
- **Journal strategy** — Venue recommendations for [Physics](docs/journal-strategies.md#particle-physics-phenomenology), [AI/ML](docs/journal-strategies.md#aiml-conferences--journals), and [Interdisciplinary](docs/journal-strategies.md#interdisciplinary-science-ml--natural-sciences) research

<details>
<summary><strong>Under the hood</strong></summary>

- **Plot manifest** — Structured `plot_manifest.json` with metadata, section hints, and captions for automated report integration
- **Gemini fallback chain** — Resilient 3-tier model fallback: `gemini-3.1-pro-preview` → `gemini-3-pro-preview` → `gemini-2.5-pro`
- **Cross-phase artifact contracts** — Each phase validates incoming artifacts before running

</details>

## Usage

| Command | Description |
|:---|:---|
| `/magi-researchers:research "topic"` | Full pipeline (all 5 phases) |
| `/magi-researchers:research-brainstorm "topic"` | Brainstorming with cross-verification |
| `/magi-researchers:research-implement` | Implementation (needs existing plan) |
| `/magi-researchers:research-test` | Testing & visualization |
| `/magi-researchers:research-report` | Report generation |

### Output Structure

```
outputs/{topic_YYYYMMDD_vN}/
├── brainstorm/          # 5 cross-verified brainstorm documents
├── plan/                # Research plan
├── src/                 # Implementation
├── tests/               # Test suite
├── plots/               # PNG + PDF + plot_manifest.json
└── report.md            # Final structured report
```

<details>
<summary><strong>Recommended Permissions</strong></summary>

Add to `.claude/settings.local.json`:

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

</details>

## Roadmap

- [x] Multi-model brainstorming with cross-verification
- [x] Domain templates & journal strategy templates
- [x] Plot manifest, report gap detection & MAGI traceability review
- [x] LaTeX math formatting & Gemini fallback chain
- [ ] Example artifact gallery
- [ ] Terminal demo GIF
- [ ] More domain & journal strategy templates

## Contributing

Contributions welcome — especially new domain templates. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
