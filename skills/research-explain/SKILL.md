# Research Explain Skill

## Description
Generates high-quality explanations of concepts using Gemini and Codex in parallel (Phase 1: MAGI strategy exploration), then synthesizes a single-voice explanation with Claude (Phase 2: convergent generation).

## Usage
```
/research-explain "concept" [--domain physics|ai_ml|statistics|mathematics|paper] [--audience general-public|high-school|undergraduate|phd-student|researcher|expert|"free text"] [--weights '{"clarity":0.2,"accuracy":0.2}'] [--depth low|medium|high|max] [--personas N] [--claude-only] [--substitute "Gemini -> Opus"]
```

## Arguments
- `$ARGUMENTS` — The concept to explain and optional flags:
  - `--domain` — Knowledge domain (physics, ai_ml, statistics, mathematics, paper). Auto-inferred if omitted.
  - `--audience` — Target audience (default: `phd-student`):
    - `general-public` — No assumed technical background
    - `high-school` — Basic math/science literacy
    - `undergraduate` — Introductory college-level knowledge in the domain
    - `phd-student` — Graduate-level domain knowledge (default)
    - `researcher` — Active researcher familiar with the field
    - `expert` — Deep specialist in the exact sub-field
    - `"free text"` — Any custom audience description (e.g., `"medical doctors learning ML"`)
  - `--weights` — JSON object of scoring weights for explanation quality ranking. Keys: `clarity`, `accuracy`, `depth`, `accessibility`, `completeness`, `engagement`. Values must sum to 1.0. If omitted, Claude analyzes the prompt and audience to recommend adaptive weights for user confirmation (see Step 0a).
  - `--depth` — Controls explanation pipeline depth (default: `medium`):
    - `low` — Skip Phase 1 entirely; Claude generates explanation directly
    - `medium` — Full MAGI (parallel brainstorm + cross-review) → explanation
    - `high` — MAGI + adversarial debate → explanation with misconceptions section
    - `max` — Hierarchical MAGI-in-MAGI: N persona subagents → meta-review + debate → multi-perspective deep dive
  - `--personas N|auto` — Number of explanation-specialist subagents for `--depth max` (default: `auto`, range: 2-4). When `auto`, Claude analyzes the concept to determine the optimal persona count. Ignored for other depth levels.
  - `--claude-only` — Replace all Gemini/Codex MCP calls with Claude Agent subagents. Use when external model endpoints are unavailable or for a Claude-only workflow. Two subagents with distinct cognitive styles (Creative-Divergent and Analytical-Convergent) ensure perspective diversity.
  - `--substitute "Agent -> Opus"` — Replace a specific MAGI agent with Claude (Opus). Accepted: `"Gemini -> Opus"`, `"Codex -> Opus"`. Can be specified multiple times. If both substituted, equivalent to `--claude-only`.

## Instructions

> **Shared rules**: Read `${CLAUDE_PLUGIN_ROOT}/shared/rules.md` before starting. §MCP, §Claude-Only, §LaTeX, §Substitute apply to this skill.
> **Inline fallback** (if shared rules unavailable): Gemini models: gemini-3.1-pro-preview → gemini-2.5-pro → Claude. Codex: gpt-5.4. All math in LaTeX only (no Unicode: σ₁→`$\sigma_1$`). Use `@filepath` for MCP file refs; subagents use `Read` tool.

### MCP Tool Rules
See §MCP in shared rules. Additionally:
- **Codex**: Use `mcp__codex-cli__ask-codex` for analysis/review.
- **Visualization** (if plots are generated): See §Visualization.
- **When to search**: concept definitions, pedagogical resources, common misconceptions, recent breakthroughs, related concepts, fact-checking claims

### Claude-Only Mode
See §Claude-Only and §Substitute in shared rules. This skill uses Teacher/Critic asymmetric roles (see Step 0b).

### LaTeX Formatting Rules
See §LaTeX in shared rules.

When this skill is invoked, follow these steps exactly:

### Step 0: Setup

