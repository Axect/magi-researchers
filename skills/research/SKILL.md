# Research Workflow — Full Pipeline

## Description
Runs the complete research pipeline: Brainstorming → Planning → Implementation → Testing & Visualization → Reporting. Orchestrates all phases with user checkpoints between each.

## Usage
```
/research "research topic" [--domain physics|ai_ml|statistics|mathematics|paper] [--weights '{"novelty":0.4,"feasibility":0.3,"impact":0.3}'] [--depth low|medium|high|max] [--personas N] [--resume <output_dir>]
```

## Arguments
- `$ARGUMENTS` — The research topic (required) and optional flags:
  - `--domain` — Research domain (physics, ai_ml, statistics, mathematics, paper). Auto-inferred if omitted.
  - `--weights` — JSON object of scoring weights for direction ranking. See `/research-brainstorm` for defaults per domain.
  - `--depth` — Controls brainstorm review depth (default: `medium`):
    - `low` — Skip cross-review, go directly to synthesis (fastest, lowest cost)
    - `medium` — Standard one-shot cross-review (default)
    - `high` — Cross-review + adversarial debate (most thorough, highest cost)
    - `max` — Hierarchical MAGI-in-MAGI: N persona subagents run parallel mini-MAGI pipelines, then meta-review + adversarial debate across all perspectives (deepest, highest cost)
  - `--personas N|auto` — Number of domain-specialist subagents for `--depth max` (default: `auto`, range: 2-5). When `auto`, Claude analyzes the topic to determine the optimal persona count. Ignored for other depth levels.
  - `--resume <output_dir>` — Resume an interrupted pipeline from a previous output directory. See **Resume Protocol** below.

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-3-pro-preview"` (fallback)
  3. `model: "gemini-2.5-pro"` (last resort)
- **Codex**: Use `mcp__codex-cli__brainstorm` for ideation, `mcp__codex-cli__ask-codex` for analysis/review.
- **File References**: Use `@filepath` in the prompt parameter to pass saved artifacts (e.g., `@plan/research_plan.md`)
  instead of pasting file content inline. The CLI tools read files directly, preventing context truncation.
- **Context7**: Use `mcp__plugin_context7_context7__query-docs` for library documentation lookups during implementation.
- **Visualization**: Use `matplotlib` with `scienceplots` (`['science', 'nature']` style). Save plots as PNG (300 dpi) and PDF.
- **LaTeX**: Use LaTeX for all mathematical expressions in output documents. Inline: `$...$`. Display equations: `$$` on its own line with the equation on a separate line:
  ```
  $$
  equation
  $$
  ```
  Never write display equations on a single line as `$$..equation..$$`.

When this skill is invoked, execute the full research pipeline below. **Always pause for user confirmation between phases.**

---

### Phase Gate Protocol

Phase gates are lightweight quality checkpoints inserted **before** each USER CHECKPOINT. Each gate follows the same structure but uses phase-specific criteria.

**Gate procedure:**
1. **Self-assessment**: Claude evaluates the phase output against the checklist below and assigns a confidence level: `High`, `Medium`, or `Low`.
2. **Conditional MAGI mini-review** (if confidence is `Medium` or `Low`):
   - Send the phase output to one MAGI model for a focused review (Gemini for scientific/plan quality, Codex for implementation/test quality)
   - The review prompt should target the specific checklist items that scored low
3. **Go/No-Go synthesis**: Claude writes a brief gate report with:
   - Confidence level and justification
   - Checklist scores (pass/partial/fail for each item)
   - Issues found (if any) and applied fixes
   - Go/No-Go decision
4. Save to `{phase_dir}/phase_gate.md` (e.g., `plan/phase_gate.md`)

**Phase-specific checklists:**

| Phase | Checklist Items |
|:------|:----------------|
| **Plan** (Phase 2) | Completeness (all objectives addressed), methodology soundness, resource feasibility, risk identification |
| **Implement** (Phase 3) | Code correctness, alignment with plan, error handling, dependency management |
| **Test** (Phase 4) | Coverage adequacy, edge case handling, visualization quality, result reproducibility |

> If a gate returns **No-Go**, Claude must fix the identified issues before presenting to the user. Maximum 1 fix iteration per gate.

---

### Resume Protocol

When `--resume <output_dir>` is provided, the pipeline skips initialization and infers the current phase from the **presence of key artifact files** in the output directory. This avoids requiring the LLM to maintain a separate state file — the artifacts themselves serve as checkpoints.

