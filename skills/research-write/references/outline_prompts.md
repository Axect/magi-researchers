# Phase 1b: MAGI Parallel Outline Prompts

Full MCP call specifications for the two parallel outline generation calls in Phase 1b.
Execute both calls **simultaneously**.

---

## Gemini (BALTHASAR) — Creative Outline

```
mcp__gemini-cli__ask-gemini(
  prompt: "You are an expert academic writer creating a document outline. Your approach emphasizes narrative flow, creative framing, and reader engagement.

Given:
- Mode: {mode} (see template for required sections)
- Audience: {audience}
- Domain: {domain}
- Tone: {tone}, Formality: {formality}

For each section defined in the mode template, produce:
1. **Section ID** (from template)
2. **Title** (descriptive, audience-appropriate)
3. **Purpose** (1-2 sentences: what this section accomplishes)
4. **Narrative role** (from template, plus your interpretation of how it serves the global argument)
5. **Key points** (3-5 bullet points of content to cover)
6. **Evidence to include** (specific evidence IDs from write_inputs.json)
7. **Estimated words** (within the template's max_words budget)
8. **Transition from previous section** (1 sentence describing how this section connects to the one before it)

Also define the **global argument thread**: a 2-3 sentence summary of the paper's narrative arc — the logical thread connecting all sections from motivation to conclusion.

Mode template:
@{source_dir}/write/mode_template_cache.md

Upstream intake:
@{source_dir}/write/write_inputs.json

Citation ledger:
@{source_dir}/write/citation_ledger.json",
  model: "gemini-3.1-pro-preview",
  search: true
)
```
Save to `write/gemini_outline.md`.

---

## Codex (CASPER) — Structural Outline

```
mcp__codex-cli__ask-codex(
  prompt: "You are an expert academic writer creating a document outline. Your approach emphasizes logical structure, evidence coverage, and completeness.

Given:
- Mode: {mode} (see template for required sections)
- Audience: {audience}
- Domain: {domain}
- Tone: {tone}, Formality: {formality}

For each section defined in the mode template, produce:
1. **Section ID** (from template)
2. **Title** (descriptive, audience-appropriate)
3. **Purpose** (1-2 sentences: what this section accomplishes)
4. **Narrative role** (from template, plus your interpretation of how it serves the global argument)
5. **Key points** (3-5 bullet points of content to cover)
6. **Evidence to include** (specific evidence IDs from write_inputs.json)
7. **Estimated words** (within the template's max_words budget)
8. **Transition from previous section** (1 sentence describing how this section connects to the one before it)

Also define the **global argument thread**: a 2-3 sentence summary of the paper's narrative arc — the logical thread connecting all sections from motivation to conclusion.

Focus especially on:
- Evidence coverage: every high-confidence claim should appear in at least one section
- No orphaned evidence: every evidence item should be referenced by at least one section
- Structural completeness: all required sections are present with adequate depth

Mode template:
@{source_dir}/write/mode_template_cache.md

Upstream intake:
@{source_dir}/write/write_inputs.json

Citation ledger:
@{source_dir}/write/citation_ledger.json",
  model: "gpt-5.4",
  search: true
)
```
Save to `write/codex_outline.md`.

---

## Claude-Only Fallback

> Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD, Creative Outline): Read mode template, write_inputs.json, citation_ledger.json. Per section from template: 1.Section ID, 2.Title, 3.Purpose (1-2 sentences), 4.Narrative role, 5.Key points (3-5), 6.Evidence IDs from write_inputs, 7.Estimated words (within template budget), 8.Transition from previous. Plus: global argument thread (2-3 sentence narrative arc). Emphasize narrative flow and engagement. Save to `write/gemini_outline.md`.
> - **B** (AC, Structural Outline): Read same 3 files. Same 8-field per-section structure + global argument thread. Focus: every high-confidence claim in ≥1 section, no orphaned evidence, all required sections present with adequate depth. Save to `write/codex_outline.md`.