1. Parse the concept to explain from `$ARGUMENTS`. If a `--domain` flag is provided, note the domain (physics, ai_ml, statistics, mathematics, paper). Otherwise, infer the domain from the concept.
2. **Pipeline context detection**: If an `{output_dir}` was provided by the calling context and `.workspace.json` already exists at the output root, skip directory creation and write to `{output_dir}/explain/` instead of creating a new versioned directory.
3. Create the output directory: `outputs/{sanitized_concept}_{YYYYMMDD}_v{N}/explain/`
   - Sanitize the concept: lowercase, replace spaces with underscores, remove special characters, truncate to 50 chars.
   - Use today's date in YYYYMMDD format.
   - Version: Glob for `outputs/{sanitized_concept}_{YYYYMMDD}_v*/` and set N = max existing + 1 (start at v1).
4. Write `.workspace.json` at the output directory root:
   ```json
   {
     "output_dir": "{absolute_path}",
     "skill": "research-explain",
     "concept": "{original_concept}",
     "domain": "{domain}",
     "audience": "{audience}",
     "depth": "{depth}",
     "created_at": "{ISO-8601}"
   }
   ```
5. If a domain template exists at `${CLAUDE_PLUGIN_ROOT}/templates/domains/{domain}.md`, read it for context.
6. **Parse `--audience`**: Accept `general-public`, `high-school`, `undergraduate`, `phd-student`, `researcher`, `expert`, or any quoted free-text string (default: `phd-student`). The audience propagates into every prompt, persona casting, weight defaults, and the final explanation.
7. **Parse `--weights`**:
   - **If `--weights` is explicitly provided**: Validate that keys are a subset of {`clarity`, `accuracy`, `depth`, `accessibility`, `completeness`, `engagement`} and values sum to 1.0. Save immediately to `explain/weights.json` with metadata:
     ```json
     {
       "weights": { <user-provided weights> },
       "_meta": {
         "method": "explicit",
         "domain": "<detected domain>",
         "audience": "<detected audience>"
       }
     }
     ```
     Skip Step 0a entirely.
   - **If `--weights` is not provided**: Load audience defaults as a **baseline reference only** (do not save yet — Step 0a will handle saving after user confirmation):
   - `general-public`: `{"clarity": 0.25, "accuracy": 0.15, "depth": 0.10, "accessibility": 0.25, "completeness": 0.10, "engagement": 0.15}`
   - `high-school`: `{"clarity": 0.22, "accuracy": 0.18, "depth": 0.12, "accessibility": 0.20, "completeness": 0.12, "engagement": 0.16}`
   - `undergraduate`: `{"clarity": 0.20, "accuracy": 0.20, "depth": 0.15, "accessibility": 0.15, "completeness": 0.15, "engagement": 0.15}`
   - `phd-student`: `{"clarity": 0.15, "accuracy": 0.25, "depth": 0.20, "accessibility": 0.10, "completeness": 0.20, "engagement": 0.10}`
   - `researcher`: `{"clarity": 0.10, "accuracy": 0.25, "depth": 0.25, "accessibility": 0.05, "completeness": 0.25, "engagement": 0.10}`
   - `expert`: `{"clarity": 0.05, "accuracy": 0.30, "depth": 0.25, "accessibility": 0.05, "completeness": 0.30, "engagement": 0.05}`
   - For free-text audiences: Use `phd-student` as the baseline, then adjust in Step 0a based on the audience description.
8. **Parse `--depth`**: Accept `low`, `medium`, `high`, or `max` (default: `medium`).
   - `low` — Skip Phase 1 entirely; Claude generates explanation directly (jump to Step 2)
   - `medium` — Full MAGI + one-shot cross-review → strategy synthesis → explanation
   - `high` — Full MAGI + cross-review + adversarial debate → strategy synthesis → explanation with misconceptions
   - `max` — Hierarchical MAGI-in-MAGI pipeline (Steps 1-max-a through 1-max-d replace Steps 1a/1b/1b+/1c)
9. **Parse `--personas N|auto`**: Accept integer 2-4 or the string `auto` (default: `auto`). Only used when `--depth max`; ignored otherwise.
   - If `auto`: Defer persona count determination to Step 0b, where Claude analyzes the concept's complexity, number of distinct pedagogical angles, and audience needs to select the optimal N (2-4).
   - If an explicit integer is given: Use that value directly.
10. **Parse `--claude-only`**: Boolean flag (default: `false`). When present, all Gemini/Codex MCP calls are replaced with Claude Agent subagents. See the **Claude-Only Mode** section above for the replacement table and cognitive style definitions.

