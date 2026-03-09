# Research Write Skill

## Description
Orchestrates multi-agent collaborative writing from upstream research artifacts. Produces structured documents (papers, proposals) with evidence-grounded prose, MAGI cross-review, and automated quality validation.

## Usage
```
/research-write --source <output_dir> [--mode paper|proposal] [--audience general-public|high-school|undergraduate|phd-student|researcher|expert|"free text"] [--depth low|medium|high] [--claude-only] [--resume <write_dir>]
```

## Arguments
- `$ARGUMENTS` — Required and optional flags:
  - `--source <output_dir>` — Path to an upstream research output directory containing artifacts from `/research`, `/research-brainstorm`, `/research-explain`, or `/research-report`. Required unless `--resume` is provided.
  - `--mode` — Writing mode (default: `paper`):
    - `paper` — Academic research paper with standard structure (abstract, introduction, methodology, experiments, results, discussion, limitations, conclusion, references)
    - `proposal` — Grant or funding proposal with persuasive structure (executive summary, problem statement, proposed approach, preliminary results, timeline, budget, broader impact, references)
  - `--audience` — Target audience (default: `researcher`):
    - `general-public` — No assumed technical background
    - `high-school` — Basic math/science literacy
    - `undergraduate` — Introductory college-level knowledge in the domain
    - `phd-student` — Graduate-level domain knowledge
    - `researcher` — Active researcher familiar with the field (default)
    - `expert` — Deep specialist in the exact sub-field
    - `"free text"` — Any custom audience description (e.g., `"medical doctors learning ML"`)
  - `--depth` — Controls review thoroughness (default: `medium`):
    - `low` — Skip MAGI cross-review; Claude reviews alone
    - `medium` — Standard MAGI cross-review (Gemini + Codex review in parallel)
    - `high` — MAGI cross-review + Devil's Advocate adversarial pass on high-stakes sections
  - `--claude-only` — Replace all Gemini/Codex MCP calls with Claude Agent subagents. Use when external model endpoints are unavailable. See **Claude-Only Mode** section below.
  - `--resume <write_dir>` — Resume an interrupted write pipeline from a previous write output directory. See **Resume Protocol** below.

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-2.5-pro"` (fallback)
  3. Claude (last resort — skip Gemini MCP tool, use Claude directly)
- **Codex**: Use `model: "gpt-5.4"` for all Codex MCP calls. Use `mcp__codex-cli__ask-codex` for analysis/review. If Codex fails 2+ times, fall back to Claude directly.
- **File References**: Use `@filepath` in the prompt parameter to pass saved artifacts (e.g., `@write/outline.md`)
  instead of pasting file content inline. The CLI tools read files directly, preventing context truncation.
- **Web Search**: Use web search freely whenever factual verification, recent developments, or literature context would strengthen the writing:
  - **Claude**: Use the `WebSearch` tool directly
  - **Gemini**: Add `search: true` to `mcp__gemini-cli__ask-gemini` calls
  - **Codex**: Add `search: true` to `mcp__codex-cli__ask-codex` calls
  - **When to search**: citation verification, related work references, fact-checking claims, confirming state-of-the-art results, checking terminology conventions
  - **Claude-only mode**: Claude Agent subagents cannot use WebSearch. The main Claude agent should search beforehand and include findings in the subagent prompt.
- **Visualization**: Use `matplotlib` with `scienceplots` (`['science', 'nature']` style). Save plots as PNG (300 dpi) and PDF.
- **LaTeX**: Use LaTeX for all mathematical expressions in output documents. Inline: `$...$`. Display equations: `$$` on its own line with the equation on a separate line:
  ```
  $$
  equation
  $$
  ```
  Never write display equations on a single line as `$$..equation..$$`.

### Claude-Only Mode

When `--claude-only` is active, **all** Gemini/Codex MCP tool calls are replaced with Claude Agent subagents (`subagent_type: general-purpose`). The table below maps each original call to its replacement:

| Original Call | Replacement | Cognitive Style |
|---|---|---|
| `mcp__gemini-cli__brainstorm` | Agent subagent A | **Creative-Divergent**: unconventional connections, "What if?" scenarios, wide exploration, questioning assumptions |
| `mcp__codex-cli__brainstorm` | Agent subagent B | **Analytical-Convergent**: step-by-step feasibility, established methodologies, deep evaluation, practical constraints, risk assessment |
| `mcp__gemini-cli__ask-gemini` | Agent subagent A | Same Creative-Divergent style |
| `mcp__codex-cli__ask-codex` | Agent subagent B | Same Analytical-Convergent style |

**Key rules for claude-only mode:**
1. **File access**: Subagents use the `Read` tool to access files (no `@filepath` syntax).
2. **Output filenames**: Keep original names (`gemini_outline.md`, `codex_outline.md`, etc.) — add a header `> Source: Claude Agent subagent (claude-only mode, {style})` to each output file.
3. **Independence**: Both subagents are spawned simultaneously so neither can see the other's output.

### LaTeX Formatting Rules
When writing mathematical expressions in any output document (outlines, drafts, final documents):
- **Inline math**: Use `$...$` for short expressions within a sentence (e.g., `$\alpha = 0.05$`, `$O(n \log n)$`)
- **Display equations**: Use `$$` on its own line, with the equation on a separate line:
  ```
  $$
  \hat{\theta}_{\text{MLE}} = \arg\max_\theta \prod_{i=1}^{n} f(x_i \mid \theta)
  $$
  ```
