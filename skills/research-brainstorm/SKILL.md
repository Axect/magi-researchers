# Research Brainstorm Skill

## Description
Generates and cross-validates research ideas using Gemini and Codex in parallel, then synthesizes results with Claude.

## Usage
```
/research-brainstorm "research topic" [--domain physics|ai_ml|statistics|mathematics|paper] [--weights '{"novelty":0.4,...}'|adaptive] [--depth low|medium|high|max|auto] [--personas N] [--claude-only] [--substitute "Gemini -> Opus"]
```

## Arguments
- `$ARGUMENTS` — The research topic and optional flags:
  - `--domain` — Research domain (physics, ai_ml, statistics, mathematics, paper). Auto-inferred if omitted.
  - `--weights` — Scoring mode for finding ranking:
    - **Omitted (default — holistic mode)**: Claude ranks findings based on its own expert judgment, with detailed rationale for each ranking position. No numeric dimension weights are used.
    - **JSON object** (e.g., `'{"novelty":0.4,"feasibility":0.2,"impact":0.2,"rigor":0.1,"scalability":0.1}'`): Weighted scoring — dimensions `novelty`, `feasibility`, `impact`, `rigor`, `scalability` with values summing to 1.0.
    - **`adaptive`**: Claude analyzes the prompt, adjusts domain defaults, and asks for user confirmation before scoring (see Step 0a).
  - `--depth` — Controls review depth (default: `medium`):
    - `low` — Skip cross-review, go directly to synthesis
    - `medium` — Standard one-shot cross-review (current behavior)
    - `high` — Cross-review + evidence anchoring + adversarial debate round
    - `max` — Hierarchical MAGI-in-MAGI: N persona subagents run parallel mini-MAGI pipelines, then meta-review + evidence anchoring + adversarial debate across all perspectives
    - `auto` — Adaptive depth: starts as medium, auto-escalates to high or deep based on cross-review disagreement signals (see T12)
  - `--personas N|auto` — Number of domain-specialist subagents for `--depth max` (default: `auto`, range: 2-4). When `auto`, Claude analyzes the topic to determine the optimal persona count. Ignored for other depth levels.
  - `--claude-only` — Replace all Gemini/Codex MCP calls with Claude Agent subagents. Use when external model endpoints are unavailable or for a Claude-only workflow. Two subagents with distinct cognitive styles (Creative-Divergent and Analytical-Convergent) ensure perspective diversity.
  - `--substitute "Agent -> Opus"` — Replace a specific MAGI agent with a Claude (Opus) subagent. Accepted forms: `"Gemini -> Opus"`, `"Codex -> Opus"`. Can be specified multiple times. Use when a specific model hits rate limits but other models are still available. The substituted agent uses the same cognitive style mapping as `--claude-only` mode. If both agents are substituted, functionally equivalent to `--claude-only`. Mutually exclusive with `--claude-only` (if both provided, `--claude-only` takes precedence).

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-2.5-pro"` (fallback)
  3. Claude Opus subagent (last resort — skip Gemini MCP tool, spawn an Agent subagent with T1-CD cognitive style, same as `--substitute "Gemini -> Opus"`)
- **Codex**: Use `model: "gpt-5.4"` for all Codex MCP calls. Use `mcp__codex-cli__brainstorm` for ideation, `mcp__codex-cli__ask-codex` for analysis/review. If Codex fails 2+ times, fall back to a Claude Opus subagent with T1-AC cognitive style (same as `--substitute "Codex -> Opus"`).
- **File References**: Use `@filepath` in the prompt parameter to pass saved artifacts (e.g., `@brainstorm/codex_ideas.md`)
  instead of pasting file content inline. The CLI tools read files directly, preventing context truncation.
- **Web Search**: Use web search freely whenever factual verification, recent developments, or literature context would strengthen the discussion:
  - **Claude**: Use the `WebSearch` tool directly
  - **Gemini**: Add `search: true` to `mcp__gemini-cli__ask-gemini` or `mcp__gemini-cli__brainstorm` calls
  - **Codex**: Add `search: true` to `mcp__codex-cli__ask-codex` or `mcp__codex-cli__brainstorm` calls
  - **When to search**: prior work verification, methodological precedents, dataset/library availability, related approaches, fact-checking quantitative claims
  - **Claude-only mode**: Claude Agent subagents cannot use WebSearch. The main Claude agent should search beforehand and include findings in the subagent prompt.

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
2. **Output filenames**: Keep original names (`gemini_ideas.md`, `codex_ideas.md`, etc.) — add a header `> Source: Claude Agent subagent (claude-only mode, {style})` to each output file.
3. **Independence**: Both subagents are spawned simultaneously so neither can see the other's output.
4. **`--depth max` internal subagents**: Within each persona's mini-MAGI pipeline, use **Expansive Explorer** (replaces Gemini) and **Grounded Builder** (replaces Codex) cognitive styles to maintain internal diversity.

### Agent Substitution (`--substitute`)

When `--substitute` is used, only the specified agent's MCP calls are replaced with Claude Agent subagents. The replacement uses the **same cognitive style and prompt structure** as `--claude-only` mode:

| Substituted Agent | Replacement Cognitive Style |
|---|---|
| Gemini → Opus | **Creative-Divergent** (same as claude-only Gemini replacement) |
| Codex → Opus | **Analytical-Convergent** (same as claude-only Codex replacement) |

**Key differences from `--claude-only`:**
- Only the substituted agent's calls change; the other agent continues using its MCP tool normally.
- Both substituted (Claude subagent) and non-substituted (MCP) calls can still execute in parallel.
- File naming is unchanged (`gemini_ideas.md`, `codex_ideas.md`, etc.). Add header `> Source: Claude Agent subagent (substituted for {Agent}, {CognitiveStyle})` to files written by substituted agents.
- For `--depth max` internal subagents: the substituted agent uses **Expansive Explorer** (if Gemini) or **Grounded Builder** (if Codex).

> **Substitution shorthand**: Throughout this document, every `> **If \`--claude-only\`**:` block also applies when the relevant agent is substituted via `--substitute`. When only one agent is substituted, apply the replacement only to that agent's call — the other agent's call remains unchanged as an MCP tool call. Both can still execute in parallel.

### Reusable Templates

Templates T1–T12 are defined in `references/templates.md`. **Read that file** when you need template definitions. Quick reference:

| ID | Name | Purpose |
|---|---|---|
| T1 | Cognitive Styles | CD, AC, EE, GB style directives |
| T2 | Review Instructions | T2-Science, T2-Feasibility review format with AGREE/DISAGREE/INSUFFICIENT verdicts |
| T3 | DCR Debate Framework | Defend/Concede/Revise + Concession Tax + Hybrid Tribunal |
| T4 | Mechanism Requirement | 1-2 sentence mechanism for each idea |
| T5 | Subagent Output Convention | File naming and header format |
| T6 | Subagent Prompt Structure | 6-part prompt template for claude-only subagents |
| T7 | Finding Summary Footer | 6-field compact reference block per finding |
| T8 | Synthesis Epilogue | Research Gaps, Non-Recommendations, Next Three Steps |
| T9 | Pre-flight Query | OpenAlex + WebSearch query format (uses `scripts/openalex_search.py`) |
| T10 | Persona Briefing | Persona-specific filtered briefing format |
| T11 | Evidence Anchoring | Disputed claim search + classification format |
| T12 | Depth Escalation Criteria | Contention score calculation + decision matrix (uses `scripts/parse_verdicts.py`) |

