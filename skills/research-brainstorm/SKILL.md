# Research Brainstorm Skill

## Description
Generates and cross-validates research ideas using Gemini and Codex in parallel, then synthesizes results with Claude.

## Usage
```
/research-brainstorm "research topic" [--domain physics|ai_ml|statistics|mathematics|paper] [--weights '{"novelty":0.4,"feasibility":0.3,"impact":0.3}'] [--depth low|medium|high|max] [--personas N] [--claude-only]
```

## Arguments
- `$ARGUMENTS` — The research topic and optional flags:
  - `--domain` — Research domain (physics, ai_ml, statistics, mathematics, paper). Auto-inferred if omitted.
  - `--weights` — JSON object of scoring weights for direction ranking. Keys: `novelty`, `feasibility`, `impact`, `rigor`, `scalability`. Values must sum to 1.0. If omitted, Claude analyzes the prompt and recommends adaptive weights for user confirmation (see Step 0a).
  - `--depth` — Controls review depth (default: `medium`):
    - `low` — Skip cross-review, go directly to synthesis
    - `medium` — Standard one-shot cross-review (current behavior)
    - `high` — Cross-review + adversarial debate round
    - `max` — Hierarchical MAGI-in-MAGI: N persona subagents run parallel mini-MAGI pipelines, then meta-review + adversarial debate across all perspectives
  - `--personas N|auto` — Number of domain-specialist subagents for `--depth max` (default: `auto`, range: 2-5). When `auto`, Claude analyzes the topic to determine the optimal persona count. Ignored for other depth levels.
  - `--claude-only` — Replace all Gemini/Codex MCP calls with Claude Agent subagents. Use when external model endpoints are unavailable or for a Claude-only workflow. Two subagents with distinct cognitive styles (Creative-Divergent and Analytical-Convergent) ensure perspective diversity.

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-2.5-pro"` (fallback)
  3. Claude (last resort — skip Gemini MCP tool, use Claude directly)
- **Codex**: Use `mcp__codex-cli__brainstorm` for ideation, `mcp__codex-cli__ask-codex` for analysis/review. If Codex fails 2+ times, fall back to Claude directly.
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

When this skill is invoked, follow these steps exactly:

### Step 0: Setup

1. Parse the research topic from `$ARGUMENTS`. If a `--domain` flag is provided, note the domain (physics, ai_ml, statistics, mathematics, paper). Otherwise, infer the domain from the topic.
2. Create the output directory: `outputs/{sanitized_topic}_{YYYYMMDD}_v{N}/brainstorm/`
   - Sanitize the topic: lowercase, replace spaces with underscores, remove special characters, truncate to 50 chars.
   - Use today's date in YYYYMMDD format.
   - Version: Glob for `outputs/{sanitized_topic}_{YYYYMMDD}_v*/` and set N = max existing + 1 (start at v1).
3. If a domain template exists at `${CLAUDE_PLUGIN_ROOT}/templates/domains/{domain}.md`, read it for context.
4. **Parse `--weights`**:
   - **If `--weights` is explicitly provided**: Validate that keys are a subset of {`novelty`, `feasibility`, `impact`, `rigor`, `scalability`} and values sum to 1.0. Save immediately to `brainstorm/weights.json` with metadata:
     ```json
     {
       "weights": { <user-provided weights> },
       "_meta": {
         "method": "explicit",
         "domain": "<detected domain>"
       }
     }
     ```
     Skip Step 0a entirely.
   - **If `--weights` is not provided**: Load domain defaults as a **baseline reference only** (do not save yet — Step 0a will handle saving after user confirmation):
   - `physics`: `{"novelty": 0.30, "feasibility": 0.15, "impact": 0.25, "rigor": 0.20, "scalability": 0.10}`
   - `ai_ml`: `{"novelty": 0.25, "feasibility": 0.25, "impact": 0.25, "rigor": 0.10, "scalability": 0.15}`
   - `statistics`: `{"novelty": 0.25, "feasibility": 0.20, "impact": 0.20, "rigor": 0.25, "scalability": 0.10}`
   - `mathematics`: `{"novelty": 0.35, "feasibility": 0.10, "impact": 0.20, "rigor": 0.30, "scalability": 0.05}`
   - `paper`: `{"novelty": 0.20, "feasibility": 0.25, "impact": 0.30, "rigor": 0.15, "scalability": 0.10}`
