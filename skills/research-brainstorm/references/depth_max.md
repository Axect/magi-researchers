# Depth Max: MAGI-in-MAGI Pipeline

> This file contains the `--depth max`-specific steps. Read this file when `--depth max` is active.
> These steps (1-max-a through 1-max-d) replace Steps 1a/1b/1b+/1c from the main SKILL.md.

### Step 1-max-a: Layer 1 — Parallel Persona Subagents

> **If `--depth` is not `max`**: Skip Steps 1-max-a through 1-max-d entirely. Use Steps 1a/1b/1b+/1c instead.

Spawn **N Task subagents simultaneously** (one per persona, `subagent_type: general-purpose`). Each subagent receives the persona definition and executes a self-contained mini-MAGI pipeline:

**Each subagent prompt includes:**
1. **Containment directive** (MUST be first): `"DO NOT create any directories. DO NOT run Step 0 setup. All directories already exist. Write files ONLY to the exact absolute paths listed below. Do NOT interpret SKILL.md setup instructions as applicable to you."`
2. The **absolute `{output_dir}` path** and the **absolute persona subdirectory path** (`{output_dir}/brainstorm/persona_{i}/`)
3. The persona definition (name, expertise, guiding question, primary lens) from `brainstorm/personas.md`
4. The research topic and domain template (if available)
5. If `brainstorm/briefing_persona_{i}.md` exists: the **absolute path** to the persona-specific briefing file, with instruction: "Include this literature briefing as context for brainstorm steps A and B — let it inform but not constrain ideation."
6. The following 5-step execution plan:
7. The active mode flags: `--claude-only: true/false` and/or `--substitute: [list]`. When `--claude-only` is active or a relevant agent is substituted, the subagent must replace MCP calls A/B and C+D with the corresponding Agent sub-subagents as described in the `> **If --claude-only**:` blocks above. When only one agent is substituted (e.g., `"Gemini -> Opus"`), replace only that agent's calls; use the other agent's MCP tool normally.

   **A. Gemini Brainstorm** — Call `mcp__gemini-cli__brainstorm` with the persona's viewpoint. If `brainstorm/briefing_persona_{i}.md` exists, include via `@{output_dir}/brainstorm/briefing_persona_{i}.md`. Save to `brainstorm/persona_{i}/gemini_ideas.md`.

   **B. Codex Brainstorm** — Call `mcp__codex-cli__brainstorm` with the persona's viewpoint. If `brainstorm/briefing_persona_{i}.md` exists, include via `@{output_dir}/brainstorm/briefing_persona_{i}.md`. Save to `brainstorm/persona_{i}/codex_ideas.md`.

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

---

### Step 1-max-b: Layer 1 — Output Collection

0. **Post-completion path audit** (per Subagent Containment Rule):
   - `Glob` for `outputs/*_v*/` and verify only the expected output directory exists for this session's date/topic.
   - Check for `brainstorm/` in the project root (`Glob` for `brainstorm/`).
   - If spurious directories are found: delete them. If they contain artifacts that should have been in `{output_dir}`, move the files first, then delete the directory.
1. Use Glob to verify that all N `brainstorm/persona_{i}/conclusion.md` files exist.
   - If any are missing, re-spawn the failed subagent(s) (maximum 1 retry per subagent). If the retry also fails, proceed with the available N-1 (or fewer) persona outputs and note the gap in the synthesis. Do not abort the pipeline for a single persona failure.
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

---

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

**Phase B+ — Evidence Anchoring (meta-level):**

Apply §EvidenceAnchoring and **T11** to the meta-level disagreements identified in Phase B:

1. Read `brainstorm/meta_disagreements.md` and extract the 3 disputed claims.
2. For each claim, run OpenAlex + WebSearch per **T11** (execute searches in parallel).
3. Save to `brainstorm/meta_claim_evidence.md` using the **T11** format.

This provides real-world evidence for the Layer 2 adversarial debate, grounding cross-persona disputes in published literature.

**Phase C — Consolidate Debate Context + Adversarial Debate:**

Before the debate calls, create consolidated context files (each containing exactly what the opposing model needs):
- `brainstorm/debate_context_for_gemini.md` — concatenate `brainstorm/meta_disagreements.md` + `brainstorm/meta_review_codex.md` + (if exists) `brainstorm/meta_claim_evidence.md`
- `brainstorm/debate_context_for_codex.md` — concatenate `brainstorm/meta_disagreements.md` + `brainstorm/meta_review_gemini.md` + (if exists) `brainstorm/meta_claim_evidence.md`

Then execute the debate calls **simultaneously**. Each call includes: `[Meta-Reviewer]` context, consolidated debate context file, **T3** debate framework, and instruction to cite evidence from `meta_claim_evidence.md` when defending or conceding.

