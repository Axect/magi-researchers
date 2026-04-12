# Changelog

All notable changes to MAGI Researchers are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [0.19.0] — 2026-04-12

### Added
- **Research Direction Document (Step 0a)** — New foundational step replacing Question Orientation and Research Question Brainstorming. Produces an 8-section structured document (`brainstorm/research_direction.md`) through 4 phases:
  - Phase 1: Core Framing — user-driven dialogue extracting research question, motivation, hypothesis, expected results, methodology scope, and constraints (1-5 questions, skip logic for rich prompts)
  - Phase 2: Literature & Landscape Survey — automated OpenAlex + WebSearch to populate prior work, methodology landscape, gaps, and hypothesis evidence
  - Phase 3: Document Draft — AI synthesizes Phase 1 + Phase 2 into T13 template format
  - Phase 4: Review & Refinement — user reviews and modifies via dialogue (max 3 rounds)
- **T13 template** — Research Direction Document format definition added to `references/templates.md`

### Changed
- **Step reordering** — Pipeline initialization now flows: Step 0 (Setup) → Step 0a (Research Direction) → Step 0b (Persona) → Step 0c (Weights) → Step 0d (Pre-flight). Previously: Step 0a (Weights) → Step 0b (Persona) → Step 0c (Question Brainstorming) → Step 0d (Pre-flight)
- **Persona Casting (Step 0b)** — Now reads `research_direction.md` to inform persona selection. Guiding questions target gaps and methodology challenges identified in the document
- **Adaptive Weights (Step 0c, was Step 0a)** — Signal detection now analyzes the structured Research Direction Document sections instead of the raw topic string
- **Pre-flight (Step 0d)** — No longer runs broad topic search (already done in Step 0a Phase 2). Loads Phase 2 literature as baseline, runs only persona-targeted supplemental searches
- **Step 1a brainstorming** — Prompts now include `@research_direction.md` as grounding context
- **Step 1c Question Fidelity** — Now compares against `research_direction.md` Sections 1, 3, 4 (Research Question, Hypothesis, Expected Results) instead of raw `.workspace.json` topic
- **Retroactive Question Crystallization** — Compares crystallized question against Research Direction Document Section 1 instead of raw input

### Removed
- **Question Orientation** — 3-level framing table (Operational/Conceptual/Philosophical) removed from Step 0. Scope considerations are now addressed naturally during Phase 1 Core Framing dialogue
- **Research Question Brainstorming (Step 0c)** — 5-phase AI assessment + dialogue system replaced by the more comprehensive Research Direction Document
- **`brainstorm/question_refinement.md`** — Replaced by `brainstorm/research_direction.md`

---

## [0.18.2] — 2026-04-10

### Changed
- **Research Question Brainstorming (Step 0c)** — Replaced 3-tier automated question refinement with interactive brainstorming protocol:
  - Runs at all depths unconditionally (no `--depth` branching)
  - Phase 1: Internal assessment (Specificity/Clarity/Research-readiness) with skip option if all pass
  - Phase 2: Human-in-the-loop dialogue loop — one question at a time, multiple choice preferred
  - Phase 3: 2-3 research direction proposals with recommendation
  - Phase 4: Scope level confirmation (Operational/Conceptual/Philosophical)
  - Phase 5: Final question confirmation before proceeding
  - Outputs `brainstorm/question_refinement.md` tracing the full refinement process

### Removed
- **Tier 3 MAGI Question Refinement** — Removed AI-only multi-model question discussion from `depth_max.md`. Research direction now always stays aligned with user intent via interactive dialogue.

---

## [0.18.1] — 2026-04-04

### Added
- **`/research-search` skill** — Standalone literature search via OpenAlex + optional WebSearch. Supports `--filter`, `--sort`, `--limit`, `--web`, `--save` flags. 3-tier sparse-result fallback (simplify query → broaden filter → drop type filter)
- **New flags in `config/flags.yaml`** — `filter`, `sort`, `limit`, `web`, `save` scoped to `research-search`