### Step 0a: Adaptive Weight Recommendation

> **If `--weights` was explicitly provided**: Skip this step entirely (weights already saved in Step 0).

When `--weights` is omitted, Claude analyzes the concept and audience to recommend context-appropriate weights:

1. **Analyze the concept and audience** for explanation-nature signals:

   | Signal | Example Keywords | Effect |
   |--------|-----------------|--------|
   | Highly abstract/formal | proof, axiom, topology, category theory | accuracy↑, depth↑, accessibility↓ |
   | Intuitive/visual concept | geometry, flow, wave, phase space | clarity↑, engagement↑ |
   | Counterintuitive concept | paradox, entanglement, Monty Hall | engagement↑, accuracy↑ |
   | Prerequisite-heavy | requires: linear algebra, measure theory | completeness↑, accessibility↓ |
   | Common misconceptions exist | entropy, natural selection, p-value | accuracy↑, clarity↑ |
   | Applied/practical | algorithm, protocol, technique, tool | accessibility↑, engagement↑ |
   | Foundational/core concept | fundamental, basis, definition | completeness↑, accuracy↑ |
   | Broad/survey topic | overview, introduction, survey | completeness↑, depth↓ |
   | Narrow/advanced topic | specific theorem, edge case, subtlety | depth↑, accessibility↓ |

2. **Generate recommended weights**: Starting from the audience baseline loaded in Step 0, apply adjustments based on detected signals:
   - Each signal adjusts relevant dimensions by ±0.05 to ±0.10
   - After all adjustments, **normalize** so values sum to 1.0
   - **Clamp** each dimension to the range [0.05, 0.45] before final normalization

3. **Present a comparison table** to the user:

   ```
   Detected signals: [list of signals found in the concept/audience]

   | Dimension       | Audience Default | Recommended | Adjustment Reason               |
   |-----------------|-----------------|-------------|----------------------------------|
   | clarity         | 0.15            | 0.20        | +0.05 (counterintuitive concept) |
   | accuracy        | 0.25            | 0.30        | +0.05 (common misconceptions)    |
   | depth           | 0.20            | 0.15        | -0.05 (broad survey topic)       |
   | accessibility   | 0.10            | 0.10        | (no change)                      |
   | completeness    | 0.20            | 0.15        | -0.05 (narrow scope)             |
   | engagement      | 0.10            | 0.10        | (no change)                      |
   ```

4. **Ask the user for confirmation** using `AskUserQuestion`:
   - Option A: **"Accept recommended weights"** (Recommended) — use the adaptive weights
   - Option B: **"Use audience defaults"** — use the unmodified audience baseline
   - Other: User provides custom weights as JSON

   If the user provides custom weights: validate keys and sum. Maximum 1 retry on invalid input; fall back to audience defaults on continued failure.

5. **Save to `explain/weights.json`** with metadata based on the user's choice:
   ```json
   {
     "weights": { <chosen weights> },
     "_meta": {
       "method": "<adaptive-recommended|audience-default|custom>",
       "domain": "<detected domain>",
       "audience": "<detected audience>",
       "audience_defaults": { <original audience baseline> },
       "signals_detected": ["counterintuitive concept", "common misconceptions", ...],
       "adjustments_applied": {
         "accuracy": "+0.05 (common misconceptions)",
         "clarity": "+0.05 (counterintuitive concept)"
       }
     }
   }
   ```
   - If "Accept recommended": `method` = `"adaptive-recommended"`
   - If "Use audience defaults": `method` = `"audience-default"`, `signals_detected` and `adjustments_applied` are still recorded for traceability
   - If custom JSON: `method` = `"custom"`

### Step 0b: Dynamic Persona Casting

After setup, Claude analyzes the concept, domain, and audience to assign specialist personas:

**For `--depth low`:** Skip this step entirely.

**For `--depth medium|high` (2 personas — asymmetric Teacher/Critic roles):**