5. **Parse `--depth`**: Accept `low`, `medium`, `high`, or `max` (default: `medium`).
   - `low` — Skip Step 1b (cross-review), go directly to Step 1c (synthesis)
   - `medium` — Standard one-shot cross-review (current default behavior)
   - `high` — Cross-review + adversarial debate (Step 1b+)
   - `max` — Hierarchical MAGI-in-MAGI pipeline (Steps 1-max-a through 1-max-d replace Steps 1a/1b/1b+/1c)
6. **Parse `--personas N|auto`**: Accept integer 2-5 or the string `auto` (default: `auto`). Only used when `--depth max`; ignored otherwise.
   - If `auto`: Defer persona count determination to Step 0b, where Claude analyzes the topic's complexity, number of distinct sub-disciplines, and methodological diversity to select the optimal N (2-5).
   - If an explicit integer is given: Use that value directly.
7. **Parse `--claude-only`**: Boolean flag (default: `false`). When present, all Gemini/Codex MCP calls are replaced with Claude Agent subagents. See the **Claude-Only Mode** section above for the replacement table and cognitive style definitions.

### Step 0a: Adaptive Weight Recommendation

> **If `--weights` was explicitly provided**: Skip this step entirely (weights already saved in Step 0).

When `--weights` is omitted, Claude analyzes the research prompt to recommend topic-appropriate weights:

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

After setup, Claude analyzes the topic and domain to assign specialist personas:

**For `--depth low|medium|high` (2 personas):**

1. Analyze the topic's sub-disciplines, methodologies, and key challenges.
2. Assign a **Gemini persona** — a domain expert profile best suited for creative/theoretical ideation on this topic (e.g., "Theoretical cosmologist specializing in dark energy models" or "Bayesian statistician with expertise in causal inference").
3. Assign a **Codex persona** — a practitioner/builder profile best suited for implementation-focused ideation (e.g., "Computational physicist with GPU simulation experience" or "ML engineer specializing in scalable training pipelines").
4. Each persona definition should include: name/title, expertise areas (3-5 bullet points), and a guiding question that shapes their perspective. **Name the persona after a real historical figure (위인) whose work is closely related to the persona's domain** (e.g., a statistical learning theorist → "R. A. Fisher", a theoretical physicist → "Emmy Noether", a computational pioneer → "John von Neumann"). This immediately signals the persona's intellectual lineage and analytical style.
5. Personas **complement** the domain template — they do not override it. The domain template provides general context; personas provide topic-specific focus.
6. **If `--claude-only`**: Relabel the personas in `brainstorm/personas.md`:
   - "Gemini persona" → "Subagent A (Creative-Divergent)"
   - "Codex persona" → "Subagent B (Analytical-Convergent)"
   - Include the cognitive style directive in each persona definition so subagents receive it directly.
7. Save to `brainstorm/personas.md`.

**For `--depth max` (N personas):**

1. Analyze the topic's sub-disciplines, methodologies, and key challenges.
2. **Determine N** (if `--personas auto`):
   - Evaluate the topic along these dimensions:
     - **Sub-discipline count**: How many distinct research sub-fields does this topic span?
     - **Methodological diversity**: Does it require both theoretical and empirical approaches? Simulation? Formal proofs?
     - **Interdisciplinary breadth**: Does it bridge multiple domains (e.g., physics + ML, statistics + biology)?
   - Selection heuristic:
     - **N=2**: Narrow, well-defined topic within a single sub-field (e.g., "optimizing a specific algorithm")
     - **N=3**: Standard research topic spanning theory and practice (e.g., "novel regularization methods for deep learning")
     - **N=4**: Broad topic crossing 2+ sub-fields or requiring distinct application perspectives (e.g., "physics-informed neural networks for fluid dynamics")
     - **N=5**: Highly interdisciplinary or contentious topic where a dedicated critic perspective adds value (e.g., "quantum advantage claims in machine learning")
   - Announce the chosen N and reasoning to the user before proceeding.
   - If `--personas` was given as an explicit integer (2-5), use that value directly and skip this analysis.
3. Cast **N domain-specialist personas** (model-independent — each persona runs both Gemini and Codex):
   - **N=2**: Theory/Concepts, Computation/Implementation
   - **N=3**: Theory/Concepts, Computation/Implementation, Empirical/Validation
   - **N=4**: + Application/Interdisciplinary
   - **N=5**: + Critique/Skepticism