- **Gemini**: `mcp__gemini-cli__ask-gemini`, `model: "gemini-3.1-pro-preview"`, ref: `@{output_dir}/brainstorm/debate_context_for_gemini.md` → Save to `brainstorm/meta_debate_gemini.md`
- **Codex**: `mcp__codex-cli__ask-codex`, `model: "gpt-5.4"`, ref: `@{output_dir}/brainstorm/debate_context_for_codex.md` → Save to `brainstorm/meta_debate_codex.md`

> **If `--claude-only`**: Replace both debate calls with two Agent subagents (simultaneously), per **T6**:
> - **Subagent A** (T1-CD): Read `brainstorm/debate_context_for_gemini.md`. Apply **T3** debate framework. Cite real evidence when defending or conceding. Save to `brainstorm/meta_debate_gemini.md` per **T5**.
> - **Subagent B** (T1-AC): Read `brainstorm/debate_context_for_codex.md`. Apply **T3** debate framework. Cite real evidence when defending or conceding. Save to `brainstorm/meta_debate_codex.md` per **T5**.

---

### Step 1-max-d: Layer 3 — Final Enriched Synthesis

**MELCHIOR Active Synthesis Protocol** (`--depth max` — Philosopher-Arbiter):

You are MELCHIOR as Philosopher-Arbiter across three layers. Before reading ANY model output files:

**0. Prior Declaration** (mandatory, FIRST action):
Write in synthesis.md: "**Opus Prior (Pre-Evidence)**: Based on the topic '{topic}' and domain '{domain}' alone, I expect the top 2-3 findings to be: [list]. I will record which are confirmed, overturned, or absent after synthesis."
Do NOT open any persona conclusion, meta-review, or debate file until this prior is saved.

After reading all evidence, you are REQUIRED to:
(a) Resolve at least one inter-layer contradiction explicitly — name the contradicting claims and your resolution.
(b) Add one theoretical context or historical precedent not raised by any persona (**[MELCHIOR]** marker).
(c) Write a "**Prior vs. Posterior**" section documenting which prior expectations were confirmed, overturned, and what was unexpected.

Apply **Convergence Interrogation** and **Intertextual Addition** as defined below.

**Convergence Interrogation** (mandatory for `--depth max`):
For each finding that appears in both models' outputs, classify as:
- **Type A convergence**: Models arrived via different reasoning paths or evidence. No confidence adjustment.
- **Type B convergence**: Both models cite the same named source, method, or prior result. Apply confidence note: "Type B convergence — shared training reference, not independent validation."
- **Type C convergence (False Consensus)**: Both models agree, but neither provides a concrete mechanism, independent evidence, or specific scenario — agreement is based on surface plausibility or deference to the other model. Apply per §AntiConsensus: confidence is automatically downgraded one level (High → Medium, Medium → Low). If a Type C finding ranks in the Top 3, MELCHIOR MUST construct an adversarial objection against it regardless of depth level.
- **Type D convergence (Shared Blind Spot)**: All models/personas agree on a **methodological choice** (metric definition, null model, analytical framework, measurement protocol) that none independently derived or validated — they adopted it as a shared unexamined assumption. Type D triggers a mandatory **methodological audit**: MELCHIOR must either (a) provide independent justification for the shared assumption (cite a derivation, validation study, or limiting-case argument), or (b) flag it as an unvalidated assumption with confidence downgrade one level. **Type D detection heuristic**: For each top finding, ask "What metric or method do ALL sources use without questioning? Could a different reasonable metric yield a contradictory result?" If yes, classify as Type D.

**Intertextual Addition** (mandatory, all depths):
You MUST add at least one perspective, connection, or counter-argument from your own knowledge that no model raised. Mark with **[MELCHIOR]**. This is NOT derived from model outputs — it is your independent intellectual contribution as the third MAGI personality.

