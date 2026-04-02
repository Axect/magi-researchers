# Depth Max: Hierarchical MAGI-in-MAGI Pipeline

> This file contains all `--depth max`-specific steps for the research-explain skill.
> Read this file when `--depth max` is active.
> Steps 1-max-a through 1-max-d replace Steps 1a/1b/1b+/1c from the main SKILL.md.
> The `--depth max` persona casting logic in Step 0b also lives here.

---

## Step 0b (depth max): Dynamic Persona Casting — N Personas

> This section applies only when `--depth max`. For `--depth medium|high`, see Step 0b in the main SKILL.md.

1. Analyze the concept's sub-topics, prerequisite structure, common misconceptions, and audience needs.
2. **Determine N** (if `--personas auto`):
   - Evaluate the concept along these dimensions:
     - **Conceptual layering**: How many distinct conceptual layers does this explanation require?
     - **Prerequisite diversity**: Does it require knowledge from multiple distinct fields?
     - **Misconception density**: Are there many common misconceptions or confusion neighbors?
   - Selection heuristic:
     - **N=2**: Simple concept within a single field (e.g., "what is a derivative?")
     - **N=3**: Standard concept spanning theory, intuition, and application (e.g., "entropy in information theory")
     - **N=4**: Multi-faceted concept requiring historical, theoretical, applied, and pedagogical perspectives, or highly interdisciplinary/deeply misunderstood concept (e.g., "gauge symmetry in physics", "quantum entanglement")
   - Announce the chosen N and reasoning to the user before proceeding.
   - If `--personas` was given as an explicit integer (2-4), use that value directly and skip this analysis.
3. Cast **N explanation-specialist personas** (model-independent — each persona runs both Gemini and Codex):
   - **N=2**: Intuitive Explainer, Rigorous Formalist
   - **N=3**: Intuitive Explainer, Rigorous Formalist, Applied Practitioner
   - **N=4**: + Historical/Conceptual Genealogist or Misconception Hunter / Devil's Advocate (based on concept)
4. Each persona definition must include:
   - **Name/title** — Use a real historical figure (위인) whose work aligns with this persona's domain (e.g., "Richard Feynman — Intuitive Physics Explainer", "Emmy Noether — Abstract Structure Specialist", "John Tukey — Practical Data Analyst"). The figure's intellectual legacy should resonate with the persona's explanatory lens.
   - **Expertise areas** (3-5 bullet points)
   - **Guiding question** that shapes their perspective
   - **Primary lens** (one sentence summarizing their explanatory viewpoint)
5. Personas are **complementary** — they should cover distinct dimensions of the explanation space with minimal overlap.
6. **If `--claude-only`**: Within each persona's mini-MAGI pipeline, relabel the internal model roles:
   - "Gemini" → "Expansive Explorer" (pushes boundaries, explores emerging approaches, proposes frontier ideas)
   - "Codex" → "Grounded Builder" (focuses on proven approaches, clear implementation paths, established tools)
   - Include these cognitive style directives in the persona file so subagents receive them directly.
7. Save to `explain/personas.md`.

---

## Step 1-max-a: Layer 1 — Parallel Persona Subagents

> **If `--depth` is not `max`**: Skip Steps 1-max-a through 1-max-d entirely. Use Steps 1a/1b/1b+/1c instead.

Spawn **N Task subagents simultaneously** (one per persona, `subagent_type: general-purpose`). Each subagent receives the persona definition and executes a self-contained mini-MAGI pipeline:

**Each subagent prompt includes:**
1. The persona definition (name, expertise, guiding question, primary lens) from `explain/personas.md`
2. The concept, audience, and domain template (if available)
3. The following 5-step execution plan:

   **A. Gemini Explanation Draft** — Call `mcp__gemini-cli__ask-gemini` with the persona's viewpoint to generate an explanation draft from this persona's perspective. Save to `explain/persona_{i}/gemini_ideas.md`.

   **B. Codex Critical Analysis** — Call `mcp__codex-cli__ask-codex` with the persona's viewpoint to generate a critical analysis (prerequisites, misconceptions, confusion neighbors) from this perspective. Save to `explain/persona_{i}/codex_ideas.md`.

   > **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously** within each persona subagent:
   > - **A'** (Expansive Explorer): Explanation draft from persona's perspective. Same 5-section deliverables as Step 1a Agent A. Save to `explain/persona_{i}/gemini_ideas.md`.
   > - **B'** (Grounded Builder): Critical analysis from persona's perspective. Same 5-section deliverables as Step 1a Agent B. Save to `explain/persona_{i}/codex_ideas.md`.

   **C+D. Cross-Review (simultaneous):**
   - Gemini (Teacher) reviews Codex analysis using `@{output_dir}/explain/persona_{i}/codex_ideas.md` → save to `explain/persona_{i}/gemini_review_of_codex.md`
   - Codex (Critic) reviews Gemini draft using `@{output_dir}/explain/persona_{i}/gemini_ideas.md` → save to `explain/persona_{i}/codex_review_of_gemini.md`

   > **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
   > - **C'** (Expansive Explorer): Review `codex_ideas.md` — same 5 review dimensions as Step 1b Agent A. Save to `explain/persona_{i}/gemini_review_of_codex.md`.
   > - **D'** (Grounded Builder): Review `gemini_ideas.md` — same 6 evaluation dimensions as Step 1b Agent B. Per issue: passage + why + fix. Save to `explain/persona_{i}/codex_review_of_gemini.md`.

   **E. Persona Conclusion** — The subagent synthesizes its top explanation strategies and key pedagogical insights, noting areas of internal agreement and disagreement between the two models (or two cognitive styles in claude-only mode). Save to `explain/persona_{i}/conclusion.md`.

Wait for all N subagents to complete before proceeding.

---

## Step 1-max-b: Layer 1 — Output Collection

1. Use Glob to verify that all N `explain/persona_{i}/conclusion.md` files exist.
   - If any are missing, re-spawn the failed subagent(s) and wait for completion. Maximum 1 retry per failed subagent. If retry also fails, proceed with N-1 persona outputs and note the gap.
2. Read all N `conclusion.md` files.
3. Construct a **cross-persona summary** identifying:
   - **Recurring explanation strategies** — approaches proposed by 2+ personas
   - **Unique pedagogical insights** — ideas that appeared in only one persona's output
   - **Explicit disagreements** — contradictory assessments of explanation approach, misconception risk, or audience calibration
4. **Consolidate conclusions for Layer 2**: Create `explain/all_conclusions.md` by concatenating
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

---

## Step 1-max-c: Layer 2 — Meta-Review + Adversarial Debate

**Phase A — Parallel Meta-Reviews:**

Execute simultaneously:

**Gemini Meta-Review:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "You are reviewing the outputs of {N} explanation-specialist personas who independently analyzed how to explain: {concept} to audience: {audience}

Here are all persona conclusions:
@{output_dir}/explain/all_conclusions.md

Provide a meta-review covering:
1. **Coverage analysis** — Which aspects of the explanation space are well-covered vs. underexplored?
2. **Quality assessment** — Rate each persona's explanation strategy (clarity, accuracy, audience calibration) on a 1-10 scale
3. **Cross-persona synthesis** — What emerges when combining all perspectives that no single persona captured?
4. **Top 3 disagreements** — Identify the 3 most significant points where personas contradict each other (e.g., on misconception risk, analogy choices, or precision-accessibility tradeoffs), with specific quotes
5. **Recommended explanation strategy** — Your top approach considering all perspectives",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```
Save to `explain/meta_review_gemini.md`.

**Codex Meta-Review:**
```
mcp__codex-cli__ask-codex(
  prompt: "You are reviewing the outputs of {N} explanation-specialist personas who independently analyzed how to explain: {concept} to audience: {audience}

Here are all persona conclusions:
@{output_dir}/explain/all_conclusions.md

Provide a meta-review covering:
1. **Coverage analysis** — Which aspects of the explanation space are well-covered vs. underexplored?
2. **Quality assessment** — Rate each persona's explanation strategy (clarity, accuracy, audience calibration) on a 1-10 scale
3. **Cross-persona synthesis** — What emerges when combining all perspectives that no single persona captured?
4. **Top 3 disagreements** — Identify the 3 most significant points where personas contradict each other, with specific quotes
5. **Recommended explanation strategy** — Your top approach considering all perspectives",
  model: "gpt-5.4"
)
```
Save to `explain/meta_review_codex.md`.

> **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD): Read `all_conclusions.md`. Deliverables: 1.Coverage analysis, 2.Quality assessment (rate each persona 1-10 on clarity/accuracy/calibration), 3.Cross-persona synthesis, 4.Top 3 disagreements (with specific quotes), 5.Recommended explanation strategy. Save to `explain/meta_review_gemini.md`.
> - **B** (AC): Read `all_conclusions.md`. Same 5-section deliverables with rigor/accuracy focus. Save to `explain/meta_review_codex.md`.