3. Each persona definition must include:
   - **Name/title** — **Use a real historical figure (위인) whose work aligns with this persona's domain** (e.g., "Alan Turing — Computation Theory Specialist", "Marie Curie — Experimental Methodology Pioneer", "Claude Shannon — Information-Theoretic Analyst"). The figure's intellectual legacy should resonate with the persona's analytical lens.
   - **Expertise areas** (3-5 bullet points)
   - **Guiding question** that shapes their perspective
   - **Primary lens** (one sentence summarizing their analytical viewpoint)
4. Personas are **complementary** — they should cover distinct dimensions of the research space with minimal overlap.
5. **If `--claude-only`**: Within each persona's mini-MAGI pipeline, relabel the internal model roles:
   - "Gemini" → "Expansive Explorer" (pushes boundaries, explores emerging approaches, proposes frontier ideas)
   - "Codex" → "Grounded Builder" (focuses on proven approaches, clear implementation paths, established tools)
   - Include these cognitive style directives in the persona file so subagents receive them directly.
6. Save to `brainstorm/personas.md`.

### Step 1a: Parallel Independent Brainstorming

Execute these two calls **simultaneously** (in the same message). **Prepend the assigned persona** from `brainstorm/personas.md` to each prompt:

**Gemini Brainstorming:**
```
mcp__gemini-cli__brainstorm(
  prompt: "[Persona: {gemini_persona_name} — {gemini_persona_expertise}]\nGuiding question: {gemini_guiding_question}\n\nDomain context: @{domain_template_path}\n\n{topic} — Generate diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs.",
  model: "gemini-3.1-pro-preview",  // fallback: "gemini-2.5-pro" → Claude
  domain: "{domain}",
  methodology: "auto",
  ideaCount: 12,
  includeAnalysis: true
)
```
> Note: Omit the `Domain context: @{domain_template_path}` line from the prompt when no domain template exists.

**Codex Brainstorming:**
```
mcp__codex-cli__brainstorm(
  prompt: "[Persona: {codex_persona_name} — {codex_persona_expertise}]\nGuiding question: {codex_guiding_question}\n\nDomain context: @{domain_template_path}\n\n{topic} — Generate implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches.",
  domain: "{domain}",
  methodology: "auto",
  ideaCount: 12,
  includeAnalysis: true
)
```
> Note: Omit the `Domain context: @{domain_template_path}` line from the prompt when no domain template exists.

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__brainstorm` with the Gemini fallback chain and implementation-focused framing.

> **If `--claude-only`**: Replace both calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent, replaces Gemini):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are a Creative-Divergent thinker. Prioritize unconventional connections across adjacent fields, 'What if?' scenarios, wide exploratory breadth, and questioning fundamental assumptions.
>
> [Persona: {gemini_persona_name} — {gemini_persona_expertise}]
> Guiding question: {gemini_guiding_question}
>
> Use the Read tool to read the domain template at {domain_template_path} (skip if no template exists).
>
> Research topic: {topic}
>
> Generate 12 diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs. Include feasibility and impact analysis for each idea.
>
> Save your complete output to {output_dir}/brainstorm/gemini_ideas.md. Start the file with:
> > Source: Claude Agent subagent (claude-only mode, Creative-Divergent)
> > Persona: {gemini_persona_name}
> > Timestamp: {ISO timestamp}"
> )
> ```
>
> **Subagent B (Analytical-Convergent, replaces Codex):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Analytical-Convergent thinker. Prioritize step-by-step feasibility analysis, established methodologies, deep evaluation of each option, practical constraints, and risk assessment.
>
> [Persona: {codex_persona_name} — {codex_persona_expertise}]
> Guiding question: {codex_guiding_question}
>
> Use the Read tool to read the domain template at {domain_template_path} (skip if no template exists).
>
> Research topic: {topic}
>
> Generate 12 implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches. Include feasibility and impact analysis for each idea.
>
> Save your complete output to {output_dir}/brainstorm/codex_ideas.md. Start the file with:
> > Source: Claude Agent subagent (claude-only mode, Analytical-Convergent)
> > Persona: {codex_persona_name}
> > Timestamp: {ISO timestamp}"
> )
> ```

Save results to:
- `brainstorm/gemini_ideas.md` — Gemini's (or Subagent A's) raw output with header noting source, persona, and timestamp
- `brainstorm/codex_ideas.md` — Codex's (or Subagent B's) raw output with header noting source, persona, and timestamp

### Step 1b: Cross-Check (`--depth medium` or `--depth high` only)

> **If `--depth low`**: Skip this step entirely and proceed to Step 1c.

After both brainstorming results are saved, execute these two calls **simultaneously**. **Prepend the assigned persona** to each review prompt:

**Gemini reviews Codex ideas (Round 1):**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {gemini_persona_name} — {gemini_persona_expertise}]\n\nReview the following research ideas for technical feasibility, scientific rigor, novelty, and potential impact. Identify strengths, weaknesses, and suggest improvements for each idea.\n\n@{output_dir}/brainstorm/codex_ideas.md",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-2.5-pro" → Claude
)
```

