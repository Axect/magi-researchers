# Changelog

All notable changes to MAGI Researchers are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

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
