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

> **Shared rules**: Read `${CLAUDE_PLUGIN_ROOT}/shared/rules.md` before starting. §MCP, §Claude-Only, §LaTeX, §Visualization, §Substitute apply to this skill.
> **Inline fallback** (if shared rules unavailable): Gemini models: gemini-3.1-pro-preview → gemini-2.5-pro → Claude. Codex: gpt-5.4. All math in LaTeX only (no Unicode: σ₁→`$\sigma_1$`). Use `@filepath` for MCP file refs; subagents use `Read` tool.

### MCP Tool Rules
See §MCP, §Visualization, §LaTeX in shared rules. Additionally:
- **Codex**: Use `/codex:rescue --wait --model gpt-5.4` for both ideation and analysis/review, invoked via `Skill(skill: "codex:rescue", args: "--wait --model gpt-5.4 {task prompt}")`. Reference file paths directly in the task prompt (no `@filepath` syntax for Codex; include web search instruction in the task prompt when needed).
- **When to search**: citation verification, related work references, fact-checking claims, confirming state-of-the-art results, checking terminology conventions

### Claude-Only Mode
See §Claude-Only and §Substitute in shared rules.

### LaTeX Formatting Rules
See §LaTeX in shared rules.

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
| Source code | `src/**/*` | Optional | Implementation details |
| Test results | `tests/**/*` | Optional | Validation data |
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

**3. Validate with maintained utility:**

After Claude generates both JSON files, validate them using the repository-maintained validator.

Determine the plugin root directory by navigating two levels up from this skill's base directory (e.g., if this skill is loaded from `.../skills/research-write/`, the plugin root is `../../` relative to that path). The `Base directory for this skill:` header injected by Claude Code provides the absolute path. Then run:

```bash
uv run python <plugin_root>/utils/validate_intake.py write/write_inputs.json write/citation_ledger.json
```

Where `<plugin_root>` is the resolved absolute path to the plugin installation directory (the directory containing `skills/`, `utils/`, `schemas/`).

> **Important**: Do NOT generate a validation script at runtime. Use the maintained `utils/validate_intake.py` utility. This ensures deterministic, testable validation across all pipeline runs.

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

Save a copy of the loaded template to `write/mode_template_cache.md` before proceeding to Step 1b. This cached copy is referenced by `@filepath` in subsequent model calls.

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
Skill(
  skill: "codex:rescue",
  args: "--wait --model gpt-5.4 You are an expert academic writer creating a document outline. Your approach emphasizes logical structure, evidence coverage, and completeness.

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

Search the web for relevant information. Read and analyze the files at {source_dir}/write/mode_template_cache.md, {source_dir}/write/write_inputs.json, and {source_dir}/write/citation_ledger.json"
)
```
Save to `write/codex_outline.md`.

> **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD, Creative Outline): Read mode template, write_inputs.json, citation_ledger.json. Per section from template: 1.Section ID, 2.Title, 3.Purpose (1-2 sentences), 4.Narrative role, 5.Key points (3-5), 6.Evidence IDs from write_inputs, 7.Estimated words (within template budget), 8.Transition from previous. Plus: global argument thread (2-3 sentence narrative arc). Emphasize narrative flow and engagement. Save to `write/gemini_outline.md`.
> - **B** (AC, Structural Outline): Read same 3 files. Same 8-field per-section structure + global argument thread. Focus: every high-confidence claim in ≥1 section, no orphaned evidence, all required sections present with adequate depth. Save to `write/codex_outline.md`.

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
     > **Anti-pattern:** Do NOT list figures in a table at the end of the document. Every figure must be embedded inline with `![caption](path)` immediately before or after the paragraph that discusses it. Orphaned figure tables are a document quality failure.
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
3. Before embedding each plot evidence block, verify that the `ref` path exists (Glob check). If the file is missing, mark the evidence block as `<!-- EVIDENCE BLOCK: {id} (MISSING FILE: {ref}) -->` and log a warning.

4. Save the pre-assembled evidence blocks to `write/evidence_blocks/{section_id}.md`.

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
Skill(
  skill: "codex:rescue",
  args: "--wait --model gpt-5.4 You are a meticulous technical editor evaluating a {mode} draft. Review for structural integrity, evidence completeness, and formatting quality.

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

Read and analyze the files at {source_dir}/write/draft.md, {source_dir}/write/section_contracts.json, and {source_dir}/write/write_inputs.json"
)
```
Save to `write/codex_review.md`.

