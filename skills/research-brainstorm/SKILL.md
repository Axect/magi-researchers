# Research Brainstorm Skill

## Description
Generates and cross-validates research ideas using Gemini and Codex in parallel, then synthesizes results with Claude.

## Usage
```
/research-brainstorm "research topic" [--domain physics|ai_ml|statistics|mathematics|paper] [--weights '{"novelty":0.4,"feasibility":0.3,"impact":0.3}'] [--depth low|medium|high|max] [--personas N]
```

## Arguments
- `$ARGUMENTS` — The research topic and optional flags:
  - `--domain` — Research domain (physics, ai_ml, statistics, mathematics, paper). Auto-inferred if omitted.
  - `--weights` — JSON object of scoring weights for direction ranking. Keys: `novelty`, `feasibility`, `impact`, `rigor`, `scalability`. Values must sum to 1.0. If omitted, domain-specific defaults are used.
  - `--depth` — Controls review depth (default: `medium`):
    - `low` — Skip cross-review, go directly to synthesis
    - `medium` — Standard one-shot cross-review (current behavior)
    - `high` — Cross-review + adversarial debate round
    - `max` — Hierarchical MAGI-in-MAGI: N persona subagents run parallel mini-MAGI pipelines, then meta-review + adversarial debate across all perspectives
  - `--personas N` — Number of domain-specialist subagents for `--depth max` (default: 3, range: 2-5). Ignored for other depth levels.

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-3-pro-preview"` (fallback)
  3. `model: "gemini-2.5-pro"` (last resort)
- **Codex**: Use `mcp__codex-cli__brainstorm` for ideation, `mcp__codex-cli__ask-codex` for analysis/review.

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
4. **Parse `--weights`**: If provided, validate that keys are a subset of {`novelty`, `feasibility`, `impact`, `rigor`, `scalability`} and values sum to 1.0. If not provided, use domain defaults:
   - `physics`: `{"novelty": 0.30, "feasibility": 0.15, "impact": 0.25, "rigor": 0.20, "scalability": 0.10}`
   - `ai_ml`: `{"novelty": 0.25, "feasibility": 0.25, "impact": 0.25, "rigor": 0.10, "scalability": 0.15}`
   - `statistics`: `{"novelty": 0.25, "feasibility": 0.20, "impact": 0.20, "rigor": 0.25, "scalability": 0.10}`
   - `mathematics`: `{"novelty": 0.35, "feasibility": 0.10, "impact": 0.20, "rigor": 0.30, "scalability": 0.05}`
   - `paper`: `{"novelty": 0.20, "feasibility": 0.25, "impact": 0.30, "rigor": 0.15, "scalability": 0.10}`
   - Save to `brainstorm/weights.json`.
5. **Parse `--depth`**: Accept `low`, `medium`, `high`, or `max` (default: `medium`).
   - `low` — Skip Step 1b (cross-review), go directly to Step 1c (synthesis)
   - `medium` — Standard one-shot cross-review (current default behavior)
   - `high` — Cross-review + adversarial debate (Step 1b+)
   - `max` — Hierarchical MAGI-in-MAGI pipeline (Steps 1-max-a through 1-max-d replace Steps 1a/1b/1b+/1c)
6. **Parse `--personas N`**: Accept integer 2-5 (default: 3). Only used when `--depth max`; ignored otherwise.

### Step 0b: Dynamic Persona Casting

After setup, Claude analyzes the topic and domain to assign specialist personas:

**For `--depth low|medium|high` (2 personas):**

1. Analyze the topic's sub-disciplines, methodologies, and key challenges.
2. Assign a **Gemini persona** — a domain expert profile best suited for creative/theoretical ideation on this topic (e.g., "Theoretical cosmologist specializing in dark energy models" or "Bayesian statistician with expertise in causal inference").
3. Assign a **Codex persona** — a practitioner/builder profile best suited for implementation-focused ideation (e.g., "Computational physicist with GPU simulation experience" or "ML engineer specializing in scalable training pipelines").
4. Each persona definition should include: name/title, expertise areas (3-5 bullet points), and a guiding question that shapes their perspective.
5. Personas **complement** the domain template — they do not override it. The domain template provides general context; personas provide topic-specific focus.
6. Save to `brainstorm/personas.md`.

**For `--depth max` (N personas):**

1. Analyze the topic's sub-disciplines, methodologies, and key challenges.
2. Cast **N domain-specialist personas** (model-independent — each persona runs both Gemini and Codex):
   - **N=2**: Theory/Concepts, Computation/Implementation
   - **N=3**: Theory/Concepts, Computation/Implementation, Empirical/Validation
   - **N=4**: + Application/Interdisciplinary
   - **N=5**: + Critique/Skepticism
3. Each persona definition must include:
   - **Name/title** (e.g., "Dr. Theoretician — Formal Methods Specialist")
   - **Expertise areas** (3-5 bullet points)
   - **Guiding question** that shapes their perspective
   - **Primary lens** (one sentence summarizing their analytical viewpoint)
4. Personas are **complementary** — they should cover distinct dimensions of the research space with minimal overlap.
5. Save to `brainstorm/personas.md`.