- Never write display equations inline as `$$..equation..$$` on a single line — always use line breaks
- Use display equations for: key formulas, derivations, loss functions, objective functions, main results
- Use inline math for: variable names, parameter values, complexity notation, short expressions in running text
- Include this formatting instruction in prompts to Gemini and Codex when the topic involves mathematical content

When this skill is invoked, follow these steps exactly:

---

### Phase 0: Setup & Intake

#### Step 0a: Parse Arguments

1. Parse `$ARGUMENTS`:
   - Extract `--source <output_dir>` (required unless `--resume`). Validate the directory exists using `Glob`.
   - Extract `--mode` (default: `paper`). Validate against supported modes: `paper`, `proposal`.
   - Extract `--audience` (default: `researcher`). Store as-is (predefined keyword or free-text string).
   - Extract `--depth` (default: `medium`). Validate: `low`, `medium`, `high`.
   - Extract `--claude-only` (boolean, default: `false`).
   - **Parse `--resume <write_dir>`**: If provided, skip to the **Resume Protocol** below.

2. Determine the domain by reading upstream artifacts:
   - Check for `brainstorm/weights.json` in the source directory — the `_meta.domain` field contains the domain.
   - If not found, check `brainstorm/personas.md` for domain context.
   - If neither exists, infer domain from the source directory name or contents.

3. Create the write output directory inside the source directory:
   ```
   {source_dir}/write/
   ```
   If `write/` already exists, announce that existing artifacts will be preserved and new artifacts will be added alongside them.

4. Announce to the user: source directory, mode, audience, depth, domain, and claude-only status.

#### Step 0b: Locate Upstream Artifacts

Inventory the source directory for available artifacts using `Glob`:

| Artifact | Path | Required | Purpose |
|:---------|:-----|:---------|:--------|
| Brainstorm synthesis | `brainstorm/synthesis.md` | Recommended | Research directions, key findings |
| Research plan | `plan/research_plan.md` | Recommended | Methodology, objectives |
| Murder board | `plan/murder_board.md` | Optional | Stress-test results |
| Mitigations | `plan/mitigations.md` | Optional | Plan revisions |
| Source code | `src/**/*.py` | Optional | Implementation details |
| Test results | `tests/**/*.py` | Optional | Validation data |
| Plot manifest | `plots/plot_manifest.json` | Optional | Figures with metadata |
| Report | `report.md` | Optional | Pre-existing report draft |
| Explain outputs | `explain/**/*.md` | Optional | Concept explanations |
| Brainstorm personas | `brainstorm/personas.md` | Optional | Expert persona context |
| Weights | `brainstorm/weights.json` | Optional | Scoring weights used |

For each artifact found, read the first 5 lines to confirm it is non-empty.

**On missing recommended artifacts**: Warn the user which recommended artifacts are absent. Ask: "The following recommended artifacts are missing: [list]. The document will have thinner coverage in the corresponding sections. Proceed anyway?" Continue on confirmation.

#### Step 0c: Generate Intake Artifacts

Claude reads all located upstream artifacts and generates two structured JSON files. This is an **LLM extraction task** — Claude performs the semantic extraction; Python validates the schema.

**1. Generate `write/write_inputs.json`:**

Claude reads all upstream artifacts and produces:
```json
{
  "source_dir": "{source_dir}",
  "mode": "paper|proposal",
  "audience": "{audience}",
  "domain": "{domain}",
  "claims": [
    {
      "id": "claim-1",
      "text": "Our method achieves 15% improvement over baseline",
      "source": "brainstorm/synthesis.md",
      "confidence": "high|medium|low",
      "evidence_ids": ["ev-1", "ev-3"]
    }
  ],
  "evidence": [
    {
      "id": "ev-1",
      "type": "plot|metric|test_result|code|explanation",
      "ref": "plots/fig_convergence.png",
      "description": "Convergence plot showing ...",
      "caption": "Figure 1: ...",
      "section_hint": "results"
    }
  ],
  "definitions": [
    {
      "term": "MAGI architecture",
      "explanation": "Multi-Agent Guided Investigation ...",
      "source": "explain/magi_architecture.md"
    }
  ],
  "key_findings": [
    {
      "id": "finding-1",
      "summary": "...",
      "supporting_claims": ["claim-1", "claim-3"],
      "narrative_weight": "primary|secondary|supporting"
    }
  ],
  "sections_available": ["background", "methodology", "results", "testing"]
}
```

**Guidelines for extraction:**
- Extract claims conservatively — only include assertions backed by evidence in the upstream artifacts
- Assign `confidence: "high"` only when a claim has both quantitative data and a supporting plot/test
- Assign `confidence: "low"` to claims inferred from text without direct data support
- Link each claim to its evidence via `evidence_ids`
- Use `section_hint` from `plot_manifest.json` if available; otherwise infer from context
- For definitions, prefer explain outputs; fall back to inline definitions in synthesis/plan

**2. Generate `write/citation_ledger.json`:**

Claude reads all upstream artifacts and produces:
```json
{
  "citations": [
    {
      "id": "ref-1",
      "claim_id": "claim-1",
      "source_type": "upstream_artifact|web_search|assumed",
      "source_path": "brainstorm/synthesis.md",
      "source_detail": "Section 3, Direction 1",
      "resolved": true,
      "needs_verification": false
    }
  ],
  "unresolved_claims": [
    {
      "claim_id": "claim-5",
      "reason": "No supporting data found in upstream artifacts",
      "recommendation": "remove|verify_with_search|mark_as_tentative"
    }
  ]
}
```

