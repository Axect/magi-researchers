# CLAUDE.md

## Version Management

When bumping the version in `pyproject.toml`, the following files must also be updated to keep the plugin version in sync:

- `.claude-plugin/plugin.json` — `"version"` field
- `.claude-plugin/marketplace.json` — `"version"` field inside the `plugins` array

Claude Code reads the version from these JSON files, not from `pyproject.toml`. Forgetting to update them causes the marketplace to show a stale version.