### Step 1a: Parallel Independent Brainstorming

Execute these two calls **simultaneously** (in the same message). **Prepend the assigned persona** from `brainstorm/personas.md` to each prompt:

**Gemini Brainstorming:**
```
mcp__gemini-cli__brainstorm(
  prompt: "[Persona: {gemini_persona_name} — {gemini_persona_expertise}]\nGuiding question: {gemini_guiding_question}\n\n{topic} — Generate diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs.",
  model: "gemini-3.1-pro-preview",  // fallback: "gemini-3-pro-preview" → "gemini-2.5-pro"
  domain: "{domain}",
  methodology: "auto",
  ideaCount: 12,
  includeAnalysis: true,
  existingContext: "{domain template content if available}"
)
```

**Codex Brainstorming:**
```
mcp__codex-cli__brainstorm(
  prompt: "[Persona: {codex_persona_name} — {codex_persona_expertise}]\nGuiding question: {codex_guiding_question}\n\n{topic} — Generate implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches.",
  domain: "{domain}",
  methodology: "auto",
  ideaCount: 12,
  includeAnalysis: true,
  existingContext: "{domain template content if available}"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__brainstorm` with the Gemini fallback chain and implementation-focused framing.

Save results to:
- `brainstorm/gemini_ideas.md` — Gemini's raw output with header noting source, persona, and timestamp
- `brainstorm/codex_ideas.md` — Codex's raw output with header noting source, persona, and timestamp

### Step 1b: Cross-Check (`--depth medium` or `--depth high` only)

> **If `--depth low`**: Skip this step entirely and proceed to Step 1c.

After both brainstorming results are saved, execute these two calls **simultaneously**. **Prepend the assigned persona** to each review prompt:

**Gemini reviews Codex ideas (Round 1):**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {gemini_persona_name} — {gemini_persona_expertise}]\n\nReview the following research ideas for technical feasibility, scientific rigor, novelty, and potential impact. Identify strengths, weaknesses, and suggest improvements for each idea.\n\n{codex_ideas content}",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-3-pro-preview" → "gemini-2.5-pro"
)
```

**Codex reviews Gemini ideas (Round 1):**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {codex_persona_name} — {codex_persona_expertise}]\n\nReview the following research ideas for implementation feasibility, computational practicality, available tools/datasets, and timeline realism. Identify strengths, weaknesses, and suggest improvements for each idea.\n\n{gemini_ideas content}"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__ask-gemini` with the Gemini fallback chain.

Save results to:
- `brainstorm/gemini_review_of_codex.md`
- `brainstorm/codex_review_of_gemini.md`

### Step 1b+: Adversarial Debate (`--depth high` only)

> **If `--depth low` or `--depth medium`**: Skip this step entirely.

After Round 1 cross-review, Claude identifies the **top 3 points of disagreement** between Gemini and Codex (e.g., conflicting feasibility assessments, divergent novelty ratings, opposing recommendations).

Execute Round 2 **simultaneously**:

**Gemini Round 2 — Defend/Concede/Revise:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {gemini_persona_name}]\n\nYou reviewed Codex's ideas and Codex reviewed yours. Here are the top 3 points of disagreement:\n\n{disagreement_summary}\n\nFor each disagreement:\n1. **Defend** your position if you believe it is correct, providing additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new position if appropriate\n\nYour original review:\n{gemini_review_of_codex}\n\nCodex's review of your ideas:\n{codex_review_of_gemini}",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```

**Codex Round 2 — Defend/Concede/Revise:**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {codex_persona_name}]\n\nYou reviewed Gemini's ideas and Gemini reviewed yours. Here are the top 3 points of disagreement:\n\n{disagreement_summary}\n\nFor each disagreement:\n1. **Defend** your position if you believe it is correct, providing additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new position if appropriate\n\nYour original review:\n{codex_review_of_gemini}\n\nGemini's review of your ideas:\n{gemini_review_of_codex}"
)
```

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

   **C+D. Cross-Review (simultaneous):**
   - Gemini reviews Codex ideas → `brainstorm/persona_{i}/gemini_review_of_codex.md`
   - Codex reviews Gemini ideas → `brainstorm/persona_{i}/codex_review_of_gemini.md`

   **E. Persona Conclusion** — The subagent synthesizes its top 3 research directions, noting areas of internal agreement and disagreement between the two models. Save to `brainstorm/persona_{i}/conclusion.md`.

Wait for all N subagents to complete before proceeding.

### Step 1-max-b: Layer 1 — Output Collection

1. Use Glob to verify that all N `brainstorm/persona_{i}/conclusion.md` files exist.
   - If any are missing, re-spawn the failed subagent(s) and wait for completion.
2. Read all N `conclusion.md` files.
3. Construct a **cross-persona summary** identifying:
   - **Recurring themes** — directions proposed by 2+ personas
   - **Unique directions** — ideas that appeared in only one persona's output
   - **Explicit disagreements** — contradictory assessments across personas

### Step 1-max-c: Layer 2 — Meta-Review + Adversarial Debate

**Phase A — Parallel Meta-Reviews:**

Execute simultaneously:

**Gemini Meta-Review:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "You are reviewing the outputs of {N} domain-specialist research personas who independently analyzed: {topic}\n\nHere are their conclusions:\n{all N conclusion.md contents}\n\nProvide a meta-review covering:\n1. **Coverage analysis** — Which aspects of the research space are well-covered vs. underexplored?\n2. **Quality assessment** — Rate each persona's conclusions (depth, rigor, creativity) on a 1-10 scale\n3. **Cross-persona synthesis** — What emerges when combining all perspectives that no single persona captured?\n4. **Top 3 disagreements** — Identify the 3 most significant points where personas contradict each other, with specific quotes\n5. **Recommended directions** — Your top 5 research directions considering all perspectives",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```
Save to `brainstorm/meta_review_gemini.md`.

