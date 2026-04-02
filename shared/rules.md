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

## §SchemaValidation

At each phase transition, validate all JSON artifacts produced by the completing phase against their schemas using `utils/validate_schema.py`:

```bash
uv run python utils/validate_schema.py {output_dir}
```

**Auto-detected artifacts**: `weights.json`, `plot_manifest.json`, `execution_manifest.json`, `report_versions.json`, `write_inputs.json`, `citation_ledger.json`, `section_contracts.json`, `*_checkpoint.json`.

**Rules:**
1. Run validation **after** a phase writes its artifacts and **before** presenting the phase checkpoint to the user.
2. If validation **fails**: fix the malformed artifact(s) and re-validate. Maximum 1 fix iteration.
3. If validation **passes**: proceed to the user checkpoint. No action needed.
4. For artifacts not auto-detected (custom JSON files): skip validation — only schema-mapped artifacts are checked.
5. Use `--json` flag when capturing results programmatically: `uv run python utils/validate_schema.py --json {output_dir}`.

---

## §AntiConsensus

LLM agents are biased toward agreement. The following rules counteract premature consensus, evidence-free concessions, and forced hybrid compromises.

**Rule 1 — Agreement costs evidence.** When a reviewer agrees with a claim from another model, the reviewer MUST provide at least one piece of independent supporting evidence — a different reasoning path, a different source, or a concrete scenario — that the original proponent did not cite. "I agree because it seems reasonable" is not permitted. If no independent evidence can be found, use the INSUFFICIENT verdict instead.

**Rule 2 — Concessions require a named defeater.** In the DCR debate framework, a Concede MUST name the specific evidence or logical step from the opponent that defeated the original position. If the conceding party cannot articulate what changed their mind, the concession is invalid — revert to Defend or acknowledge the topic as unresolved. "The opponent makes a fair point" without specifics is capitulation, not concession.

**Rule 3 — Hybrid proposals carry burden of proof.** Any "hybrid," "combined," or "best-of-both-worlds" proposal must independently justify itself: (a) a concrete scenario where the hybrid outperforms each pure approach, (b) a concrete scenario where the hybrid underperforms, and (c) a mechanism explaining the synergy beyond "A's strength + B's strength." If these cannot be provided, the hybrid must be withdrawn in favor of one pure position.

**Rule 4 — False consensus is classified and penalized.** During Convergence Interrogation, agreements where neither model provides concrete mechanism, independent evidence, or a specific supporting scenario are classified as **Type C convergence (False Consensus)**. Type C findings have their confidence automatically downgraded one level. If a Type C finding reaches the Top 3 in synthesis, MELCHIOR must construct an adversarial objection against it.

**Rule 5 — Unresolved disagreements are preserved.** It is better to report a genuine disagreement than to manufacture false consensus. Disagreements where neither side has sufficient evidence to prevail should be recorded as "**Unresolved — insufficient evidence on both sides**" and presented to the user as open questions, not papered over with compromises.

---

## §PhaseGate

Phase gates are lightweight quality checkpoints before each USER CHECKPOINT:

1. **Self-assessment**: Evaluate phase output against the phase-specific checklist; assign confidence: `High`, `Medium`, or `Low`.
2. **Conditional MAGI mini-review** (if `Medium` or `Low`): Send output to one MAGI model (Gemini for scientific/plan quality, Codex for implementation/test quality). **If `--claude-only` or the relevant agent is substituted**: use a Claude Agent subagent per §SubagentExec (CD for Gemini substitute, AC for Codex substitute).
3. **Go/No-Go synthesis**: Write gate report — confidence, checklist scores (pass/partial/fail), issues found, fixes applied, Go/No-Go decision.
4. Save to `{phase_dir}/phase_gate.md`.

> If **No-Go**: fix issues before presenting to user. Maximum 1 fix iteration per gate.

---

## §PreFlight

Pre-flight context gathering runs at `--depth medium`, `--depth high`, `--depth max`, and `--depth auto` (skip for `--depth low`). It provides grounded evidence before brainstorming, with **persona-specific filtering** to prevent premature consensus.

**Evidence sources** (run in parallel):