**Codex reviews Gemini ideas (Round 1):**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {codex_persona_name} — {codex_persona_expertise}]\n\nReview the following research ideas for implementation feasibility, computational practicality, available tools/datasets, and timeline realism. Identify strengths, weaknesses, and suggest improvements for each idea.\n\n@{output_dir}/brainstorm/gemini_ideas.md"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__ask-gemini` with the Gemini fallback chain.

> **If `--claude-only`**: Replace both calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent, replaces Gemini reviewing Codex):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are a Creative-Divergent reviewer. Prioritize unconventional connections, wide exploratory breadth, and questioning assumptions.
>
> [Persona: {gemini_persona_name} — {gemini_persona_expertise}]
>
> Use the Read tool to read: {output_dir}/brainstorm/codex_ideas.md
>
> Review these research ideas for technical feasibility, scientific rigor, novelty, and potential impact. Identify strengths, weaknesses, and suggest improvements for each idea.
>
> Save your review to {output_dir}/brainstorm/gemini_review_of_codex.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Creative-Divergent)"
> )
> ```
>
> **Subagent B (Analytical-Convergent, replaces Codex reviewing Gemini):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Analytical-Convergent reviewer. Prioritize step-by-step feasibility, practical constraints, and risk assessment.
>
> [Persona: {codex_persona_name} — {codex_persona_expertise}]
>
> Use the Read tool to read: {output_dir}/brainstorm/gemini_ideas.md
>
> Review these research ideas for implementation feasibility, computational practicality, available tools/datasets, and timeline realism. Identify strengths, weaknesses, and suggest improvements for each idea.
>
> Save your review to {output_dir}/brainstorm/codex_review_of_gemini.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Analytical-Convergent)"
> )
> ```

Save results to:
- `brainstorm/gemini_review_of_codex.md`
- `brainstorm/codex_review_of_gemini.md`

### Step 1b+: Adversarial Debate (`--depth high` only)

> **If `--depth low` or `--depth medium`**: Skip this step entirely.

After Round 1 cross-review, Claude identifies the **top 3 points of disagreement** between Gemini and Codex (e.g., conflicting feasibility assessments, divergent novelty ratings, opposing recommendations). **Save the disagreement summary to `brainstorm/disagreements.md`** before the debate calls.

Execute Round 2 **simultaneously**:

**Gemini Round 2 — Defend/Concede/Revise:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {gemini_persona_name}]\n\nYou reviewed Codex's ideas and Codex reviewed yours. Here are the top 3 points of disagreement:\n\n@{output_dir}/brainstorm/disagreements.md\n\nFor each disagreement:\n1. **Defend** your position if you believe it is correct, providing additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new position if appropriate\n\nYour original review:\n@{output_dir}/brainstorm/gemini_review_of_codex.md\n\nCodex's review of your ideas:\n@{output_dir}/brainstorm/codex_review_of_gemini.md",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```

