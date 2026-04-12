# Reusable Templates (T1–T13)

> This file contains the full definitions of all reusable templates referenced by ID in SKILL.md.
> Read this file when executing any step that references a template (e.g., "per **T2**", "apply **T3**").

**T1: Cognitive Styles**

| ID | Style | One-line directive |
|---|---|---|
| T1-CD | Creative-Divergent | Unconventional connections across adjacent fields, "What if?" scenarios, wide exploratory breadth, questioning fundamental assumptions |
| T1-AC | Analytical-Convergent | Step-by-step feasibility analysis, established methodologies, deep evaluation, practical constraints, risk assessment |
| T1-EE | Expansive Explorer | Push boundaries, explore emerging approaches, propose frontier ideas, challenge conventional thinking. (Replaces Gemini in `--depth max` internal subagents) |
| T1-GB | Grounded Builder | Focus on proven approaches, clear implementation paths, established tools, demonstrable results. (Replaces Codex in `--depth max` internal subagents) |

**T2: Review Instructions**

- **T2-Science**: Review for technical feasibility, scientific rigor, novelty, and potential impact.
  **Pre-review**: Before reviewing, write a 2-sentence summary of the document being reviewed (title + main thesis). This confirms you are reviewing the correct file.
  For each idea, separated by `---`:
  (0) **Identity check**: Restate the idea's title and core claim in one sentence.
  (1) Restate the proponent's mechanism in your own words.
  (2) Identify strengths and weaknesses — for each, explain concretely in what scenario it manifests and why it matters.
  (3) Pose one counterfactual: "If component X were removed, would the claim still hold?"
  (4) **Verdict** — choose exactly one per §AntiConsensus:
      - **AGREE**: State your independent supporting evidence (different from the proponent's). Agreement without independent evidence is not permitted.
      - **DISAGREE**: State what is wrong and under what conditions your objection would be invalidated.
      - **INSUFFICIENT**: Evidence is too weak to judge either way. State what evidence would resolve the ambiguity.
  (5) Suggest improvements.
- **T2-Feasibility**: Review for implementation feasibility, computational practicality, available tools/datasets, and timeline realism.
  **Pre-review**: Before reviewing, write a 2-sentence summary of the document being reviewed (title + main thesis). This confirms you are reviewing the correct file.
  For each idea, separated by `---`:
  (0) **Identity check**: Restate the idea's title and core claim in one sentence.
  (1) Restate the proponent's mechanism.
  (2) Strengths and weaknesses with concrete scenarios.
  (3) Name the warrant connecting the claimed benefit to the proposed mechanism.
  (4) **Verdict** — choose exactly one per §AntiConsensus:
      - **AGREE**: State your independent supporting evidence (different from the proponent's). Agreement without independent evidence is not permitted.
      - **DISAGREE**: State what is wrong and under what conditions your objection would be invalidated.
      - **INSUFFICIENT**: Evidence is too weak to judge either way. State what evidence would resolve the ambiguity.
  (5) Suggest improvements.

**T3: DCR Debate Framework**

For each disagreement: (1) **Defend** your position if correct, providing additional evidence. (2) **Concede** if the opposing argument is stronger, explaining why. (3) **Revise** your assessment to a new position if appropriate. Walk through reasoning step by step — explain the logic chain so a reader can follow exactly why you defend, concede, or revise.

**Concession Tax** (per §AntiConsensus): Every Concede MUST include:
- (a) Which specific piece of evidence or logical step in the opponent's argument defeated your position.
- (b) "Would I still hold my original position without that evidence?" — answer Yes or No.
- (c) If No: acknowledge the original idea was weakly grounded; this lowers the finding's confidence in synthesis.
A concession that cannot name the defeating evidence is not a concession — it is capitulation. Revert to Defend if you cannot articulate why the opponent is right.

**Hybrid Tribunal** (per §AntiConsensus): If you propose a "hybrid," "combined," or "best-of-both" approach:
- (a) Name one concrete scenario where the hybrid outperforms each pure approach independently.
- (b) Name one concrete scenario where the hybrid is worse than at least one pure approach.
- (c) Explain the hybrid's own mechanism — not just "A's strength + B's strength," but how the combination produces a result neither achieves alone.
- (d) If (a)–(c) cannot be satisfied, withdraw the hybrid and choose one pure position to defend.

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
- **[MELCHIOR] Judgment** — Opus's one-sentence verdict: endorse, revise, or reject, with the core reason. This is Opus's voice, not a model summary.

**T8: Synthesis Epilogue**

After the ranked findings and before "Recommended Path Forward", include these three sections:

1. **Research Gaps** (depth-conditional):
   - `--depth low`: Identify topics where the single model hedged or avoided confident claims. Note as "potential gap (single-model signal)."
   - `--depth medium|high|max|auto`: Identify topics where BOTH/ALL models hedged or avoided confident claims (convergent hedge). Note as "**Research Frontier** — convergent avoidance across independent models suggests genuine knowledge gap." Distinguish scope gaps (topic avoided entirely) from evidence gaps (specific claim hedged).

2. **Non-Recommendations** (`--depth medium|high|max|auto` only):
   Cross-model rejection block. List ideas that one model generated but other model(s) explicitly rejected during cross-review, with rejection reasons. Criteria: rejection must be from a model that has NOT seen the generating model's output (independent rejection). Format: "**Do Not Pursue**: [idea] — Rejected by [model] because: [reason]."

3. **Next Three Steps**:

   **Decisive Experiment** (required, exactly one, placed FIRST):
   Before the tiered steps, identify the single experiment that would most shift confidence in the top finding, **regardless of cost or timeline**. Format:
   > **Decisive Experiment**: [description] — This would resolve [specific uncertainty] because [causal reasoning]. Feasibility: [Low/Medium/High].

   This anchors the action plan in causal logic before feasibility narrows the scope. Even if feasibility is Low, stating the decisive experiment clarifies what the incremental steps are approximating.

   **Tiered Action Steps** — For each top-ranked finding (Tier 1 and Tier 2), provide three concrete actions across a tiered timeline:
   - **Tier A** (< 1 day, existing data/models): Quick validation or diagnostic using what is already available.
   - **Tier B** (~ 1 week, existing models + new analysis): Deeper analysis, new measurements on existing checkpoints, or small-scale experiments.
   - **Tier C** (~ 1 month, new training/infrastructure): Training controlled variants, large-scale experiments, or new model development.
   Require at least one step from each tier. Each step specifies:
   - **Type**: Empirical (run experiment) / Design (write protocol) / Review (read/verify) / **Intervention** (train a controlled variant) / **Ablation** (remove/modify a component) / **Null** (construct a null model or negative control)
   - **Action**: verb + object + success criterion
   Example: "[Tier A, Empirical] Compute CI ratio on existing checkpoints at 5 temperatures — success: monotonic trend confirms or refutes the prediction within 1 hour."
   Example: "[Tier C, Intervention] Train local-window attention transformer interpolating between PixelCNN and LatticeGPT receptive fields — success: CI scales with window size ($R^2 > 0.8$)."
   Findings that cannot produce at least one Tier A step and one Intervention/Ablation/Null step are automatically classified as Tier 3 (speculative, condensed treatment).

**T9: Pre-flight Query**

Construct two parallel evidence-gathering queries for the research topic per §PreFlight:

1. **OpenAlex** (academic literature): Run `scripts/openalex_search.py` (bundled script):
   ```bash
   uv run python ${CLAUDE_PLUGIN_ROOT}/skills/research-brainstorm/scripts/openalex_search.py "{topic}" --filter "publication_year:>2021,type:article|review" --limit 10 --format md
   ```
   If the topic contains domain-specific jargon and results are sparse (< 3 papers), retry with broader keywords.

2. **WebSearch** (recent developments):
   ```
   WebSearch(query: "{topic} recent advances 2024 2025 2026")
   ```

Combine results into `brainstorm/preflight_context.md`:
```
## Academic Literature (OpenAlex)
[numbered list of papers with title, authors, year, citations, DOI, abstract excerpt]

## Recent Developments (Web)
[key findings and trends from web search, with source URLs]

## Methodological Landscape
[2-3 sentences summarizing common approaches and known limitations based on the above]
```

**Source cap**: 10 papers from OpenAlex + 5 web sources = 15 total max.

**T10: Persona Briefing**

From `brainstorm/preflight_context.md`, create persona-specific briefings per §PreFlight. Each briefing is a **filtered and reframed view** of the same evidence:

For `--depth medium|high|auto` (2-model pipeline):

| Target | File | Focus | Filter Question |
|---|---|---|---|
| Gemini persona | `brainstorm/briefing_gemini.md` | Failure cases, counterexamples, pitfalls, unexplored alternatives | "What has gone wrong, and what hasn't been tried?" |
| Codex persona | `brainstorm/briefing_codex.md` | Implementations, tools, datasets, benchmarks, constraints | "What exists to build on, and what are the constraints?" |

For `--depth max` (N-persona pipeline): Create `brainstorm/briefing_persona_{i}.md` for each persona, filtered by that persona's expertise and guiding question from `personas.md`.

Each briefing file structure:
```
## Key Papers (3-5 most relevant)
[papers filtered for this persona's concerns, with 1-sentence relevance note each]

## Domain Context
[2-3 sentences framing the landscape from this persona's perspective]

## Critical Questions
[2-3 questions this persona should investigate based on the evidence]
```

Claude/MELCHIOR receives the full unfiltered `preflight_context.md` directly during synthesis (not a filtered briefing).

**T11: Evidence Anchoring**

After cross-review (T2), for each idea that received a **DISAGREE** or **INSUFFICIENT** verdict, per §EvidenceAnchoring:

1. **Extract the disputed claim**: Identify the core mechanism or assertion under dispute from the review file.
2. **Construct search query**: Derive a precise query from the claim (key technical terms + methodological approach + domain).
3. **Search for evidence** (execute in parallel):
   - **OpenAlex**: Run `scripts/openalex_search.py "{claim_query}" --filter "publication_year:>2020" --sort "relevance_score:desc" --limit 5 --format md`
   - **WebSearch**: `"{claim_query}" evidence OR study OR experiment`
4. **Classify evidence**:
   - **Supporting**: directly supports the disputed mechanism
   - **Contradicting**: provides counterexample or contradicts
   - **Tangential**: related but not directly addressing

Save to `brainstorm/claim_evidence.md`:
```
## Disputed Claim 1: [claim summary]
**Original verdict**: [DISAGREE/INSUFFICIENT] by [model]
**Idea**: [idea title from brainstorm]
**Search queries**: [list]

### Supporting Evidence
- [Paper title] ([year], cited: N): [1 sentence — how it supports]

### Contradicting Evidence
- [Paper title] ([year], cited: N): [1 sentence — how it contradicts]

### Evidence Assessment
[1-2 sentences: does evidence resolve the dispute? Which side is stronger?]

---
```

**Scope limits** (per §EvidenceAnchoring):
- Maximum **5** disputed claims (prioritize DISAGREE over INSUFFICIENT, higher-ranked ideas first)
- Maximum **5** OpenAlex + **3** web results per claim
- No evidence found → "No direct evidence found — dispute remains empirical"

**T12: Depth Escalation Criteria**

After Step 1b cross-review, analyze T2 verdict distribution to determine if depth should escalate. Only applies when `--depth auto`.

1. **Count verdicts**: Run `scripts/parse_verdicts.py` (bundled script):
   ```bash
   uv run python ${CLAUDE_PLUGIN_ROOT}/skills/research-brainstorm/scripts/parse_verdicts.py {output_dir}/brainstorm/gemini_review_of_codex.md {output_dir}/brainstorm/codex_review_of_gemini.md
   ```
   This outputs JSON with `n_agree`, `n_disagree`, `n_insufficient`, `n_total`, `contention_score`.

2. **Guard**: If `n_total = 0`, warn the user and default to `contention_score = 0.0` (stay at medium).

3. **Decision matrix**:

   | Condition | Escalation | Effect |
   |---|---|---|
   | `contention_score < 0.30` | Stay **medium** | Proceed to Step 1c (Critical Editor) |
   | `0.30 ≤ contention_score < 0.50` | Escalate to **high** | Add Step 1b-ev + Step 1b+ + Step 1c (Adversarial Critic) |
   | `contention_score ≥ 0.50` | Escalate to **deep** | Add Step 1b-ev + Step 1b+ + Step 1b-deep + Step 1c (Adversarial Critic Enhanced — see Step 1c role definitions) |

4. **Reuse guarantee**: All existing artifacts (brainstorm, reviews) are preserved. Escalation only **adds** steps; it never re-runs completed steps.

5. **Log** to `brainstorm/escalation_analysis.md`:
   ```
   ## Depth Escalation Analysis

   **Original depth**: auto (started as medium)
   **Verdict counts**: AGREE={n}, DISAGREE={n}, INSUFFICIENT={n}, Total={n}
   **Contention score**: {score:.2f}
   **Decision**: {Remained at medium / Escalated to high / Escalated to deep}
   **Rationale**: {1-2 sentence explanation}
   **Top contested ideas**: {list top 3 by disagreement intensity}
   ```

**T13: Research Direction Document**

8-section structured document produced by Step 0a. Combines user input (Phase 1 Core Framing dialogue) with literature survey (Phase 2 OpenAlex + WebSearch). Used as the foundational artifact for the entire brainstorm pipeline.

**Sections:**

1. **Research Question** — single-sentence refined question (blockquote)
2. **Motivation & Context** — why this matters, what gap it addresses (2-3 paragraphs)
3. **Hypothesis** — falsifiable statement or expected pattern (blockquote)
4. **Expected Results** — what confirms/refutes the hypothesis (specific metrics)
5. **Prior Work** — 5-10 key references as table (Paper, Year, Cited, Relevance)
   - **5a. Methodological Landscape** — dominant approaches, strengths, limitations (2-3 paragraphs)
6. **Methodology Candidates** — 2-3 approaches as table (Approach, Description, Pros, Cons, Feasibility)
7. **Success Criteria** — concrete, measurable evaluation criteria
8. **Constraints & Scope** — In Scope / Out of Scope / Resource Constraints

**Metadata footer**: Original prompt, domain, document version, Phase 2 source count.

**Downstream consumers**: Step 0b (persona casting), Step 0c (weight signals), Step 0d (pre-flight baseline), Step 1a (brainstorm grounding), Step 1c/1-max-d (question fidelity check).