### Changed
- **Adaptive Question Refinement (Step 0c)** — Replaced `--depth max`-only MAGI discussion with 3-tier adaptive approach at all depths:
  - Tier 1 (all depths): Claude evaluates Specificity/Clarity/Research-readiness — proceeds directly if all Pass
  - Tier 2 (`--depth medium+`): Presents assessment + suggested refinements to user if Marginal/Fail
  - Tier 3 (`--depth max` only): Full MAGI discussion only when Tier 2 cannot resolve Fail criteria

### Fixed
- **OpenAlex type filter** — Updated `type:journal-article|proceedings-article` → `type:article|review` across `templates.md` (T9), `shared/rules.md` (§PreFlight), and `openalex_search.py` help text. OpenAlex deprecated the old type taxonomy, causing all filtered searches to return 0 results
- **`/research-search` default sort** — Changed from `cited_by_count:desc` to `relevance_score:desc` for more topic-relevant results

---

## [0.18.0] — 2026-04-03

### Added
- **Pre-flight Context Gathering (Step 0d)** — OpenAlex API + WebSearch gather academic literature before brainstorming (`--depth medium+`). Results are filtered into persona-specific briefings (T9/T10, §PreFlight) to prevent premature consensus — each persona sees the same evidence framed through its reasoning mandate
- **Evidence-Anchored Review (Step 1b-ev)** — After T2 cross-review, DISAGREE/INSUFFICIENT verdicts trigger targeted literature search via OpenAlex + WebSearch (T11, §EvidenceAnchoring). Real papers are fed into T3 DCR debate so models cite published evidence when they Defend or Concede. Runs at `--depth high+`
- **Evidence Anchoring at meta-level (Phase B+)** — For `--depth max`, evidence anchoring runs at Layer 2 against cross-persona disagreements, saving to `meta_claim_evidence.md`
- **Adaptive Depth Escalation (`--depth auto`)** — New depth mode that starts as medium, analyzes T2 verdict distribution after cross-review (T12 contention score), and auto-escalates: stay medium (< 0.30), escalate to high (0.30-0.50), or escalate to deep (>= 0.50)
- **Focused Deep Investigation (Step 1b-deep)** — For `--depth auto` escalated to deep: pro/con argument pairs on the top 3 contested ideas with role alternation to prevent positional bias
- **`scripts/parse_verdicts.py`** — Deterministic T2 verdict parser: counts AGREE/DISAGREE/INSUFFICIENT across review files, calculates contention score. Used by `--depth auto` for reproducible escalation decisions
- **`scripts/openalex_search.py`** — OpenAlex API wrapper: search, filter, sort, abstract reconstruction from inverted index. Used by T9 pre-flight and T11 evidence anchoring
- **§PreFlight in `shared/rules.md`** — Pre-flight context gathering rules with persona-aware briefing table
- **§EvidenceAnchoring in `shared/rules.md`** — Evidence anchoring rules with scope limits, evidence classification, and `--depth max` meta-level path

### Changed
- **SKILL.md Progressive Disclosure** — Three largest skills refactored into `references/` for depth-conditional loading:
  - `research-brainstorm`: 1,164 → 670 lines (3 reference files + 2 scripts)
  - `research-explain`: 811 → 426 lines (2 reference files)
  - `research-write`: 844 → 485 lines (5 reference files)
- **Step 1b+ debate calls** now include `claim_evidence.md` as `@`-reference when evidence anchoring ran
- **Step 1-max-d read list** expanded with `meta_claim_evidence.md` and `preflight_context.md`
- **Step 1c MELCHIOR roles** updated with `--depth auto` mappings (medium → Critical Editor, high → Adversarial Critic, deep → Adversarial Critic Enhanced)
- **Mechanical checklists** (Steps 1c and 1-max-d) expanded with evidence anchoring and depth escalation verification items
- **Output Files trees** updated with all new artifacts
- **Step 0c** now has `--claude-only` block (previously missing)

---

## [0.17.1] — 2026-04-02

### Reverted
- **Codex: restore MCP tools for brainstorm/analysis** — Reverted `codex-plugin-cc` migration (v0.17.0). `codex:rescue` is an agentic task runner designed for code investigation, not direct API calls — brainstorm/analysis tasks took 3+ minutes vs ~5 seconds with MCP tools. Restored `mcp__codex-cli__brainstorm` for ideation and `mcp__codex-cli__ask-codex` for analysis/review across all skills