1. Read all available documents:
   - `weights.json`, `personas.md`, `research_direction.md`
   - All N `persona_{i}/conclusion.md` files
   - `meta_review_gemini.md`, `meta_review_codex.md`
   - `meta_debate_gemini.md`, `meta_debate_codex.md`
   - `meta_claim_evidence.md` (created by Phase B+ evidence anchoring)
   - `preflight_context.md` (full unfiltered literature context for MELCHIOR's direct reference)

**Scope Divergence Check** (mandatory for `--depth max`):
Compare scope declarations from Step 1-max-a model outputs. If personas interpreted the question with substantially different scope:
- Note in synthesis: "**Scope Note**: [Persona A] interpreted this as [X]; [Persona B] interpreted this as [Y]. This synthesis covers both interpretations — reply to narrow if needed."
- If scopes are aligned: omit this section.

2. Load `weights.json` and check `_meta.method`:
   - **If `method` is `"holistic"`**: Use holistic ranking — Claude reads all persona conclusions, meta-reviews, and debate resolutions, then directly ranks research findings based on integrated expert judgment. **No numeric dimension scores are computed.** For each finding, provide a **Ranking Rationale** (3-5 sentences) that references specific persona arguments, cross-persona consensus/disagreement, and debate outcomes. Explicitly compare against adjacent-ranked findings.
   - **If `method` is not `"holistic"`**: Compute **weighted scores** for each research finding (same 0-10 rating per dimension, weighted sum).
3. Produce an **enriched `brainstorm/synthesis.md`** — a research analysis that preserves the core scientific reasoning, mathematical formulations, testable predictions, and falsification conditions from persona conclusions. The synthesis must explain WHY each approach works (mechanism), not just WHAT to do (action plan). Structure:
   1. **Personas Used** — table of N personas with name, expertise summary, and primary lens
   2. **Scoring Method** — document the ranking approach (holistic or weighted with `_meta.method`)
   3. **Top Research Findings** (Core Findings, Top 5) — ranked, 300-600 words each. For each:
      - **(a) Mechanism Narrative** (150-250 words, continuous prose, REQUIRED)
      - **(b) Mathematical Core & Predictions** — preserve key equations, numerical predictions with error bars
      - **(c) Falsification Criteria** — what result would disprove this finding?
      - **(d) T7 Summary Footer** — Motivation, Expected Effects, Side Effects, Key Evidence, Confidence, [MELCHIOR] Judgment
      - **(e) Ranking Rationale** — holistic (3-5 sentences) or weighted (score breakdown)
      - **(f) [MELCHIOR] Verdict** — Endorse/Revise/Reject/Demote with reason
      - Which personas supported this finding
   4. **Appendix: Additional Findings** — structured summary table for rank 6+
   5. **Cross-Persona Consensus** — ideas where 3+ personas independently converged
   6. **Unique Contributions** — valuable ideas from a single persona
   7. **Debate Resolution** — for each of the 3 debated disagreements
   8. **Cross-Validation Connections** — cross-persona convergence, contradictions, complementary mechanisms
   9. **Emergent Insights** — patterns visible only from the cross-persona vantage point
   10. **Prior vs. Posterior** — confirms/overturns Prior Declaration
   11. **Synthesis Epilogue (T8)** — Research Gaps, Non-Recommendations, Next Three Steps
   12. **Recommended Path Forward** — grounded in multi-persona analysis
   13. **MAGI Process Traceability** — table mapping findings to source persona and artifact

4. **[MELCHIOR] Comprehensive Self-Review** (mandatory, revision trigger):

   Evaluate the synthesis on five axes (2-4 sentences + verdict PASS/REVISE each):

   **(a) Question Fidelity** — Do top findings answer the research question, hypothesis, and expected results from `brainstorm/research_direction.md` (Sections 1, 3, 4)? Use `.workspace.json` `original_topic` for root drift detection.
   **(b) Inter-Finding Coherence** — Contradictions acknowledged or unintentional?
   **(c) Aggregate Mechanism Audit** — N/5 novel mechanisms vs. restatements. Flag if N < 2.
   **(d) Causal vs. Diagnostic Balance** — Count Intervention/Ablation/Null vs. Empirical/Design/Review steps. Mandatory REVISE if no causal steps.
   **(e) Blind Spot Confession** — 1-2 unaddressed questions a domain expert would ask.

   **Revision protocol**: If any axis yields REVISE, fix before proceeding. Update verdict to PASS with note.

5. After self-review, verify (mechanical checklist):
   - [ ] Each top finding explains WHY (causal mechanism), not just WHAT
   - [ ] **Mechanism Depth Test** applied
   - [ ] Each top finding has at least one equation or numerical prediction
   - [ ] Operational content below 15%
   - [ ] At least one **[MELCHIOR]** marker
   - [ ] Each top finding has (f) [MELCHIOR] Verdict
   - [ ] Prior Declaration with >= 2 specific mechanisms
   - [ ] Convergence Interrogation Type A/B/D classification
   - [ ] `meta_claim_evidence.md` acknowledged in synthesis
   - [ ] `preflight_context.md` referenced by MELCHIOR
   If any check fails, revise before finalizing.
6. Save to `brainstorm/synthesis.md`.

**Retroactive Question Crystallization** (always, all depths):
After completing the ranked synthesis, examine the top 5 findings and identify the research question they collectively answer. If this crystallized question differs substantively from the Research Direction Document's Section 1 (Research Question):
- Append a "**Note on Question Scope**" section: "The brainstorm converged around: *'[crystallized question]'*. This is [narrower/broader/differently-framed] than your original question. If you intended the original framing, consider re-running with scope: [adjusted scope]."
- If the crystallized question matches the original: omit this section entirely.