**Phase B — Disagreement Extraction:**

Claude reads both meta-reviews and extracts the **top 3 cross-persona disagreements** — prioritizing disagreements identified by both reviewers. For each disagreement, produce a structured summary: the claim, which personas support each side, and the core pedagogical tension. **Save the meta-disagreement summary to `explain/meta_disagreements.md`** before the debate calls.

**Phase C — Consolidate Debate Context + Adversarial Debate:**

Before the debate calls, create consolidated context files (each containing exactly what the opposing model needs):
- `explain/debate_context_for_gemini.md` — concatenate `meta_disagreements.md` + `meta_review_codex.md`
- `explain/debate_context_for_codex.md` — concatenate `meta_disagreements.md` + `meta_review_gemini.md`

Then execute the debate calls **simultaneously**:

```
mcp__gemini-cli__ask-gemini(
  prompt: "[Meta-Reviewer]
Target audience: {audience}

You reviewed {N} persona conclusions on explaining {concept} and identified top disagreements. Below is the disagreement summary followed by Codex's meta-review for context:

@{output_dir}/explain/debate_context_for_gemini.md

For each disagreement:
1. **Defend** your position with pedagogical evidence or learning science reasoning
2. **Concede** if the opposing argument better serves the audience's understanding
3. **Revise** your assessment to a new synthesized position if appropriate",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```
Save to `explain/meta_debate_gemini.md`.

```
mcp__codex-cli__ask-codex(
  prompt: "[Meta-Reviewer]
Target audience: {audience}

You reviewed {N} persona conclusions on explaining {concept} and identified top disagreements. Below is the disagreement summary followed by Gemini's meta-review for context:

@{output_dir}/explain/debate_context_for_codex.md

For each disagreement:
1. **Defend** your position with pedagogical evidence or learning science reasoning
2. **Concede** if the opposing argument better serves the audience's understanding
3. **Revise** your assessment to a new synthesized position if appropriate",
  model: "gpt-5.4"
)
```
Save to `explain/meta_debate_codex.md`.

> **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD): Read `debate_context_for_gemini.md`. Per disagreement: Defend (with pedagogical evidence) / Concede (if opposing better serves audience understanding) / Revise (new synthesized position). Save to `explain/meta_debate_gemini.md`.
> - **B** (AC): Read `debate_context_for_codex.md`. Per disagreement: Defend (with evidence) / Concede (if opposing better serves audience understanding) / Revise (new synthesized position). Save to `explain/meta_debate_codex.md`.

---

## Step 1-max-d: Layer 3 — Final Enriched Strategy Synthesis

1. Read all available documents:
   - `weights.json`, `personas.md`
   - All N `persona_{i}/conclusion.md` files
   - `meta_review_gemini.md`, `meta_review_codex.md`
   - `meta_debate_gemini.md`, `meta_debate_codex.md`
2. Load `weights.json` and extract the `"weights"` object. Compute **weighted scores** for each explanation strategy (same 0-10 rating per dimension, weighted sum).
3. Produce an **enriched `explain/synthesis.md`** with the following structure:
   1. **Personas Used** — table of N personas with name, expertise summary, and primary lens
   2. **Scoring Weights** — the weights used for ranking (from `weights.json`), including `_meta.method` to document how weights were selected (explicit, adaptive-recommended, audience-default, or custom)
   3. **Top Explanation Strategies** — ranked by weighted score, with:
      - Score breakdown per dimension (clarity, accuracy, depth, accessibility, completeness, engagement)
      - Which personas supported this strategy
      - Key arguments for and against
   4. **Cross-Persona Consensus** — explanation approaches where 3+ personas independently converged
   5. **Unique Contributions** — valuable pedagogical insights that only a single persona identified
   6. **Debate Resolution** — for each of the 3 debated disagreements: the original tension, how each meta-reviewer responded (defend/concede/revise), and the synthesized resolution
   7. **Emergent Insights** — pedagogical patterns or explanation connections visible only from the cross-persona vantage point
   8. **Recommended Explanation Strategy** — Claude's top recommendation with reasoning grounded in the multi-persona analysis
   9. **MAGI Process Traceability** — table mapping each conclusion to its source persona, layer, and artifact file path
4. Save to `explain/synthesis.md`.
5. **Proceed to Step 2** for final explanation generation.