---

## [0.17.0] — 2026-04-01

### Changed
- **Codex integration: MCP → codex-plugin-cc** — Replaced `@cexll/codex-mcp-server` MCP tools (`mcp__codex-cli__brainstorm`, `mcp__codex-cli__ask-codex`) with the official OpenAI `codex-plugin-cc` Claude Code plugin. All Codex calls now use `/codex:rescue --wait --model gpt-5.4` via the `Skill` tool
- **Installation flow** — Codex setup changed from `claude mcp add` to plugin marketplace install (`/plugin marketplace add openai/codex-plugin-cc`) with `/codex:setup` verification step
- **File references for Codex** — Replaced `@filepath` syntax with direct file path references in the task prompt (Codex reads files from the repo autonomously)
- **Web search for Codex** — Replaced `search: true` parameter with natural language instruction in the task prompt
- **Recommended permissions** — Replaced `mcp__codex-cli__ask-codex` / `mcp__codex-cli__brainstorm` with `Skill(codex:*)`

---

## [0.16.0] — 2026-03-31

### Added
- **Mechanism Depth Test** — New verification checklist item (Step 1c & Step 1-max-d): substitute key mechanism term with generic phrase; if the finding still makes the same prediction, demote from finding to framing. Catches tautological explanations ranked as top findings
- **Type D Convergence (Shared Blind Spot)** — Fourth convergence classification in Convergence Interrogation: detects when all models agree on an unvalidated methodological assumption (metric, null model, framework) without independent derivation. Triggers mandatory MELCHIOR audit or confidence downgrade
- **Decisive Experiment field** — Required field at the top of T8 Next Three Steps: identifies the single most confidence-shifting experiment regardless of cost, anchoring the action plan in causal logic before feasibility narrows scope
- **Tiered Timeline** — T8 Next Three Steps replaces fixed "2 weeks" with Tier A (< 1 day) / Tier B (~ 1 week) / Tier C (~ 1 month), requiring at least one step from each tier
- **Intervention/Ablation/Null step types** — T8 step taxonomy expanded from {Empirical, Design, Review} to include {Intervention, Ablation, Null} for causal experiments
- **[MELCHIOR] Comprehensive Self-Review** — Mandatory holistic quality gate after synthesis writing, before mechanical checklist. Evaluates five axes: Question Fidelity, Inter-Finding Coherence, Aggregate Mechanism Audit, Causal vs Diagnostic Balance, Blind Spot Confession. REVISE verdict triggers mandatory revision before finalization

### Changed
- **T8 Tier 3 auto-classification** — Updated criteria: findings must produce at least one Tier A step AND one Intervention/Ablation/Null step, or be auto-classified as Tier 3 (speculative)
- **Convergence Interrogation references** — Updated from Type A/B to Type A/B/D throughout verification checklists

---

## [0.15.0] — 2026-03-27

### Added
- **Schema Auto-Validators** — `utils/validate_schema.py` validates all JSON artifacts against the 8 existing schemas at phase transitions. Auto-detects schema from filename, supports directory scanning, `--json` output, and explicit `--schema` flag. Closes the gap between "documented schemas" and "enforced contracts"
- **`§SchemaValidation` in `shared/rules.md`** — Phase transition protocol: validate after phase writes, before user checkpoint. Referenced by all SKILL files
- **`§AntiConsensus` in `shared/rules.md`** — 5 rules counteracting LLM agreement bias: evidence-gated agreement, concession tax, hybrid tribunal, false consensus detection, unresolved disagreement preservation
- **T2 Review Verdict** — Cross-review templates now require explicit AGREE/DISAGREE/INSUFFICIENT verdict per idea, with independent evidence required for agreement
- **T3 Concession Tax** — DCR debate concessions must name the specific defeating evidence; concessions without named defeaters revert to Defend
- **T3 Hybrid Tribunal** — Hybrid proposals must prove independent value via outperformance scenario, underperformance scenario, and synergy mechanism; failure to satisfy → withdrawal
- **Type C convergence (False Consensus)** — New classification in Convergence Interrogation for agreements without concrete mechanism or independent evidence; auto-downgrades confidence one level

### Changed
- **`jsonschema>=4.20` dependency** — Added for JSON Schema draft 2020-12 validation support

