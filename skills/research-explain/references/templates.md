# Research Explain — Reusable Templates

> This file contains extracted template definitions referenced from the main SKILL.md.
> Read the relevant section when directed by a pointer in SKILL.md.

---

## T1: Audience Weight Defaults

Default scoring weights per audience level (used as baseline in Step 0 and Step 0a):

| Audience | clarity | accuracy | depth | accessibility | completeness | engagement |
|---|---|---|---|---|---|---|
| `general-public` | 0.25 | 0.15 | 0.10 | 0.25 | 0.10 | 0.15 |
| `high-school` | 0.22 | 0.18 | 0.12 | 0.20 | 0.12 | 0.16 |
| `undergraduate` | 0.20 | 0.20 | 0.15 | 0.15 | 0.15 | 0.15 |
| `phd-student` | 0.15 | 0.25 | 0.20 | 0.10 | 0.20 | 0.10 |
| `researcher` | 0.10 | 0.25 | 0.25 | 0.05 | 0.25 | 0.10 |
| `expert` | 0.05 | 0.30 | 0.25 | 0.05 | 0.30 | 0.05 |

For free-text audiences: Use `phd-student` as the baseline, then adjust in Step 0a based on the audience description.

---

## T2: Step 0a — Adaptive Weight Recommendation (Full Procedure)

> Read this section when Step 0a runs (i.e., when `--weights` was NOT explicitly provided).

### Signal Detection Table

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

### Procedure

1. **Analyze the concept and audience** for signals from the table above.
2. **Generate recommended weights**: Starting from the audience baseline (T1), apply adjustments based on detected signals:
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
     "weights": { "<chosen weights>" },
     "_meta": {
       "method": "<adaptive-recommended|audience-default|custom>",
       "domain": "<detected domain>",
       "audience": "<detected audience>",
       "audience_defaults": { "<original audience baseline>" },
       "signals_detected": ["counterintuitive concept", "common misconceptions", "..."],
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

---

## T3: explanation.md — Output Template Structure

> Read this section when generating `explain/explanation.md` in Step 2.
> Word count targets: `low`: 200-500 w | `medium`: 1,000-2,000 w | `high`: 3,000-5,000 w | `max`: 5,000-10,000 w

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

---

## T4: Output File Trees by Depth

> Reference when documenting expected output structure.

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