**Phase inference rules** (evaluated top-down; first match wins):

| Condition | Inference | Action |
|:----------|:----------|:-------|
| `report.md` exists | Pipeline complete | Inform user; offer to re-run specific phases |
| `plots/plot_manifest.json` exists | Phase 4 complete | Resume from Phase 5 (Reporting) |
| `src/` contains at least one `.py` file | Phase 3 complete | Resume from Phase 4 (Testing) |
| `plan/research_plan.md` exists | Phase 2 complete | Resume from Phase 3 (Implementation) |
| `brainstorm/synthesis.md` exists | Phase 1 complete | Resume from Phase 2 (Planning) |
| None of the above | No phase complete | Start from Phase 1 (Brainstorming) |

**Resume procedure:**
1. Use the `Glob` tool to check for each artifact in the order above.
2. Read the first few lines of the matched artifact to confirm it is non-empty.
3. Announce to the user: detected phase, output directory, and which phase will be resumed.
4. Read the domain template if `brainstorm/personas.md` or `brainstorm/weights.json` exist (to restore context).
5. Continue the pipeline from the inferred phase, skipping all prior phases.

> **Important**: On resume, do NOT re-create the output directory or overwrite existing artifacts. Append or create only the artifacts for the resumed phase and beyond.

---

### Artifact Contract Protocol

Before starting each phase (2 through 5), verify that the required predecessor artifacts exist and are non-empty. Use the `Glob` and `Read` tools for deterministic, tool-based validation — do not rely on memory or assumptions.

**Required artifacts per phase:**

| Phase | Required Artifacts | Validation Method |
|:------|:-------------------|:------------------|
| **Phase 2** (Plan) | `brainstorm/synthesis.md` | Glob + Read first 3 lines (non-empty) |
| **Phase 3** (Implement) | `plan/research_plan.md` | Glob + Read first 3 lines (non-empty) |
| **Phase 4** (Test) | At least one `.py` file in `src/`, `plan/research_plan.md` | Glob for `src/**/*.py` + Glob for plan |
| **Phase 5** (Report) | `brainstorm/synthesis.md`, `plan/research_plan.md`, at least one `.py` in `src/`, `plots/plot_manifest.json` | Glob for each path |

**On validation failure:**
1. List the missing or empty artifacts with specific file paths.
2. Ask the user: "The following artifacts are missing: [list]. Would you like to (a) go back and generate them, or (b) proceed anyway?"
3. If the user chooses to proceed, continue with a warning note in the phase gate.

---

### Phase 0: Initialization

1. Parse `$ARGUMENTS`:
   - Extract the research topic (everything before flags or the entire string)
   - Extract domain if `--domain` is specified; otherwise infer from topic keywords
   - **Parse `--resume <output_dir>`**: If provided, skip steps 2-6 and execute the **Resume Protocol** above. The pipeline will jump directly to the inferred phase.