1. Analyze the concept's sub-topics, prerequisite structure, common misconceptions, and audience needs.
2. Assign a **Teacher persona (Agent A / Gemini)** — an expert communicator profile suited for explaining this concept to the target audience (e.g., "Richard Feynman — Intuitive Physics Explainer" or "3Blue1Brown-style Visual Mathematics Educator"). The Teacher's job is to **draft the best possible explanation**.
3. Assign a **Critic persona (Agent B / Codex)** — a pedagogical analyst profile suited for finding flaws in explanations (e.g., "George Pólya — Mathematical Problem-Solving Analyst" or "Cognitive Science Assessment Specialist"). The Critic's job is to **identify prerequisites, misconceptions, confusion neighbors, and calibration questions**.
4. Each persona definition should include: name/title, expertise areas (3-5 bullet points), and a guiding question that shapes their perspective. **Name the persona after a real historical figure (위인) whose work is closely related to the persona's domain** (e.g., a physics explainer → "Richard Feynman", a mathematics pedagogue → "George Pólya", a statistical educator → "Florence Nightingale"). This immediately signals the persona's intellectual lineage and communication style.
5. Personas are **complementary**: the Teacher builds understanding, the Critic stress-tests it.
6. **If `--claude-only`**: Relabel the personas in `explain/personas.md`:
   - "Teacher persona (Gemini)" → "Subagent A (Creative-Divergent, Teacher)"
   - "Critic persona (Codex)" → "Subagent B (Analytical-Convergent, Critic)"
   - Include the cognitive style directive in each persona definition so subagents receive it directly.
7. Save to `explain/personas.md`.

**For `--depth max` (N personas):**

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
   - **Name/title** — **Use a real historical figure (위인) whose work aligns with this persona's domain** (e.g., "Richard Feynman — Intuitive Physics Explainer", "Emmy Noether — Abstract Structure Specialist", "John Tukey — Practical Data Analyst"). The figure's intellectual legacy should resonate with the persona's explanatory lens.
   - **Expertise areas** (3-5 bullet points)
   - **Guiding question** that shapes their perspective
   - **Primary lens** (one sentence summarizing their explanatory viewpoint)
5. Personas are **complementary** — they should cover distinct dimensions of the explanation space with minimal overlap.
6. **If `--claude-only`**: Within each persona's mini-MAGI pipeline, relabel the internal model roles:
   - "Gemini" → "Expansive Explorer" (pushes boundaries, explores emerging approaches, proposes frontier ideas)
   - "Codex" → "Grounded Builder" (focuses on proven approaches, clear implementation paths, established tools)
   - Include these cognitive style directives in the persona file so subagents receive them directly.
7. Save to `explain/personas.md`.

### Step 1a: Parallel Asymmetric Analysis (`--depth medium|high|max`)

> **If `--depth low`**: Skip this step entirely and proceed to Step 2.
> **If `--depth max`**: Skip this step — use Steps 1-max-a through 1-max-d instead.

Execute these two calls **simultaneously** (in the same message). **Prepend the assigned persona** from `explain/personas.md` to each prompt. Note: Unlike brainstorming (which uses `brainstorm` tools for both agents), explanation uses `ask-gemini` and `ask-codex` for role-specific prompts.

**Agent A — Teacher Draft (Gemini):**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {teacher_persona_name} — {teacher_persona_expertise}]
Guiding question: {teacher_guiding_question}
Target audience: {audience}

Domain context: @{domain_template_path}

Concept to explain: {concept}

You are a master explainer. Generate a comprehensive draft explanation of this concept for the specified audience. Your explanation should:

1. **Core Explanation**: Build understanding from first principles appropriate to the audience level. Use analogies, examples, and progressive complexity.
2. **Key Intuitions**: What are the 2-3 most important intuitions the audience must grasp?
3. **Mathematical Formalism** (if applicable): Include relevant equations with clear notation explanations. Follow LaTeX formatting rules: inline math with $...$ and display equations with $$ on separate lines.
4. **Concrete Examples**: Provide 2-3 worked examples or real-world applications.
5. **Connections**: How does this concept relate to concepts the audience likely already knows?

