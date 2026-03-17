# Shared Rules

> All SKILL files reference these §-anchored sections. Read this file before executing any skill.

## §MCP

**Gemini fallback chain** (try each in order; on error/timeout/model-not-found, try next):
1. `model: "gemini-3.1-pro-preview"` (preferred)
2. `model: "gemini-2.5-pro"` (fallback)
3. Claude (last resort — skip Gemini MCP tool, use Claude directly)

**Codex**: Use `model: "gpt-5.4"` for all Codex MCP calls. If Codex fails 2+ times, fall back to Claude directly.

**File References**: Use `@filepath` in the prompt parameter to pass saved artifacts instead of pasting file content inline. The CLI tools read files directly, preventing context truncation.

**Context7**: Use `mcp__plugin_context7_context7__query-docs` for library documentation lookups. Call `resolve-library-id` first to get the library ID.

**Web Search**: Use web search freely whenever factual verification, recent developments, or literature context would strengthen the analysis:
- **Claude**: Use the `WebSearch` tool directly
- **Gemini**: Add `search: true` to `mcp__gemini-cli__ask-gemini` or `mcp__gemini-cli__brainstorm` calls
- **Codex**: Add `search: true` to `mcp__codex-cli__ask-codex` or `mcp__codex-cli__brainstorm` calls
- **Claude-only mode**: Claude Agent subagents cannot use WebSearch. The main Claude agent should search beforehand and include findings in the subagent prompt.

---

## §Visualization

Use `matplotlib` with `scienceplots` (`['science', 'nature']` style). Save plots as PNG (300 dpi) and PDF.

> **IMPORTANT:** All figures MUST use `scienceplots` with `['science', 'nature']` style. If existing plots were generated without this style, they must be regenerated before inclusion. Do NOT use manual `plt.rcParams` overrides — they conflict with scienceplots defaults.
>
> **Technical note (`text.usetex`):** `['science', 'nature']` enables `text.usetex=True`. All plot text (axis labels, annotations, titles, legends) must be ASCII or LaTeX-escaped. Unicode characters (`π`, `²`, `⁴`, `≈`) cause `RuntimeError`. Use `r'$\pi$'`, `r'$^2$'`, `r'$^4$'`, `r'$\approx$'` instead. Always test plot generation before committing.
>
> **Figure sizing:** Use Nature column widths — single column: 3.5 in, double column: 7.2 in.

---

## §LaTeX

> **Hard requirement:** All mathematical expressions must use LaTeX (`$...$` for inline, `$$...$$` for display). Unicode math symbols (`σ₁`, `π₁`, `ℝ`, `∈`, `≈`, `²`, etc.) are **NOT acceptable**. Always use LaTeX equivalents: `$\sigma_1$`, `$\pi_1$`, `$\mathbb{R}$`, `$\in$`, `$\approx$`, `$^2$`.

- **Inline math**: `$...$` for short expressions (e.g., `$\alpha = 0.05$`, `$O(n \log n)$`)
- **Display equations**: `$$` on its own line, equation on a separate line:
  ```
  $$
  equation
  $$
  ```
- Never write display equations inline as `$$..equation..$$` on a single line
- Use display equations for: key formulas, derivations, loss functions, objective functions, main results
- Use inline math for: variable names, parameter values, complexity notation, short expressions
- Include this formatting instruction in prompts to Gemini and Codex when mathematical content is involved

---

## §Claude-Only

When `--claude-only` is active, **all** Gemini/Codex MCP tool calls are replaced with Claude Agent subagents (`subagent_type: general-purpose`):

| Original Call | Replacement | Cognitive Style |
|---|---|---|
| `mcp__gemini-cli__ask-gemini` / `brainstorm` | Agent subagent A | **Creative-Divergent** (CD): unconventional connections, "What if?" scenarios, wide exploration, questioning assumptions |
| `mcp__codex-cli__ask-codex` / `brainstorm` | Agent subagent B | **Analytical-Convergent** (AC): step-by-step feasibility, established methodologies, deep evaluation, practical constraints, risk assessment |

**Key rules:**
1. **File access**: Subagents use the `Read` tool (no `@filepath` syntax).
2. **Output filenames**: Keep original names (`gemini_*.md`, `codex_*.md`) — add header `> Source: Claude Agent subagent (claude-only mode, {style})`.
3. **Independence**: Both subagents are spawned simultaneously so neither sees the other's output.
4. **`--depth max` internal subagents**: Within each persona's mini-MAGI pipeline, use **Expansive Explorer** (replaces Gemini) and **Grounded Builder** (replaces Codex) cognitive styles.

---

## §Substitute

> Every `> **If --claude-only**:` block also applies when the relevant agent is substituted via `--substitute "Agent -> Opus"`. When only one agent is substituted, apply replacement only to that agent's call; the non-substituted agent uses its MCP tool normally.

- `--substitute` and `--claude-only` are mutually exclusive (`--claude-only` takes precedence).
- If both agents are substituted, treat as `--claude-only`.

---

## §SubagentExec

When constructing a `--claude-only` Agent subagent replacement, follow this template:

1. **Assign cognitive style** — Creative-Divergent (CD) for Gemini replacements; Analytical-Convergent (AC) for Codex replacements; Adversarial-Critical for murder board / hostile reviewer calls.
2. **List files to read** — `Use the Read tool to read: {file_list}` (one file per line).
3. **State the task** — the same core prompt as the MCP call, adapted for the Agent format.
4. **Specify output** — `Save to {path}. Start with: > Source: Claude Agent subagent (claude-only mode, {style})` OR `Return structured text — do not save to a file.`
5. **Spawn simultaneously** — A (CD) and B (AC) in the same message.
6. **Persona injection** — If `personas.md` exists, prepend the assigned persona to each subagent prompt.

---

## §PhaseGate

Phase gates are lightweight quality checkpoints before each USER CHECKPOINT:

1. **Self-assessment**: Evaluate phase output against the phase-specific checklist; assign confidence: `High`, `Medium`, or `Low`.
2. **Conditional MAGI mini-review** (if `Medium` or `Low`): Send output to one MAGI model (Gemini for scientific/plan quality, Codex for implementation/test quality). **If `--claude-only` or the relevant agent is substituted**: use a Claude Agent subagent per §SubagentExec (CD for Gemini substitute, AC for Codex substitute).
3. **Go/No-Go synthesis**: Write gate report — confidence, checklist scores (pass/partial/fail), issues found, fixes applied, Go/No-Go decision.
4. Save to `{phase_dir}/phase_gate.md`.

> If **No-Go**: fix issues before presenting to user. Maximum 1 fix iteration per gate.