**Codex Round 2 — Defend/Concede/Revise:**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {codex_persona_name}]\n\nYou reviewed Gemini's ideas and Gemini reviewed yours. Here are the top 3 points of disagreement:\n\n@{output_dir}/brainstorm/disagreements.md\n\nFor each disagreement:\n1. **Defend** your position if you believe it is correct, providing additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new position if appropriate\n\nYour original review:\n@{output_dir}/brainstorm/codex_review_of_gemini.md\n\nGemini's review of your ideas:\n@{output_dir}/brainstorm/gemini_review_of_codex.md"
)
```

> **If `--claude-only`**: Replace both debate calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent, replaces Gemini Round 2):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are a Creative-Divergent debater. Prioritize unconventional reasoning and questioning assumptions.
>
> [Persona: {gemini_persona_name}]
>
> You reviewed the opposing side's ideas and they reviewed yours. Use the Read tool to read:
> - {output_dir}/brainstorm/disagreements.md
> - {output_dir}/brainstorm/gemini_review_of_codex.md
> - {output_dir}/brainstorm/codex_review_of_gemini.md
>
> For each disagreement:
> 1. **Defend** your position if you believe it is correct, providing additional evidence or reasoning
> 2. **Concede** if the opposing argument is stronger, explaining why
> 3. **Revise** your assessment to a new position if appropriate
>
> Save to {output_dir}/brainstorm/debate_round2_gemini.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Creative-Divergent)"
> )
> ```
>
> **Subagent B (Analytical-Convergent, replaces Codex Round 2):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Analytical-Convergent debater. Prioritize evidence-based reasoning and practical constraints.
>
> [Persona: {codex_persona_name}]
>
> You reviewed the opposing side's ideas and they reviewed yours. Use the Read tool to read:
> - {output_dir}/brainstorm/disagreements.md
> - {output_dir}/brainstorm/codex_review_of_gemini.md
> - {output_dir}/brainstorm/gemini_review_of_codex.md
>
> For each disagreement:
> 1. **Defend** your position if you believe it is correct, providing additional evidence or reasoning
> 2. **Concede** if the opposing argument is stronger, explaining why
> 3. **Revise** your assessment to a new position if appropriate
>
> Save to {output_dir}/brainstorm/debate_round2_codex.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Analytical-Convergent)"
> )
> ```

Save results to:
- `brainstorm/debate_round2_gemini.md`
- `brainstorm/debate_round2_codex.md`

### Step 1-max-a: Layer 1 — Parallel Persona Subagents (`--depth max` only)

> **If `--depth` is not `max`**: Skip Steps 1-max-a through 1-max-d entirely. Use Steps 1a/1b/1b+/1c instead.

Spawn **N Task subagents simultaneously** (one per persona, `subagent_type: general-purpose`). Each subagent receives the persona definition and executes a self-contained mini-MAGI pipeline:

**Each subagent prompt includes:**
1. The persona definition (name, expertise, guiding question, primary lens) from `brainstorm/personas.md`
2. The research topic and domain template (if available)
3. The following 5-step execution plan:

   **A. Gemini Brainstorm** — Call `mcp__gemini-cli__brainstorm` with the persona's viewpoint. Save to `brainstorm/persona_{i}/gemini_ideas.md`.

   **B. Codex Brainstorm** — Call `mcp__codex-cli__brainstorm` with the persona's viewpoint. Save to `brainstorm/persona_{i}/codex_ideas.md`.

   > **If `--claude-only`**: Replace A and B above with two Agent sub-subagents, executed **simultaneously** within the persona subagent:
   >
   > **A'. Expansive Explorer (replaces Gemini):**
   > ```
   > Agent(
   >   subagent_type: "general-purpose",
   >   prompt: "You are an Expansive Explorer. Push boundaries, explore emerging approaches, and propose ideas at the frontier of what's possible. Challenge conventional thinking and seek novel combinations.
   >
   > [Persona: {persona_i_name} — {persona_i_expertise}]
   > Guiding question: {persona_i_guiding_question}
   >
   > Use the Read tool to read the domain template at {domain_template_path} (skip if none).
   >
   > Research topic: {topic}
   >
   > Generate 12 creative research ideas from this persona's perspective. Save to {output_dir}/brainstorm/persona_{i}/gemini_ideas.md. Start with:
   > > Source: Claude Agent subagent (claude-only mode, Expansive Explorer)"
   > )
   > ```
   >
   > **B'. Grounded Builder (replaces Codex):**
   > ```
   > Agent(
   >   subagent_type: "general-purpose",
   >   prompt: "You are a Grounded Builder. Focus on proven approaches with clear implementation paths, established tools, and demonstrable results. Prioritize what can be built and validated now.
   >
   > [Persona: {persona_i_name} — {persona_i_expertise}]
   > Guiding question: {persona_i_guiding_question}
   >
   > Use the Read tool to read the domain template at {domain_template_path} (skip if none).
   >
   > Research topic: {topic}
   >
   > Generate 12 implementation-focused research ideas from this persona's perspective. Save to {output_dir}/brainstorm/persona_{i}/codex_ideas.md. Start with:
   > > Source: Claude Agent subagent (claude-only mode, Grounded Builder)"
   > )
   > ```

   **C+D. Cross-Review (simultaneous):**
   - Gemini reviews Codex ideas using `@{output_dir}/brainstorm/persona_{i}/codex_ideas.md` → save to `brainstorm/persona_{i}/gemini_review_of_codex.md`
   - Codex reviews Gemini ideas using `@{output_dir}/brainstorm/persona_{i}/gemini_ideas.md` → save to `brainstorm/persona_{i}/codex_review_of_gemini.md`

   > **If `--claude-only`**: Replace C+D above with two Agent sub-subagents, executed **simultaneously**:
   >
   > **C'. Expansive Explorer reviews Grounded Builder's ideas:**
   > ```
   > Agent(
   >   subagent_type: "general-purpose",
   >   prompt: "You are an Expansive Explorer reviewer. Question constraints and look for hidden potential.
   >
   > [Persona: {persona_i_name}]
   >
   > Use the Read tool to read: {output_dir}/brainstorm/persona_{i}/codex_ideas.md
   >
   > Review these ideas for novelty, scientific rigor, and potential impact. Identify strengths, weaknesses, and improvements.
   >
   > Save to {output_dir}/brainstorm/persona_{i}/gemini_review_of_codex.md. Start with:
   > > Source: Claude Agent subagent (claude-only mode, Expansive Explorer)"
   > )
   > ```
   >
   > **D'. Grounded Builder reviews Expansive Explorer's ideas:**
   > ```
   > Agent(
   >   subagent_type: "general-purpose",
   >   prompt: "You are a Grounded Builder reviewer. Evaluate practical feasibility and implementation viability.
   >
   > [Persona: {persona_i_name}]
   >
   > Use the Read tool to read: {output_dir}/brainstorm/persona_{i}/gemini_ideas.md
   >
   > Review these ideas for implementation feasibility, computational practicality, and timeline realism. Identify strengths, weaknesses, and improvements.
   >
   > Save to {output_dir}/brainstorm/persona_{i}/codex_review_of_gemini.md. Start with:
   > > Source: Claude Agent subagent (claude-only mode, Grounded Builder)"
   > )
   > ```

   **E. Persona Conclusion** — The subagent synthesizes its top 3 research directions, noting areas of internal agreement and disagreement between the two models (or two cognitive styles in claude-only mode). Save to `brainstorm/persona_{i}/conclusion.md`.

Wait for all N subagents to complete before proceeding.

### Step 1-max-b: Layer 1 — Output Collection

1. Use Glob to verify that all N `brainstorm/persona_{i}/conclusion.md` files exist.
   - If any are missing, re-spawn the failed subagent(s) and wait for completion.
2. Read all N `conclusion.md` files.
3. Construct a **cross-persona summary** identifying:
   - **Recurring themes** — directions proposed by 2+ personas
   - **Unique directions** — ideas that appeared in only one persona's output
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

**Gemini Meta-Review:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "You are reviewing the outputs of {N} domain-specialist research personas who independently analyzed: {topic}\n\nHere are all persona conclusions:\n@{output_dir}/brainstorm/all_conclusions.md\n\nProvide a meta-review covering:\n1. **Coverage analysis** — Which aspects of the research space are well-covered vs. underexplored?\n2. **Quality assessment** — Rate each persona's conclusions (depth, rigor, creativity) on a 1-10 scale\n3. **Cross-persona synthesis** — What emerges when combining all perspectives that no single persona captured?\n4. **Top 3 disagreements** — Identify the 3 most significant points where personas contradict each other, with specific quotes\n5. **Recommended directions** — Your top 5 research directions considering all perspectives",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```
Save to `brainstorm/meta_review_gemini.md`.