Write for maximum clarity and understanding. Use the persona's communication style.",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-2.5-pro" → Claude
)
```
> Note: Omit the `Domain context: @{domain_template_path}` line from the prompt when no domain template exists.

**Agent B — Critic Analysis (Codex):**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {critic_persona_name} — {critic_persona_expertise}]
Guiding question: {critic_guiding_question}
Target audience: {audience}

Domain context: @{domain_template_path}

Concept to explain: {concept}

You are a pedagogical analyst and explanation critic. Generate a comprehensive critical analysis covering:

1. **Prerequisites Map**: What concepts must the audience understand before this one? List in dependency order. For each, note whether the audience level likely already has it.
2. **Common Misconceptions** (at least 5): For each misconception:
   - State the misconception clearly
   - Explain why it is plausible (what leads people to believe it)
   - Explain precisely why it is wrong
   - Provide a corrective reframing
3. **Confusion Neighbors**: Concepts that are commonly confused with this one. For each pair:
   - This concept IS NOT [confused concept]
   - Key distinguishing feature
4. **Precision-Accessibility Tradeoffs**: Where must an explanation sacrifice precision for accessibility at this audience level? What simplifications are acceptable vs. dangerous?
5. **Calibration Questions** (5-10): Questions that test genuine understanding (not just recall). Include expected correct answers and common wrong answers with explanations of what each wrong answer reveals about the student's misunderstanding.",
  model: "gpt-5.4"
)
```
> Note: Omit the `Domain context: @{domain_template_path}` line from the prompt when no domain template exists.

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__ask-gemini` with the Gemini fallback chain and critic-focused framing.

> **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD, Teacher): Draft explanation of {concept} for {audience} using persona. Read domain template. Deliverables: 1.Core Explanation (first principles, analogies, progressive complexity), 2.Key Intuitions (2-3), 3.Mathematical Formalism (LaTeX), 4.Concrete Examples (2-3 worked), 5.Connections to audience's existing knowledge. Use persona's communication style. Save to `explain/gemini_ideas.md`.
> - **B** (AC, Critic): Critical analysis for {concept}/{audience} using persona. Deliverables: 1.Prerequisites Map (dependency order; note which audience likely has), 2.Common Misconceptions (≥5; each: statement → why plausible → why wrong → corrective reframing), 3.Confusion Neighbors (per pair: "IS NOT" + key distinguishing feature), 4.Precision-Accessibility Tradeoffs, 5.Calibration Questions (5-10; each: question + correct answer + common wrong answers + what each wrong answer reveals). Save to `explain/codex_ideas.md`.

Save results to:
- `explain/gemini_ideas.md` — Teacher's (or Subagent A's) draft explanation with header noting source, persona, and timestamp
- `explain/codex_ideas.md` — Critic's (or Subagent B's) analysis with header noting source, persona, and timestamp

### Step 1b: Cross-Check (`--depth medium` or `--depth high` only)

> **If `--depth low`**: Skip this step entirely and proceed to Step 2.

**Pre-check**: Verify `gemini_ideas.md` and `codex_ideas.md` both exist and are non-empty before proceeding. If either is missing, re-run only the failed agent from Step 1a.

After both Phase 1a results are saved, execute these two calls **simultaneously**. **Prepend the assigned persona** to each review prompt:

**Teacher reviews Critic's analysis (Round 1):**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {teacher_persona_name} — {teacher_persona_expertise}]
Target audience: {audience}

Review the following critical analysis of an explanation for: {concept}

@{output_dir}/explain/codex_ideas.md

For each item in the Critic's analysis:
1. **Misconceptions**: Are these real misconceptions at this audience level? Are any missing? Would your explanation actually trigger any of these?
2. **Prerequisites**: Agree/disagree with the prerequisite ordering? Are any prerequisites overestimated or underestimated for this audience?
3. **Confusion Neighbors**: Are these the right confusion neighbors? Suggest additions or removals.
4. **Precision-Accessibility Tradeoffs**: Are the identified tradeoffs fair? Where would you push back?
5. **Calibration Questions**: Would your explanation enable the audience to answer these correctly? Flag any questions that are unfair for the audience level.

Also note: What aspects of the Critic's analysis should change your draft explanation?",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-2.5-pro" → Claude
)
```

**Critic reviews Teacher's draft (Round 1):**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {critic_persona_name} — {critic_persona_expertise}]
Target audience: {audience}

Review the following draft explanation of: {concept}

@{output_dir}/explain/gemini_ideas.md