2. Create the output directory structure:
   ```
   outputs/{sanitized_topic}_{YYYYMMDD}_v{N}/
   ├── brainstorm/
   ├── plan/
   ├── src/
   ├── tests/
   └── plots/
   ```
   - Sanitize topic: lowercase, spaces→underscores, remove special chars, max 50 chars
   - Date format: YYYYMMDD (today's date)
   - Version: Glob for `outputs/{sanitized_topic}_{YYYYMMDD}_v*/` and set N = max existing + 1 (start at v1)
3. If the domain has a template in `${CLAUDE_PLUGIN_ROOT}/templates/domains/`, read it as context.
4. **Parse `--weights`**: If provided, validate and store. If omitted, domain defaults will be used by the brainstorm sub-skill.
5. **Parse `--depth`**: Accept `low`, `medium` (default), `high`, or `max`.
6. **Parse `--personas N|auto`**: Accept integer 2-5 or the string `auto` (default: `auto`). Only used when `--depth max`; ignored otherwise.
   - If `auto`: Defer persona count determination to Phase 1 (brainstorm sub-skill Step 0b), where Claude analyzes the topic to select the optimal N.
   - If an explicit integer is given: Use that value directly.
7. Announce to the user: topic, domain, output directory, **active weights** (user-provided or domain default), **depth level**, and **persona count** (if `max`; show `auto` if no explicit `--personas` was given).

---

### Phase 1: Brainstorming

Execute the `/magi-researchers:research-brainstorm` workflow, **forwarding all flags**: `--domain`, `--weights`, `--depth`, and `--personas` (only when `--depth max`).

**Step 0 & 0b — Setup & Persona Casting:**
- Brainstorm sub-skill parses weights and depth, assigns expert personas
- Outputs: `brainstorm/weights.json`, `brainstorm/personas.md`
- Personas are used in all subsequent phases where MAGI models are invoked

**Step 1a — Parallel Brainstorming (with personas):**
- Gemini and Codex brainstorm independently with assigned personas
- Save to `brainstorm/gemini_ideas.md` and `brainstorm/codex_ideas.md`

**Step 1b — Cross-Check (`--depth medium|high`):**
- Gemini reviews Codex ideas → `brainstorm/gemini_review_of_codex.md`
- Codex reviews Gemini ideas → `brainstorm/codex_review_of_gemini.md`
- Skipped if `--depth low`

**Step 1b+ — Adversarial Debate (`--depth high` only):**
- Top 3 disagreements identified → Round 2 defend/concede/revise
- Outputs: `brainstorm/debate_round2_gemini.md`, `brainstorm/debate_round2_codex.md`

**Steps 1-max-a~d — Hierarchical MAGI-in-MAGI (`--depth max` only):**
- **Layer 1**: N persona subagents spawned in parallel, each running a mini-MAGI pipeline (Gemini brainstorm + Codex brainstorm + cross-review + conclusion) → `brainstorm/persona_{i}/`
- **Layer 2**: Gemini and Codex meta-review all N conclusions; Claude extracts top 3 disagreements; adversarial debate (defend/concede/revise) → `brainstorm/meta_review_*.md`, `brainstorm/meta_debate_*.md`
- **Layer 3**: Claude produces enriched synthesis with cross-persona consensus, unique contributions, debate resolution, and emergent insights → `brainstorm/synthesis.md`

**Step 1c — Synthesis (with weighted scoring):**
- Claude reads all documents, applies weights from `weights.json` to rank directions
- Creates `brainstorm/synthesis.md` with weighted scores and debate resolution (if applicable)
- Present top research directions to user

**>>> USER CHECKPOINT: Confirm research direction <<<**

---

### Phase 2: Research Planning

**Artifact Contract**: Verify `brainstorm/synthesis.md` exists and is non-empty (Glob + Read first 3 lines). On failure, follow the Artifact Contract Protocol above.

**Step 2a — Plan Drafting:**
1. Based on user-confirmed direction from Phase 1:
   - Define specific research objectives
   - Outline the technical approach (algorithms, models, data)
   - Specify implementation requirements (language, libraries, compute)
   - Design the test strategy
   - Plan visualizations
2. Save to `plan/research_plan.md`

**Step 2b — Murder Board:**

Submit the research plan to Gemini as a hostile reviewer to stress-test for critical flaws:

```
mcp__gemini-cli__ask-gemini(
  prompt: "You are a hostile but fair research reviewer. Your job is to find fatal flaws in this research plan — flaws that would cause the research to fail, produce invalid results, or waste significant effort.\n\nAttack the plan on these dimensions:\n1. **Methodological flaws**: Are there fundamental errors in the proposed approach?\n2. **Missing assumptions**: What unstated assumptions could invalidate results?\n3. **Scalability risks**: Will this approach break on realistic problem sizes?\n4. **Data/resource gaps**: Are required datasets, compute, or libraries actually available?\n5. **Novelty concerns**: Has this exact approach been tried and failed before?\n\nFor each flaw found, rate its severity (Critical/Major/Minor) and explain the likely failure mode.\n\nResearch Plan:\n@{output_dir}/plan/research_plan.md",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```

Save to `plan/murder_board.md`.

**Step 2c — Mitigations:**

Claude reviews each flaw from the murder board and documents a mitigation strategy:

1. For each identified flaw:
   - Acknowledge or dispute the flaw (with reasoning)
   - If acknowledged: propose a concrete mitigation (plan modification, fallback strategy, or scoping change)
   - Rate mitigation confidence: `High`, `Medium`, `Low`
2. If any mitigation has `Low` confidence, perform **one revision pass**: update the relevant section of `research_plan.md` and re-assess.
3. Save to `plan/mitigations.md`.

**Phase Gate: Plan** — Execute the Phase Gate Protocol with Plan checklist.

**>>> USER CHECKPOINT: Approve research plan <<<**
Present to user: plan summary, murder board highlights, mitigations, and gate result.

---

### Phase 3: Implementation

**Artifact Contract**: Verify `plan/research_plan.md` exists and is non-empty (Glob + Read first 3 lines). On failure, follow the Artifact Contract Protocol above.

Execute the `/magi-researchers:research-implement` workflow:

1. Follow `research_plan.md` to implement code in `src/`
2. Use Context7 for library documentation as needed
3. Validate basic functionality

**Phase Gate: Implement** — Execute the Phase Gate Protocol with Implement checklist.

4. Present implementation summary to user, including gate result.

**>>> USER CHECKPOINT: Review implementation <<<**

---

### Phase 4: Testing & Visualization

**Artifact Contract**: Verify at least one `.py` file exists in `src/` (Glob `src/**/*.py`) and `plan/research_plan.md` exists. On failure, follow the Artifact Contract Protocol above.

Execute the `/magi-researchers:research-test` workflow:

**Step 1 — Test Design:**
- Consult Gemini for test case suggestions
- Claude synthesizes test strategy
- Present to user for approval

**Step 2 — Test Execution:**
- Write tests in `tests/`
- Run with `uv run pytest tests/ -v`
- Report results

**Step 3 — Visualization:**
- Generate plots using matplotlib + scienceplots (`['science', 'nature']` style)
- Save as PNG (300 dpi) and PDF in `plots/`

**Step 4 — Plot Manifest:**
- Generate `plots/plot_manifest.json` with metadata for every plot: plot_id, file paths, description, section_hint, publication-ready caption, and markdown snippet
- This manifest is the primary input for Phase 5's plot integration

**Phase Gate: Test** — Execute the Phase Gate Protocol with Test checklist.

**>>> USER CHECKPOINT: Review test results and visualizations <<<**

---

### Phase 5: Reporting

**Artifact Contract**: Verify all of the following exist (Glob for each): `brainstorm/synthesis.md`, `plan/research_plan.md`, at least one `.py` in `src/`, and `plots/plot_manifest.json`. On failure, follow the Artifact Contract Protocol above.

Execute the `/magi-researchers:research-report` workflow:

**Step 0 — Gather & Health Check:**
- Inventory all phase outputs
- Read `plots/plot_manifest.json` (create if missing but plots exist)
- Verify all plot files are present and valid

**Step 1 — Content Assembly & Plot Mapping:**
- Read all phase artifacts
- Map manifest plots to report sections using `section_hint` tags

**Step 2 — Report Draft with Integrated Plots:**
- Generate `report.md` using `${CLAUDE_PLUGIN_ROOT}/templates/report_template.md` structure
- Actively embed plots from the manifest with contextualizing paragraphs and quantitative observations
- Include all sections: Background, Brainstorming, Methodology, Implementation, Results, Testing, Conclusion

**Step 3 — Gap Detection & Plot Generation Loop (max 2 iterations):**
- Identify claims without supporting figures or results needing visualization
- Generate new plots (write matplotlib code → execute → save to `plots/` → update manifest)
- Re-draft affected sections with newly generated plots

**Step 4 — MAGI Traceability Review (parallel cross-verification):**
- **Inject personas**: If `brainstorm/personas.md` exists, prepend the assigned personas to Gemini and Codex review prompts for continuity
- Gemini (BALTHASAR) reviews for scientific rigor: orphaned claims, orphaned plots, weak claim-evidence links, caption quality
- Codex (CASPER) reviews for visualization quality: missing visualizations, plot-narrative mismatch, encoding improvements, reproducibility gaps
- Claude (MELCHIOR) synthesizes both reviews — consensus issues are high-priority fixes, divergent suggestions evaluated on merit

**Step 5 — Write Final Report:**
- Save finalized `report.md`
- Present summary with plot integration statistics

**>>> USER CHECKPOINT: Review and finalize report <<<**

---

### Completion

Announce completion with:
- Output directory location
- Summary of all generated artifacts
- Any follow-up suggestions (e.g., expand implementation, add more tests, explore alternative directions)

## Notes
- If any phase fails, stop and inform the user with clear error context
- User can skip phases by saying "skip" at any checkpoint
- The workflow state is maintained through artifact files — use `--resume <output_dir>` to resume an interrupted pipeline from the last completed phase
- Each phase skill can also be run independently outside this pipeline
