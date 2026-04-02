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
- **Codex**: Use `mcp__codex-cli__ask-codex` for analysis/review.
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

> **Schema reference**: Read `references/intake_schemas.md` for the full `write_inputs.json` and `citation_ledger.json` schemas and extraction guidelines.

**1. Generate `write/write_inputs.json`** using the schema in `references/intake_schemas.md`.

**2. Generate `write/citation_ledger.json`** using the schema in `references/intake_schemas.md`.

**3. Validate with maintained utility:**

Determine the plugin root directory by navigating two levels up from this skill's base directory (e.g., if this skill is loaded from `.../skills/research-write/`, the plugin root is `../../` relative to that path). The `Base directory for this skill:` header injected by Claude Code provides the absolute path. Then run:

```bash
uv run python <plugin_root>/utils/validate_intake.py write/write_inputs.json write/citation_ledger.json
```

> **Important**: Do NOT generate a validation script at runtime. Use the maintained `utils/validate_intake.py` utility.

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

> **Full prompts**: Read `references/outline_prompts.md` for the complete MCP call specifications. Execute both calls **simultaneously**.

Generate two independent outlines using the mode template, `write_inputs.json`, and audience context:
- **Gemini (BALTHASAR)** — Creative Outline emphasizing narrative flow and reader engagement. Save to `write/gemini_outline.md`.
- **Codex (CASPER)** — Structural Outline emphasizing evidence coverage and completeness. Save to `write/codex_outline.md`.

If `--claude-only`: see the Claude-Only Fallback in `references/outline_prompts.md`.

#### Step 1c: Synthesize Section Contracts

Claude reads both outlines and synthesizes a canonical outline with per-section contracts:

1. **Merge outlines**: For each section, take the stronger content from each outline:
   - Prefer Gemini's narrative framing and transitions
   - Prefer Codex's evidence coverage and structural completeness
   - Resolve conflicts by favoring the version that covers more evidence items

2. **Define the global argument thread**: Synthesize both outlines' argument threads into a single 3-5 sentence narrative arc that connects all sections.

3. **Generate `write/section_contracts.json`** using the schema in `references/intake_schemas.md`.

4. **Determine drafting order**: Based on section dependencies from the mode template:
   - Independent sections first (e.g., `related_work` for papers, `problem_statement` for proposals)
   - Dependent sections next, respecting dependency chains
   - Summary sections last (e.g., `abstract` for papers, `executive_summary` for proposals)
   - The `drafting_order` field is a 1-indexed integer reflecting this order.

5. **Evidence coverage check**: Verify that every high-confidence claim from `write_inputs.json` appears in at least one section's `claim_ids`. Verify that every evidence item appears in at least one section's `evidence_ids`. Report any orphaned claims or evidence.