---

## [0.14.0] — 2026-03-23

### Added
- **Step 3.5: Draft Validation Gate** — `validate_draft.py` auto-runs before MAGI traceability review (Step 4), catching structural issues (missing evidence blocks, LaTeX violations, missing sections, word budget overruns) early
- **Depth-scaled plot budget** — Gap detection loop constraints now scale by `--depth` (min: 2 plots, default: 6, high: 12, max: 15) instead of a fixed 6-plot cap
- **Feedback tier keyword signals** — Step 6b now includes explicit keyword lists for Tier 1/2/3 classification, with fallback to user confirmation when ambiguous

### Changed
- **`plot_manifest.schema.json` v1.1.0** — Added `style`, `dpi`, `source_script`, `source_function`, `generation_date` fields for automated style validation
- **`report_versions.schema.json` v1.1.0** — Added structured `changes` array (type/files/section/reason) replacing flat `feedback_summary`-only tracking

### Fixed
- **`validate_draft.py` status strings** — `"PASSED"`/`"FAILED"` → `"pass"`/`"fail"` to match SKILL.md contract

---

## [0.13.0] — 2026-03-17

### Added
- **`shared/rules.md`** — Single source of truth for cross-cutting rules: §MCP (Gemini fallback chain, Codex model, file refs, web search), §Visualization (scienceplots, 300dpi, Nature widths), §LaTeX (Unicode ban, display equation format), §Claude-Only (MCP→Agent mapping, 4 key rules), §Substitute, §SubagentExec (6-step template), §PhaseGate (4-step procedure)
- **Inline fallback** — All 6 modified SKILL files carry a 1-line fallback (MCP chain, Codex model, LaTeX ban, scienceplots essentials) for resilience when `shared/rules.md` is not loaded
- **Brainstorm: LaTeX Unicode hard ban** — Explicit `> Hard requirement` block added to brainstorm skill
- **Brainstorm: Pipeline context detection** — Sub-skill invocations skip directory creation when `.workspace.json` already exists
- **Brainstorm: Weight normalization verification** — Verify sum equals 1.00 after rounding

### Changed
- **SKILL compression** — 7 SKILL files compressed via §-references and claude-only block reduction (4,807 → 4,201 lines, net −606 / −12.6% including shared/rules.md)
- **Claude-only blocks** — Verbose 30–55 line `Agent()` blocks compressed to 3–4 line §SubagentExec references while preserving deliverable specs, evaluation criteria, issue taxonomies, and role-specific debate criteria
- **Brainstorm: Ambiguous workspace resolution** — `.workspace.json` Glob now prefers topic-matching workspace; asks user on ambiguity

### Fixed
- **P0: orchestrator `--personas` range** — `2-5` → `2-4` (matched Arguments section)
- **P0: execute Step 3** — "Proceeding" replaced with explicit user confirmation pause
- **P0: execute Step 4-PARTIAL `state`** — Fixed to conditional `FAILED|PARTIAL` (was hardcoded `FAILED`)
- **P0: execute Step 4-PARTIAL `downstream_allowed`** — Fixed to conditional based on partial artifact presence (was hardcoded `true`)
- **P0: implement Step 3b `cwd`** — `"src/"` → `"."` (execution from output root, not src/)

---

## [0.12.0] — 2026-03-16

### Added
- **MELCHIOR Active Synthesis Protocol** — Claude/Opus elevated from mechanical aggregator to active third MAGI personality with depth-conditional roles (Curator, Critical Editor, Adversarial Critic, Philosopher-Arbiter)
- **Convergence Interrogation** — Type A/B classification for convergent findings (genuine vs. shared-bias convergence)
- **Intertextual Addition** — Mandatory `[MELCHIOR]` original contribution injected into synthesis
- **MELCHIOR Verdict** — Per-finding `(f) [MELCHIOR] Verdict` section with Endorse/Revise/Reject and reasoning

---

## [0.11.0] — 2026-03-12