Evaluate the Teacher's explanation on these dimensions:
1. **Accuracy**: Are there any incorrect statements, oversimplifications that cross into inaccuracy, or misleading analogies?
2. **Completeness**: Does it cover all essential aspects? What critical gaps exist?
3. **Audience Calibration**: Is the language, depth, and assumed knowledge appropriate for {audience}?
4. **Misconception Risk**: Does any part of the explanation inadvertently reinforce common misconceptions?
5. **Analogy Fidelity**: Do the analogies accurately map to the concept? Where do they break down, and are those breakdown points acknowledged?
6. **Progressive Structure**: Does the explanation build understanding in the right order? Are there logical jumps?

For each issue found, provide:
- The specific problematic passage
- Why it's problematic
- A suggested fix",
  model: "gpt-5.4"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__ask-gemini` with the Gemini fallback chain.

> **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD, Teacher reviewing Critic): Read `codex_ideas.md`. Review all 5 sections: misconceptions (real at this level? missing?), prerequisites (ordering? over/underestimated?), confusion neighbors (additions/removals?), precision-accessibility tradeoffs (fair?), calibration questions (answerable from your explanation?). Also: what should change in your draft? Save to `explain/gemini_review_of_codex.md`.
> - **B** (AC, Critic reviewing Teacher): Read `gemini_ideas.md`. Evaluate 6 dimensions: accuracy, completeness, audience calibration, misconception risk, analogy fidelity (where do analogies break?), progressive structure (logical jumps?). Per issue: specific passage + why problematic + suggested fix. Save to `explain/codex_review_of_gemini.md`.

Save results to:
- `explain/gemini_review_of_codex.md`
- `explain/codex_review_of_gemini.md`

### Step 1b+: Adversarial Debate (`--depth high` only)

> **If `--depth low` or `--depth medium`**: Skip this step entirely.

After Round 1 cross-review, Claude identifies the **top 3 points of disagreement** between the Teacher and Critic, focusing on these explanation-specific criteria:
- **Misconception risk**: Disagreement on whether an explanation approach reinforces misconceptions
- **Analogy fidelity**: Disagreement on whether an analogy is accurate enough or dangerously misleading
- **Precision-accessibility tradeoff**: Disagreement on where the acceptable simplification boundary lies for this audience

**Save the disagreement summary to `explain/disagreements.md`** before the debate calls.

Execute Round 2 **simultaneously**:

**Teacher Round 2 — Defend/Concede/Revise:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "[Persona: {teacher_persona_name}]
Target audience: {audience}

You (Teacher) and the Critic reviewed each other's work on explaining: {concept}

Here are the top 3 points of disagreement:

@{output_dir}/explain/disagreements.md

For each disagreement:
1. **Defend** your pedagogical choice if you believe it best serves understanding for this audience, providing evidence from learning science or teaching experience
2. **Concede** if the Critic's objection reveals a genuine accuracy or misconception risk, explaining why
3. **Revise** your approach to a new position that balances clarity and accuracy if appropriate

Your original review:
@{output_dir}/explain/gemini_review_of_codex.md

Critic's review of your draft:
@{output_dir}/explain/codex_review_of_gemini.md",
  model: "gemini-3.1-pro-preview"  // fallback chain applies
)
```

**Critic Round 2 — Defend/Concede/Revise:**
```
mcp__codex-cli__ask-codex(
  prompt: "[Persona: {critic_persona_name}]
Target audience: {audience}

You (Critic) and the Teacher reviewed each other's work on explaining: {concept}

Here are the top 3 points of disagreement:

@{output_dir}/explain/disagreements.md

For each disagreement:
1. **Defend** your objection if you believe the accuracy/misconception risk is genuine, providing specific examples of how learners are misled
2. **Concede** if the Teacher's pedagogical choice genuinely aids understanding without significant accuracy cost, explaining why
3. **Revise** your assessment to a new position that respects both rigor and accessibility if appropriate

Your original review:
@{output_dir}/explain/codex_review_of_gemini.md

Teacher's review of your analysis:
@{output_dir}/explain/gemini_review_of_codex.md",
  model: "gpt-5.4"
)
```

