# Changelog

All notable changes to MAGI Researchers are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

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
- **Gemini fallback chain** — Resilient 3-tier model fallback: `gemini-3.1-pro-preview` → `gemini-3-pro-preview` → `gemini-2.5-pro`

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

[0.4.0]: https://github.com/Axect/magi-researchers/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Axect/magi-researchers/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/Axect/magi-researchers/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/Axect/magi-researchers/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/Axect/magi-researchers/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Axect/magi-researchers/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Axect/magi-researchers/releases/tag/v0.1.0
