# Evaluation Report: Single-Model vs MAGI Multi-Model Brainstorming

**Date:** 2026-02-26
**Task:** Discovering Unknown Damping Functions from Noisy Oscillator Data
**Evaluation Method:** Blind test evaluated by MAGI (`research-brainstorm --depth hard`)

> **Experiment Metadata**
>
> | Key | Value |
> |-----|-------|
> | **Type** | Qualitative Case Study (N=1) |
> | **Domain** | Physics — Nonlinear Dynamics / System Identification |
> | **Evaluator** | MAGI (Blind LLM-as-judge, `--depth high`) |
> | **Compute Ratio** | ~7:1 (MAGI pipeline vs single-model call) |
> | **Self-Evaluation** | Yes — see [Limitations](#limitations--threats-to-validity) |
> | **Reproducibility** | Full — see [Reproduce This Experiment](#reproduce-this-experiment) |

---

## Experiment Design

### Prompt

All four sources received an identical prompt asking to brainstorm 5-7 diverse approaches for discovering the unknown damping function $f(\dot{x})$ in:

$$
m\ddot{x} + f(\dot{x}) + kx = 0
$$

given noisy displacement data (1 kHz, 10 s, $\sigma = 0.05$). Each approach required: method name, mathematical formulation, implementation sketch, strengths, weaknesses, and expected output.

Full prompt: [`prompt.md`](./prompt.md)

### Sources

| Source | Model | Approach |
|--------|-------|----------|
| Single | Claude (Opus 4.6) | Direct response to the prompt |
| Single | Gemini (gemini-3.1-pro-preview) | Direct response to the prompt |
| Single | Codex (gpt-5-codex) | Direct response to the prompt |
| Multi | MAGI (`research-brainstorm --depth hard`) | Gemini + Codex parallel brainstorm → cross-review → adversarial debate → Claude synthesis |

### Environment & Baselines

| | Claude | Gemini | Codex | MAGI |
|---|---|---|---|---|
| **Model ID** | `claude-opus-4-6` | `gemini-3.1-pro-preview` | `gpt-5-codex` | Gemini + Codex + Claude |
| **Date** | 2026-02-26 | 2026-02-26 | 2026-02-26 | 2026-02-26 |
| **System prompt** | None (raw prompt) | None (raw prompt) | None (raw prompt) | Persona-augmented (see below) |
| **Temperature** | Default | Default | Default | Default |
| **Model calls** | 1 | 1 | 1 | ~7 (3 Gemini + 3 Codex + 1 Claude synthesis) |
| **Output size** | ~18.8 KB (7 approaches) | ~9.7 KB (6 approaches) | ~6.8 KB (6 approaches) | ~15.5 KB (7 approaches) |
| **Plugins/tools** | None | None | None | MCP (gemini-cli, codex-cli) |

**Note on MAGI's prompt flow:** Single models received the raw prompt directly. MAGI's pipeline prepended expert personas to each model call and included iterative refinement (cross-review, adversarial debate). This means MAGI had both more compute and a structurally different prompt flow — see [Limitations](#limitations--threats-to-validity).

### Evaluation

The four outputs were anonymized as File 1-4 and evaluated via a separate MAGI `research-brainstorm --depth hard` session. Two evaluator personas independently scored each file, then cross-reviewed each other's scores and debated disagreements before Claude synthesized final scores.

### Scoring Weights (Physics Domain)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Novelty | 0.30 | Originality of approaches and creative combinations |
| Feasibility | 0.15 | Implementation practicality on a standard laptop |
| Impact | 0.25 | Potential to actually solve the stated problem |
| Rigor | 0.20 | Mathematical correctness and physical soundness |
| Scalability | 0.10 | Generalizability to related problems |

---

## Results

### Final Rankings

| Rank | Source | Score | # Approaches | Code? | Unique Contribution |
|------|--------|------:|:------------:|:-----:|---------------------|
| **1st** | **MAGI** | **90** | 7 | No | Classical physics diagnostics + modern ML pipeline |
| 2nd | Claude | 84 | 7 | Yes | PINN with Gumbel-Softmax model selector |
| 3rd | Codex | 80 | 6 | No | Odd-symmetry Neural ODE constraint |
| 4th | Gemini | 67 | 6 | No | Accessible high-level overview |

### Score Breakdown

| Dimension | MAGI | Claude | Codex | Gemini |
|-----------|-----:|-------:|------:|-------:|
| Novelty (×0.30) | **27.8** | 25.5 | 24.0 | 18.8 |
| Feasibility (×0.15) | 12.4 | **12.4** | 12.0 | 10.1 |
| Impact (×0.25) | **22.5** | 21.3 | 19.4 | 17.5 |
| Rigor (×0.20) | **18.0** | 17.0 | 17.0 | 13.5 |
| Scalability (×0.10) | **8.5** | 7.8 | 7.5 | 6.5 |
| **Total** | **89.2** | **84.0** | **79.9** | **66.4** |

```
MAGI    ████████████████████████████████████████████████████████████████████████████████████████░░  90
Claude  ████████████████████████████████████████████████████████████████████████████████████░░░░░░  84
Codex   ████████████████████████████████████████████████████████████████████████████████░░░░░░░░░░  80
Gemini  █████████████████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░  67
        0    10    20    30    40    50    60    70    80    90   100
```

---

## Analysis

### What MAGI Did Differently

MAGI's output stood out in three key areas that no single model produced:

**1. Classical Physics Diagnostics (Unique to MAGI)**

Harmonic Balance and Hilbert Envelope Analysis — two zero-derivative rapid diagnostic methods — appeared only in the MAGI output. These leverage fundamental oscillator physics to classify damping type in seconds, before any heavy computation. No single model proposed this "diagnose first, compute later" strategy.

- Harmonic Balance: Extract $c_{eq}(A)$ from logarithmic decrements → constant = viscous, linear in $A$ = quadratic
- Hilbert Envelope: $\ln A(t)$ linear → exponential decay (viscous); $1/A(t)$ linear → algebraic decay (quadratic)

**2. Staged Pipeline Architecture**

MAGI organized approaches into a coherent 4-stage pipeline with realistic time budgets:

```
Stage 1: Rapid Diagnostics    < 1 min    (Hilbert, Harmonic Balance)
Stage 2: Symbolic Discovery    < 10 min   (WSINDy)
Stage 3: Validation            < 30 min   (Energy Balance, AIC/BIC)
Stage 4: Fallback              1-4 hours  (Neural ODE, GP, Bayesian)
```

Single-model outputs listed methods independently without an integrated decision framework.

**3. Noise-Aware Method Selection**

MAGI correctly identified numerical differentiation as the central challenge at $\sigma = 0.05$ and consistently avoided second-derivative methods. The WSINDy weak formulation was positioned as the primary discovery tool — not just one option among many.

### Where MAGI Struggled

MAGI was not universally superior. Each single model produced ideas or qualities that MAGI's synthesis missed:

| Gap | Detail | Which Model Won |
|-----|--------|-----------------|
| **No runnable code** | MAGI produced zero code snippets. Claude provided working examples for every approach (pysindy, dynesty, torchdiffeq, PySR, sklearn GP). A practitioner could start coding immediately from Claude's output but would need to write everything from scratch using MAGI's. | Claude |
| **Missing novel architectures** | Claude's PINN with Gumbel-Softmax model selector (differentiable discrete model selection via temperature annealing) and Codex's odd-symmetry constraint $f_\theta(v) = g_\theta(v) - g_\theta(-v)$ were creative, physics-informed neural network designs that did not appear in MAGI's synthesis. The cross-review and debate process filtered these out — likely because the Codex persona prioritized classical feasibility over neural network novelty. | Claude, Codex |
| **Accessibility** | MAGI's output assumed an expert-level reader familiar with nonlinear dynamics and sparse regression. Gemini's response was written for a broader engineering audience, making it more suitable as a teaching or introductory resource. | Gemini |
| **Prompt fairness** | MAGI's pipeline included persona augmentation, cross-review, and adversarial debate — structural advantages not available to single models. This is a feature of the system, but it means the comparison is not compute-equivalent (see [Limitations](#limitations--threats-to-validity)). | N/A |

### Key Evaluator Observations

The evaluation process itself (conducted via MAGI) produced these consensus points:

1. **WSINDy recognition is a quality signal.** Files that correctly identified WSINDy (weak-form SINDy) as state-of-the-art for noisy ODE discovery scored significantly higher.
2. **Pointwise $\ddot{x}$ at $\sigma=0.05$ is catastrophic.** Methods relying on second derivatives from noisy data were flagged as likely failures. MAGI avoided this consistently; Claude proposed it in 2 of 7 approaches.
3. **Code matters for feasibility, but strategy matters more.** Claude's code coverage boosted its feasibility score, but MAGI's superior methodological strategy earned higher overall marks.

### Debated Points During Evaluation

| Issue | Gemini Evaluator | Codex Evaluator | Resolved Score |
|-------|-----------------|-----------------|----------------|
| MAGI overall | 93 (theoretical mastery) | 85.3 → 88 (revised up) | **90** |
| Gemini overall | 64 (PySR+ODE catastrophic) | 69.3 (shallow but serviceable) | **67** |
| Code omission penalty | Secondary to formulation | Essential for reproducibility | Both valid; audience-dependent |

---

## Limitations & Threats to Validity

This experiment is a **qualitative case study (N=1)**, not a statistically significant benchmark. The following limitations should be considered when interpreting the results:

### Self-Evaluation Bias

The evaluation was conducted using MAGI itself. While the outputs were anonymized (File 1-4) and the evaluator personas did not know which file came from which source, MAGI's evaluation pipeline (Gemini + Codex cross-review + Claude synthesis) may share structural biases with MAGI's generation pipeline. Specifically:

- The evaluator personas may favor the multi-stage workflow structure that MAGI produces
- LLMs may recognize stylistic patterns from their own outputs despite anonymization
- The scoring rubric (weighted toward Novelty and Impact) may systematically favor diverse, synthesized outputs

**Mitigation:** We publish all raw outputs and the evaluation prompt so readers can form their own judgments. An independent evaluation by a non-MAGI judge is planned for a future release.

### Compute Asymmetry

MAGI used approximately **7 model calls** (3 Gemini + 3 Codex + 1 Claude synthesis) across its pipeline, while each single model received **1 call**. This is not a fair compute comparison — it is a comparison of *system architectures*. MAGI's advantage may partly stem from simply having more inference budget rather than from the cross-verification process itself.

**What this does NOT prove:** That MAGI is "smarter" than any single model. A single model with a self-critique loop (e.g., Claude asked 3 times to brainstorm, review, then synthesize) might close the gap. We have not tested this baseline.

### Domain Narrowness

This experiment tested a single physics problem (damped oscillator equation discovery). The results do not generalize to:
- Other domains (AI/ML, statistics, mathematics)
- Other task types (coding, writing, planning)
- Other difficulty levels

### Single Trial

All results are from a single run (N=1) with default temperature settings. LLM outputs are non-deterministic; repeating the experiment may yield different scores. We do not report confidence intervals.

### Prompt Fairness

Single models received the raw prompt. MAGI's internal pipeline augmented the prompt with expert personas and iterative refinement stages. This structural difference is part of MAGI's design, but it means the comparison is between "raw model" and "model + orchestration framework" — not between models at equal footing.

---

## Conclusions

1. **MAGI outperformed all single models** by +6 points over the next best (Claude). The multi-model process produced a qualitatively different response — not just "more ideas" but a fundamentally better-structured approach that combines classical physics insight with modern ML.

2. **The gap is methodological, not quantitative.** MAGI's advantage isn't having more approaches (7 vs 6-7), but having the *right combination* of approaches organized into a principled workflow. No single model independently proposed both rapid classical diagnostics and modern surrogate-assisted inference.

3. **Single models have complementary strengths.** Claude excelled at implementation detail, Codex at mathematical elegance, Gemini at accessibility. MAGI's synthesis captured the theoretical and strategic strengths but missed the implementation detail (no code) and some novel formulations from individual models.

4. **The evaluation was itself an example of MAGI's value.** The blind evaluation used the same multi-model cross-review and adversarial debate process, producing nuanced scoring that caught errors (Codex retracting a false criticism after Gemini pointed out the math) and resolved genuine disagreements through structured debate.

5. **This is an N=1 case study with known biases.** The self-evaluation, compute asymmetry, and domain narrowness mean these results should be treated as an illustrative example of MAGI's potential, not as a definitive benchmark. We encourage readers to reproduce the experiment and draw their own conclusions.

---

## Reproduce This Experiment

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with MAGI plugin installed
- MCP servers: `gemini-cli`, `codex-cli` (see [main README](../../README.md#get-started))
- API keys for Anthropic, Google AI, and OpenAI

### Steps

**1. Run single-model baselines** (one prompt, three models):

```bash
# In Claude Code, send the contents of examples/damped_oscillator_comparison/prompt.md
# to each model individually and save the responses.

# Claude: paste the prompt directly in Claude Code
# Gemini: use gemini-cli or Google AI Studio
# Codex: use codex-cli or OpenAI Playground
```

**2. Run MAGI brainstorm:**

```
/magi-researchers:research-brainstorm --depth high "Discovering unknown damping function f(x_dot) in m*x_ddot + f(x_dot) + k*x = 0 from noisy displacement data (1kHz, 10s, sigma=0.05). Brainstorm 5-7 approaches ranging from classical to modern ML." --domain physics
```

**3. Anonymize and evaluate:**

```
# Strip model-identifying information from all outputs
# Run evaluation via MAGI:
/magi-researchers:research-brainstorm --depth high "Evaluate these 4 anonymized responses to a damped oscillator equation discovery problem. Score each on Novelty, Feasibility, Impact, Rigor, Scalability (0-10)." --domain physics
```

### Estimated Cost & Time

| Step | Time | Estimated Cost |
|------|------|---------------|
| Single-model baselines (3 models) | ~5 min | ~$0.30 |
| MAGI brainstorm (`--depth high`) | ~10 min | ~$0.80 |
| MAGI evaluation (`--depth high`) | ~10 min | ~$0.80 |
| **Total** | **~25 min** | **~$1.90** |

Costs are approximate and depend on model pricing at the time of execution.

---

## Files

| File | Description |
|------|-------------|
| [`prompt.md`](./prompt.md) | Identical prompt given to all models |
| [`claude.md`](./claude.md) | Claude single-model output |
| [`gemini.md`](./gemini.md) | Gemini single-model output |
| [`codex.md`](./codex.md) | Codex single-model output |
| [`magi_blind.md`](./magi_blind.md) | MAGI output (anonymized for blind evaluation) |
| [`magi_synthesis.md`](./magi_synthesis.md) | MAGI output (full, with cross-review and debate traces) |