> **If `--claude-only`**: Per §SubagentExec, spawn **simultaneously**:
> - **A** (CD, Teacher Round 2): Read `disagreements.md` + `gemini_review_of_codex.md` + `codex_review_of_gemini.md`. Per disagreement: Defend (with learning science evidence) / Concede (if genuine accuracy or misconception risk) / Revise (balance clarity + accuracy). Save to `explain/debate_round2_gemini.md`.
> - **B** (AC, Critic Round 2): Read same 3 files. Per disagreement: Defend (with specific examples of how learners are misled) / Concede (if pedagogical choice genuinely aids understanding without accuracy cost) / Revise (balance rigor + accessibility). Save to `explain/debate_round2_codex.md`.

Save results to:
- `explain/debate_round2_gemini.md`
- `explain/debate_round2_codex.md`

### Step 1-max-a: Layer 1 — Parallel Persona Subagents (`--depth max` only)

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

### Step 1-max-b: Layer 1 — Output Collection

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

### Step 1-max-c: Layer 2 — Meta-Review + Adversarial Debate

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

### Step 1-max-d: Layer 3 — Final Enriched Strategy Synthesis (`--depth max`)

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

### Step 1c: Strategy Synthesis

> **If `--depth max`**: Skip — synthesis is produced by Step 1-max-d above.
> **If `--depth low`**: Skip — proceed directly to Step 2.

1. Read all available documents:
   - Always: `gemini_ideas.md`, `codex_ideas.md`
   - If `--depth medium` or `high`: `gemini_review_of_codex.md`, `codex_review_of_gemini.md`
   - If `--depth high`: `debate_round2_gemini.md`, `debate_round2_codex.md`
   - Always: `weights.json`, `personas.md`
2. Load `weights.json` and extract the `"weights"` object. Use the weights to compute a **weighted score** for each explanation strategy:
   - For each candidate strategy, rate it on each weight dimension (0-10 scale): clarity, accuracy, depth, accessibility, completeness, engagement
   - Compute the weighted sum: `score = Σ(weight_i × rating_i)`
   - Rank strategies by weighted score
3. Synthesize into an **explanation strategy document** that includes:
   - **Personas Used** — brief summary of assigned Teacher and Critic personas
   - **Scoring Weights** — the weights used for ranking (from `weights.json`), including `_meta.method`
   - **Recommended Explanation Strategy** (ranked by weighted score, showing score breakdown):
     - Best analogies and examples to use
     - Optimal explanation structure/ordering
     - Key intuitions to emphasize
   - **Prerequisites Summary** — consolidated prerequisite chain for the target audience
   - **Misconception Inventory** — merged and deduplicated misconceptions from both agents
   - **Confusion Neighbors** — consolidated confusion neighbor list
   - **Consensus Points** — pedagogical choices both agents agreed on
   - **Divergence Points** — areas of disagreement and how to resolve them
   - **Debate Resolution** (`--depth high` only) — for each of the 3 debated disagreements, document the final resolution: who conceded, what was revised, and the synthesized position
   - **Calibration Questions** — best questions from the Critic's analysis, selected for the target audience
4. Save to `explain/synthesis.md`.

### Step 2: Explanation Generation

Claude reads all Phase 1 artifacts and generates the final explanation. This step is **always** executed by Claude directly (never delegated to MCP tools) to ensure a single authoritative voice.

**For `--depth low`** (no Phase 1 artifacts):
1. Read `explain/weights.json` (if available).
2. If a domain template exists, read it for context.
3. Generate `explain/explanation.md` directly based on the concept, audience, and domain.

**For `--depth medium|high|max`** (Phase 1 artifacts available):
1. Read `explain/synthesis.md` and all referenced artifacts.
2. Read `explain/weights.json` to understand the quality priorities.

**Generate `explain/explanation.md`** with the following structure. Target word count depends on depth:
- `low`: 200-500 words
- `medium`: 1,000-2,000 words
- `high`: 3,000-5,000 words
- `max`: 5,000-10,000 words