### Changed
- **Narrative-first synthesis structure** — Synthesis output redesigned to produce research analysis instead of project management documents
- **"Direction" → "Finding" terminology** — Forces present/past tense descriptions instead of future-tense project proposals
- **Per-finding narrative structure** — Mechanism Narrative (150–250 words prose) → Mathematical Core & Predictions → Falsification Criteria → T7 Footer
- **T7 demoted** — From body structure to 1–2 sentence summary footer
- **Expanded findings** — Top 5 full findings + appendix table (was: top 3 full + rest brief)
- **3-item self-check** — Mechanism exists, equation exists, ops content < 15%

---

## [0.10.2] — 2026-03-12

### Fixed
- **Subagent containment** — Added containment directive, prompt-level guards, and post-completion path audit to prevent persona/meta-reviewer subagents from creating duplicate output directories

### Added
- **3-tier report feedback loop** — Report generation with iterative version tracking

---

## [0.10.1] — 2026-03-11

### Fixed
- **Path safety** — Added `brainstorm/` prefix to all claude-only and MCP `@filepath` references; strengthened T5 template and Path Safety Rule for absolute paths
- **Weights schema** — Created `weights.schema.json` to enforce consistent holistic/explicit format
- **Persona cap** — Maximum personas reduced from 5 to 4
- **Opus fallback** — Fallback targets Opus subagent instead of Gemini/Claude directly

### Added
- **Emergent Insights and MAGI Process Traceability** added to Step 1c synthesis template

---

## [0.10.0] — 2026-03-11

### Added
- **Holistic scoring** (default) — When `--weights` is omitted, the synthesizing agent ranks ideas using expert judgment instead of numeric dimension weights
- **Agent substitution** — `--substitute "Gemini -> Opus"` replaces a rate-limited model with Claude across all pipeline stages (brainstorming, cross-review, debate, meta-review)
- **Workspace anchor** — `.workspace.json` locks the absolute output directory path, preventing artifact drift after context compression
- **Token-optimized skills** — Reusable templates (T1–T7) reduce brainstorm skill size by ~35%

---

## [0.9.0] — 2026-03-09

### Fixed
- **Polyglot write intake** — `research-write` artifact inventory now uses `src/**/*` and `tests/**/*` instead of Python-specific `*.py` globs, matching the v0.8.1 language-agnostic design
- **`--personas` default** — README now correctly documents `auto` (was `3`), matching the SKILL.md definition
- **`--claude-only` flag** — Restored to README flags table (was removed in v0.8.0 README update)
- **Stale model reference** — Removed deprecated `gemini-3-pro-preview` from `research-test` MCP Tool Rules and README "Under the hood" section
- **Semantic phase names** — Pipeline table uses semantic names (Brainstorm, Plan, Implement, Execute, Test, Report) instead of numbered phases; "Phase 3.5" eliminated from user-facing output
- **Structured execution status** — `pre_execution_status.md` replaced with `pre_execution_status.json` (typed fields: `state`, `error_class`, `severity`, `retryable`, `downstream_allowed`, `next_action`); legacy `.md` fallback preserved for v0.8.x workspaces
- **Atomic staging false-skip** — `results/.staging/` excluded from existence check so incomplete staged files no longer trigger false early-exit
- **Execution manifest consumption** — `research-execute` now applies `cwd`, `env`, and `timeout_override_ms` from `execution_manifest.json` when launching processes
- **Validator edge cases** — `validate_intake.py` and `validate_draft.py` now guard against non-dict JSON roots, non-dict array items, and missing required sections; `validate_draft.py` supports `--json` output mode
- **Plot manifest schema** — `plot_manifest.schema.json` now enforces Common Restrictions (PNG + PDF or SVG) via `anyOf` constraint
- **Plugin root resolution** — `research-write` validator references use skill base directory resolution instead of undefined `{PLUGIN_ROOT}` variable

### Added
- **Centralized flag manifest** — `config/flags.yaml` declares all flags, defaults, allowed values, and model fallback chains as a single source of truth for all SKILL files
- **Staleness fingerprinting** — `research-execute` compares SHA-256 hashes of `src/` and `plan/research_plan.md` before reusing existing `results/`; stale results trigger re-execution prompt
- **`fatal/unknown` error class** — `research-execute` error classification now includes a fallback for unclassifiable errors (segfault, disk-full, etc.) that immediately writes FAILED status
- **Maintained validation utilities** — `research-write` references repository-maintained `utils/validate_intake.py` and `utils/validate_draft.py` instead of LLM-generated scripts
- **JSON Schema definitions** — `schemas/` directory with versioned schemas for `plot_manifest.json`, `write_inputs.json`, `citation_ledger.json`, `section_contracts.json`, `execution_manifest.json`, and `checkpoint.json`

