# Research Brainstorm Skill

## Description
Generates and cross-validates research ideas using Gemini and Codex in parallel, then synthesizes results with Claude.

## Usage
```
/research-brainstorm "research topic" [--domain physics|ai_ml|statistics|mathematics|paper] [--weights '{"novelty":0.4,...}'|adaptive] [--depth low|medium|high|max] [--personas N] [--claude-only] [--substitute "Gemini -> Opus"]
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
    - `high` — Cross-review + adversarial debate round
    - `max` — Hierarchical MAGI-in-MAGI: N persona subagents run parallel mini-MAGI pipelines, then meta-review + adversarial debate across all perspectives
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

The following templates are referenced by ID throughout this document. When executing, expand the template in context.

**T1: Cognitive Styles**

| ID | Style | One-line directive |
|---|---|---|
| T1-CD | Creative-Divergent | Unconventional connections across adjacent fields, "What if?" scenarios, wide exploratory breadth, questioning fundamental assumptions |
| T1-AC | Analytical-Convergent | Step-by-step feasibility analysis, established methodologies, deep evaluation, practical constraints, risk assessment |
| T1-EE | Expansive Explorer | Push boundaries, explore emerging approaches, propose frontier ideas, challenge conventional thinking. (Replaces Gemini in `--depth max` internal subagents) |
| T1-GB | Grounded Builder | Focus on proven approaches, clear implementation paths, established tools, demonstrable results. (Replaces Codex in `--depth max` internal subagents) |

**T2: Review Instructions**

- **T2-Science**: Review for technical feasibility, scientific rigor, novelty, and potential impact. For each idea: (1) Restate the proponent's mechanism in your own words. (2) Identify strengths and weaknesses — for each, explain concretely in what scenario it manifests and why it matters. (3) Pose one counterfactual: "If component X were removed, would the claim still hold?" (4) Suggest improvements.
- **T2-Feasibility**: Review for implementation feasibility, computational practicality, available tools/datasets, and timeline realism. For each idea: (1) Restate the proponent's mechanism. (2) Strengths and weaknesses with concrete scenarios. (3) Name the warrant connecting the claimed benefit to the proposed mechanism. (4) Suggest improvements.

**T3: DCR Debate Framework**

For each disagreement: (1) **Defend** your position if correct, providing additional evidence. (2) **Concede** if the opposing argument is stronger, explaining why. (3) **Revise** your assessment to a new position if appropriate. Walk through reasoning step by step — explain the logic chain so a reader can follow exactly why you defend, concede, or revise.

**T4: Mechanism Requirement**

For each idea, include a brief mechanism (1-2 sentences): how and why does this approach address the stated problem?

**T5: Subagent Output Convention**

Save to `{output_dir}/brainstorm/{filename}` (absolute path). `{output_dir}` comes from `.workspace.json`; `{filename}` is specified in each step (e.g., `gemini_ideas.md`). Start the file with: `> Source: Claude Agent subagent ({mode}, {style})` followed by persona name and ISO timestamp. Mode is `claude-only mode` or `substituted for {Agent}`. **Never save files outside `{output_dir}/brainstorm/`.**

**T6: Subagent Prompt Structure**

Every claude-only/substituted subagent follows this structure: (1) T1 cognitive style directive. (2) Persona context: `[Persona: {name} — {expertise}]` + guiding question. (3) **Absolute `{output_dir}` path** (from `.workspace.json`). (4) Read domain template via Read tool (skip if none). (5) Task-specific instruction. (6) Output per T5 using absolute paths.

**T7: Finding Summary Footer**

Each ranked research finding ends with a T7 summary footer — a compact reference block (each field 1-2 sentences) placed AFTER the main narrative body. T7 is a summary, not the body itself:
- **Motivation** — Why is this finding significant? What gap does it address? (1-2 sentences)
- **Expected Effects** — Concrete benefits in brief. (1-2 sentences)
- **Side Effects** — Risks or prerequisites. Reference specific review/debate points; do not fabricate. (1-2 sentences)
- **Key Evidence** — Which arguments led here and what was debated. (1-2 sentences)
- **Confidence** — High/Medium/Low tied to a specific warrant weakness (e.g., "Medium — assumes standard optimizer dynamics; second-order methods may change the analysis").

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
- Include this formatting instruction in prompts to Gemini and Codex when the topic involves mathematical content

### Path Safety Rule

**ALL artifacts MUST be written under `{output_dir}/`.** Never write brainstorm files (`*.md`, `*.json`) directly to the project root, the user's working directory, or any path outside `outputs/`.

- `{output_dir}` is the **absolute path** stored in `.workspace.json` at the output directory root.
- **Before writing any file**: if `{output_dir}` is uncertain (e.g., after context compression), recover it by reading `.workspace.json`:
  1. `Glob` for `outputs/*/.workspace.json`, select the most recently modified match.
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
5. **Parse `--depth`**: Accept `low`, `medium`, `high`, or `max` (default: `medium`).
   - `low` — Skip Step 1b (cross-review), go directly to Step 1c (synthesis)
   - `medium` — Standard one-shot cross-review (current default behavior)
   - `high` — Cross-review + adversarial debate (Step 1b+)
   - `max` — Hierarchical MAGI-in-MAGI pipeline (Steps 1-max-a through 1-max-d replace Steps 1a/1b/1b+/1c)
6. **Parse `--personas N|auto`**: Accept integer 2-4 or the string `auto` (default: `auto`). Only used when `--depth max`; ignored otherwise.
   - If `auto`: Defer persona count determination to Step 0b, where Claude analyzes the topic's complexity, number of distinct sub-disciplines, and methodological diversity to select the optimal N (2-4).
   - If an explicit integer is given: Use that value directly.
7. **Parse `--claude-only`**: Boolean flag (default: `false`). When present, all Gemini/Codex MCP calls are replaced with Claude Agent subagents. See the **Claude-Only Mode** section above for the replacement table and cognitive style definitions.
8. **Parse `--substitute`**: Accept zero or more `--substitute "Agent -> Opus"` flags. Valid agent names: `Gemini`, `Codex`. Valid target: `Opus`. When specified, the named agent's MCP calls are replaced with Claude Agent subagents using the same cognitive style mappings as `--claude-only` mode (see **Agent Substitution** section). `--substitute` and `--claude-only` are mutually exclusive — if both are provided, `--claude-only` takes precedence. If both `"Gemini -> Opus"` and `"Codex -> Opus"` are specified, treat as equivalent to `--claude-only`.

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

4. **Ask the user for confirmation** using `AskUserQuestion`:
   - Option A: **"Accept recommended weights"** (Recommended) — use the adaptive weights
   - Option B: **"Use domain defaults"** — use the unmodified domain baseline
   - Other: User provides custom weights as JSON

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

**For `--depth low|medium|high` (2 personas):**

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

### Step 1a: Parallel Independent Brainstorming

Execute these two calls **simultaneously** (in the same message). **Prepend the assigned persona** from `brainstorm/personas.md` to each prompt:

Each call includes: persona context, guiding question, domain template (if exists, via `@{domain_template_path}`), and **T4** mechanism requirement. Use `ideaCount: 12, includeAnalysis: true, methodology: "auto"`.

**Gemini**: `mcp__gemini-cli__brainstorm`, `model: "gemini-3.1-pro-preview"` — Generate diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs.

**Codex**: `mcp__codex-cli__brainstorm`, `model: "gpt-5.4"` — Generate implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches.

> Note: If Codex MCP is unavailable, fall back to a Claude Opus subagent with T1-AC cognitive style (same as `--substitute "Codex -> Opus"`), using the Codex persona and implementation-focused framing per **T6**.

> **If `--claude-only`**: Replace both calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD, Gemini persona): Generate 12 diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs. Apply **T4**. Save to `brainstorm/gemini_ideas.md` per **T5**.
> - **Subagent B** (T1-AC, Codex persona): Generate 12 implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches. Apply **T4**. Save to `brainstorm/codex_ideas.md` per **T5**.

Save results to:
- `brainstorm/gemini_ideas.md` — Gemini's (or Subagent A's) raw output with header noting source, persona, and timestamp
- `brainstorm/codex_ideas.md` — Codex's (or Subagent B's) raw output with header noting source, persona, and timestamp

### Step 1b: Cross-Check (`--depth medium` or `--depth high` only)

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

### Step 1b+: Adversarial Debate (`--depth high` only)

> **If `--depth low` or `--depth medium`**: Skip this step entirely.

After Round 1 cross-review, Claude identifies the **top 3 points of disagreement** between Gemini and Codex (e.g., conflicting feasibility assessments, divergent novelty ratings, opposing recommendations). **Save the disagreement summary to `brainstorm/disagreements.md`** before the debate calls.

Execute Round 2 **simultaneously**:

**Round 2 — Defend/Concede/Revise** (execute simultaneously):

Each call includes: persona context, `@{output_dir}/brainstorm/disagreements.md`, **T3** debate framework, own review, and opposing review.

- **Gemini**: `mcp__gemini-cli__ask-gemini`, `model: "gemini-3.1-pro-preview"`, refs: `@{output_dir}/brainstorm/gemini_review_of_codex.md` + `@{output_dir}/brainstorm/codex_review_of_gemini.md`
- **Codex**: `mcp__codex-cli__ask-codex`, `model: "gpt-5.4"`, refs: `@{output_dir}/brainstorm/codex_review_of_gemini.md` + `@{output_dir}/brainstorm/gemini_review_of_codex.md`

> **If `--claude-only`**: Replace both debate calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD, Gemini persona): Read `brainstorm/disagreements.md`, `brainstorm/gemini_review_of_codex.md`, `brainstorm/codex_review_of_gemini.md`. Apply **T3** debate framework. Save to `brainstorm/debate_round2_gemini.md` per **T5**.
> - **Subagent B** (T1-AC, Codex persona): Read `brainstorm/disagreements.md`, `brainstorm/codex_review_of_gemini.md`, `brainstorm/gemini_review_of_codex.md`. Apply **T3** debate framework. Save to `brainstorm/debate_round2_codex.md` per **T5**.

Save results to:
- `brainstorm/debate_round2_gemini.md`
- `brainstorm/debate_round2_codex.md`

### Step 1-max-a: Layer 1 — Parallel Persona Subagents (`--depth max` only)

> **If `--depth` is not `max`**: Skip Steps 1-max-a through 1-max-d entirely. Use Steps 1a/1b/1b+/1c instead.

Spawn **N Task subagents simultaneously** (one per persona, `subagent_type: general-purpose`). Each subagent receives the persona definition and executes a self-contained mini-MAGI pipeline:

**Each subagent prompt includes:**
1. **Containment directive** (MUST be first): `"DO NOT create any directories. DO NOT run Step 0 setup. All directories already exist. Write files ONLY to the exact absolute paths listed below. Do NOT interpret SKILL.md setup instructions as applicable to you."`
2. The **absolute `{output_dir}` path** and the **absolute persona subdirectory path** (`{output_dir}/brainstorm/persona_{i}/`)
3. The persona definition (name, expertise, guiding question, primary lens) from `brainstorm/personas.md`
4. The research topic and domain template (if available)
5. The following 5-step execution plan:

   **A. Gemini Brainstorm** — Call `mcp__gemini-cli__brainstorm` with the persona's viewpoint. Save to `brainstorm/persona_{i}/gemini_ideas.md`.

   **B. Codex Brainstorm** — Call `mcp__codex-cli__brainstorm` with the persona's viewpoint. Save to `brainstorm/persona_{i}/codex_ideas.md`.

   > **If `--claude-only`**: Replace A and B with two Agent sub-subagents (simultaneously), per **T6**:
   > - **A'** (T1-EE, persona_{i}): Generate 12 creative research ideas from this persona's perspective. Apply **T4**. Save to `brainstorm/persona_{i}/gemini_ideas.md` per **T5**.
   > - **B'** (T1-GB, persona_{i}): Generate 12 implementation-focused ideas from this persona's perspective. Apply **T4**. Save to `brainstorm/persona_{i}/codex_ideas.md` per **T5**.

   **C+D. Cross-Review (simultaneous):**
   - Gemini reviews Codex ideas using `@{output_dir}/brainstorm/persona_{i}/codex_ideas.md` → save to `brainstorm/persona_{i}/gemini_review_of_codex.md`
   - Codex reviews Gemini ideas using `@{output_dir}/brainstorm/persona_{i}/gemini_ideas.md` → save to `brainstorm/persona_{i}/codex_review_of_gemini.md`
   > **If `--claude-only`**: Replace C+D with two Agent sub-subagents (simultaneously), per **T6**:
   > - **C'** (T1-EE, persona_{i}): Read `{output_dir}/brainstorm/persona_{i}/codex_ideas.md`. Apply **T2-Science** review. Save to `brainstorm/persona_{i}/gemini_review_of_codex.md` per **T5**.
   > - **D'** (T1-GB, persona_{i}): Read `{output_dir}/brainstorm/persona_{i}/gemini_ideas.md`. Apply **T2-Feasibility** review. Save to `brainstorm/persona_{i}/codex_review_of_gemini.md` per **T5**.

   **E. Persona Conclusion** — The subagent synthesizes its top 3 research findings. For each finding, provide:
   - **Mechanism** — How does this solve the problem? Walk through the cause-effect chain so a reader unfamiliar with the technique can understand the reasoning.
   - **Evidence** — What specific arguments from the brainstorm/review support this? Why are they convincing?
   - **Comparison** — Why this approach over the most obvious alternative?
   Note areas of internal agreement and disagreement between the two models (or two cognitive styles in claude-only mode). Save to `brainstorm/persona_{i}/conclusion.md`.

Wait for all N subagents to complete before proceeding.

### Step 1-max-b: Layer 1 — Output Collection

0. **Post-completion path audit** (per Subagent Containment Rule):
   - `Glob` for `outputs/*_v*/` and verify only the expected output directory exists for this session's date/topic.
   - Check for `brainstorm/` in the project root (`Glob` for `brainstorm/`).
   - If spurious directories are found: delete them. If they contain artifacts that should have been in `{output_dir}`, move the files first, then delete the directory.
1. Use Glob to verify that all N `brainstorm/persona_{i}/conclusion.md` files exist.
   - If any are missing, re-spawn the failed subagent(s) and wait for completion.
2. Read all N `conclusion.md` files.
3. Construct a **cross-persona summary** identifying:
   - **Recurring themes** — findings proposed by 2+ personas
   - **Unique findings** — ideas that appeared in only one persona's output
   - **Explicit disagreements** — contradictory assessments across personas
4. **Consolidate conclusions for Layer 2**: Create `brainstorm/all_conclusions.md` by concatenating
   all N conclusion files with clear separators:
   ```markdown
   # Persona 1: {persona_1_name} — {persona_1_lens}

   {persona_1_conclusion_content}

   ---

   # Persona 2: {persona_2_name} — {persona_2_lens}

   {persona_2_conclusion_content}

   ---

   ... (for all N personas)
   ```
   This single consolidated file replaces multiple @-references in Layer 2 calls.

### Step 1-max-c: Layer 2 — Meta-Review + Adversarial Debate

**Phase A — Parallel Meta-Reviews:**

Execute simultaneously:

**Meta-Review prompt** (same for both, execute simultaneously):
```
"You are reviewing the outputs of {N} domain-specialist research personas who independently analyzed: {topic}\n\nHere are all persona conclusions:\n@{output_dir}/brainstorm/all_conclusions.md\n\nProvide a meta-review covering:\n1. **Coverage analysis** — Which aspects are well-covered vs. underexplored?\n2. **Quality assessment** — Rate each persona's conclusions (depth, rigor, creativity) on a 1-10 scale\n3. **Cross-persona synthesis** — What emerges when combining all perspectives?\n4. **Top 3 disagreements** — Most significant contradictions with specific quotes\n5. **Recommended findings** — Top 5 research findings. For each, explain the mechanism."
```
- **Gemini**: `mcp__gemini-cli__ask-gemini`, `model: "gemini-3.1-pro-preview"` → Save to `brainstorm/meta_review_gemini.md`
- **Codex**: `mcp__codex-cli__ask-codex`, `model: "gpt-5.4"` → Save to `brainstorm/meta_review_codex.md`

> **If `--claude-only`**: Replace both meta-review calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD): Read `brainstorm/all_conclusions.md`. Provide meta-review with the 5-point structure above. Save to `brainstorm/meta_review_gemini.md` per **T5**.
> - **Subagent B** (T1-AC): Read `brainstorm/all_conclusions.md`. Provide meta-review with the 5-point structure above. Save to `brainstorm/meta_review_codex.md` per **T5**.

**Phase B — Disagreement Extraction:**

Claude reads both meta-reviews and extracts the **top 3 cross-persona disagreements** — prioritizing disagreements identified by both reviewers. For each disagreement, produce a structured summary: the claim, which personas support each side, and the core tension. **Save the meta-disagreement summary to `brainstorm/meta_disagreements.md`** before the debate calls.

**Phase C — Consolidate Debate Context + Adversarial Debate:**

Before the debate calls, create consolidated context files (each containing exactly what the opposing model needs):
- `brainstorm/debate_context_for_gemini.md` — concatenate `brainstorm/meta_disagreements.md` + `brainstorm/meta_review_codex.md`
- `brainstorm/debate_context_for_codex.md` — concatenate `brainstorm/meta_disagreements.md` + `brainstorm/meta_review_gemini.md`

Then execute the debate calls **simultaneously**. Each call includes: `[Meta-Reviewer]` context, consolidated debate context file, **T3** debate framework.

- **Gemini**: `mcp__gemini-cli__ask-gemini`, `model: "gemini-3.1-pro-preview"`, ref: `@{output_dir}/brainstorm/debate_context_for_gemini.md` → Save to `brainstorm/meta_debate_gemini.md`
- **Codex**: `mcp__codex-cli__ask-codex`, `model: "gpt-5.4"`, ref: `@{output_dir}/brainstorm/debate_context_for_codex.md` → Save to `brainstorm/meta_debate_codex.md`

> **If `--claude-only`**: Replace both debate calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD): Read `brainstorm/debate_context_for_gemini.md`. Apply **T3** debate framework. Save to `brainstorm/meta_debate_gemini.md` per **T5**.
> - **Subagent B** (T1-AC): Read `brainstorm/debate_context_for_codex.md`. Apply **T3** debate framework. Save to `brainstorm/meta_debate_codex.md` per **T5**.

### Step 1-max-d: Layer 3 — Final Enriched Synthesis (`--depth max`)

1. Read all available documents:
   - `weights.json`, `personas.md`
   - All N `persona_{i}/conclusion.md` files
   - `meta_review_gemini.md`, `meta_review_codex.md`
   - `meta_debate_gemini.md`, `meta_debate_codex.md`
2. Load `weights.json` and check `_meta.method`:
   - **If `method` is `"holistic"`**: Use holistic ranking — Claude reads all persona conclusions, meta-reviews, and debate resolutions, then directly ranks research findings based on integrated expert judgment. **No numeric dimension scores are computed.** For each finding, provide a **Ranking Rationale** (3-5 sentences) that references specific persona arguments, cross-persona consensus/disagreement, and debate outcomes. Explicitly compare against adjacent-ranked findings.
   - **If `method` is not `"holistic"`**: Compute **weighted scores** for each research finding (same 0-10 rating per dimension, weighted sum).
3. Produce an **enriched `brainstorm/synthesis.md`** — a research analysis that preserves the core scientific reasoning, mathematical formulations, testable predictions, and falsification conditions from persona conclusions. The synthesis must explain WHY each approach works (mechanism), not just WHAT to do (action plan). Structure:
   1. **Personas Used** — table of N personas with name, expertise summary, and primary lens
   2. **Scoring Method** — document the ranking approach:
      - **Holistic mode**: State "Holistic Expert Judgment" and explain that findings were ranked by integrated assessment across all personas, meta-reviews, and debates without numeric weights
      - **Weighted mode**: Show the weights used for ranking (from `weights.json`), including `_meta.method` (explicit, adaptive-recommended, domain-default, or custom)
   3. **Top Research Findings** (Core Findings, Top 5) — ranked. Present the top 5 findings using the full narrative structure below. Each finding: 300-600 words. For each finding:
      - **(a) Mechanism Narrative** (150-250 words, continuous prose, REQUIRED) — Explain the causal or mathematical mechanism step by step; preserve key equations, variable meanings, and derivation paths from persona conclusions. If a persona conclusion contains a mathematical formulation, reproduce it here with attribution.
      - **(b) Mathematical Core & Predictions** — Preserve key equations inline from persona conclusions. Include specific numerical predictions with error bars where available.
      - **(c) Falsification Criteria** — What result would disprove this finding?
      - **(d) T7 Summary Footer** — Compact reference (each field 1-2 sentences): Motivation, Expected Effects, Side Effects, Key Evidence, Confidence
      - **(e) Ranking Rationale**:
        - **[Holistic mode]** 3-5 sentence justification referencing persona arguments, cross-persona consensus, and debate outcomes
        - **[Weighted mode]** Score breakdown per dimension
      - Which personas supported this finding
   4. **Appendix: Additional Findings** — For findings ranked 6+, provide a structured summary table: `| Finding | Core Claim (1 sentence) | Key Equation/Metric | Predicted Outcome | Source Persona(s) | Confidence |`. Do NOT omit mathematical content — condense it into the Key Equation column.
   5. **Cross-Persona Consensus** — ideas where 3+ personas independently converged
   6. **Unique Contributions** — valuable ideas that only a single persona identified
   7. **Debate Resolution** — for each of the 3 debated disagreements: the original tension, how each meta-reviewer responded (defend/concede/revise), and the synthesized resolution
   8. **Cross-Validation Connections** — Unexpected connections between different personas' conclusions: where independent analyses converge on the same prediction, contradict each other, or reveal complementary mechanisms. These cross-persona connections are the unique value of synthesis that cannot be found in any individual conclusion.
   9. **Emergent Insights** — patterns or connections visible only from the cross-persona vantage point that no individual persona captured
   10. **Recommended Path Forward** — Claude's top recommendation with reasoning grounded in the multi-persona analysis
   11. **MAGI Process Traceability** — table mapping each conclusion to its source persona, layer, and artifact file path
4. After completing the synthesis, verify:
   - [ ] Each top finding explains WHY the approach works (causal mechanism), not just WHAT to measure
   - [ ] Each top finding contains at least one equation or specific numerical prediction from persona conclusions
   - [ ] Operational content (GPU hours, timeline, risk ratings) is below 15% of total length; if exceeded, move excess to an appendix
   If any check fails, revise the relevant finding before finalizing.
5. Save to `brainstorm/synthesis.md`.

### Step 1c: Claude Synthesis

> **If `--depth max`**: Skip — synthesis is produced by Step 1-max-d above.

1. Read all available documents:
   - Always: `gemini_ideas.md`, `codex_ideas.md`
   - If `--depth medium` or `high`: `gemini_review_of_codex.md`, `codex_review_of_gemini.md`
   - If `--depth high`: `debate_round2_gemini.md`, `debate_round2_codex.md`
   - Always: `weights.json`, `personas.md`
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
   - **Appendix: Additional Findings** — For findings ranked 6+, provide a structured summary table: `| Finding | Core Claim (1 sentence) | Key Equation/Metric | Predicted Outcome | Source Model(s) | Confidence |`. Do NOT omit mathematical content — condense it into the Key Equation column.
   - **Consensus Points** — ideas both models agreed on
   - **Divergence Points** — areas of disagreement and how to resolve them
   - **Debate Resolution** (`--depth high` only) — for each of the 3 debated disagreements, document the final resolution: who conceded, what was revised, and the synthesized position
   - **Cross-Validation Connections** — Unexpected connections between different models' outputs: where independent analyses converge on the same prediction, contradict each other, or reveal complementary mechanisms. These cross-model connections are the unique value of synthesis that cannot be found in any individual brainstorm output.
   - **Emergent Insights** — patterns or connections visible only when combining both models' outputs that neither model captured individually
   - **MAGI Process Traceability** — table mapping each ranked finding to its source model(s) and artifact file path(s) (e.g., which ideas came from Gemini vs. Codex, which reviews supported/challenged them)
   - **Recommended Path Forward** — Claude's recommendation with reasoning
4. After completing the synthesis, verify:
   - [ ] Each top finding explains WHY the approach works (causal mechanism), not just WHAT to measure
   - [ ] Each top finding contains at least one equation or specific numerical prediction from brainstorm/review outputs
   - [ ] Operational content (GPU hours, timeline, risk ratings) is below 15% of total length; if exceeded, move excess to an appendix
   If any check fails, revise the relevant finding before finalizing.
5. Save to `brainstorm/synthesis.md`.

### Step 2: User Feedback

Present the synthesis to the user with:
- A concise summary of the top 3-5 research findings
- Clear options for the user to choose, modify, or combine findings
- Ask for any additional constraints or preferences

Wait for user input before proceeding.

## Output Files

**`--depth low|medium|high`:**
```
brainstorm/
├── weights.json                  # Scoring weights + selection metadata (always)
├── personas.md                   # Assigned expert personas (always)
├── gemini_ideas.md               # Gemini brainstorm output (always)
├── codex_ideas.md                # Codex brainstorm output (always)
├── gemini_review_of_codex.md     # Cross-review (--depth medium|high)
├── codex_review_of_gemini.md     # Cross-review (--depth medium|high)
├── disagreements.md              # Disagreement summary for debate (--depth high only)
├── debate_round2_gemini.md       # Adversarial debate (--depth high only)
├── debate_round2_codex.md        # Adversarial debate (--depth high only)
└── synthesis.md                  # Claude synthesis (always)
```

**`--depth max`:**
```
brainstorm/
├── weights.json                  # Scoring weights + selection metadata
├── personas.md                   # N domain-specialist personas
├── persona_1/                    # Persona 1 mini-MAGI output
│   ├── gemini_ideas.md
│   ├── codex_ideas.md
│   ├── gemini_review_of_codex.md
│   ├── codex_review_of_gemini.md
│   └── conclusion.md
├── persona_2/                    # Persona 2 mini-MAGI output
│   └── ...                       # (same 5 files)
├── persona_N/                    # Persona N mini-MAGI output
│   └── ...
├── all_conclusions.md            # Consolidated persona conclusions for Layer 2
├── meta_review_gemini.md         # Gemini meta-review of all conclusions
├── meta_review_codex.md          # Codex meta-review of all conclusions
├── meta_disagreements.md         # Meta-disagreement summary for debate
├── debate_context_for_gemini.md  # Consolidated: disagreements + Codex meta-review
├── debate_context_for_codex.md   # Consolidated: disagreements + Gemini meta-review
├── meta_debate_gemini.md         # Adversarial debate — Gemini
├── meta_debate_codex.md          # Adversarial debate — Codex
└── synthesis.md                  # Enriched final synthesis
```