**Codex Meta-Review:**
```
mcp__codex-cli__ask-codex(
  prompt: "You are reviewing the outputs of {N} domain-specialist research personas who independently analyzed: {topic}\n\nHere are all persona conclusions:\n@{output_dir}/brainstorm/all_conclusions.md\n\nProvide a meta-review covering:\n1. **Coverage analysis** — Which aspects of the research space are well-covered vs. underexplored?\n2. **Quality assessment** — Rate each persona's conclusions (depth, rigor, creativity) on a 1-10 scale\n3. **Cross-persona synthesis** — What emerges when combining all perspectives that no single persona captured?\n4. **Top 3 disagreements** — Identify the 3 most significant points where personas contradict each other, with specific quotes\n5. **Recommended directions** — Your top 5 research directions considering all perspectives"
)
```
Save to `brainstorm/meta_review_codex.md`.

> **If `--claude-only`**: Replace both meta-review calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent, replaces Gemini Meta-Review):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are a Creative-Divergent meta-reviewer. Look for emergent patterns, underexplored spaces, and unconventional combinations across perspectives.
>
> Use the Read tool to read: {output_dir}/brainstorm/all_conclusions.md
>
> You are reviewing the outputs of {N} domain-specialist research personas who independently analyzed: {topic}
>
> Provide a meta-review covering:
> 1. **Coverage analysis** — Which aspects are well-covered vs. underexplored?
> 2. **Quality assessment** — Rate each persona's conclusions (depth, rigor, creativity) on a 1-10 scale
> 3. **Cross-persona synthesis** — What emerges when combining all perspectives?
> 4. **Top 3 disagreements** — Identify the 3 most significant contradictions with specific quotes
> 5. **Recommended directions** — Your top 5 research directions
>
> Save to {output_dir}/brainstorm/meta_review_gemini.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Creative-Divergent)"
> )
> ```
>
> **Subagent B (Analytical-Convergent, replaces Codex Meta-Review):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Analytical-Convergent meta-reviewer. Focus on methodological rigor, feasibility, and practical implementation paths across perspectives.
>
> Use the Read tool to read: {output_dir}/brainstorm/all_conclusions.md
>
> You are reviewing the outputs of {N} domain-specialist research personas who independently analyzed: {topic}
>
> Provide a meta-review covering:
> 1. **Coverage analysis** — Which aspects are well-covered vs. underexplored?
> 2. **Quality assessment** — Rate each persona's conclusions (depth, rigor, creativity) on a 1-10 scale
> 3. **Cross-persona synthesis** — What emerges when combining all perspectives?
> 4. **Top 3 disagreements** — Identify the 3 most significant contradictions with specific quotes
> 5. **Recommended directions** — Your top 5 research directions
>
> Save to {output_dir}/brainstorm/meta_review_codex.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Analytical-Convergent)"
> )
> ```