### Changed
- **Execution contract separation** — `research-implement` emits `execution_manifest.json` with typed execution fields; `research-execute` consumes this manifest instead of parsing `research_plan.md` YAML frontmatter
- **Process-group isolation** — `research-execute` runs commands in isolated process groups (`setsid`) with staggered teardown (SIGTERM → grace period → SIGKILL) on timeout
- **Atomic results staging** — `research-execute` writes to `results/.staging/` and promotes atomically on success; prevents half-written results from triggering false early-exit
- **Normalized `--resume`** — Both `/research` and `/research-write` now accept workspace root directory; internal inference determines which sub-pipeline to resume
- **Checkpoint manifests** — Each phase emits `{phase}_checkpoint.json` with completion timestamp and SHA-256 input hashes; resume validates hash currency before skipping phases

---

## [0.8.1] — 2026-03-09

### Added
- **`/research-execute` skill (Phase 3.5)** — Dedicated code execution phase between Implement and Test. Reads `execution_cmd` and `dry_run_cmd` deterministically from `research_plan.md` YAML frontmatter. No keyword heuristics, no entry-point guessing. Supports dry-run verification, 30-min timeout, structured error classification (minor/logic/environment), and `results/pre_execution_status.md` output.
- **`research_plan.md` YAML frontmatter** — Phase 2 (Plan) now scaffolds `languages`, `ecosystem`, `execution_cmd`, `dry_run_cmd`, `expected_outputs`, and `estimated_runtime` fields. Phase 3 (Implement) fills execution fields after writing code.

### Changed
- **Language-agnostic implementation** — `research-implement` no longer assumes Python. Detects existing ecosystem from `src/` files (package managers first, then file extensions). Priority: reality (`src/`) > plan intent > domain defaults. Any language with scripted Ubuntu setup is supported; Python/uv remains the safe fallback.
- **Two-tier testing** — `research-test` separates Tier 1 (unit, mock-based, always runs) from Tier 2 (integration, depends on `results/`, gracefully skipped if absent). Test frameworks are chosen to match the detected workspace — no single framework enforced.
- **Common Restrictions** — Phase 4 enforces four output-interface contracts regardless of tool choice: `plot_manifest.json` (fixed schema), PNG + PDF/SVG dual format, execution evidence, and dependency spec file. Internal tooling is autonomous.
- **Workspace Detection** — Both `research-implement` and `research-test` scan `src/` for package manager files and file extensions to determine the active language/ecosystem before making any tool decisions.
- **Removed pre-execution heuristics from `research-test`** — All code execution logic (entry-point detection, keyword scanning, auto-fix, 10-min timeout) moved to the dedicated `research-execute` skill.
- **Resume Protocol updated** — `results/pre_execution_status.md` is now the Phase 3.5 completion checkpoint. `src/` containing any source file (not only `.py`) triggers Phase 3.5 resume.
- **Artifact Contract updated** — Phase 4 no longer requires Python-specific glob; accepts any source file. Phase 3.5 contract requires `execution_cmd` in plan frontmatter.

---

## [0.7.1] — 2026-03-03

### Changed
- **Gemini fallback chain** — Removed deprecated `gemini-3-pro-preview`; new chain: `gemini-3.1-pro-preview` → `gemini-2.5-pro` → Claude
- **Codex fallback** — If Codex fails 2+ times, fall back to Claude directly

---

## [0.7.0] — 2026-03-03

### Added
- **`/research-explain` skill** — Concept explanation via MAGI Teacher-Critic pipeline with audience-adaptive depth

---

## [0.6.1] — 2026-03-02

### Changed
- **Named personas** — Personas now named after real historical figures related to their domain

---

## [0.6.0] — 2026-03-01

### Added
- **`--claude-only` flag** — Replace Gemini/Codex MCP calls with Claude Agent subagents for environments without external MCP servers

---

## [0.5.4] — 2026-02-28