**Codex Meta-Review:**
```
mcp__codex-cli__ask-codex(
  prompt: "You are reviewing the outputs of {N} domain-specialist research personas who independently analyzed: {topic}\n\nHere are their conclusions:\n{all N conclusion.md contents}\n\nProvide a meta-review covering:\n1. **Coverage analysis** — Which aspects of the research space are well-covered vs. underexplored?\n2. **Quality assessment** — Rate each persona's conclusions (depth, rigor, creativity) on a 1-10 scale\n3. **Cross-persona synthesis** — What emerges when combining all perspectives that no single persona captured?\n4. **Top 3 disagreements** — Identify the 3 most significant points where personas contradict each other, with specific quotes\n5. **Recommended directions** — Your top 5 research directions considering all perspectives"
)
```
Save to `brainstorm/meta_review_codex.md`.

**Phase B — Disagreement Extraction:**

Claude reads both meta-reviews and extracts the **top 3 cross-persona disagreements** — prioritizing disagreements identified by both reviewers. For each disagreement, produce a structured summary: the claim, which personas support each side, and the core tension.

**Phase C — Adversarial Debate (simultaneous):**

```
mcp__gemini-cli__ask-gemini(
  prompt: "[Meta-Reviewer]\n\nYou reviewed {N} persona conclusions and identified these top 3 disagreements:\n\n{disagreement_summary}\n\nCodex's meta-review highlighted:\n{codex_meta_review_summary}\n\nFor each disagreement:\n1. **Defend** your position with additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new synthesized position if appropriate",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```
Save to `brainstorm/meta_debate_gemini.md`.

```
mcp__codex-cli__ask-codex(
  prompt: "[Meta-Reviewer]\n\nYou reviewed {N} persona conclusions and identified these top 3 disagreements:\n\n{disagreement_summary}\n\nGemini's meta-review highlighted:\n{gemini_meta_review_summary}\n\nFor each disagreement:\n1. **Defend** your position with additional evidence or reasoning\n2. **Concede** if the opposing argument is stronger, explaining why\n3. **Revise** your assessment to a new synthesized position if appropriate"
)
```
Save to `brainstorm/meta_debate_codex.md`.

### Step 1-max-d: Layer 3 — Final Enriched Synthesis (`--depth max`)

1. Read all available documents:
   - `weights.json`, `personas.md`
   - All N `persona_{i}/conclusion.md` files
   - `meta_review_gemini.md`, `meta_review_codex.md`
   - `meta_debate_gemini.md`, `meta_debate_codex.md`
2. Load `weights.json` and compute **weighted scores** for each research direction (same 0-10 rating per dimension, weighted sum).
3. Produce an **enriched `brainstorm/synthesis.md`** with the following structure:
   1. **Personas Used** — table of N personas with name, expertise summary, and primary lens
   2. **Scoring Weights** — the weights used for ranking (from `weights.json`)
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
2. Load `weights.json` and use the weights to compute a **weighted score** for each research direction:
   - For each candidate direction, rate it on each weight dimension (0-10 scale)
   - Compute the weighted sum: `score = Σ(weight_i × rating_i)`
   - Rank directions by weighted score
3. Synthesize into a coherent research direction document that includes:
   - **Personas Used** — brief summary of assigned Gemini and Codex personas
   - **Scoring Weights** — the weights used for ranking (from `weights.json`)
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
├── weights.json                  # Scoring weights (always)
├── personas.md                   # Assigned expert personas (always)
├── gemini_ideas.md               # Gemini brainstorm output (always)
├── codex_ideas.md                # Codex brainstorm output (always)
├── gemini_review_of_codex.md     # Cross-review (--depth medium|high)
├── codex_review_of_gemini.md     # Cross-review (--depth medium|high)
├── debate_round2_gemini.md       # Adversarial debate (--depth high only)
├── debate_round2_codex.md        # Adversarial debate (--depth high only)
└── synthesis.md                  # Claude synthesis (always)
```

**`--depth max`:**
```
brainstorm/
├── weights.json                  # Scoring weights
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
├── meta_review_gemini.md         # Gemini meta-review of all conclusions
├── meta_review_codex.md          # Codex meta-review of all conclusions
├── meta_debate_gemini.md         # Adversarial debate — Gemini
├── meta_debate_codex.md          # Adversarial debate — Codex
└── synthesis.md                  # Enriched final synthesis
```
