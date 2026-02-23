# Contributing to MAGI Researchers

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Axect/magi-researchers.git
   cd magi-researchers
   ```

2. Install dependencies with [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```

3. Set up MCP servers for Claude Code (see [README.md](README.md#mcp-servers-required)).

4. Run the plugin locally:
   ```bash
   claude --plugin-dir .
   ```

## Ways to Contribute

### Domain Templates

One of the most impactful contributions is adding domain templates. Create a new markdown file in `templates/domains/`:

```
templates/domains/your_domain.md
```

Follow the structure of existing templates (`physics.md`, `ai_ml.md`, `statistics.md`, `mathematics.md`, `paper.md`) — include domain-specific guidance for brainstorming, implementation, and evaluation.

### Bug Reports

Found a bug? [Open an issue](https://github.com/Axect/magi-researchers/issues/new?template=bug_report.md) with:
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS, Claude Code version)

### Feature Requests

Have an idea? [Open a feature request](https://github.com/Axect/magi-researchers/issues/new?template=feature_request.md) describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

### Code Contributions

1. Fork the repository
2. Create a feature branch from `dev`:
   ```bash
   git checkout dev
   git checkout -b feature/your-feature
   ```
3. Make your changes
4. Test locally with `claude --plugin-dir .`
5. Submit a pull request to the `dev` branch

## Pull Request Guidelines

- Target the `dev` branch (not `main`)
- Keep changes focused — one feature or fix per PR
- Update documentation if your change affects usage
- Add or update domain templates if applicable
- Describe what your PR does and why

## Project Structure

```
magi-researchers/
├── .claude-plugin/       # Plugin metadata
├── agents/               # Agent definitions
├── magi_researchers/     # Python package
├── skills/               # Skill definitions (phases)
├── templates/            # Domain & report templates
└── outputs/              # Generated research outputs
```

## Code Style

- Python: Follow existing conventions in the codebase
- Markdown: Use ATX-style headers, fenced code blocks
- YAML/JSON: Preserve full decimal precision for numeric values

## Questions?

Open a [discussion](https://github.com/Axect/magi-researchers/discussions) or reach out via issues.