**3. Validate with Python:**

After Claude generates both JSON files, write a validation script and run it:

```python
# Claude writes this script to write/validate_intake.py, then executes it
import json
import sys

def validate_intake(inputs_path, ledger_path):
    """Validate write_inputs.json and citation_ledger.json schemas."""
    errors = []

    # Load and validate write_inputs.json
    with open(inputs_path) as f:
        inputs = json.load(f)

    required_keys = ["source_dir", "mode", "audience", "domain", "claims", "evidence"]
    for key in required_keys:
        if key not in inputs:
            errors.append(f"write_inputs.json missing required key: {key}")

    # Validate claim-evidence links
    evidence_ids = {e["id"] for e in inputs.get("evidence", [])}
    for claim in inputs.get("claims", []):
        if "id" not in claim or "text" not in claim:
            errors.append(f"Claim missing required fields: {claim}")
        for ev_id in claim.get("evidence_ids", []):
            if ev_id not in evidence_ids:
                errors.append(f"Claim {claim['id']} references unknown evidence: {ev_id}")

    # Load and validate citation_ledger.json
    with open(ledger_path) as f:
        ledger = json.load(f)

    claim_ids = {c["id"] for c in inputs.get("claims", [])}
    for citation in ledger.get("citations", []):
        if citation.get("claim_id") and citation["claim_id"] not in claim_ids:
            errors.append(f"Citation {citation['id']} references unknown claim: {citation['claim_id']}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"VALIDATION PASSED: {len(inputs['claims'])} claims, {len(inputs['evidence'])} evidence items, {len(ledger['citations'])} citations")

if __name__ == "__main__":
    validate_intake(sys.argv[1], sys.argv[2])
```

Run with: `uv run python write/validate_intake.py write/write_inputs.json write/citation_ledger.json`

If validation fails, Claude fixes the JSON files and re-runs validation. Maximum 2 fix attempts.

---

### Phase 1: Outline

#### Step 1a: Load Mode Template

Read the mode template from `${CLAUDE_PLUGIN_ROOT}/templates/writing/{mode}.md`.

Parse the YAML frontmatter to extract:
- `sections` — ordered list of section definitions with `id`, `required`, `max_words`, `evidence_slots`, `style`, `narrative_role`
- `export` — target export formats
- `total_max_words` — overall word budget
- `tone`, `jargon_budget`, `formality` — style constraints

Read the Markdown body for section dependencies and evidence integration guidelines.

#### Step 1b: MAGI Parallel Outline Generation

Generate two independent outlines using the mode template, `write_inputs.json`, and audience context. Execute both calls **simultaneously**:

**Gemini (BALTHASAR) — Creative Outline:**
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

**Codex (CASPER) — Structural Outline:**
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

> **If `--claude-only`**: Replace both calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent — Creative Outline):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are a Creative-Divergent expert academic writer creating a document outline. Your approach emphasizes narrative flow, creative framing, and reader engagement. You think in 'What if?' scenarios and explore unconventional angles.
>
> Use the Read tool to read:
> - {source_dir}/write/mode_template_cache.md
> - {source_dir}/write/write_inputs.json
> - {source_dir}/write/citation_ledger.json
>
> Given:
> - Mode: {mode}
> - Audience: {audience}
> - Domain: {domain}
>
> For each section defined in the mode template, produce:
> 1. Section ID (from template)
> 2. Title (descriptive, audience-appropriate)
> 3. Purpose (1-2 sentences)
> 4. Narrative role (from template + your interpretation)
> 5. Key points (3-5 bullet points)
> 6. Evidence to include (specific evidence IDs from write_inputs.json)
> 7. Estimated words (within template budget)
> 8. Transition from previous section
>
> Also define the global argument thread: 2-3 sentences summarizing the narrative arc.
>
> Save to {source_dir}/write/gemini_outline.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Creative-Divergent)"
> )
> ```
>
> **Subagent B (Analytical-Convergent — Structural Outline):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Analytical-Convergent expert academic writer creating a document outline. Your approach emphasizes logical structure, evidence coverage, and completeness. You think step-by-step and focus on practical constraints.
>
> Use the Read tool to read:
> - {source_dir}/write/mode_template_cache.md
> - {source_dir}/write/write_inputs.json
> - {source_dir}/write/citation_ledger.json
>
> Given:
> - Mode: {mode}
> - Audience: {audience}
> - Domain: {domain}
>
> For each section defined in the mode template, produce:
> 1. Section ID (from template)
> 2. Title (descriptive, audience-appropriate)
> 3. Purpose (1-2 sentences)
> 4. Narrative role (from template + your interpretation)
> 5. Key points (3-5 bullet points)
> 6. Evidence to include (specific evidence IDs from write_inputs.json)
> 7. Estimated words (within template budget)
> 8. Transition from previous section
>
> Focus especially on:
> - Evidence coverage: every high-confidence claim appears in at least one section
> - No orphaned evidence: every evidence item is referenced
> - Structural completeness: all required sections present
>
> Also define the global argument thread.
>
> Save to {source_dir}/write/codex_outline.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Analytical-Convergent)"
> )
> ```

#### Step 1c: Synthesize Section Contracts