```markdown
# {Concept}

> Audience: {audience} | Depth: {depth} | Domain: {domain}

## Core Explanation

[Main explanation written in a single authoritative voice. Build understanding progressively from the audience's existing knowledge. Use analogies, examples, and mathematical formalism as appropriate for the audience level. Follow LaTeX formatting rules for all mathematical expressions.

This section should:
- Open with an intuitive hook that connects to the audience's existing knowledge
- Build concepts progressively, each building on the previous
- Include concrete examples at each stage of abstraction
- Use the best analogies identified in Phase 1 (if available)
- Acknowledge and correct common misconceptions inline where natural
- Include mathematical formalism at the appropriate level for the audience]

## Common Misconceptions and Why They Fail

> Include this section only for `--depth high` or `--depth max`.

[For each misconception (at least 3-5):

### Misconception: "{Statement of the misconception}"

**Why it's plausible**: {What makes this easy to believe}

**Why it's wrong**: {Precise explanation of the error}

**The correct understanding**: {Corrective reframing that sticks}
]

## Confusion Neighbors

> Include this section only for `--depth medium`, `--depth high`, or `--depth max`.

| This Concept | Is NOT | Key Difference |
|---|---|---|
| {concept} | {confused concept 1} | {distinguishing feature} |
| {concept} | {confused concept 2} | {distinguishing feature} |
| ... | ... | ... |

[Brief paragraph explaining why each confusion arises and how to keep them straight.]

## Test Your Understanding

> Include this section only for `--depth medium`, `--depth high`, or `--depth max`.

[5-10 questions that test genuine understanding (not recall). Calibrated for the target audience level. Each question should:
- Target a specific concept from the Core Explanation
- Have a clear correct answer
- Have plausible wrong answers that reveal specific misunderstandings

Format:
1. **{Question}**
   <details><summary>Answer</summary>
   {Answer with explanation of why common wrong answers are wrong}
   </details>
]
```

**Quality checklist** (verify before saving):
- [ ] All mathematical expressions follow LaTeX formatting rules
- [ ] Language and complexity are calibrated for the target audience
- [ ] Best analogies from Phase 1 are incorporated (if Phase 1 was run)
- [ ] No "committee voice" — the explanation reads as one coherent author
- [ ] Misconceptions section (if included) addresses those identified in Phase 1
- [ ] Confusion neighbors table is accurate and complete
- [ ] Test questions target genuine understanding, not memorization

Save to `explain/explanation.md`.

### Step 3: User Feedback

Present the explanation to the user with:
- A concise summary of what was generated (concept, audience, depth, word count)
- The location of all output files
- Clear options for refinement:
  - **Adjust audience level**: Re-generate for a different audience
  - **Adjust depth**: Add/remove sections
  - **Refine specific section**: Focus on improving one part
  - **Expand a topic**: Deep-dive into a specific aspect mentioned in the explanation

Wait for user input before proceeding.

## Output Files

**`--depth low`:**
```
explain/
├── weights.json                  # Scoring weights + selection metadata (if Step 0a ran)
└── explanation.md                # Final explanation (always)
```

**`--depth medium`:**
```
explain/
├── weights.json                  # Scoring weights + selection metadata
├── personas.md                   # Assigned Teacher + Critic personas
├── gemini_ideas.md               # Teacher's draft explanation
├── codex_ideas.md                # Critic's analysis (prerequisites, misconceptions, etc.)
├── gemini_review_of_codex.md     # Teacher reviews Critic
├── codex_review_of_gemini.md     # Critic reviews Teacher
├── synthesis.md                  # Explanation strategy synthesis
└── explanation.md                # Final explanation
```

**`--depth high`:**
```
explain/
├── weights.json                  # Scoring weights + selection metadata
├── personas.md                   # Assigned Teacher + Critic personas
├── gemini_ideas.md               # Teacher's draft explanation
├── codex_ideas.md                # Critic's analysis
├── gemini_review_of_codex.md     # Teacher reviews Critic
├── codex_review_of_gemini.md     # Critic reviews Teacher
├── disagreements.md              # Disagreement summary for debate
├── debate_round2_gemini.md       # Adversarial debate — Teacher
├── debate_round2_codex.md        # Adversarial debate — Critic
├── synthesis.md                  # Explanation strategy synthesis
└── explanation.md                # Final explanation (with Misconceptions section)
```

**`--depth max`:**
```
explain/
├── weights.json                  # Scoring weights + selection metadata
├── personas.md                   # N explanation-specialist personas
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
├── synthesis.md                  # Enriched strategy synthesis
└── explanation.md                # Final multi-perspective deep dive explanation
```