**Phase B — Disagreement Extraction:**

Claude reads both meta-reviews and extracts the **top 3 cross-persona disagreements** — prioritizing disagreements identified by both reviewers. For each disagreement, produce a structured summary: the claim, which personas support each side, and the core tension. **Save the meta-disagreement summary to `brainstorm/meta_disagreements.md`** before the debate calls.

**Phase C — Consolidate Debate Context + Adversarial Debate:**

Before the debate calls, create consolidated context files (each containing exactly what the opposing model needs):
- `brainstorm/debate_context_for_gemini.md` — concatenate `meta_disagreements.md` + `meta_review_codex.md`
- `brainstorm/debate_context_for_codex.md` — concatenate `meta_disagreements.md` + `meta_review_gemini.md`

Then execute the debate calls **simultaneously**:

```
mcp__gemini-cli__ask-gemini(
  prompt: "[Meta-Reviewer]\n\nYou reviewed {N} persona conclusions and identified top disagreements. Below is the disagreement summary followed by Codex's meta-review for context:\n\n@{output_dir}/brainstorm/debate_context_for_gemini.md\n\nFor each disagreement:\n1. **Defend** your position with additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new synthesized position if appropriate",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```
Save to `brainstorm/meta_debate_gemini.md`.

```
mcp__codex-cli__ask-codex(
  prompt: "[Meta-Reviewer]\n\nYou reviewed {N} persona conclusions and identified top disagreements. Below is the disagreement summary followed by Gemini's meta-review for context:\n\n@{output_dir}/brainstorm/debate_context_for_codex.md\n\nFor each disagreement:\n1. **Defend** your position with additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new synthesized position if appropriate"
)
```
Save to `brainstorm/meta_debate_codex.md`.