Claude reads both outlines and synthesizes a canonical outline with per-section contracts:

1. **Merge outlines**: For each section, take the stronger content from each outline:
   - Prefer Gemini's narrative framing and transitions
   - Prefer Codex's evidence coverage and structural completeness
   - Resolve conflicts by favoring the version that covers more evidence items

2. **Define the global argument thread**: Synthesize both outlines' argument threads into a single 3-5 sentence narrative arc that connects all sections.

3. **Generate `write/section_contracts.json`**:
```json
{
  "global_argument_thread": "This paper argues that ... by showing ... which leads to ...",
  "mode": "paper",
  "audience": "researcher",
  "sections": [
    {
      "id": "introduction",
      "title": "Introduction",
      "purpose": "Motivate the problem and state contributions",
      "narrative_role": "Establish why this problem matters and what we do about it",
      "key_points": ["point 1", "point 2", "point 3"],
      "evidence_ids": ["ev-1", "ev-5"],
      "claim_ids": ["claim-1", "claim-2"],
      "max_words": 1500,
      "style": "Motivate problem, state contributions, outline paper structure.",
      "transition_from_previous": null,
      "transition_to_next": "Having established the problem, we now survey related work.",
      "drafting_order": 3
    }
  ]
}
```

4. **Determine drafting order**: Based on the section dependencies from the mode template:
   - Independent sections first (e.g., `related_work` for papers, `problem_statement` for proposals)
   - Dependent sections next, respecting dependency chains
   - Summary sections last (e.g., `abstract` for papers, `executive_summary` for proposals)
   - The `drafting_order` field is a 1-indexed integer reflecting this order.

5. **Evidence coverage check**: Verify that every high-confidence claim from `write_inputs.json` appears in at least one section's `claim_ids`. Verify that every evidence item appears in at least one section's `evidence_ids`. Report any orphaned claims or evidence.

6. Save the synthesized outline to `write/outline.md` (human-readable Markdown version) and `write/section_contracts.json` (machine-readable).

#### Step 1d: User Checkpoint — Outline Approval

**>>> USER CHECKPOINT: Approve outline <<<**

Present to the user:
- The global argument thread
- A summary table of all sections: title, purpose, narrative role, word budget, evidence count
- Any orphaned claims or evidence items
- The proposed drafting order

Wait for user approval. The user may:
- Approve the outline as-is
- Request modifications to specific sections (update `section_contracts.json` accordingly)
- Add or remove sections (within mode template constraints — required sections cannot be removed)
- Reorder the narrative

> This is **Hard Gate 1** — the most important checkpoint. No drafting begins until the user approves the outline.

---

### Phase 2: Draft

#### Step 2a: Prepare Evidence Blocks

Before generating any section prose, Claude pre-assembles evidence blocks for each section. This is the core evidence integration strategy: **LLMs write prose AROUND pre-placed evidence, NOT with macros.**

For each section (in drafting order):

1. Read the section contract from `write/section_contracts.json`.
2. For each `evidence_id` in the section's `evidence_ids`:
   - Look up the evidence in `write_inputs.json`
   - If `type == "plot"`: Generate a Markdown figure embed block:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-1 -->
     ![{caption}]({ref})
     *{caption}*
     <!-- END EVIDENCE BLOCK -->
     ```
   - If `type == "metric"`: Generate an inline metric reference:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-2 -->
     **Key metric**: {description} — {value}
     <!-- END EVIDENCE BLOCK -->
     ```
   - If `type == "test_result"`: Generate a results summary block:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-3 -->
     **Validation**: {description}
     <!-- END EVIDENCE BLOCK -->
     ```
   - If `type == "code"`: Generate a code reference:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-4 -->
     See implementation in `{ref}`: {description}
     <!-- END EVIDENCE BLOCK -->
     ```
3. Save the pre-assembled evidence blocks to `write/evidence_blocks/{section_id}.md`.

#### Step 2b: Section-by-Section Drafting

Generate each section in the order specified by `drafting_order` in `section_contracts.json`. For each section:

**Context provided to the LLM** (scoped to prevent context bloat):
- The section's own contract (from `section_contracts.json`)
- The global argument thread (2-3 sentences)
- Pre-assembled evidence blocks for this section (from `write/evidence_blocks/{section_id}.md`)
- The relevant claims from `write_inputs.json` (only claims listed in the section's `claim_ids`)
- Preceding section summaries: for each already-drafted section, provide only the section title + first paragraph + last paragraph (not the full text)
- Audience and style constraints from the mode template

**Drafting prompt** (sent to Claude — Claude drafts all sections directly for voice consistency):

For each section, Claude:
1. Reads the section contract, evidence blocks, and relevant claims
2. Writes the section prose, integrating pre-placed evidence blocks naturally into the narrative
3. Ensures the section:
   - Opens with a transition from the previous section (using the `transition_from_previous` field)
   - Covers all key points listed in the contract
   - References all pre-placed evidence with concrete quantitative observations (not passive "see figure below")
   - Stays within the `max_words` budget (±10%)
   - Matches the style, tone, and formality constraints
   - Closes with a transition to the next section (using the `transition_to_next` field)
4. After writing the section, generates a 1-2 sentence summary for use as context by subsequent sections

Save each section to `write/sections/{section_id}.md`.
Save each section summary to `write/sections/{section_id}_summary.md`.

#### Step 2c: Assemble Full Draft

After all sections are drafted:

1. Concatenate all sections in the order defined by the mode template (NOT drafting order — presentation order).
2. Add a document title derived from the global argument thread and source directory topic.
3. For paper mode: add author placeholder, date, and abstract positioning.
4. For proposal mode: add a title page with project title, PI placeholder, and date.
5. Save the assembled draft to `write/draft.md`.

#### Step 2d: Narrative Arc Tracking

Claude reads the full assembled draft and evaluates the narrative arc:

1. **Thread continuity check**: Does each section's opening connect to the previous section's closing? Are there abrupt topic shifts?
2. **Argument progression**: Does the document build its case progressively? Does the conclusion follow from the evidence presented?
3. **Tone consistency**: Is the voice consistent across all sections? (Flagged only — resolution happens in Phase 3.)

Save the narrative arc assessment to `write/narrative_arc_assessment.md`. This feeds into the Phase 3 global coherence pass.

---

### Phase 3: Review

#### Step 3a: MAGI Cross-Review

> Skip this step if `--depth low`. For `--depth low`, proceed directly to Step 3c (DocCI Validation).

Execute both review calls **simultaneously**:

**Gemini (BALTHASAR) — Content Quality Review:**
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

**Codex (CASPER) — Structure & Evidence Review:**
```
mcp__codex-cli__ask-codex(
  prompt: "You are a meticulous technical editor evaluating a {mode} draft. Review for structural integrity, evidence completeness, and formatting quality.

Evaluate each section on:
1. **Word budget compliance**: Is each section within ±10% of its allocated word budget?
2. **Evidence completeness**: Are all evidence items from the section contract actually referenced in the text?
3. **Citation integrity**: Are all claims traceable to upstream artifacts? Flag any claims that appear fabricated.
4. **LaTeX correctness**: Are mathematical expressions properly formatted (inline $...$ and display $$ on separate lines)?
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

> **If `--claude-only`**: Replace both calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent — Content Quality Review):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are a Creative-Divergent academic reviewer. You look for gaps in reasoning, missed connections, and opportunities for deeper analysis.
>
> Use the Read tool to read:
> - {source_dir}/write/draft.md
> - {source_dir}/write/section_contracts.json
> - {source_dir}/write/write_inputs.json
>
> Review the {mode} draft for content quality. Evaluate each section on:
> 1. Claim support — is every claim backed by evidence?
> 2. Evidence integration — are figures discussed with concrete observations?
> 3. Narrative flow — does the argument build progressively?
> 4. Audience appropriateness for {audience}
> 5. Completeness — any obvious gaps?
>
> For each issue: Section ID, issue type, severity (critical/major/minor), specific text, and fix suggestion.
>
> Also evaluate the global argument thread.
>
> Save to {source_dir}/write/gemini_review.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Creative-Divergent)"
> )
> ```
>
> **Subagent B (Analytical-Convergent — Structure & Evidence Review):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Analytical-Convergent technical editor. You focus on structural integrity, evidence completeness, and formatting precision.
>
> Use the Read tool to read:
> - {source_dir}/write/draft.md
> - {source_dir}/write/section_contracts.json
> - {source_dir}/write/write_inputs.json
>
> Review the {mode} draft for structural integrity. Evaluate each section on:
> 1. Word budget compliance (±10% of allocated budget)
> 2. Evidence completeness — all contract evidence referenced?
> 3. Citation integrity — all claims traceable to upstream artifacts?
> 4. LaTeX correctness
> 5. Structural compliance with mode template
>
> For each issue: Section ID, issue type, severity (critical/major/minor), specific text, and fix suggestion.
>
> Also check for orphaned evidence items.
>
> Save to {source_dir}/write/codex_review.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Analytical-Convergent)"
> )
> ```

#### Step 3b: Devil's Advocate Review

> Skip this step if `--depth low` or `--depth medium`. Only execute for `--depth high`.

Identify the **high-stakes sections** — sections with the most critical/major issues from Step 3a, plus any section tagged as `required: true` in the mode template that has `narrative_role` containing "evidence", "method", or "result".

For each high-stakes section (max 3 sections), submit to Gemini as a hostile reviewer:

```
mcp__gemini-cli__ask-gemini(
  prompt: "You are a hostile but fair reviewer of the '{section_title}' section. Your job is to find fatal flaws that would cause a reviewer to reject this {mode}.

Attack on these dimensions:
1. **Overclaiming**: Does the text promise more than the evidence supports?
2. **Missing counterarguments**: Are obvious objections left unaddressed?
3. **Methodological gaps**: Is the methodology described with sufficient rigor to reproduce?
4. **Evidence cherry-picking**: Are unfavorable results omitted or downplayed?
5. **Logical fallacies**: Are there non sequiturs, false equivalences, or circular reasoning?

For each flaw found, rate severity (Critical/Major/Minor) and provide a concrete fix.

Section text:
@{source_dir}/write/sections/{section_id}.md

Section contract:
[inline the specific section contract from section_contracts.json]

Supporting evidence:
@{source_dir}/write/evidence_blocks/{section_id}.md",
  model: "gemini-3.1-pro-preview"
)
```
Save each to `write/devils_advocate_{section_id}.md`.

> **If `--claude-only`**: Replace with a Claude Agent subagent:
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Adversarial-Critical reviewer. Your cognitive style is hostile but fair — you actively search for fatal flaws, overclaiming, and logical fallacies. You are NOT here to be helpful; you are here to break the argument.
>
> Use the Read tool to read:
> - {source_dir}/write/sections/{section_id}.md
> - {source_dir}/write/evidence_blocks/{section_id}.md
>
> Attack the '{section_title}' section on:
> 1. Overclaiming — does the text promise more than evidence supports?
> 2. Missing counterarguments
> 3. Methodological gaps
> 4. Evidence cherry-picking
> 5. Logical fallacies
>
> For each flaw: severity (Critical/Major/Minor) and concrete fix.
>
> Save to {source_dir}/write/devils_advocate_{section_id}.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Adversarial-Critical)"
> )
> ```