### Added
- **Adaptive weight recommendation** — Step 0a automatically suggests domain-appropriate scoring weights before brainstorming

---

## [0.5.3] — 2026-02-28

### Fixed
- Use single `@`-reference per CLI call in `--depth max` Layer 2

---

## [0.5.2] — 2026-02-28

### Changed
- `--personas` default changed from `3` to `auto` for `--depth max`

---

## [0.5.1] — 2026-02-28

Migrate all MCP tool calls to `@filepath` references for reliable artifact delivery.

### Changed
- All SKILL files updated to use `@filepath` references in MCP prompt parameters instead of inline `{content}` placeholders — prevents context truncation for large artifacts
- Added "File References" rule to MCP Tool Rules section in all five SKILL files (`research-brainstorm`, `research`, `research-test`, `research-report`, `research-implement`)

### Added
- `brainstorm/disagreements.md` — persisted disagreement summary used by `--depth high` adversarial debate `@` references
- `brainstorm/meta_disagreements.md` — persisted meta-disagreement summary used by `--depth max` meta-debate `@` references

---

## [0.5.0] — 2026-02-28

Hierarchical multi-persona brainstorming — N domain-specialist subagents debate in parallel, then converge through meta-review and adversarial synthesis.

### Added
- **`--depth max`** — Three-layer MAGI-in-MAGI pipeline:
  - **Layer 1**: N persona subagents run parallel mini-MAGI pipelines (Gemini brainstorm + Codex brainstorm + cross-review + conclusion)
  - **Layer 2**: Gemini and Codex meta-review all N conclusions, Claude identifies top 3 cross-persona disagreements, adversarial debate (defend/concede/revise)
  - **Layer 3**: Claude final synthesis with enriched structure — cross-persona consensus, unique contributions, debate resolution, emergent insights
- **`--personas N`** flag — Number of Layer 1 subagents for `--depth max` (default: 3, range: 2-5)
- Enriched `synthesis.md` structure for max depth with per-persona scoring, emergent insights, and MAGI process traceability
- Per-persona output directories: `brainstorm/persona_{i}/` with 5 artifacts each
- Meta-layer artifacts: `meta_review_*.md`, `meta_debate_*.md`

### Changed
- `--depth` flag accepts `max` as fourth option in `/research-brainstorm` and `/research`
- Step 0b persona casting extended: `max` casts N domain-specific personas (not model-paired)
- `/research` forwards `--personas` flag to brainstorm sub-skill

### Unchanged
- `low`, `medium`, `high` depth paths completely unmodified
- All existing output locations and structures identical
- Resume protocol, artifact contracts, phase gates unaffected

---

## [0.4.0] — 2026-02-25

A stabilization release focused on pipeline resilience, session resume, and quality gate standardization.

### Added
- **Resume protocol** — `--resume <output_dir>` flag for `/research` that infers the current pipeline phase from artifact file presence and continues from the last completed phase
- **Artifact contract protocol** — Tool-based (Glob/Read) validation of required predecessor artifacts before each phase, with user-facing "Override or retry?" on failure
- **Standalone phase gates** — `/research-implement` and `/research-test` now generate `phase_gate.md` independently (previously only emitted by the orchestrator)
- Implementation phase gate checklist: code correctness, plan alignment, error handling, dependency management
- Test phase gate checklist: coverage adequacy, edge case handling, visualization quality, result reproducibility

### Changed
- **Step renumbering** in `/research-test`: `4a` → `1`, `4b` → `2`, `4c` → `3`, `4d` → `4`, `5` → `6` (with new Step 5 for phase gate)
- Report template Appendix F: `src/phase_gate.md` and `tests/phase_gate.md` no longer marked "if available" (now always generated)
- `/research` Phase 4 references updated to match new step numbers
- Notes section updated to reference `--resume` flag for interrupted pipeline recovery

---

## [0.3.0] — 2026-02-25

A major feature release introducing weighted scoring, expert personas, adversarial debate, plan stress-testing, and automated quality gates.