### LaTeX Formatting Rules
When writing mathematical expressions in any output document (brainstorm ideas, synthesis, etc.):
- **Inline math**: Use `$...$` for short expressions within a sentence (e.g., `$x^2 + y^2 = r^2$`)
- **Display equations**: Use `$$` on its own line, with the equation on a separate line:
  ```
  $$
  \mathcal{L} = -\frac{1}{4} F_{\mu\nu} F^{\mu\nu} + \bar{\psi}(i\gamma^\mu D_\mu - m)\psi
  $$
  ```
- Never write display equations inline as `$$..equation..$$` on a single line — always use line breaks
- **Always** include this formatting instruction in prompts to Gemini and Codex (regardless of whether the topic appears mathematical — topics often produce equations unexpectedly)

> **Hard requirement:** Unicode math symbols (σ₁, π₁, ℝ, ∈, ≈, ², etc.) are **NOT acceptable** in any output document. They render inconsistently across viewers and break PDF export. Always use LaTeX equivalents: `$\sigma_1$`, `$\pi_1$`, `$\mathbb{R}$`, `$\in$`, `$\approx$`, `$^2$`.

### Path Safety Rule

**ALL artifacts MUST be written under `{output_dir}/`.** Never write brainstorm files (`*.md`, `*.json`) directly to the project root, the user's working directory, or any path outside `outputs/`.

- `{output_dir}` is the **absolute path** stored in `.workspace.json` at the output directory root.
- **Before writing any file**: if `{output_dir}` is uncertain (e.g., after context compression), recover it by reading `.workspace.json`:
  1. `Glob` for `outputs/*/.workspace.json`. If multiple matches found, prefer the one whose `topic` field matches the current research topic. If still ambiguous, ask the user to confirm the output directory. If no `.workspace.json` is found, stop and ask the user to provide the output directory explicitly.
  2. `Read` the file and extract `output_dir`.
- **Subagent prompts**: always include the absolute `{output_dir}` path from `.workspace.json`. Never pass a relative path.
- **Subagent file paths must be absolute**: Every file path in a subagent prompt MUST be `{output_dir}/brainstorm/{filename}` (absolute). Never use bare filenames like `gemini_ideas.md` — always use `{output_dir}/brainstorm/gemini_ideas.md`. This prevents subagents from writing to the user's working directory (CWD) instead of the output directory.

### Subagent Containment Rule

**Only the main agent (Layer 0) creates directories.** All subagents (Layer 1 persona subagents, Layer 2 meta-reviewers, and any sub-subagents they spawn) are **consumers** of a pre-created directory structure, never creators.

- **Subagents MUST NOT**:
  1. Run Step 0 (Setup) — they must never create new `outputs/` directories, `.workspace.json` files, or `brainstorm/` folders.
  2. Create any directory under `outputs/` — all `persona_{i}/` subdirectories are pre-created by the main agent before subagent launch.
  3. Create `brainstorm/` or any other directory in the project root or CWD.
  4. Sanitize the topic into a directory name — this is exclusively the main agent's responsibility.
  5. Interpret `SKILL.md` Step 0 instructions as applicable to themselves — subagents execute only their assigned pipeline steps (A through E for persona subagents, or the specific review/debate task for Layer 2 subagents).

- **Subagent prompts MUST include** this explicit negative instruction:
  > "DO NOT create any directories. DO NOT run Step 0 setup. All directories already exist. Write files ONLY to the exact absolute paths listed below."

- **Main agent pre-creates** all directories before launching subagents:
  - For `--depth max`: `brainstorm/persona_{1..N}/` directories are created before Step 1-max-a.
  - For all depths: `brainstorm/` is created in Step 0.

- **Post-completion audit** (main agent responsibility): After all subagents complete, the main agent MUST:
  1. `Glob` for `outputs/*_v*/` and compare against the expected single output directory.
  2. Check for any `brainstorm/` directory in the project root.
  3. Delete any spurious directories and warn the user if artifacts were misplaced.

When this skill is invoked, follow these steps exactly:

### Step 0: Setup

0. **Pipeline context detection**: If this skill was invoked as a sub-skill from `/research` (i.e., `{output_dir}` was provided by the calling context and `.workspace.json` already exists at the output root), skip directory creation (items 2-8 below). Read `{output_dir}` from `.workspace.json` and use `{output_dir}/brainstorm/` as the working directory. Only create a new versioned directory when invoked standalone.

1. Parse the research topic from `$ARGUMENTS`. If a `--domain` flag is provided, note the domain (physics, ai_ml, statistics, mathematics, paper). Otherwise, infer the domain from the topic.
2. Create the output directory: `outputs/{sanitized_topic}_{YYYYMMDD}_v{N}/brainstorm/`
   - Sanitize the topic: lowercase, replace spaces with underscores, remove special characters, truncate to 50 chars.
   - Use today's date in YYYYMMDD format.
   - Version: Glob for `outputs/{sanitized_topic}_{YYYYMMDD}_v*/` and set N = max existing + 1 (start at v1).
   - **Write workspace anchor**: Save `.workspace.json` at the output directory root (`outputs/{sanitized_topic}_{YYYYMMDD}_v{N}/.workspace.json`):
     ```json
     {
       "output_dir": "{absolute_path_to_output_dir}",
       "topic": "{original_topic}",
       "domain": "{domain}",
       "created_at": "{ISO-8601 timestamp}"
     }
     ```
     Use `pwd` or equivalent to resolve the absolute path. This file anchors all subsequent file writes.