6. Save the synthesized outline to `write/outline.md` (human-readable Markdown) and `write/section_contracts.json` (machine-readable).

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
2. For each `evidence_id` in the section's `evidence_ids`, generate the appropriate block:
   - `type == "plot"`:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-1 -->
     ![{caption}]({ref})
     *{caption}*
     <!-- END EVIDENCE BLOCK -->
     ```
     > **Anti-pattern:** Do NOT list figures in a table at the end of the document. Every figure must be embedded inline with `![caption](path)` immediately before or after the paragraph that discusses it.
   - `type == "metric"`:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-2 -->
     **Key metric**: {description} — {value}
     <!-- END EVIDENCE BLOCK -->
     ```
   - `type == "test_result"`:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-3 -->
     **Validation**: {description}
     <!-- END EVIDENCE BLOCK -->
     ```
   - `type == "code"`:
     ```markdown
     <!-- EVIDENCE BLOCK: ev-4 -->
     See implementation in `{ref}`: {description}
     <!-- END EVIDENCE BLOCK -->
     ```
3. Before embedding each plot evidence block, verify that the `ref` path exists (Glob check). If missing, mark as `<!-- EVIDENCE BLOCK: {id} (MISSING FILE: {ref}) -->` and log a warning.
4. Save pre-assembled evidence blocks to `write/evidence_blocks/{section_id}.md`.

#### Step 2b: Section-by-Section Drafting

Generate each section in the order specified by `drafting_order` in `section_contracts.json`. For each section:

**Context provided** (scoped to prevent context bloat):
- The section's own contract (from `section_contracts.json`)
- The global argument thread (2-3 sentences)
- Pre-assembled evidence blocks for this section (from `write/evidence_blocks/{section_id}.md`)
- The relevant claims from `write_inputs.json` (only claims listed in the section's `claim_ids`)
- Preceding section summaries: for each already-drafted section, provide only the section title + first paragraph + last paragraph
- Audience and style constraints from the mode template

For each section, Claude:
1. Reads the section contract, evidence blocks, and relevant claims
2. Writes the section prose, integrating pre-placed evidence blocks naturally into the narrative
3. Ensures the section:
   - Opens with a transition from the previous section (`transition_from_previous` field)
   - Covers all key points listed in the contract
   - References all pre-placed evidence with concrete quantitative observations (not passive "see figure below")
   - Stays within the `max_words` budget (±10%)
   - Matches the style, tone, and formality constraints
   - Closes with a transition to the next section (`transition_to_next` field)
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

Save the narrative arc assessment to `write/narrative_arc_assessment.md`. This feeds into the Phase 3d global coherence pass.

---

### Phase 3: Review

#### Step 3a: MAGI Cross-Review

> Skip this step if `--depth low`. For `--depth low`, proceed directly to Step 3c (DocCI Validation).

> **Full prompts**: Read `references/review_prompts.md` for the complete MCP call specifications. Execute both calls **simultaneously**.

Execute two parallel review calls:
- **Gemini (BALTHASAR)** — Content Quality Review: claim support, evidence integration, narrative flow, audience fit, completeness. Save to `write/gemini_review.md`.
- **Codex (CASPER)** — Structure & Evidence Review: word budget compliance, evidence completeness, citation integrity, LaTeX correctness, structural compliance. Save to `write/codex_review.md`.

If `--claude-only`: see the Claude-Only Fallback in `references/review_prompts.md`.

#### Step 3b: Devil's Advocate Review

> Skip this step if `--depth low` or `--depth medium`. Only execute for `--depth high`.

> **Full spec**: Read `references/depth_high.md` for selection criteria, the full adversarial prompt, Claude-Only fallback, and fix application rules.

Identify high-stakes sections (most critical/major issues from Step 3a + required sections with evidence/method/result narrative roles). Apply adversarial review to at most 3 sections. Save each result to `write/devils_advocate_{section_id}.md`.

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
   > **Data integrity:** Do NOT fabricate data for illustrative plots. If no data exists for a needed visualization, note the gap textually rather than generating synthetic values.

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

Determine the plugin root directory by navigating two levels up from this skill's base directory. The `Base directory for this skill:` header injected by Claude Code provides the absolute path. Then run:

```bash
uv run python <plugin_root>/utils/validate_draft.py write/revised_draft.md write/section_contracts.json write/write_inputs.json
```

> **Important**: Do NOT generate a validation script at runtime. Use the maintained `utils/validate_draft.py` utility.

**On validation failure**: Claude reads the validation report, fixes the identified issues in `write/revised_draft.md`, and re-runs validation. Maximum 2 fix iterations.

Save the validation report to `write/validation_report.json`.

---

### Phase 4: Finalize

#### Step 4a: Macro Resolution Fallback

Before presenting to the user, scan the draft for any remaining unresolved macros. If MAGI model outputs introduced any `{{fig:id}}` or `{{ref:id}}` patterns during review, resolve them now:

1. Scan `write/revised_draft.md` for patterns matching `{{fig:...}}` or `{{ref:...}}`.
2. If any are found, read `references/macro_resolution.md` for the full script source, write it to `write/resolve_macros.py`, then run:
   ```bash
   uv run python write/resolve_macros.py write/revised_draft.md write/write_inputs.json write/citation_ledger.json
   ```
   If unresolved macros remain, Claude manually resolves them by reading the intake data and making inline replacements.
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

3. Generate `write/writing_state.json` using the schema in `references/intake_schemas.md`.

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