### Added
- **Weighted direction scoring** — `--weights` flag with domain-specific defaults (novelty, feasibility, impact, rigor, scalability); saved to `brainstorm/weights.json`
- **Dynamic persona casting** — Claude assigns topic-specific expert personas to Gemini and Codex before brainstorming; saved to `brainstorm/personas.md`
- **Adversarial debate** (`--depth high`) — After cross-review, models defend/concede/revise on their top 3 disagreements; outputs `debate_round2_gemini.md` and `debate_round2_codex.md`
- **Murder board** — Gemini stress-tests the research plan as a hostile reviewer; Claude documents mitigations for each flaw (`plan/murder_board.md`, `plan/mitigations.md`)
- **Phase gates** — Automated quality checkpoints (self-assessment + conditional MAGI mini-review) before each user approval step; saved as `phase_gate.md` per phase
- **Depth control** — `--depth` flag (`low` / `medium` / `high`) to manage review thoroughness and token budget
- Report template Appendix E (MAGI Process Artifacts) and Appendix F (Quality Assurance)
- Research report now inventories and integrates all new artifacts (personas, weights, debate, murder board, phase gates)

### Changed
- Brainstorm synthesis now uses weighted scoring to rank directions instead of unweighted consensus
- Pipeline table and README restructured with "New in v0.3.0" section, usage examples, and collapsible artifact tree
- Roadmap reformatted — shipped items collapsed inline, future items expanded with new entries (session resume, cost estimation)

---

## [0.2.3] — 2026-02-25

### Removed
- `research-advisor` agent (consolidated into main research workflow)

---

## [0.2.2] — 2026-02-24

### Added
- **LaTeX formatting rules** — Enforced inline `$...$` and display `$$` equation formatting across all SKILL files and output documents
- LaTeX formatting instructions included in Gemini/Codex prompts for math-heavy topics

### Changed
- README restructured for clarity; journal strategy content moved to `docs/journal-strategies.md`

---

## [0.2.1] — 2026-02-24

### Added
- **Plot manifest** — `plot_manifest.json` with metadata, section hints, and captions for automated report integration
- **Report gap detection** — Mini-loop that identifies unsupported claims and auto-generates plots (max 2 iterations)
- **MAGI traceability review** — Three-model cross-verification of the final report (orphaned claims, orphaned plots, weak links)
- **Gemini fallback chain** — Resilient 3-tier model fallback: `gemini-3.1-pro-preview` → `gemini-2.5-pro` → Claude

---

## [0.2.0] — 2026-02-23

### Added
- **Journal strategy templates** — Venue recommendations for Physics, AI/ML, and Interdisciplinary research
- **Domain templates** — Paper, Statistics, and Mathematics domains (extending existing Physics and AI/ML)
- Expanded README with Why MAGI section, comparison table, and recommended permissions

---

## [0.1.0] — 2026-02-18

Initial release.

### Added
- Five-phase research pipeline: Brainstorm → Plan → Implement → Test & Visualize → Report
- Multi-model orchestration with Claude (MELCHIOR), Gemini (BALTHASAR), Codex (CASPER)
- Cross-model brainstorming and peer review
- Physics and AI/ML domain templates
- Publication-quality plots with `matplotlib` + `scienceplots`
- Session versioning for output directories
- Claude Code plugin structure with marketplace support

---

[0.12.0]: https://github.com/Axect/magi-researchers/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/Axect/magi-researchers/compare/v0.10.2...v0.11.0
[0.10.2]: https://github.com/Axect/magi-researchers/compare/v0.10.1...v0.10.2
[0.10.1]: https://github.com/Axect/magi-researchers/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/Axect/magi-researchers/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/Axect/magi-researchers/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/Axect/magi-researchers/compare/v0.7.1...v0.8.1
[0.7.1]: https://github.com/Axect/magi-researchers/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/Axect/magi-researchers/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/Axect/magi-researchers/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/Axect/magi-researchers/compare/v0.5.4...v0.6.0
[0.5.4]: https://github.com/Axect/magi-researchers/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/Axect/magi-researchers/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/Axect/magi-researchers/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/Axect/magi-researchers/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/Axect/magi-researchers/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Axect/magi-researchers/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Axect/magi-researchers/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/Axect/magi-researchers/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/Axect/magi-researchers/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/Axect/magi-researchers/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Axect/magi-researchers/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Axect/magi-researchers/releases/tag/v0.1.0
