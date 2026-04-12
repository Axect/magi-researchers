# Research Workflow — Full Pipeline

## Description
Runs the complete research pipeline: Brainstorming → Planning → Implementation → Testing & Visualization → Reporting. Orchestrates all phases with user checkpoints between each.

## Usage
```
/research "research topic" [--domain physics|ai_ml|statistics|mathematics|paper] [--weights '{"novelty":0.4,...}'|adaptive] [--depth low|medium|high|max] [--personas N] [--claude-only] [--substitute "Gemini -> Opus"] [--resume <output_dir>]
```

## Arguments
- `$ARGUMENTS` — The research topic (required) and optional flags:
  - `--domain` — Research domain (physics, ai_ml, statistics, mathematics, paper). Auto-inferred if omitted.
  - `--weights` — Scoring mode for direction ranking:
    - **Omitted (default)**: Holistic ranking — Claude ranks directions by expert judgment with detailed rationale. No numeric weights.
    - **JSON object**: Weighted scoring with dimension weights summing to 1.0.
    - **`adaptive`**: Claude analyzes the prompt and recommends weights for user confirmation.
    See `/research-brainstorm` for full details.
  - `--depth` — Controls brainstorm review depth (default: `medium`):
    - `low` — Skip cross-review, go directly to synthesis (fastest, lowest cost)
    - `medium` — Standard one-shot cross-review (default)
    - `high` — Cross-review + adversarial debate (most thorough, highest cost)
    - `max` — Hierarchical MAGI-in-MAGI: N persona subagents run parallel mini-MAGI pipelines, then meta-review + adversarial debate across all perspectives (deepest, highest cost)
  - `--personas N|auto` — Number of domain-specialist subagents for `--depth max` (default: `auto`, range: 2-4). When `auto`, Claude analyzes the topic to determine the optimal persona count. Ignored for other depth levels.
  - `--claude-only` — Replace all Gemini/Codex MCP calls with Claude Agent subagents across all phases. Use when external model endpoints are unavailable. Forwarded to all sub-skills automatically.
  - `--substitute "Agent -> Opus"` — Replace a specific MAGI agent with Claude (Opus). Accepted: `"Gemini -> Opus"`, `"Codex -> Opus"`. Can be specified multiple times. Forwarded to all sub-skills. If both agents are substituted, equivalent to `--claude-only`. Mutually exclusive with `--claude-only` (`--claude-only` takes precedence).
  - `--resume <output_dir>` — Resume an interrupted pipeline from a previous output directory. See **Resume Protocol** below.

## Instructions

> **Shared rules**: Read `${CLAUDE_PLUGIN_ROOT}/shared/rules.md` before starting. §MCP, §Visualization, §LaTeX, §PhaseGate, §Substitute apply to this skill.
> **Inline fallback** (if shared rules unavailable): Gemini models: gemini-3.1-pro-preview → gemini-2.5-pro → Claude. Codex: gpt-5.4. All math in LaTeX only (no Unicode). scienceplots `['science','nature']`, 300dpi PNG+PDF, Nature widths (3.5/7.2in). Use `@filepath` for MCP file refs; subagents use `Read` tool.

### MCP Tool Rules
See §MCP, §Visualization, §LaTeX in shared rules. Additionally:
- **Codex**: Use `mcp__codex-cli__brainstorm` for ideation, `mcp__codex-cli__ask-codex` for analysis/review.
- **Context7**: Use during implementation phase for library documentation lookups.
- **When to search**: prior work verification, methodological precedents, dataset/library availability, related approaches, fact-checking quantitative claims

### Path Safety Rule

**ALL artifacts MUST be written under `{output_dir}/`.** Never write files directly to the project root or any path outside `outputs/`.

- `{output_dir}` is the **absolute path** stored in `.workspace.json` at the output directory root.
- **Before writing any file**: if `{output_dir}` is uncertain (e.g., after context compression), recover it:
  1. `Glob` for `outputs/*/.workspace.json`, select the most recently modified match.
  2. `Read` the file and extract `output_dir`.
- **Subagent prompts and sub-skill invocations**: always include the absolute `{output_dir}` path.

When this skill is invoked, execute the full research pipeline below. **Always pause for user confirmation between phases.**

---

### Phase Gate Protocol
See §PhaseGate in shared rules. Phase-specific checklists:

| Phase | Checklist Items |
|:------|:----------------|
| **Plan** | Completeness (all objectives addressed), methodology soundness, resource feasibility, risk identification |
| **Implement** | Code correctness, alignment with plan, error handling, dependency management |
| **Execute** | Exit code 0, `results/` populated (or EXISTING/PARTIAL with user acknowledgment), `pre_execution_status.json` written |
| **Test** | Tier 1 unit test coverage, edge case handling, Common Restrictions fulfilled (plot_manifest.json, dual format, dependency spec), result reproducibility |

---

### Resume Protocol

When `--resume <output_dir>` is provided, the pipeline skips initialization and infers the current phase from the **presence of key artifact files** in the output directory. This avoids requiring the LLM to maintain a separate state file — the artifacts themselves serve as checkpoints.

> **Unified semantics**: `--resume` always accepts the workspace root directory (e.g., `outputs/topic_20260309_v1/`). Whether resuming a research pipeline or a write sub-pipeline, the same root path is used. The system infers the correct sub-context internally.

**Phase inference rules** (evaluated top-down; first match wins):

| Condition | Inference | Action |
|:----------|:----------|:-------|
| `report.md` exists | Pipeline complete | Inform user; offer to re-run specific phases |
| `plots/plot_manifest.json` exists | Test phase complete | Resume from the Report phase |
| `results/pre_execution_status.json` exists (or `pre_execution_status.md` for legacy v0.8.x) | Execute phase complete | Resume from the Test phase |
| `src/` contains at least one source file | Implement phase complete | Resume from the Execute phase |
| `plan/research_plan.md` exists | Plan phase complete | Resume from the Implement phase |
| `brainstorm/synthesis.md` exists | Brainstorm phase complete | Resume from the Plan phase |
| None of the above | No phase complete | Start from the Brainstorm phase |

**Checkpoint hash validation** (when checkpoint files exist):
After determining the resume phase from artifact presence, check if a checkpoint file exists for the detected completed phase (e.g., `plan/plan_checkpoint.json`). If found:
1. Read the `input_hashes` field
2. Recompute hashes of the referenced input files
3. If hashes match: proceed with resume (inputs unchanged)
4. If hashes differ: warn the user that upstream artifacts have changed since this phase completed. Ask: "(a) Re-run this phase with updated inputs, or (b) Proceed anyway with existing outputs?"

> Checkpoint validation is additive — if no checkpoint file exists (e.g., from a pre-v0.9.0 run), fall back to the existing artifact-presence inference.

**Resume procedure:**
1. Read `{output_dir}/.workspace.json` to restore the absolute output path and metadata.
2. Use the `Glob` tool to check for each artifact in the order above.
3. Read the first few lines of the matched artifact to confirm it is non-empty.
4. Announce to the user: detected phase, output directory, and which phase will be resumed.
5. Read the domain template if `brainstorm/personas.md` or `brainstorm/weights.json` exist (to restore context).
6. Continue the pipeline from the inferred phase, skipping all prior phases.

> **Important**: On resume, do NOT re-create the output directory or overwrite existing artifacts. Append or create only the artifacts for the resumed phase and beyond.

---

### Artifact Contract Protocol

Before starting each phase (2 through 5), verify that the required predecessor artifacts exist and are non-empty. Use the `Glob` and `Read` tools for deterministic, tool-based validation — do not rely on memory or assumptions.

**Required artifacts per phase:**

| Phase | Required Artifacts | Validation Method |
|:------|:-------------------|:------------------|
| **Plan** | `brainstorm/synthesis.md` | Glob + Read first 3 lines (non-empty) |
| **Implement** | `plan/research_plan.md` | Glob + Read first 3 lines (non-empty) |
| **Execute** | At least one source file in `src/`, `plan/research_plan.md` with `execution_cmd` in frontmatter | Glob `src/**/*` + Read frontmatter |
| **Test** | At least one source file in `src/`, `plan/research_plan.md` | Glob `src/**/*` + Glob for plan. Note: `results/pre_execution_status.json` is optional — its absence means Tier 2 integration tests will be skipped (fall back to `.md` for legacy) |
| **Report** | `brainstorm/synthesis.md`, `plan/research_plan.md`, at least one source file in `src/`, `plots/plot_manifest.json` | Glob for each path |