3. If a domain template exists at `${CLAUDE_PLUGIN_ROOT}/templates/domains/{domain}.md`, read it for context.
4. **Parse `--weights`** — All `weights.json` files **MUST** conform to the schema at `schemas/weights.schema.json`. The exact structure has two required top-level keys (`weights` and `_meta`) with no additional properties:
   - **If `--weights` is a JSON object**: Validate that keys are exactly {`novelty`, `feasibility`, `impact`, `rigor`, `scalability`} and values sum to 1.0. Save immediately to `brainstorm/weights.json`:
     ```json
     {
       "weights": {
         "novelty": 0.40,
         "feasibility": 0.20,
         "impact": 0.20,
         "rigor": 0.10,
         "scalability": 0.10
       },
       "_meta": {
         "method": "explicit",
         "domain": "<detected domain>"
       }
     }
     ```
     Skip Step 0a entirely.
   - **If `--weights adaptive`**: Load domain defaults as a **baseline reference only** (do not save yet — Step 0a will handle saving after user confirmation):
     - `physics`: `{"novelty": 0.30, "feasibility": 0.15, "impact": 0.25, "rigor": 0.20, "scalability": 0.10}`
     - `ai_ml`: `{"novelty": 0.25, "feasibility": 0.25, "impact": 0.25, "rigor": 0.10, "scalability": 0.15}`
     - `statistics`: `{"novelty": 0.25, "feasibility": 0.20, "impact": 0.20, "rigor": 0.25, "scalability": 0.10}`
     - `mathematics`: `{"novelty": 0.35, "feasibility": 0.10, "impact": 0.20, "rigor": 0.30, "scalability": 0.05}`
     - `paper`: `{"novelty": 0.20, "feasibility": 0.25, "impact": 0.30, "rigor": 0.15, "scalability": 0.10}`
   - **If `--weights` is omitted (default — holistic mode)**: Save immediately to `brainstorm/weights.json`:
     ```json
     {
       "weights": null,
       "_meta": {
         "method": "holistic",
         "domain": "<detected domain>"
       }
     }
     ```
     **Holistic format is exactly the above — `weights` is `null` (not an empty object, not omitted), `_meta` contains only `method` and `domain`.** No other keys or variations.
     Skip Step 0a entirely. In Step 1c / Step 1-max-d, Claude will rank findings using holistic expert judgment instead of numeric weighted scoring.
5. **Parse `--depth`**: Accept `low`, `medium`, `high`, `max`, or `auto` (default: `medium`).
   - `low` — Skip Step 1b (cross-review), go directly to Step 1c (synthesis)
   - `medium` — Standard one-shot cross-review (current default behavior)
   - `high` — Cross-review + evidence anchoring + adversarial debate (Step 1b-ev + Step 1b+)
   - `max` — Hierarchical MAGI-in-MAGI pipeline (Steps 1-max-a through 1-max-d replace Steps 1a/1b/1b+/1c)
   - `auto` — Starts as `medium`, then escalates based on T2 disagreement signals (see Step 1b-esc and **T12**). Pre-flight (Step 0d) always runs for `auto`.
6. **Parse `--personas N|auto`**: Accept integer 2-4 or the string `auto` (default: `auto`). Only used when `--depth max`; ignored otherwise.
   - If `auto`: Defer persona count determination to Step 0b, where Claude analyzes the topic's complexity, number of distinct sub-disciplines, and methodological diversity to select the optimal N (2-4).
   - If an explicit integer is given: Use that value directly.
7. **Parse `--claude-only`**: Boolean flag (default: `false`). When present, all Gemini/Codex MCP calls are replaced with Claude Agent subagents. See the **Claude-Only Mode** section above for the replacement table and cognitive style definitions.
8. **Parse `--substitute`**: Accept zero or more `--substitute "Agent -> Opus"` flags. Valid agent names: `Gemini`, `Codex`. Valid target: `Opus`. When specified, the named agent's MCP calls are replaced with Claude Agent subagents using the same cognitive style mappings as `--claude-only` mode (see **Agent Substitution** section). `--substitute` and `--claude-only` are mutually exclusive — if both are provided, `--claude-only` takes precedence. If both `"Gemini -> Opus"` and `"Codex -> Opus"` are specified, treat as equivalent to `--claude-only`.
9. **Question Orientation** (always, all depths):
   Before proceeding to brainstorming, present:
   ```
   **Question Orientation** *(no response needed — for scope anchoring only)*

   | Level | Framing |
   |-------|---------|
   | Operational | [concrete, mechanism-level version] |
   | Conceptual ← default | [mid-level, framework-focused version] |
   | Philosophical | [abstract, principle-level version] |

   Reply "operational" or "philosophical" to shift depth. Otherwise, proceeding with Conceptual.

   **Adjacent Questions**:
   - Simpler: [question whose answer is a useful component]
   - Broader: [research program that fully solving this would advance]
   ```
   If the user replies with a level shift, adjust the topic framing accordingly. Otherwise, proceed immediately.

### Step 0a: Adaptive Weight Recommendation

> **Skip unless `--weights adaptive`**: This step only runs when `--weights adaptive` is explicitly specified. If `--weights` is omitted (holistic mode) or a JSON object (explicit mode), weights are already saved in Step 0.

When `--weights adaptive` is specified, Claude analyzes the research prompt to recommend topic-appropriate weights:

1. **Analyze the research prompt** for research-nature signals:

   | Signal | Example Keywords | Effect |
   |--------|-----------------|--------|
   | Theoretical/Formal | proof, formal, theorem, analytical | rigor↑, feasibility↓ |
   | Experimental/Empirical | experiment, data, empirical, measurement | feasibility↑, rigor↑ |
   | Applied/Engineering | deploy, production, tool, system | feasibility↑, scalability↑ |
   | Exploratory/Innovative | novel, first, unexplored, new paradigm | novelty↑, feasibility↓ |
   | Practicality emphasis | practical, real-world, industry | feasibility↑, scalability↑ |
   | Rigor emphasis | rigorous, convergence, guarantee | rigor↑ |
   | Impact emphasis | breakthrough, paradigm, transformative | impact↑, novelty↑ |
   | Narrow scope | specific algorithm, single method | rigor↑, feasibility↑ |
   | Broad scope | interdisciplinary, broad, cross-domain | novelty↑, impact↑ |

2. **Generate recommended weights**: Starting from the domain baseline loaded in Step 0, apply adjustments based on detected signals:
   - Each signal adjusts relevant dimensions by ±0.05 to ±0.10
   - After all adjustments, **normalize** so values sum to 1.0
   - **Clamp** each dimension to the range [0.05, 0.45] before final normalization

3. **Present a comparison table** to the user:

   ```
   Detected signals: [list of signals found in the prompt]

   | Dimension     | Domain Default | Recommended | Adjustment Reason            |
   |---------------|---------------|-------------|------------------------------|
   | novelty       | 0.30          | 0.35        | +0.05 (exploratory research) |
   | feasibility   | 0.15          | 0.10        | -0.05 (theoretical focus)    |
   | impact        | 0.25          | 0.25        | (no change)                  |
   | rigor         | 0.20          | 0.25        | +0.05 (formal methods)       |
   | scalability   | 0.10          | 0.05        | -0.05 (narrow scope)         |
   ```

After computing final weights, verify they sum to exactly 1.00 (round each to 2 decimal places if necessary; re-normalize if rounding causes drift). Display the sum in the comparison table.

4. **Ask the user for confirmation** using `AskUserQuestion`:
   - Option A: **"Accept recommended weights"** (Recommended) — use the adaptive weights
   - Option B: **"Use domain defaults"** — use the unmodified domain baseline
   - Other: User provides custom weights as JSON

If the user provides custom weights: validate that (1) keys are exactly `{novelty, feasibility, impact, rigor, scalability}`, and (2) values sum to 1.0 (within tolerance 0.01). If invalid, present the error and ask again. Maximum 1 retry; on continued failure, fall back to domain defaults with a note in `weights.json`.