#### Step 3c: Claude Synthesizes Reviews & Applies Fixes

Claude reads all review outputs and applies fixes:

1. **Read reviews**: `write/gemini_review.md`, `write/codex_review.md`, and any `write/devils_advocate_*.md` files.

2. **Triage issues**:
   - **Consensus issues** (flagged by both Gemini and Codex): High-priority fixes, apply immediately
   - **Divergent issues** (flagged by only one reviewer): Evaluate on merit, apply where appropriate
   - **Devil's Advocate findings**: Apply all Critical fixes; evaluate Major fixes on merit

3. **Apply section-level fixes**: For each section with issues:
   - Re-read the section contract and evidence blocks
   - Rewrite the section incorporating all accepted fixes
   - Ensure fixes don't introduce new problems (check word budget, evidence coverage)
   - Save the revised section to `write/sections/{section_id}.md` (overwrite)

4. **Escalation trigger**: If any fix requires changing a section's scope or adding/removing key points not in the section contract, **update `section_contracts.json`** and flag this for the user:
   > "Section contract for '{section_id}' has been modified during review. Changes: [list]. These will be shown for approval in Phase 4."

5. Re-assemble the revised draft: `write/revised_draft.md`.

#### Step 3d: Global Coherence Pass

After all section-level fixes are applied, Claude performs a focused coherence pass:

1. Read the full `write/revised_draft.md`.
2. Read `write/narrative_arc_assessment.md` from Phase 2d.
3. **Rewrite ONLY transition sentences** — the first and last paragraphs of each section — to create narrative flow across the entire document.
4. Check that the global argument thread is maintained from introduction through conclusion.
5. Save the coherence-edited draft to `write/revised_draft.md` (overwrite).

> This is NOT a full rewrite. It is a bounded, focused pass that touches only inter-section boundaries. The goal is to eliminate the "Frankenstein" effect of section-by-section generation.

#### Step 3e: DocCI Validation

Claude writes and runs a validation script to perform automated quality checks:

```python
# Claude writes this script to write/validate_draft.py, then executes it
import json
import re
import sys

def validate_draft(draft_path, contracts_path, inputs_path):
    """Automated document quality checks."""
    results = {"passed": [], "failed": [], "warnings": []}

    with open(draft_path) as f:
        draft = f.read()
    with open(contracts_path) as f:
        contracts = json.load(f)
    with open(inputs_path) as f:
        inputs = json.load(f)

    # 1. Math delimiter balance
    inline_opens = draft.count('$') - 2 * draft.count('$$')
    if inline_opens % 2 != 0:
        results["failed"].append("Unbalanced inline math delimiters ($)")
    else:
        results["passed"].append("Inline math delimiters balanced")

    display_count = draft.count('$$')
    if display_count % 2 != 0:
        results["failed"].append("Unbalanced display math delimiters ($$)")
    else:
        results["passed"].append("Display math delimiters balanced")

    # 2. Evidence block completeness
    evidence_ids_in_draft = set(re.findall(r'EVIDENCE BLOCK: ([\w-]+)', draft))
    required_evidence = set()
    for section in contracts.get("sections", []):
        for ev_id in section.get("evidence_ids", []):
            required_evidence.add(ev_id)
    missing = required_evidence - evidence_ids_in_draft
    if missing:
        results["failed"].append(f"Missing evidence blocks: {', '.join(missing)}")
    else:
        results["passed"].append("All required evidence blocks present")

    # 3. Section presence
    for section in contracts.get("sections", []):
        section_marker = f"## {section['title']}" if 'title' in section else f"## {section['id'].replace('_', ' ').title()}"
        # Also check for # (H1) level headers
        if section_marker not in draft and section['id'] not in draft.lower():
            results["warnings"].append(f"Section '{section['id']}' may be missing from draft")

    # 4. Word budget per section (approximate)
    sections_text = re.split(r'\n##\s+', draft)
    for section in contracts.get("sections", []):
        max_words = section.get("max_words", 0)
        if max_words == 0:
            continue
        # Find the matching section text (approximate match)
        for text_block in sections_text:
            if section.get("title", section["id"]).lower() in text_block[:100].lower():
                word_count = len(text_block.split())
                if word_count > max_words * 1.1:
                    results["warnings"].append(
                        f"Section '{section['id']}' exceeds budget: {word_count}/{max_words} words (+{word_count - max_words})"
                    )
                break

    # 5. Orphaned evidence check
    all_evidence = {e["id"] for e in inputs.get("evidence", [])}
    orphaned = all_evidence - evidence_ids_in_draft
    if orphaned:
        results["warnings"].append(f"Orphaned evidence (not in draft): {', '.join(orphaned)}")

    # Print results
    print("=== DocCI Validation Report ===")
    print(f"\nPASSED ({len(results['passed'])}):")
    for p in results["passed"]:
        print(f"  [PASS] {p}")
    print(f"\nFAILED ({len(results['failed'])}):")
    for f_item in results["failed"]:
        print(f"  [FAIL] {f_item}")
    print(f"\nWARNINGS ({len(results['warnings'])}):")
    for w in results["warnings"]:
        print(f"  [WARN] {w}")

    # Save as JSON
    with open(draft_path.replace('.md', '_validation.json'), 'w') as f:
        json.dump(results, f, indent=2)

    if results["failed"]:
        sys.exit(1)
    print("\nOverall: PASSED (with warnings)" if results["warnings"] else "\nOverall: PASSED")

if __name__ == "__main__":
    validate_draft(sys.argv[1], sys.argv[2], sys.argv[3])
```

