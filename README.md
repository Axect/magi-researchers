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
  <a href="#roadmap">Roadmap</a> &bull;
  <a href="CHANGELOG.md">Changelog</a>
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
| **1. Brainstorm** | Three models generate and cross-review ideas with expert personas | `brainstorm/` |
| **2. Plan** | Concrete research plan, stress-tested by a hostile reviewer | `plan/` |
| **3. Implement** | Claude writes code with live library doc lookups | `src/` |
| **4. Test & Visualize** | Collaborative test design + publication-quality plots | `tests/` + `plots/` |
| **5. Report** | Structured report with cross-verified claim-evidence integrity | `report.md` |

### New in v0.3.0

- **Weighted direction scoring** — Rank research ideas by novelty, feasibility, impact, rigor, and scalability with domain-tuned or custom weights
- **Dynamic persona casting** — Each model gets a topic-specific expert identity (e.g., *"Bayesian statistician with causal inference expertise"*), sharpening ideation
- **Adversarial debate** — At `--depth high`, models defend, concede, or revise on their top disagreements before synthesis
- **Murder board** — Gemini attacks the research plan as a hostile reviewer; Claude documents mitigations for every flaw found
- **Phase gates** — Automated quality checkpoints with conditional MAGI mini-review before each user approval step
- **Depth control** — `--depth low` for fast/cheap runs, `medium` (default) for standard review, `high` for full adversarial analysis

### Core Capabilities

- **Publication-quality plots** — `matplotlib` + `scienceplots` (Nature theme), PNG 300 dpi + vector PDF
- **MAGI traceability review** — All three models cross-verify the final report for orphaned claims and figures
- **Report gap detection** — Auto-generates missing visualizations from existing data
- **Domain templates** — Built-in context for Physics, AI/ML, Statistics, Mathematics, and Paper Writing
- **Journal strategy** — Venue recommendations for [Physics](docs/journal-strategies.md#particle-physics-phenomenology), [AI/ML](docs/journal-strategies.md#aiml-conferences--journals), and [Interdisciplinary](docs/journal-strategies.md#interdisciplinary-science-ml--natural-sciences) research
- **LaTeX math** — Proper inline and display equations across all outputs

<details>
<summary><strong>Under the hood</strong></summary>

- **Plot manifest** — Structured `plot_manifest.json` with metadata, section hints, and captions for automated report integration
- **Gemini fallback chain** — Resilient 3-tier model fallback: `gemini-3.1-pro-preview` → `gemini-3-pro-preview` → `gemini-2.5-pro`
- **Cross-phase artifact contracts** — Each phase validates incoming artifacts before running
- **Depth-controlled token budget** — `--depth low` skips cross-review for fast/cheap runs; `--depth high` enables full adversarial debate

</details>

## Usage

| Command | Description |
|:---|:---|
| `/magi-researchers:research "topic"` | Full pipeline (all 5 phases) |
| `/magi-researchers:research-brainstorm "topic"` | Brainstorming with cross-verification |
| `/magi-researchers:research-implement` | Implementation (needs existing plan) |
| `/magi-researchers:research-test` | Testing & visualization |
| `/magi-researchers:research-report` | Report generation |

### Flags

| Flag | Values | Default | Description |
|:---|:---|:---|:---|
| `--domain` | `physics` `ai_ml` `statistics` `mathematics` `paper` | auto-inferred | Research domain for context and weight defaults |
| `--weights` | JSON object | domain default | Custom scoring weights (keys: `novelty`, `feasibility`, `impact`, `rigor`, `scalability`) |
| `--depth` | `low` `medium` `high` | `medium` | Review thoroughness — controls cross-review and adversarial debate |

```bash
# Quick brainstorm with default settings
/magi-researchers:research "neural ODE solvers for stiff systems" --domain physics

# Deep analysis with custom weights and adversarial debate
/magi-researchers:research "causal inference in observational studies" --domain statistics --depth high --weights '{"novelty":0.2,"rigor":0.4,"feasibility":0.2,"impact":0.15,"scalability":0.05}'

# Fast ideation only (no cross-review, lowest cost)
/magi-researchers:research-brainstorm "transformer alternatives for long sequences" --domain ai_ml --depth low
```

### Output Structure

```
outputs/{topic_YYYYMMDD_vN}/
├── brainstorm/       # Personas, ideas, cross-reviews, debate, synthesis
├── plan/             # Research plan, murder board, mitigations, phase gate
├── src/              # Implementation
├── tests/            # Test suite
├── plots/            # PNG + PDF + plot_manifest.json
└── report.md         # Final structured report
```

<details>
<summary><strong>Full artifact tree</strong></summary>

```
brainstorm/
├── weights.json              # Scoring weights
├── personas.md               # Expert personas
├── gemini_ideas.md           # Gemini brainstorm
├── codex_ideas.md            # Codex brainstorm
├── gemini_review_of_codex.md # Cross-review (depth ≥ medium)
├── codex_review_of_gemini.md # Cross-review (depth ≥ medium)
├── debate_round2_gemini.md   # Adversarial debate (depth = high)
├── debate_round2_codex.md    # Adversarial debate (depth = high)
└── synthesis.md              # Weighted synthesis

plan/
├── research_plan.md          # Research plan
├── murder_board.md           # Plan stress-test
├── mitigations.md            # Flaw mitigations
└── phase_gate.md             # Plan quality gate
```

</details>

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

**Shipped:**&ensp; Multi-model brainstorming & cross-verification &bull; Domain & journal strategy templates &bull; Plot manifest & gap detection &bull; MAGI traceability review &bull; LaTeX math & Gemini fallback chain &bull; Weighted scoring & dynamic personas &bull; Adversarial debate &bull; Murder board & phase gates &bull; Depth-controlled token budget

**Up next:**
- [ ] Example artifact gallery — real research outputs to showcase the pipeline
- [ ] Terminal demo GIF — one-command walkthrough
- [ ] More domain & journal strategy templates
- [ ] Session resume — pick up interrupted pipelines mid-phase
- [ ] Cost estimation — token budget preview before execution

## Contributing

Contributions welcome — especially new domain templates. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
