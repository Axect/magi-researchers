# Phase 3a: MAGI Cross-Review Prompts

Full MCP call specifications for the two parallel review calls in Phase 3a.
Execute both calls **simultaneously**. Skip entire step if `--depth low`.

---

## Gemini (BALTHASAR) — Content Quality Review

```
mcp__gemini-cli__ask-gemini(
  prompt: "You are a rigorous academic reviewer evaluating a {mode} draft. Review for content quality, scientific rigor, and narrative coherence.

Evaluate each section on:
1. **Claim support**: Is every claim backed by evidence from the document? Flag unsupported assertions.
2. **Evidence integration**: Are figures and metrics discussed with concrete observations, not just mentioned?
3. **Narrative flow**: Does the argument build progressively? Are transitions smooth?
4. **Audience appropriateness**: Is the technical depth appropriate for the target audience ({audience})?
5. **Completeness**: Are there obvious gaps — important aspects of the topic not addressed?

For each issue found, specify:
- Section ID
- Issue type (unsupported_claim | weak_evidence | narrative_gap | audience_mismatch | missing_content)
- Severity (critical | major | minor)
- The specific text or gap
- A concrete fix suggestion

Also evaluate the **global argument thread**: Does the document successfully argue what it sets out to argue?

Draft:
@{source_dir}/write/draft.md

Section contracts:
@{source_dir}/write/section_contracts.json

Intake data:
@{source_dir}/write/write_inputs.json",
  model: "gemini-3.1-pro-preview"
)
```
Save to `write/gemini_review.md`.

---

## Codex (CASPER) — Structure & Evidence Review

```
mcp__codex-cli__ask-codex(
  prompt: "You are a meticulous technical editor evaluating a {mode} draft. Review for structural integrity, evidence completeness, and formatting quality.

Evaluate each section on:
1. **Word budget compliance**: Is each section within ±10% of its allocated word budget?
2. **Evidence completeness**: Are all evidence items from the section contract actually referenced in the text?
3. **Citation integrity**: Are all claims traceable to upstream artifacts? Flag any claims that appear fabricated.
4. **LaTeX correctness**: Are mathematical expressions properly formatted (inline `$...$` and display `$$` on separate lines)? **Flag any bare Unicode math symbols** in prose (`α`, `σ`, `π`, `²`, `≈`, `∈`, `ℝ`) — these must be replaced with LaTeX equivalents.
5. **Structural compliance**: Does the document follow the mode template's required section order?

For each issue found, specify:
- Section ID
- Issue type (budget_violation | missing_evidence | untraced_claim | latex_error | structural_error)
- Severity (critical | major | minor)
- The specific text or gap
- A concrete fix suggestion

Also check for **orphaned evidence**: items in write_inputs.json that are never referenced in the draft.

Draft:
@{source_dir}/write/draft.md

Section contracts:
@{source_dir}/write/section_contracts.json

Intake data:
@{source_dir}/write/write_inputs.json",
  model: "gpt-5.4"
)
```
Save to `write/codex_review.md`.

---

## Claude-Only Fallback

> Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD, Content Quality): Read draft.md, section_contracts.json, write_inputs.json. Review: claim support, evidence integration, narrative flow, audience fit ({audience}), completeness. Per issue: Section ID, type (`unsupported_claim`|`weak_evidence`|`narrative_gap`|`audience_mismatch`|`missing_content`), severity (critical/major/minor), specific text, concrete fix. Also evaluate: does the global argument thread hold? Save to `write/gemini_review.md`.
> - **B** (AC, Structure & Evidence): Read same 3 files. Review: word budget compliance (±10%), evidence completeness, citation integrity, LaTeX correctness (flag bare Unicode: α σ π ² ≈ ∈ ℝ), structural compliance. Per issue: Section ID, type (`budget_violation`|`missing_evidence`|`untraced_claim`|`latex_error`|`structural_error`), severity, text, fix. Also check for orphaned evidence in write_inputs.json. Save to `write/codex_review.md`.