> **If `--claude-only`**: Replace both debate calls above with two Agent subagents, executed **simultaneously**:
>
> **Subagent A (Creative-Divergent, replaces Gemini Debate):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are a Creative-Divergent debater. Defend unconventional positions with imaginative reasoning, but concede when evidence demands it.
>
> [Meta-Reviewer]
>
> Use the Read tool to read: {output_dir}/brainstorm/debate_context_for_gemini.md
>
> You reviewed {N} persona conclusions and identified top disagreements. The file contains the disagreement summary followed by the opposing meta-review.
>
> For each disagreement:
> 1. **Defend** your position with additional evidence or reasoning
> 2. **Concede** if the opposing argument is stronger, explaining why
> 3. **Revise** your assessment to a new synthesized position if appropriate
>
> Save to {output_dir}/brainstorm/meta_debate_gemini.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Creative-Divergent)"
> )
> ```
>
> **Subagent B (Analytical-Convergent, replaces Codex Debate):**
> ```
> Agent(
>   subagent_type: "general-purpose",
>   prompt: "You are an Analytical-Convergent debater. Defend positions with evidence and practical reasoning, but concede when creative arguments reveal genuine blind spots.
>
> [Meta-Reviewer]
>
> Use the Read tool to read: {output_dir}/brainstorm/debate_context_for_codex.md
>
> You reviewed {N} persona conclusions and identified top disagreements. The file contains the disagreement summary followed by the opposing meta-review.
>
> For each disagreement:
> 1. **Defend** your position with additional evidence or reasoning
> 2. **Concede** if the opposing argument is stronger, explaining why
> 3. **Revise** your assessment to a new synthesized position if appropriate
>
> Save to {output_dir}/brainstorm/meta_debate_codex.md. Start with:
> > Source: Claude Agent subagent (claude-only mode, Analytical-Convergent)"
> )
> ```

### Step 1-max-d: Layer 3 — Final Enriched Synthesis (`--depth max`)

1. Read all available documents:
   - `weights.json`, `personas.md`
   - All N `persona_{i}/conclusion.md` files
   - `meta_review_gemini.md`, `meta_review_codex.md`
   - `meta_debate_gemini.md`, `meta_debate_codex.md`
2. Load `weights.json` and extract the `"weights"` object. Compute **weighted scores** for each research direction (same 0-10 rating per dimension, weighted sum).
3. Produce an **enriched `brainstorm/synthesis.md`** with the following structure:
   1. **Personas Used** — table of N personas with name, expertise summary, and primary lens
   2. **Scoring Weights** — the weights used for ranking (from `weights.json`), including `_meta.method` to document how weights were selected (explicit, adaptive-recommended, domain-default, or custom)
   3. **Top Research Directions** — ranked by weighted score, with:
      - Score breakdown per dimension
      - Which personas supported this direction
      - Key arguments for and against
   4. **Cross-Persona Consensus** — ideas where 3+ personas independently converged
   5. **Unique Contributions** — valuable ideas that only a single persona identified
   6. **Debate Resolution** — for each of the 3 debated disagreements: the original tension, how each meta-reviewer responded (defend/concede/revise), and the synthesized resolution
   7. **Emergent Insights** — patterns or connections visible only from the cross-persona vantage point that no individual persona captured
   8. **Recommended Path Forward** — Claude's top recommendation with reasoning grounded in the multi-persona analysis
   9. **MAGI Process Traceability** — table mapping each conclusion to its source persona, layer, and artifact file path
4. Save to `brainstorm/synthesis.md`.

### Step 1c: Claude Synthesis

> **If `--depth max`**: Skip — synthesis is produced by Step 1-max-d above.

1. Read all available documents:
   - Always: `gemini_ideas.md`, `codex_ideas.md`
   - If `--depth medium` or `high`: `gemini_review_of_codex.md`, `codex_review_of_gemini.md`
   - If `--depth high`: `debate_round2_gemini.md`, `debate_round2_codex.md`
   - Always: `weights.json`, `personas.md`
2. Load `weights.json` and extract the `"weights"` object. Use the weights to compute a **weighted score** for each research direction:
   - For each candidate direction, rate it on each weight dimension (0-10 scale)
   - Compute the weighted sum: `score = Σ(weight_i × rating_i)`
   - Rank directions by weighted score
3. Synthesize into a coherent research direction document that includes:
   - **Personas Used** — brief summary of assigned Gemini and Codex personas
   - **Scoring Weights** — the weights used for ranking (from `weights.json`), including `_meta.method` to document how weights were selected
   - **Top Research Directions** (ranked by weighted score, showing score breakdown)
   - **Key Technical Approaches** for each direction
   - **Consensus Points** — ideas both models agreed on
   - **Divergence Points** — areas of disagreement and how to resolve them
   - **Debate Resolution** (`--depth high` only) — for each of the 3 debated disagreements, document the final resolution: who conceded, what was revised, and the synthesized position
   - **Recommended Path Forward** — Claude's recommendation with reasoning
4. Save to `brainstorm/synthesis.md`.

### Step 2: User Feedback

Present the synthesis to the user with:
- A concise summary of the top 3-5 research directions
- Clear options for the user to choose, modify, or combine directions
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