1. **OpenAlex** (academic literature) — via WebFetch:
   ```
   WebFetch(
     url: "https://api.openalex.org/works?search={url_encoded_topic}&sort=cited_by_count:desc&per-page=10&filter=publication_year:>2021,type:journal-article|proceedings-article&select=id,title,authorships,publication_year,cited_by_count,doi,abstract_inverted_index",
     prompt: "Extract for each paper: title, first author, year, citation count, DOI, and reconstruct the first 2 sentences of abstract from the inverted index."
   )
   ```
   If results are sparse (< 3 papers), retry with broader keywords (drop domain-specific jargon, keep core concept).
2. **WebSearch** (recent developments) — `WebSearch(query: "{topic} recent advances 2024 2025 2026")`

**Source cap**: 10 papers from OpenAlex + 5 web sources = 15 total max.

**Validation**: `preflight_context.md` must contain at least 3 references before creating briefings. If OpenAlex returns 0 results but WebSearch has results, create briefings from web results only (note reduced quality). If both return nothing, skip briefing creation and proceed without literature grounding.

**`--claude-only` note**: All WebFetch and WebSearch calls are made by the main agent. Subagents cannot use these tools.

**Persona-aware briefing**: From the raw context, create filtered views per persona. Each briefing emphasizes what matters to that persona's reasoning mandate — the same evidence, differently framed. This prevents all models from anchoring on the same narrative.

| Persona Role | Briefing Focus | Filter Question |
|---|---|---|
| Gemini persona (Critic/Creative) | Failure cases, counterexamples, methodological pitfalls, unexplored alternatives | "What has gone wrong in this space, and what hasn't been tried?" |
| Codex persona (Builder/Practitioner) | Implementations, tools/datasets, benchmarks, computational constraints | "What exists to build on, and what are the practical constraints?" |
| Claude/MELCHIOR | Full unfiltered context | (receives `preflight_context.md` directly during synthesis) |

For `--depth max` with N personas: create per-persona briefings (`briefing_persona_{i}.md`) filtered by each persona's declared expertise and guiding question. For `--claude-only` with 2-model pipeline: use `briefing_subagent_a.md` / `briefing_subagent_b.md`.

---

## §EvidenceAnchoring

Evidence anchoring runs at `--depth high`, `--depth max`, or when `--depth auto` escalates to high/deep (skip for `--depth low|medium`). It targets only **disputed claims** — ideas that received DISAGREE or INSUFFICIENT verdicts during cross-review.

**Purpose**: Ground the DCR debate in real evidence rather than model-internal knowledge alone. This strengthens §AntiConsensus Rule 1 (agreement costs evidence) and Rule 2 (concessions require a named defeater) by providing external evidence that can serve as defeaters or independent support.

**Scope limits**:
- Maximum **5 disputed claims** investigated (prioritize: DISAGREE over INSUFFICIENT; higher-ranked ideas first)
- Maximum **5 OpenAlex results + 3 web results** per claim
- If no relevant evidence found: record "No direct evidence found — dispute remains empirical"

**Evidence classification**: For each disputed claim, evidence is classified as:
- **Supporting** — directly supports the disputed mechanism or prediction
- **Contradicting** — directly contradicts or provides a counterexample
- **Tangential** — related but not directly addressing the claim

**Standard path** (`--depth high` or escalated `auto`): Evidence is saved to `brainstorm/claim_evidence.md` and passed as `@`-reference to T3 DCR debate calls, enabling models to cite real papers when they Defend, Concede, or Revise.

**`--depth max` path** (meta-level): Evidence anchoring runs at Layer 2 as Phase B+ in Step 1-max-c, targeting the **top 3 cross-persona disagreements** from `meta_disagreements.md` (not individual T2 verdicts). Results are saved to `brainstorm/meta_claim_evidence.md` and fed into the Layer 2 adversarial debate. The same scope limits and evidence classification apply. MELCHIOR reads `meta_claim_evidence.md` during Step 1-max-d synthesis.

**`--claude-only` note**: All WebFetch and WebSearch calls for evidence gathering are made by the main agent (subagents cannot use these tools). Complete evidence gathering before passing results to debate calls.

---