5. **Save to `brainstorm/weights.json`** with metadata based on the user's choice:
   ```json
   {
     "weights": { <chosen weights> },
     "_meta": {
       "method": "<adaptive-recommended|domain-default|custom>",
       "domain": "<detected domain>",
       "domain_defaults": { <original domain baseline> },
       "signals_detected": ["theoretical work", "narrow scope", ...],
       "adjustments_applied": {
         "rigor": "+0.05 (theoretical focus)",
         "feasibility": "-0.05 (theoretical focus)"
       }
     }
   }
   ```
   - If "Accept recommended": `method` = `"adaptive-recommended"`
   - If "Use domain defaults": `method` = `"domain-default"`, `signals_detected` and `adjustments_applied` are still recorded for traceability
   - If custom JSON: `method` = `"custom"`

### Step 0b: Dynamic Persona Casting

After setup, Claude analyzes the topic and domain to assign specialist personas.

**Persona definition format** (all depth levels):
- **Name/title** — Real historical figure (위인) whose work aligns with the persona's domain (e.g., "R. A. Fisher", "Emmy Noether", "John von Neumann"). The figure's intellectual legacy signals the persona's analytical style.
- **Expertise areas** (3-5 bullet points)
- **Guiding question** that shapes their perspective
- **Primary lens** (one sentence; required for `--depth max`, optional for others)

Personas **complement** the domain template — they do not override it.

**If `--claude-only`**: Relabel personas — "Gemini persona" → "Subagent A (T1-CD)", "Codex persona" → "Subagent B (T1-AC)". For `--depth max` internal roles: "Gemini" → "Expansive Explorer (T1-EE)", "Codex" → "Grounded Builder (T1-GB)". Include cognitive style directives in the persona file.

**For `--depth low|medium|high|auto` (2 personas):**

1. Analyze the topic's sub-disciplines, methodologies, and key challenges.
2. Assign a **Gemini persona** — domain expert for creative/theoretical ideation.
3. Assign a **Codex persona** — practitioner/builder for implementation-focused ideation.
4. Save to `brainstorm/personas.md`.

**For `--depth max` (N personas):**

1. **Determine N** (if `--personas auto`):
   - **N=2**: Narrow topic, single sub-field. **N=3**: Theory + practice. **N=4**: 2+ sub-fields or highly interdisciplinary.
   - Announce chosen N and reasoning. If explicit integer given, use directly.
2. Cast **N domain-specialist personas** (model-independent):
   - **N=2**: Theory/Concepts, Computation/Implementation
   - **N=3**: + Empirical/Validation. **N=4**: + Application/Interdisciplinary
3. Personas must be **complementary** — cover distinct dimensions with minimal overlap.
4. Save to `brainstorm/personas.md`.

### Step 0c: Adaptive Question Refinement

> **Runs at all depths.** Tiered assessment: Tier 1 (Claude assessment) runs always. Tier 2 (user clarification) available at `--depth medium+`. Tier 3 (MAGI discussion) available only at `--depth max`.
> Read `references/depth_max.md` for the Tier 3 MAGI pipeline definition.

**Tier 1 — Main Agent Assessment** (all depths):

Claude evaluates the research question on three criteria:

| Criterion | Pass | Marginal | Fail |
|-----------|------|----------|------|
| **Specificity** | Topic is narrow enough for actionable research directions | Topic is broad but a reasonable scope can be inferred | Topic is so broad that brainstorming would scatter (e.g., "physics", "machine learning") |
| **Clarity** | Key terms are unambiguous within the detected domain | Some terms have multiple interpretations but context disambiguates | Critical terms are ambiguous or the domain itself is unclear |
| **Research-readiness** | Question implies measurable outcomes or testable hypotheses | Outcomes are implied but not explicit | No measurable criterion can be inferred |

**Decision logic**:
- **All Pass** → Proceed to Step 0d. Log: "Question assessment: Clear. Proceeding directly."
- **Any Marginal, no Fail** → Tier 2 (if `--depth medium+`) or proceed with a narrowing note (if `--depth low`)
- **Any Fail** → Tier 3 (if `--depth max`) or Tier 2 (if `--depth medium|high|auto`) or proceed with warning (if `--depth low`)

**Tier 2 — User Clarification** (`--depth medium|high|max|auto`):

Present the assessment to the user:
```
**Question Assessment**:
- Specificity: {Pass/Marginal/Fail} — {1-sentence explanation}
- Clarity: {Pass/Marginal/Fail} — {1-sentence explanation}
- Research-readiness: {Pass/Marginal/Fail} — {1-sentence explanation}

**Suggested refinements** (pick one or provide your own):
1. {narrower/clearer version A}
2. {narrower/clearer version B}
3. Proceed as-is
```

If the user provides a refinement or selects an option, update the topic string and proceed to Step 0d. If "proceed" or option 3, continue with the original question.

**Tier 3 — MAGI Discussion** (`--depth max` only):

If any Tier 1 criterion is Fail and Tier 2 did not resolve the ambiguity (user chose "proceed as-is" despite Fail criteria), OR if the user explicitly requests deeper refinement:

> Read `references/depth_max.md` Step 0c Tier 3 section for the full MAGI pipeline (parallel Gemini+Codex analysis, Claude synthesis, scope comparison).

### Step 0d: Pre-flight Context Gathering (`--depth medium|high|max|auto`)

> **Skip if `--depth low`**: Pre-flight only runs at medium depth or above.