> **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD, Content Quality): Read draft.md, section_contracts.json, write_inputs.json. Review: claim support, evidence integration, narrative flow, audience fit ({audience}), completeness. Per issue: Section ID, type (`unsupported_claim`|`weak_evidence`|`narrative_gap`|`audience_mismatch`|`missing_content`), severity (critical/major/minor), specific text, concrete fix. Also evaluate: does the global argument thread hold? Save to `write/gemini_review.md`.
> - **B** (AC, Structure & Evidence): Read same 3 files. Review: word budget compliance (±10%), evidence completeness, citation integrity, LaTeX correctness (flag bare Unicode: α σ π ² ≈ ∈ ℝ), structural compliance. Per issue: Section ID, type (`budget_violation`|`missing_evidence`|`untraced_claim`|`latex_error`|`structural_error`), severity, text, fix. Also check for orphaned evidence in write_inputs.json. Save to `write/codex_review.md`.

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

> **If `--claude-only`**: Per §SubagentExec — **Adversarial-Critical** hostile reviewer of '{section_title}': Read `sections/{section_id}.md` + `evidence_blocks/{section_id}.md` + section contract. Attack for overclaiming, missing counterarguments, methodological gaps, evidence cherry-picking, logical fallacies. Per flaw: severity (Critical/Major/Minor) + concrete fix. Save to `write/devils_advocate_{section_id}.md`.

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
   > **Data integrity:** Figures added or regenerated during the write pipeline must be sourced from data in `src/` or test outputs in the upstream artifact directory. Do NOT fabricate data for illustrative plots. If no data exists for a needed visualization, note the gap textually rather than generating synthetic values.

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

Run the repository-maintained draft validator to perform automated quality checks.

Determine the plugin root directory by navigating two levels up from this skill's base directory (e.g., if this skill is loaded from `.../skills/research-write/`, the plugin root is `../../` relative to that path). The `Base directory for this skill:` header injected by Claude Code provides the absolute path. Then run:

```bash
uv run python <plugin_root>/utils/validate_draft.py write/revised_draft.md write/section_contracts.json write/write_inputs.json
```

Where `<plugin_root>` is the resolved absolute path to the plugin installation directory (the directory containing `skills/`, `utils/`, `schemas/`).

> **Important**: Do NOT generate a validation script at runtime. Use the maintained `utils/validate_draft.py` utility. This ensures deterministic, testable validation across all pipeline runs.

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
- Validation utilities (`validate_intake.py`, `validate_draft.py`) are maintained in the `utils/` directory at the plugin root. They are NOT generated at runtime — resolve the plugin root by navigating two levels up from this skill's base directory and use the maintained versions at `<plugin_root>/utils/`. The `resolve_macros.py` script is still written by Claude during the pipeline when needed.
- The two hard gates (outline approval + final publish) ensure the user retains authorial control over structure and content. Between gates, the pipeline progresses automatically with review-driven quality assurance.
- Section-by-section drafting uses **scoped context windows**: each section receives only its contract, evidence, and preceding section summaries — not the full document or full intake data. This prevents context bloat and "lost in the middle" failures.
- The global coherence pass (Phase 3d) rewrites ONLY transition sentences (first/last paragraphs of each section). It is NOT a full rewrite — it is a bounded task that eliminates the "Frankenstein" effect.
- For mathematical content, include LaTeX formatting instructions in MAGI model prompts. All mathematical expressions must follow the LaTeX Formatting Rules section above.
- When writing about plots and figures, always include concrete quantitative observations — never just "As shown in Figure X."
- The mode template at `${CLAUDE_PLUGIN_ROOT}/templates/writing/{mode}.md` defines section structure, word budgets, evidence slots, and style constraints. Adding new modes requires only a new template file.