Run with: `uv run python write/validate_draft.py write/revised_draft.md write/section_contracts.json write/write_inputs.json`

**On validation failure**: Claude reads the validation report, fixes the identified issues in `write/revised_draft.md`, and re-runs validation. Maximum 2 fix iterations.

Save the validation report to `write/validation_report.json`.

---

### Phase 4: Finalize

#### Step 4a: Macro Resolution Fallback

Before presenting to the user, scan the draft for any remaining unresolved macros. If MAGI model outputs introduced any `{{fig:id}}` or `{{ref:id}}` patterns during review, resolve them now:

1. Scan `write/revised_draft.md` for patterns matching `{{fig:...}}` or `{{ref:...}}`.
2. If any are found, Claude writes and runs a resolution script:

```python
# Claude writes this script to write/resolve_macros.py, then executes it
import json
import re
import sys

def resolve_macros(draft_path, inputs_path, ledger_path):
    """Resolve any remaining macros in the draft."""
    with open(draft_path) as f:
        draft = f.read()
    with open(inputs_path) as f:
        inputs = json.load(f)
    with open(ledger_path) as f:
        ledger = json.load(f)

    # Build lookup tables
    evidence_map = {e["id"]: e for e in inputs.get("evidence", [])}
    citation_map = {c["id"]: c for c in ledger.get("citations", [])}

    unresolved = []

    # Resolve {{fig:id}} → markdown image embed
    def resolve_fig(match):
        fig_id = match.group(1)
        if fig_id in evidence_map:
            ev = evidence_map[fig_id]
            return f'![{ev.get("caption", fig_id)}]({ev["ref"]})\n*{ev.get("caption", "")}*'
        unresolved.append(f"{{{{fig:{fig_id}}}}}")
        return match.group(0)

    # Resolve {{ref:id}} → citation text
    def resolve_ref(match):
        ref_id = match.group(1)
        if ref_id in citation_map:
            cit = citation_map[ref_id]
            return f'[{cit.get("source_detail", ref_id)}]'
        unresolved.append(f"{{{{ref:{ref_id}}}}}")
        return match.group(0)

    draft = re.sub(r'\{\{fig:([\w-]+)\}\}', resolve_fig, draft)
    draft = re.sub(r'\{\{ref:([\w-]+)\}\}', resolve_ref, draft)

    with open(draft_path, 'w') as f:
        f.write(draft)

    if unresolved:
        print(f"WARNING: {len(unresolved)} unresolved macros: {', '.join(unresolved)}")
        sys.exit(1)
    else:
        print("All macros resolved (or none found).")

if __name__ == "__main__":
    resolve_macros(sys.argv[1], sys.argv[2], sys.argv[3])
```

Run with: `uv run python write/resolve_macros.py write/revised_draft.md write/write_inputs.json write/citation_ledger.json`

If unresolved macros remain, Claude manually resolves them by reading the intake data and making inline replacements. This is a fallback — the primary evidence integration happens in Phase 2a via pre-inserted evidence blocks.

3. If no macros are found, skip this step.

#### Step 4b: User Checkpoint — Final Approval

**>>> USER CHECKPOINT: Approve final document <<<**

Present to the user:
- The final draft location: `write/revised_draft.md`
- A summary table:
  - Total word count and per-section word counts vs. budgets
  - Number of evidence items integrated
  - Number of claims supported vs. unresolved
  - DocCI validation status (pass/fail/warnings)
  - Review issues found and resolved (counts by severity)
- Any section contract modifications from Phase 3 (if escalation was triggered)
- Any remaining warnings from DocCI validation

The user may:
- Approve the document as final
- Request specific section revisions (Claude revises and re-validates)
- Request a full re-review at a different `--depth` level

> This is **Hard Gate 2** — the final publish gate. No export happens until the user approves.

#### Step 4c: Export

After user approval:

1. Copy the approved draft to the final document name:
   - Paper mode: `write/{topic}_paper.md`
   - Proposal mode: `write/{topic}_proposal.md`

2. Clean up evidence block markers: Remove all `<!-- EVIDENCE BLOCK: ... -->` and `<!-- END EVIDENCE BLOCK -->` HTML comments from the final document, leaving only the rendered content.

3. Generate `write/writing_state.json`:
```json
{
  "status": "complete",
  "mode": "paper",
  "audience": "researcher",
  "source_dir": "{source_dir}",
  "phases_complete": {
    "intake": true,
    "outline": true,
    "draft": true,
    "review": true,
    "finalize": true
  },
  "sections_drafted": ["introduction", "methodology", "results", "..."],
  "output_file": "write/{topic}_paper.md",
  "stats": {
    "total_words": 8500,
    "claims_supported": 12,
    "claims_unresolved": 1,
    "evidence_integrated": 8,
    "review_issues_resolved": 15
  }
}
```