**On validation failure:**
1. List the missing or empty artifacts with specific file paths.
2. Ask the user: "The following artifacts are missing: [list]. Would you like to (a) go back and generate them, or (b) proceed anyway?"
3. If the user chooses to proceed, continue with a warning note in the phase gate.

---

### Initialization

1. Parse `$ARGUMENTS`:
   - Extract the research topic (everything before flags or the entire string)
   - Extract domain if `--domain` is specified; otherwise infer from topic keywords
   - **Parse `--resume <output_dir>`**: If provided, skip steps 2-6 and execute the **Resume Protocol** above. The pipeline will jump directly to the inferred phase.
2. Create the output directory structure:
   ```
   outputs/{sanitized_topic}_{YYYYMMDD}_v{N}/
   ├── .workspace.json            # Workspace anchor (absolute path)
   ├── brainstorm/
   ├── plan/
   ├── src/
   ├── tests/
   └── plots/
   ```
   - Sanitize topic: lowercase, spaces→underscores, remove special chars, max 50 chars
   - Date format: YYYYMMDD (today's date)
   - Version: Glob for `outputs/{sanitized_topic}_{YYYYMMDD}_v*/` and set N = max existing + 1 (start at v1)
   - **Write workspace anchor**: Save `.workspace.json` at the output directory root:
     ```json
     {
       "output_dir": "{absolute_path_to_output_dir}",
       "topic": "{original_topic}",
       "domain": "{domain}",
       "created_at": "{ISO-8601 timestamp}"
     }
     ```
     Use `pwd` or equivalent to resolve the absolute path. This file anchors all subsequent file writes across all phases.
3. If the domain has a template in `${CLAUDE_PLUGIN_ROOT}/templates/domains/`, read it as context.
4. **Parse `--weights`**: If provided, validate and store. If omitted, domain defaults will be used by the brainstorm sub-skill.
5. **Parse `--depth`**: Accept `low`, `medium` (default), `high`, or `max`.
6. **Parse `--personas N|auto`**: Accept integer 2-4 or the string `auto` (default: `auto`). Only used when `--depth max`; ignored otherwise.
   - If `auto`: Defer persona count determination to the Brainstorm phase (sub-skill Step 0b), where Claude analyzes the topic to select the optimal N.
   - If an explicit integer is given: Use that value directly.
7. **Parse `--claude-only`**: Boolean flag (default: `false`). When present, all Gemini/Codex MCP calls across all phases are replaced with Claude Agent subagents. This flag is forwarded to every sub-skill invocation.
8. **Parse `--substitute`**: Accept zero or more `--substitute "Agent -> Opus"` flags. Valid agent names: `Gemini`, `Codex`. Valid target: `Opus`. Forwarded to every sub-skill invocation. Mutually exclusive with `--claude-only` (`--claude-only` takes precedence). If both agents are substituted, treat as `--claude-only`.
> **Flag forwarding**: `--claude-only` and `--substitute` flags are forwarded to **every** sub-skill invocation (brainstorm, plan, implement, execute, test, report). Each sub-skill applies the replacement rules to its own MCP calls.
9. Announce to the user: topic, domain, output directory, **active weights** (user-provided, holistic, or domain default), **depth level**, **persona count** (if `max`; show `auto` if no explicit `--personas` was given), **claude-only mode** (if active), and **agent substitutions** (if any).

---

### Brainstorm Phase

Execute the `/magi-researchers:research-brainstorm` workflow, **forwarding all flags**: `--domain`, `--weights`, `--depth`, `--personas` (only when `--depth max`), `--claude-only` (if active), and `--substitute` (if any).

**Step 0 — Setup:**
- Brainstorm sub-skill parses weights and depth flags
- Outputs: `brainstorm/weights.json`

**Step 0a — Research Direction Document (Phase 1-4):**
- Generates the research direction document including a broad literature survey (Phase 2: OpenAlex + WebSearch)
- Outputs: `brainstorm/research_direction.md`

**Step 0b — Persona Casting (informed by `research_direction.md`):**
- Assigns expert personas based on the research direction established in Step 0a
- Outputs: `brainstorm/personas.md`
- Personas are used in all subsequent phases where MAGI models are invoked

**Step 0c — Adaptive Weights (if `--weights adaptive`):**
- Claude analyzes the prompt and `research_direction.md` to recommend scoring weights for user confirmation
- Outputs: updated `brainstorm/weights.json`

**Step 0d — Pre-flight (persona-targeted searches):**
- Loads Phase 2 literature from `brainstorm/research_direction.md` (Sections 5 and 5a) as baseline context
- Runs only persona-targeted supplemental searches (no broad re-query of Step 0a literature)
- Outputs: `brainstorm/preflight_context.md`, per-persona briefing files

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

**Checkpoint**: Emit `brainstorm/brainstorm_checkpoint.json`:
```json
{
  "schema_version": "1.0.0",
  "phase": "brainstorm",
  "completed_at": "{ISO-8601 timestamp}",
  "input_hashes": {},
  "output_artifacts": ["brainstorm/synthesis.md", "brainstorm/gemini_ideas.md", "brainstorm/codex_ideas.md"]
}
```

**>>> USER CHECKPOINT: Confirm research direction <<<**

---

### Plan Phase

**Artifact Contract**: Verify `brainstorm/synthesis.md` exists and is non-empty (Glob + Read first 3 lines). On failure, follow the Artifact Contract Protocol above.

**Step 2a — Plan Drafting:**
1. Based on user-confirmed direction from the Brainstorm phase:
   - Define specific research objectives
   - Outline the technical approach (algorithms, models, data)
   - Specify implementation requirements (language, libraries, compute)
   - Design the test strategy
   - Plan visualizations
2. Save to `plan/research_plan.md`, beginning with a YAML frontmatter block:
   ```yaml
   ---
   title: "{research topic}"
   domain: "{physics|ai_ml|statistics|mathematics|paper}"
   languages: ["{primary language(s) planned}"]
   ecosystem: ["{package manager(s) planned}"]
   execution_cmd: ""          # filled in after the Implement phase
   dry_run_cmd: ""            # filled in after the Implement phase
   expected_outputs: []       # filled in after the Implement phase
   estimated_runtime: ""      # filled in after the Implement phase
   ---
   ```
   Leave execution fields empty for now — the Implement phase will populate them.

**Step 2b — Murder Board:**

Submit the research plan to Gemini as a hostile reviewer to stress-test for critical flaws:

```
mcp__gemini-cli__ask-gemini(
  prompt: "You are a hostile but fair research reviewer. Your job is to find fatal flaws in this research plan — flaws that would cause the research to fail, produce invalid results, or waste significant effort.\n\nAttack the plan on these dimensions:\n1. **Methodological flaws**: Are there fundamental errors in the proposed approach?\n2. **Missing assumptions**: What unstated assumptions could invalidate results?\n3. **Scalability risks**: Will this approach break on realistic problem sizes?\n4. **Data/resource gaps**: Are required datasets, compute, or libraries actually available?\n5. **Novelty concerns**: Has this exact approach been tried and failed before?\n\nFor each flaw found, rate its severity (Critical/Major/Minor) and explain the likely failure mode.\n\nResearch Plan:\n@{output_dir}/plan/research_plan.md",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```

Save to `plan/murder_board.md`.

> **If `--claude-only` or Gemini is substituted**: Per §SubagentExec — **Adversarial-Critical** reviewer: Read `research_plan.md`. Attack on methodological flaws, missing assumptions, scalability risks, data/resource gaps, novelty concerns. Save to `plan/murder_board.md`.

**Step 2c — Mitigations:**

Claude reviews each flaw from the murder board and documents a mitigation strategy:

1. For each identified flaw:
   - Acknowledge or dispute the flaw (with reasoning)
   - If acknowledged: propose a concrete mitigation (plan modification, fallback strategy, or scoping change)
   - Rate mitigation confidence: `High`, `Medium`, `Low`
2. If any mitigation has `Low` confidence, perform **one revision pass**: update the relevant section of `research_plan.md` and re-assess.
3. Save to `plan/mitigations.md`.

**Phase Gate: Plan** — Execute the Phase Gate Protocol with Plan checklist.

**Checkpoint**: Emit `plan/plan_checkpoint.json`:
```json
{
  "schema_version": "1.0.0",
  "phase": "plan",
  "completed_at": "{ISO-8601 timestamp}",
  "input_hashes": {
    "brainstorm/synthesis.md": "sha256:{hash}"
  },
  "output_artifacts": ["plan/research_plan.md", "plan/murder_board.md", "plan/mitigations.md", "plan/phase_gate.md"]
}
```

**>>> USER CHECKPOINT: Approve research plan <<<**
Present to user: plan summary, murder board highlights, mitigations, and gate result.

---

### Implement Phase

**Artifact Contract**: Verify `plan/research_plan.md` exists and is non-empty (Glob + Read first 3 lines). On failure, follow the Artifact Contract Protocol above.

Execute the `/magi-researchers:research-implement` workflow:

1. Follow `research_plan.md` to implement code in `src/`
2. Use Context7 for library documentation as needed
3. Validate basic functionality

**Phase Gate: Implement** — Execute the Phase Gate Protocol with Implement checklist.

**Checkpoint**: Emit `src/implement_checkpoint.json`:
```json
{
  "schema_version": "1.0.0",
  "phase": "implement",
  "completed_at": "{ISO-8601 timestamp}",
  "input_hashes": {
    "plan/research_plan.md": "sha256:{hash}"
  },
  "output_artifacts": ["src/phase_gate.md"]
}
```

4. Present implementation summary to user, including gate result.

**>>> USER CHECKPOINT: Review implementation <<<**

---

### Execute Phase

**Artifact Contract**: Verify at least one source file in `src/` and `plan/research_plan.md` with
`execution_cmd` in frontmatter. On failure, follow the Artifact Contract Protocol above.

Execute the `/magi-researchers:research-execute` workflow:

- Read `execution_cmd` and `dry_run_cmd` from `plan/research_plan.md` YAML frontmatter
- Run dry-run first (fast sanity check); fix minor errors before full run
- Run full execution; capture output to `results/run_log.txt`
- Write `results/pre_execution_status.json` (state: SUCCESS / FAILED / PARTIAL / EXISTING)
- For long-running jobs (> 15 min): inform user, recommend running externally then resuming

**Phase Gate: Execute** — Execute the Phase Gate Protocol with Execute checklist.

**Checkpoint**: Emit `results/execute_checkpoint.json`:
```json
{
  "schema_version": "1.0.0",
  "phase": "execute",
  "completed_at": "{ISO-8601 timestamp}",
  "input_hashes": {
    "plan/research_plan.md": "sha256:{hash}",
    "src/": "sha256:{combined_hash}"
  },
  "output_artifacts": ["results/pre_execution_status.json", "results/run_log.txt"]
}
```

**>>> USER CHECKPOINT: Review execution results <<<**
Present: execution status, generated artifacts, any errors encountered.

---

### Test & Visualize Phase

**Artifact Contract**: Verify at least one source file exists in `src/` (Glob `src/**/*`) and
`plan/research_plan.md` exists. `results/pre_execution_status.json` is optional — its absence causes
Tier 2 integration tests to be skipped (not a pipeline failure). Fall back to `.md` for legacy workspaces.

Execute the `/magi-researchers:research-test` workflow:

**Step 0 — Workspace Detection:**
- Scan `src/` for package managers and file extensions to detect languages and ecosystems
- Check `results/pre_execution_status.json` to determine data availability for Tier 2 tests

**Step 1 — Test Strategy Discussion:**
- Consult Gemini for test suggestions; propose two-tier plan (Tier 1 unit / Tier 2 integration)
- Choose testing tools matching detected workspace languages
- Present to user for approval

**Step 2 — Test Implementation:**
- Write Tier 1 unit tests (mock-based, always run)
- Write Tier 2 integration tests (guarded by `results/` availability)
- Run tests with the native test runner for each detected language
- Report results

**Step 3 — Visualization:**
- Choose visualization tools matching detected workspace
- Load data from `results/` if available; compute inline otherwise
- All plots must follow Common Restrictions: PNG + PDF/SVG, registered in `plot_manifest.json`

**Step 4 — Plot Manifest:**
- Generate `plots/plot_manifest.json` using the fixed schema
- All plots registered here regardless of which tool generated them
- This manifest is the primary input for the Report phase's plot integration

**Phase Gate: Test** — Execute the Phase Gate Protocol with Test checklist.

**Checkpoint**: Emit `tests/test_checkpoint.json`:
```json
{
  "schema_version": "1.0.0",
  "phase": "test",
  "completed_at": "{ISO-8601 timestamp}",
  "input_hashes": {
    "src/": "sha256:{combined_hash}",
    "results/pre_execution_status.json": "sha256:{hash} (omit key if file absent)"
  },
  "output_artifacts": ["plots/plot_manifest.json"]
}
```

If `results/pre_execution_status.json` does not exist, omit it from `input_hashes` rather than storing a placeholder.

**>>> USER CHECKPOINT: Review test results and visualizations <<<**

---

### Report Phase

**Artifact Contract**: Verify all of the following exist (Glob for each): `brainstorm/synthesis.md`, `plan/research_plan.md`, at least one source file in `src/`, and `plots/plot_manifest.json`. On failure, follow the Artifact Contract Protocol above.

If `--depth max` was used: also check for `brainstorm/all_conclusions.md`, `brainstorm/meta_review_gemini.md`, `brainstorm/meta_review_codex.md`, `brainstorm/meta_debate_gemini.md`, `brainstorm/meta_debate_codex.md` (these replace `debate_round2_*.md` files)

Execute the `/magi-researchers:research-report` workflow:

**Step 0 — Gather & Health Check:**
- Inventory all phase outputs
- Read `plots/plot_manifest.json` (create if missing but plots exist)
- Verify all plot files are present and valid

**Step 0.5 — Plot Style Validation:**
- Validate all existing plots for scienceplots compliance (`['science', 'nature']` style)
- Regenerate non-compliant plots before content assembly
- Update `plots/plot_manifest.json` with style metadata

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
- **Agent substitution**: If `--claude-only` or `--substitute` is active, substituted agents use Claude Agent subagents with their respective cognitive styles (Creative-Divergent for Gemini, Analytical-Convergent for Codex). Non-substituted agents use their MCP tools normally.
- Gemini (BALTHASAR) reviews for scientific rigor: orphaned claims, orphaned plots, weak claim-evidence links, caption quality
- Codex (CASPER) reviews for visualization quality: missing visualizations, plot-narrative mismatch, encoding improvements, reproducibility gaps, **and scienceplots style compliance**
- Claude (MELCHIOR) synthesizes both reviews — consensus issues are high-priority fixes, divergent suggestions evaluated on merit

**Step 5 — Write Final Report:**
- Save finalized `report.md` with version tracking (`report_versions.json`)
- Schema version is `1.1.0`; each version entry includes a structured `changes` array tracking what was modified
- Present summary with plot integration statistics

**Step 6 — Feedback Loop:**
- Report skill handles Tier 1 (Cosmetic) and Tier 2 (Visualization) internally
- If Tier 3 escalation occurs, control returns to orchestrator Step R2

**>>> USER CHECKPOINT: Review and finalize report <<<**

---

### Report Outer Loop (Tier 3 Handling)

**Step R1: Checkpoint**

Present report location, version, any Tier 1/2 revisions already applied. Options:
- **Approve** → Completion
- **Cosmetic/Visualization** → re-enter Report skill Step 6
- **Substantive** → Step R2

**Step R2: Pipeline Re-entry (max 2 iterations)**

1. Classify re-entry point from feedback:

   | Trigger | Re-entry Phase | Phases to re-run |
   |:--------|:---------------|:-----------------|
   | Methodology/approach change | Plan | Plan → Implement → Execute → Test → Report |
   | Code bug, new analysis | Implement | Implement → Execute → Test → Report |
   | Different parameters, rerun | Execute | Execute → Test → Report |
   | New visualization strategy | Test | Test → Report |

2. Present re-entry plan to user for confirmation.
3. On confirmation:
   a. Archive `report.md` → `report_v{N}.md`, update `report_versions.json`
   b. Delete `report.md` (reset resume protocol)
   > **Rollback note**: If the re-entry pipeline fails before a new `report.md` is produced, inform the user that the previous report is preserved as `report_v{N}.md` and can be restored by copying it back to `report.md`.
   c. Execute pipeline from re-entry phase
   d. Report skill generates new version → return to Step R1

---

### Completion

Announce completion with:
- Output directory location
- Final report version and revision history
- Summary of all generated artifacts
- Any follow-up suggestions

## Notes
- If any phase fails, stop and inform the user with clear error context
- User can skip phases by saying "skip" at any checkpoint
- The workflow state is maintained through artifact files — use `--resume <output_dir>` to resume an interrupted pipeline from the last completed phase
- Each phase skill can also be run independently outside this pipeline