Gather grounded evidence before brainstorming, per §PreFlight and **T9**/**T10**.

1. **Parallel evidence gathering** — execute simultaneously:
   - **OpenAlex query** (via WebFetch, per **T9**): Search for the research topic in academic literature. URL-encode the topic string. If results are sparse (< 3 papers), retry with broader keywords (drop domain-specific jargon, keep core concept).
   - **WebSearch** (per **T9**): Search for recent advances related to the topic.

2. **Save raw context** to `brainstorm/preflight_context.md` following the **T9** format (Academic Literature + Recent Developments + Methodological Landscape sections).

3. **Create persona-specific briefings** per **T10**:
   - For `--depth medium|high|auto`: Create `brainstorm/briefing_gemini.md` and `brainstorm/briefing_codex.md`, each filtered by the persona's reasoning mandate and guiding question from `brainstorm/personas.md`.
   - For `--depth max`: Create `brainstorm/briefing_persona_{i}.md` for each of the N personas, filtered by each persona's expertise areas and guiding question.

   > **If `--claude-only`**:
   > - For `--depth medium|high|auto` (2-model): Create `brainstorm/briefing_subagent_a.md` (Creative-Divergent focus) and `brainstorm/briefing_subagent_b.md` (Analytical-Convergent focus) with the same filtering logic.
   > - For `--depth max` (N-persona): Create `brainstorm/briefing_persona_{i}.md` for each persona (same as non-claude-only mode — briefing is filtered by persona expertise, not by model cognitive style).

4. **Validation**: Verify `preflight_context.md` contains at least 3 academic references. If OpenAlex returned 0 results but WebSearch returned results, create briefings from web results only (reduced quality is acceptable — note "Pre-flight: Literature briefing based on web sources only, no academic papers found"). If both OpenAlex and WebSearch returned no useful results, note "Pre-flight: No relevant context found — brainstorm will proceed without literature grounding" and skip briefing creation.

### Step 1a: Parallel Independent Brainstorming

Execute these two calls **simultaneously** (in the same message). **Prepend the assigned persona** from `brainstorm/personas.md` to each prompt:

Each call includes: persona context, guiding question, domain template (if exists, via `@{domain_template_path}`), **persona-specific briefing** (if Step 0d ran, via `@{output_dir}/brainstorm/briefing_{persona}.md`), and **T4** mechanism requirement. Use `ideaCount: 12, includeAnalysis: true, methodology: "auto"`.

Each brainstorm prompt must begin with: "Before listing ideas, state in one sentence: 'Scope: [how you interpret this question's boundary and focus].'" This scope declaration is collected for divergence checking in synthesis.

**Gemini**: `mcp__gemini-cli__brainstorm`, `model: "gemini-3.1-pro-preview"` — Generate diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs. If `brainstorm/briefing_gemini.md` exists, include via `@{output_dir}/brainstorm/briefing_gemini.md` and add: "Use the attached literature briefing as context — it highlights failure cases and unexplored alternatives. Let it inform but not constrain your ideation."

**Codex**: `mcp__codex-cli__brainstorm`, `model: "gpt-5.4"` — Generate implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches. If `brainstorm/briefing_codex.md` exists, include via `@{output_dir}/brainstorm/briefing_codex.md` and add: "Use the attached literature briefing as context — it highlights existing implementations and practical constraints. Let it inform but not constrain your ideation."

> Note: If Codex MCP is unavailable, fall back to a Claude Opus subagent with T1-AC cognitive style (same as `--substitute "Codex -> Opus"`), using the Codex persona and implementation-focused framing per **T6**.

> **If `--claude-only`**: Replace both calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD, Gemini persona): Generate 12 diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs. Apply **T4**. If `brainstorm/briefing_subagent_a.md` exists, include it via Read and add: "Use the attached literature briefing as context — let it inform but not constrain your ideation." Save to `brainstorm/gemini_ideas.md` per **T5**.
> - **Subagent B** (T1-AC, Codex persona): Generate 12 implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches. Apply **T4**. If `brainstorm/briefing_subagent_b.md` exists, include it via Read. Save to `brainstorm/codex_ideas.md` per **T5**.

Save results to:
- `brainstorm/gemini_ideas.md` — Gemini's (or Subagent A's) raw output with header noting source, persona, and timestamp
- `brainstorm/codex_ideas.md` — Codex's (or Subagent B's) raw output with header noting source, persona, and timestamp

**Post-generation validation** (always, all depths):
After saving `gemini_ideas.md` and `codex_ideas.md`, verify each file is non-empty and contains at least 3 idea entries (separated by `---` or numbered headers). If either file is empty or truncated:
- Retry the failed model call once with the same parameters.
- If the retry is also insufficient, warn the user before proceeding to the next step.

### Step 1b: Cross-Check (`--depth medium`, `--depth high`, or `--depth auto`)

> **If `--depth low`**: Skip this step entirely and proceed to Step 1c.

After both brainstorming results are saved, execute these two calls **simultaneously**. **Prepend the assigned persona** to each review prompt:

**Gemini reviews Codex ideas (Round 1):**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {gemini_persona_name} — {gemini_persona_expertise}]\n\nApply T2-Science review to the following research ideas:\n\n@{output_dir}/brainstorm/codex_ideas.md",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-2.5-pro" → Claude
)
```

**Codex reviews Gemini ideas (Round 1):**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {codex_persona_name} — {codex_persona_expertise}]\n\nApply T2-Feasibility review to the following research ideas:\n\n@{output_dir}/brainstorm/gemini_ideas.md",
  model: "gpt-5.4"
)
```

> Note: If Codex MCP is unavailable, fall back to a Claude Opus subagent with T1-AC cognitive style (same as `--substitute "Codex -> Opus"`), using the Codex persona per **T6**.

> **If `--claude-only`**: Replace both calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD, Gemini persona): Read `brainstorm/codex_ideas.md`. Apply **T2-Science** review. Save to `brainstorm/gemini_review_of_codex.md` per **T5**.
> - **Subagent B** (T1-AC, Codex persona): Read `brainstorm/gemini_ideas.md`. Apply **T2-Feasibility** review. Save to `brainstorm/codex_review_of_gemini.md` per **T5**.

Save results to:
- `brainstorm/gemini_review_of_codex.md`
- `brainstorm/codex_review_of_gemini.md`

### Step 1b-esc: Depth Escalation Check (`--depth auto` only)

> **Skip unless `--depth auto`**: Read `references/depth_auto.md` for the full step definition.
> Uses `scripts/parse_verdicts.py` to count verdicts and calculate contention score.
> Decision: contention < 0.30 → stay medium; 0.30-0.50 → escalate to high; >= 0.50 → escalate to deep.

### Step 1b-ev: Evidence Anchoring (`--depth high+` or escalated from `auto`)

> **Skip if `--depth low` or `--depth medium`** (unless escalated from `--depth auto`).

After cross-review, search for real evidence on disputed claims per §EvidenceAnchoring and **T11**:

1. **Read both review files** and extract all ideas with DISAGREE or INSUFFICIENT verdicts.
   - **Zero-dispute guard**: If no DISAGREE or INSUFFICIENT verdicts are found (all AGREE), skip this step entirely — no `claim_evidence.md` is created. This can happen when `--depth high` is explicitly set on a topic with strong cross-model agreement.

2. **Prioritize**: Select up to 5 disputed claims — DISAGREE first, then INSUFFICIENT; within each category, prioritize by idea ranking position.

3. **For each disputed claim** (execute searches in parallel where possible):
   - Extract the core mechanism under dispute.
   - Construct a precise search query from the claim.
   - Run OpenAlex search via WebFetch + WebSearch simultaneously, per **T11**.
   - Classify found evidence as Supporting / Contradicting / Tangential.

4. **Save** to `brainstorm/claim_evidence.md` per **T11** format.

5. **Summary statistics**: At the end of `claim_evidence.md`, append:
   ```
   ## Evidence Summary
   - Claims investigated: {n}
   - Claims with supporting evidence: {n}
   - Claims with contradicting evidence: {n}
   - Claims with no direct evidence: {n}
   ```

> **If `--claude-only`**: All WebFetch and WebSearch calls are made by the main agent (subagents cannot use these tools). Complete evidence gathering before proceeding to debate.

### Step 1b+: Adversarial Debate (`--depth high` or escalated from `auto`)

> **If `--depth low` or `--depth medium`** (and not escalated): Skip this step entirely.

After Round 1 cross-review (and evidence anchoring if `--depth high+`), Claude identifies the **top 3 points of disagreement** between Gemini and Codex (e.g., conflicting feasibility assessments, divergent novelty ratings, opposing recommendations). **Save the disagreement summary to `brainstorm/disagreements.md`** before the debate calls.

Execute Round 2 **simultaneously**:

**Round 2 — Defend/Concede/Revise** (execute simultaneously):

Each call includes: persona context, `@{output_dir}/brainstorm/disagreements.md`, **T3** debate framework, own review, opposing review, **and `@{output_dir}/brainstorm/claim_evidence.md`** (if Step 1b-ev ran — instruct models to cite real evidence when defending or conceding).

- **Gemini**: `mcp__gemini-cli__ask-gemini`, `model: "gemini-3.1-pro-preview"`, refs: `@{output_dir}/brainstorm/gemini_review_of_codex.md` + `@{output_dir}/brainstorm/codex_review_of_gemini.md` + (if exists) `@{output_dir}/brainstorm/claim_evidence.md`
- **Codex**: `mcp__codex-cli__ask-codex`, `model: "gpt-5.4"`, refs: `@{output_dir}/brainstorm/codex_review_of_gemini.md` + `@{output_dir}/brainstorm/gemini_review_of_codex.md` + (if exists) `@{output_dir}/brainstorm/claim_evidence.md`

> **If `--claude-only`**: Replace both debate calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD, Gemini persona): Read `brainstorm/disagreements.md`, `brainstorm/gemini_review_of_codex.md`, `brainstorm/codex_review_of_gemini.md`, and (if exists) `brainstorm/claim_evidence.md`. Apply **T3** debate framework. Cite real evidence from `claim_evidence.md` when defending or conceding. Save to `brainstorm/debate_round2_gemini.md` per **T5**.
> - **Subagent B** (T1-AC, Codex persona): Read `brainstorm/disagreements.md`, `brainstorm/codex_review_of_gemini.md`, `brainstorm/gemini_review_of_codex.md`, and (if exists) `brainstorm/claim_evidence.md`. Apply **T3** debate framework. Cite real evidence from `claim_evidence.md` when defending or conceding. Save to `brainstorm/debate_round2_codex.md` per **T5**.

Save results to:
- `brainstorm/debate_round2_gemini.md`
- `brainstorm/debate_round2_codex.md`

### Step 1b-deep: Focused Deep Investigation (`--depth auto`, escalation to deep only)

> **Skip unless `--depth auto` escalated to deep**. Read `references/depth_auto.md` for the full step definition.
> Pro/con argument pairs for the top 3 contested ideas, with role alternation to prevent positional bias.

### Steps 1-max-a through 1-max-d: MAGI-in-MAGI Pipeline (`--depth max` only)

> **If `--depth` is not `max`**: Skip entirely. Use Steps 1a/1b/1b+/1c instead.
> **Read `references/depth_max.md`** for the complete Layer 1-3 pipeline:
> - **Step 1-max-a**: Spawn N parallel persona subagents, each running a mini-MAGI (brainstorm + cross-review + conclusion)
> - **Step 1-max-b**: Collect and consolidate persona outputs into `all_conclusions.md`
> - **Step 1-max-c**: Meta-review + evidence anchoring (Phase B+) + adversarial debate
> - **Step 1-max-d**: MELCHIOR Philosopher-Arbiter synthesis with Prior Declaration

### Step 1c: Claude Synthesis

> **If `--depth max`**: Skip — synthesis is produced by Step 1-max-d in `references/depth_max.md`.

**MELCHIOR Active Synthesis Protocol** (depth-conditional):

You are MELCHIOR — the third personality in the MAGI triad, not a neutral aggregator. Your role varies by depth:

- `--depth low` — **MELCHIOR as Curator**: Select and present findings. You MUST add at least one **[MELCHIOR]** original observation that neither model raised. For each finding not selected for the top list, state why it was excluded.
- `--depth medium` — **MELCHIOR as Critical Editor**: You MUST revise at least one substantive claim from each model (a revision changes the recommended action, predicted outcome, or confidence level — phrasing changes do not count). Apply **Convergence Interrogation** (see below). Mark all original contributions with **[MELCHIOR]**.
- `--depth high` — **MELCHIOR as Adversarial Critic**: For the top 2 findings, construct the strongest possible objection. If the objection is fatal, demote the finding and promote the next candidate. Rankings must reflect adversarial survival, not just model consensus. When `claim_evidence.md` exists, cite real-world evidence in objections.
- `--depth auto` — MELCHIOR role is determined by the escalation decision from Step 1b-esc:
  - Remained at medium → **Critical Editor** (same as `--depth medium` above)
  - Escalated to high → **Adversarial Critic** (same as `--depth high` above)
  - Escalated to deep → **Adversarial Critic (Enhanced)**: Same as Adversarial Critic, plus: (1) for each of the 3 deeply investigated contested ideas, read `deep_investigation_{i}_pro.md` and `deep_investigation_{i}_con.md` and adjudicate which side has stronger evidence; (2) explicitly state whether the deep investigation changed the idea's ranking vs. the pre-investigation assessment; (3) apply a stricter adversarial threshold — objections must cite real-world evidence from `claim_evidence.md` when available, not just model reasoning.

**Convergence Interrogation** (mandatory for `--depth medium|high` or escalated `auto`):
For each finding that appears in both models' outputs, classify as:
- **Type A convergence**: Models arrived via different reasoning paths or evidence. No confidence adjustment.
- **Type B convergence**: Both models cite the same named source, method, or prior result. Apply confidence note: "Type B convergence — shared training reference, not independent validation."
- **Type C convergence (False Consensus)**: Both models agree, but neither provides a concrete mechanism, independent evidence, or specific scenario — agreement is based on surface plausibility or deference to the other model. Apply per §AntiConsensus: confidence is automatically downgraded one level (High → Medium, Medium → Low). If a Type C finding ranks in the Top 3, MELCHIOR MUST construct an adversarial objection against it regardless of depth level.
- **Type D convergence (Shared Blind Spot)**: Both models agree on a **methodological choice** (metric definition, null model, analytical framework, measurement protocol) that neither independently derived or validated — they adopted it as a shared unexamined assumption. Type D triggers a mandatory **methodological audit**: MELCHIOR must either (a) provide independent justification for the shared assumption (cite a derivation, validation study, or limiting-case argument), or (b) flag it as an unvalidated assumption with confidence downgrade one level. **Type D detection heuristic**: For each top finding, ask "What metric or method do BOTH sources use without questioning? Could a different reasonable metric yield a contradictory result?" If yes, classify as Type D.

**Intertextual Addition** (mandatory, all depths):
You MUST add at least one perspective, connection, or counter-argument from your own knowledge that no model raised. Mark with **[MELCHIOR]**. This is NOT derived from model outputs — it is your independent intellectual contribution as the third MAGI personality.

1. Read all available documents:
   - Always: `gemini_ideas.md`, `codex_ideas.md`
   - If `--depth medium` or `high` (or escalated from `auto`): `gemini_review_of_codex.md`, `codex_review_of_gemini.md`
   - If `--depth high` (or escalated from `auto`): `debate_round2_gemini.md`, `debate_round2_codex.md`
   - If evidence anchoring ran: `claim_evidence.md`
   - If `--depth auto` escalated to deep: `deep_investigation_{1..3}_pro.md`, `deep_investigation_{1..3}_con.md`, `escalation_analysis.md`
   - Always: `weights.json`, `personas.md`
   - If pre-flight ran: `preflight_context.md` (for MELCHIOR's direct reference to literature)

**Scope Divergence Check** (mandatory for `--depth medium|high`):
Compare scope declarations from Step 1a model outputs. If models interpreted the question with substantially different scope:
- Note in synthesis: "**Scope Note**: [Model A] interpreted this as [X]; [Model B] interpreted this as [Y]. This synthesis covers both interpretations — reply to narrow if needed."
- If scopes are aligned: omit this section.

2. Load `weights.json` and check `_meta.method`:
   - **If `method` is `"holistic"`**: Use holistic ranking — Claude reads all ideas, reviews, and debates, then directly ranks research findings based on integrated expert judgment. **No numeric dimension scores are computed.** Instead, for each finding, provide a **Ranking Rationale** (3-5 sentences) explaining why it ranks at this position. The rationale must:
     - Reference specific arguments, evidence, or debate outcomes from the brainstorm pipeline
     - Consider multiple evaluation angles (novelty, feasibility, impact, rigor, scalability) without reducing them to numbers
     - Explicitly compare against adjacent-ranked findings ("This ranks above X because... but below Y because...")
     - Note any caveats or close calls in the ranking
   - **If `method` is not `"holistic"`** (explicit, adaptive-recommended, domain-default, or custom): Use the weights to compute a **weighted score** for each research finding:
     - For each candidate finding, rate it on each weight dimension (0-10 scale)
     - Compute the weighted sum: `score = Σ(weight_i × rating_i)`
     - Rank findings by weighted score
3. Synthesize into a coherent research analysis that preserves the core scientific reasoning, mathematical formulations, testable predictions, and falsification conditions from brainstorm/review outputs. The synthesis must explain WHY each approach works (mechanism), not just WHAT to do (action plan). Structure:
   - **Personas Used** — brief summary of assigned Gemini and Codex personas
   - **Scoring Method** — document the ranking approach:
     - **Holistic mode**: State "Holistic Expert Judgment" and briefly explain that findings were ranked by integrated assessment without numeric weights
     - **Weighted mode**: Show the weights used for ranking (from `weights.json`), including `_meta.method` to document how weights were selected
   - **Top Research Findings** (Core Findings, Top 5) — ranked. Present the top 5 findings using the full narrative structure below. Each finding: 300-600 words. For each finding:
      - **(a) Mechanism Narrative** (150-250 words, continuous prose, REQUIRED) — Explain the causal or mathematical mechanism step by step; preserve key equations, variable meanings, and derivation paths. If the brainstorm/review output contains a mathematical formulation, reproduce it here with attribution.
      - **(b) Mathematical Core & Predictions** — Preserve key equations inline. Include specific numerical predictions with error bars where available.
      - **(c) Falsification Criteria** — What result would disprove this finding?
      - **(d) T7 Summary Footer** — Compact reference (each field 1-2 sentences): Motivation, Expected Effects, Side Effects, Key Evidence, Confidence
      - **(e) Ranking Rationale**:
        - **[Holistic mode]** 3-5 sentence justification referencing pipeline evidence
        - **[Weighted mode]** Score breakdown per dimension
      - **(f) [MELCHIOR] Verdict**: Opus's independent judgment on this finding:
        - **Endorse**: "I endorse this finding because [reason distinct from the finding's own stated reasoning]. [Reservation, if any.]"
        - **Revise**: "I revise: [original claim] → [revised claim]. Reason: [explanation]."
        - **Reject/Demote**: "I reject this finding's current ranking. Reason: [explanation]. Demoted to [new tier]. Promoted replacement: [candidate]."
   - **Appendix: Additional Findings** — For findings ranked 6+, provide a structured summary table: `| Finding | Core Claim (1 sentence) | Key Equation/Metric | Predicted Outcome | Source Model(s) | Confidence |`. Do NOT omit mathematical content — condense it into the Key Equation column.
   - **Consensus Points** — ideas both models agreed on
   - **Divergence Points** — areas of disagreement and how to resolve them
   - **Debate Resolution** (`--depth high` or escalated from `auto`) — for each of the 3 debated disagreements, document the final resolution: who conceded, what was revised, and the synthesized position. If `claim_evidence.md` was used, note which real-world evidence influenced the resolution.
   - **Deep Investigation Results** (`--depth auto` escalated to deep only) — for each of the 3 deeply investigated contested ideas: summarize the pro/con arguments, cite evidence, and state how the deep investigation affected the idea's ranking. Format: "**Contested Idea: [title]** — Pro: [summary]. Con: [summary]. Evidence tilts: [toward/against/inconclusive]. Ranking effect: [promoted/demoted/unchanged]."
   - **Evidence Grounding** (`--depth high+` or escalated from `auto`, if `claim_evidence.md` exists) — summary of how real-world evidence from the evidence anchoring step influenced the synthesis. Format: "**Literature-Grounded Adjustments**: [N] findings had their confidence adjusted based on published evidence. Key papers: [2-3 most influential papers with DOIs]."
   - **Cross-Validation Connections** — Unexpected connections between different models' outputs: where independent analyses converge on the same prediction, contradict each other, or reveal complementary mechanisms. These cross-model connections are the unique value of synthesis that cannot be found in any individual brainstorm output.
   - **Emergent Insights** — patterns or connections visible only when combining both models' outputs that neither model captured individually
   - **Depth Escalation Trace** (`--depth auto` only) — record the auto-escalation decision for traceability. Copy the key metrics from `escalation_analysis.md`: contention score, decision, top contested ideas.
   - **Synthesis Epilogue (T8)** — Research Gaps, Non-Recommendations, Next Three Steps (see T8 template)
   - **MAGI Process Traceability** — table mapping each ranked finding to its source model(s) and artifact file path(s) (e.g., which ideas came from Gemini vs. Codex, which reviews supported/challenged them)
   - **Recommended Path Forward** — Claude's recommendation with reasoning

4. **[MELCHIOR] Comprehensive Self-Review** (mandatory, revision trigger):

   After writing the full synthesis but BEFORE the mechanical checklist, MELCHIOR re-reads the entire synthesis as a critical reviewer. This is a holistic quality gate — not a line-item check. Append the review as a `## MELCHIOR Comprehensive Review` section at the end of synthesis.md (after Traceability, before the mechanical checklist edits).

   Evaluate the synthesis on these five axes. For each axis, write 2-4 sentences of assessment and a **verdict** (PASS / REVISE):

   **(a) Question Fidelity** — Do the top findings actually answer the original research question? Or has the synthesis drifted to an easier adjacent question? Compare the original topic (from `.workspace.json`) against what the top 3 findings collectively address. If there is drift, name it: "The original question asked X, but findings 1-3 address Y instead."

   **(b) Inter-Finding Coherence** — Do the Top 5 findings form a coherent research narrative, or do they contradict each other? If contradictions exist, are they explicitly acknowledged as productive tensions (acceptable) or unintentional inconsistencies (must fix)?

   **(c) Aggregate Mechanism Audit** — Looking at the Top 5 as a set: how many propose a genuinely new causal mechanism vs. restate known domain knowledge in new vocabulary? Count: "N/5 findings propose novel mechanisms; M/5 are refinements of known approaches." If N < 2, flag as a quality concern.

   **(d) Causal vs. Diagnostic Balance** — Across ALL Next Three Steps entries: count the step types. Report the ratio: "Intervention/Ablation/Null: X steps. Empirical/Design/Review: Y steps." If no Intervention, Ablation, or Null steps exist in the entire synthesis, this is a **mandatory REVISE** — go back and add at least one causal step per Tier 1 finding.

   **(e) Blind Spot Confession** — Name 1-2 questions that this synthesis does NOT address but that a domain expert would ask. These are not failures but honest scope limits. Format: "This synthesis does not address: [question]. Why: [reason — time constraint / outside model expertise / insufficient data]."

   **Revision protocol**: If any axis yields REVISE, go back and fix the corresponding section of the synthesis BEFORE proceeding. After revision, update the review verdict to PASS with a note: "REVISED — originally failed because [reason], fixed by [action]." Only proceed to step 5 when all five axes are PASS.

5. After completing the self-review and any revisions, verify (mechanical checklist):
   - [ ] Each top finding explains WHY the approach works (causal mechanism), not just WHAT to measure
   - [ ] **Mechanism Depth Test**: For each top finding, substitute the key mechanism term (e.g., "spectral bias", "inductive bias") with the generic phrase "something about the architecture." If the finding still makes the same prediction with the same specificity, the mechanism is a **re-description, not an explanation** — demote it from a finding to a "framing" and move it to the Appendix. Promote the next candidate.
   - [ ] Each top finding contains at least one equation or specific numerical prediction from brainstorm/review outputs
   - [ ] Operational content (GPU hours, timeline, risk ratings) is below 15% of total length; if exceeded, move excess to an appendix
   - [ ] At least one **[MELCHIOR]** marker exists in the synthesis (Intertextual Addition fulfilled)
   - [ ] Each top finding has an (f) [MELCHIOR] Verdict (Endorse/Revise/Reject with reason)
   - [ ] Convergence Interrogation Type A/B/D classification exists for convergent findings [`--depth medium|high` or escalated `auto`]
   - [ ] If `claim_evidence.md` exists: at least one finding's confidence or ranking was informed by real-world evidence, or an explicit note explains why no adjustment was needed [`--depth high+` or escalated `auto`]
   - [ ] If `--depth auto`: "Depth Escalation Trace" section exists in synthesis with contention score and decision
   - [ ] If `--depth auto` escalated to deep: "Deep Investigation Results" section exists with pro/con adjudication for each contested idea
   If any check fails, revise the relevant finding before finalizing.
6. Save to `brainstorm/synthesis.md`.

**Retroactive Question Crystallization** (always, all depths):
After completing the ranked synthesis, examine the top 5 findings and identify the research question they collectively answer. If this crystallized question differs substantively from the original input:
- Append a "**Note on Question Scope**" section: "The brainstorm converged around: *'[crystallized question]'*. This is [narrower/broader/differently-framed] than your original question. If you intended the original framing, consider re-running with scope: [adjusted scope]."
- If the crystallized question matches the original: omit this section entirely.

### Step 2: User Feedback

Present the synthesis to the user with:
- A concise summary of the top 3-5 research findings
- Clear options for the user to choose, modify, or combine findings
- Ask for any additional constraints or preferences

Wait for user input before proceeding.

## Output Files

**`--depth low|medium|high|auto`:**
```
brainstorm/
├── weights.json                      # Scoring weights + selection metadata (always)
├── personas.md                       # Assigned expert personas (always)
├── preflight_context.md              # Pre-flight literature context (--depth medium+)
├── briefing_gemini.md                # Persona-specific briefing for Gemini (--depth medium+)
├── briefing_codex.md                 # Persona-specific briefing for Codex (--depth medium+)
├── gemini_ideas.md                   # Gemini brainstorm output (always)
├── codex_ideas.md                    # Codex brainstorm output (always)
├── gemini_review_of_codex.md         # Cross-review (--depth medium|high|auto)
├── codex_review_of_gemini.md         # Cross-review (--depth medium|high|auto)
├── escalation_analysis.md            # Depth escalation decision (--depth auto only)
├── claim_evidence.md                 # Evidence for disputed claims (--depth high, or auto escalated)
├── disagreements.md                  # Disagreement summary for debate (--depth high, or auto escalated)
├── debate_round2_gemini.md           # Adversarial debate (--depth high, or auto escalated)
├── debate_round2_codex.md            # Adversarial debate (--depth high, or auto escalated)
├── deep_investigation_{i}_pro.md     # Pro argument for contested idea i (--depth auto→deep only)
├── deep_investigation_{i}_con.md     # Con argument for contested idea i (--depth auto→deep only)
└── synthesis.md                      # Claude synthesis (always)
```

**`--depth max`:**
```
brainstorm/
├── weights.json                      # Scoring weights + selection metadata
├── personas.md                       # N domain-specialist personas
├── preflight_context.md              # Pre-flight literature context
├── briefing_persona_{i}.md           # Per-persona briefing (one per persona)
├── persona_1/                        # Persona 1 mini-MAGI output
│   ├── gemini_ideas.md
│   ├── codex_ideas.md
│   ├── gemini_review_of_codex.md
│   ├── codex_review_of_gemini.md
│   └── conclusion.md
├── persona_2/                        # Persona 2 mini-MAGI output
│   └── ...                           # (same 5 files)
├── persona_N/                        # Persona N mini-MAGI output
│   └── ...
├── all_conclusions.md                # Consolidated persona conclusions for Layer 2
├── meta_review_gemini.md             # Gemini meta-review of all conclusions
├── meta_review_codex.md              # Codex meta-review of all conclusions
├── meta_disagreements.md             # Meta-disagreement summary for debate
├── meta_claim_evidence.md            # Evidence for meta-level disputed claims (Phase B+)
├── debate_context_for_gemini.md      # Consolidated: disagreements + Codex meta-review + evidence
├── debate_context_for_codex.md       # Consolidated: disagreements + Gemini meta-review + evidence
├── meta_debate_gemini.md             # Adversarial debate — Gemini
├── meta_debate_codex.md              # Adversarial debate — Codex
└── synthesis.md                      # Enriched final synthesis
```