4. Present completion summary to the user:
   - Final document path
   - Word count and section breakdown
   - Evidence integration statistics
   - Any remaining caveats or limitations

---

### Resume Protocol

When `--resume <write_dir>` is provided, the pipeline skips initialization and infers the current phase from the **presence of key artifact files** in the write output directory. The artifacts themselves serve as checkpoints — no separate state file is required for resume inference.

**Phase inference rules** (evaluated top-down; first match wins):

| Condition | Inference | Action |
|:----------|:----------|:-------|
| `write/writing_state.json` exists with `status: "complete"` | Pipeline complete | Inform user; offer to re-run specific phases |
| `write/revised_draft.md` exists | Phase 3 complete | Resume from Phase 4 (Finalize) |
| `write/draft.md` exists | Phase 2 complete | Resume from Phase 3 (Review) |
| `write/section_contracts.json` exists | Phase 1 complete | Resume from Phase 2 (Draft) |
| `write/write_inputs.json` exists | Phase 0 complete | Resume from Phase 1 (Outline) |
| None of the above | No phase complete | Start from Phase 0 (Setup & Intake) |

**Resume procedure:**
1. Use `Glob` to check for each artifact in the order above.
2. Read the first few lines of the matched artifact to confirm it is non-empty.
3. Announce to the user: detected phase, write directory, and which phase will be resumed.
4. Infer `--source`, `--mode`, and `--audience` from `write/write_inputs.json` if it exists. If not, require the user to provide `--source`.
5. Continue the pipeline from the inferred phase, skipping all prior phases.

> **Important**: On resume, do NOT re-create the write directory or overwrite existing artifacts from prior phases. Only create artifacts for the resumed phase and beyond.

---

## Output Files

The write pipeline produces artifacts in the `{source_dir}/write/` directory:

```
{source_dir}/
└── write/
    ├── write_inputs.json            # Canonical intake (claims, evidence, definitions)
    ├── citation_ledger.json         # Claim-source tracking
    ├── validate_intake.py           # Intake validation script
    ├── mode_template_cache.md       # Cached copy of mode template
    ├── gemini_outline.md            # Gemini's outline proposal
    ├── codex_outline.md             # Codex's outline proposal
    ├── outline.md                   # Synthesized canonical outline (human-readable)
    ├── section_contracts.json       # Per-section contracts (machine-readable)
    ├── evidence_blocks/
    │   ├── introduction.md          # Pre-assembled evidence for each section
    │   ├── methodology.md
    │   ├── results.md
    │   └── ...
    ├── sections/
    │   ├── introduction.md          # Individual section drafts
    │   ├── introduction_summary.md  # Section summary for context scoping
    │   ├── methodology.md
    │   ├── methodology_summary.md
    │   └── ...
    ├── draft.md                     # Assembled first draft
    ├── narrative_arc_assessment.md  # Narrative arc evaluation
    ├── gemini_review.md             # Gemini content quality review
    ├── codex_review.md              # Codex structure & evidence review
    ├── devils_advocate_*.md         # Devil's Advocate reviews (--depth high only)
    ├── revised_draft.md             # Draft after review fixes + coherence pass
    ├── validate_draft.py            # DocCI validation script
    ├── validation_report.json       # DocCI validation results
    ├── resolve_macros.py            # Macro resolution fallback script (if needed)
    ├── {topic}_paper.md             # Final export (paper mode)
    ├── {topic}_proposal.md          # Final export (proposal mode)
    └── writing_state.json           # Pipeline state manifest
```

## Notes
- The write skill is designed as a **standalone skill** invoked after upstream research phases are complete. It is NOT embedded within the `/research` pipeline — invoke it separately with `--source` pointing to a research output directory.
- If upstream artifacts are incomplete, the skill will produce a document with thinner coverage in the corresponding sections rather than failing entirely. Missing sections are flagged in the DocCI validation.
- The **evidence-first approach** (pre-inserting evidence blocks before prose generation) prevents hallucination by ensuring the LLM writes around grounded data rather than fabricating evidence to fit a narrative.
- Python utility scripts (`validate_intake.py`, `validate_draft.py`, `resolve_macros.py`) are written by Claude during the pipeline and saved in the `write/` directory. They are NOT pre-installed — Claude writes the script, then executes it.
- The two hard gates (outline approval + final publish) ensure the user retains authorial control over structure and content. Between gates, the pipeline progresses automatically with review-driven quality assurance.
- Section-by-section drafting uses **scoped context windows**: each section receives only its contract, evidence, and preceding section summaries — not the full document or full intake data. This prevents context bloat and "lost in the middle" failures.
- The global coherence pass (Phase 3d) rewrites ONLY transition sentences (first/last paragraphs of each section). It is NOT a full rewrite — it is a bounded task that eliminates the "Frankenstein" effect.
- For mathematical content, include LaTeX formatting instructions in MAGI model prompts. All mathematical expressions must follow the LaTeX Formatting Rules section above.
- When writing about plots and figures, always include concrete quantitative observations — never just "As shown in Figure X."
- The mode template at `${CLAUDE_PLUGIN_ROOT}/templates/writing/{mode}.md` defines section structure, word budgets, evidence slots, and style constraints. Adding new modes requires only a new template file.
