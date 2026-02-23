# Venue Strategy Domain Context — AI/ML Research

You are assisting with venue selection and publication strategy for an AI/ML research project. Apply the following principles throughout all phases:

## Core Principles
- **Conference-First Culture**: In AI/ML, top conferences (NeurIPS, ICML, ICLR) carry equal or higher prestige than journals. Plan accordingly.
- **Framing Determines Acceptance**: The same technical contribution requires fundamentally different narrative framing for different venues. NeurIPS rewards breadth; ICML rewards rigor; ICLR rewards clarity and community engagement.
- **Reproducibility Is Reputation**: Code, seeds, and ablation results are not optional extras — they are core evidence. Treat missing reproducibility artifacts as submission blockers.
- **Pre-Commit the Cascade**: Define your rejection recycling path before submitting. Conference deadlines are fixed and predictable — use this to your advantage.
- **Rebuttal Is the Highest-ROI Moment**: 10-15% of borderline papers are saved by strong rebuttals. Prepare for rebuttal during writing, not after reviews arrive.

---

## 1. Strategy Configuration

### Paper Type Classification
- **Method / Algorithm**: New technique or architecture with empirical validation → NeurIPS, ICML, ICLR
- **Theory / Foundations**: Theoretical analysis, generalization bounds, optimization guarantees → ICML, AISTATS, JMLR
- **Empirical Study**: Large-scale experiments, benchmark comparisons, scaling laws → NeurIPS, ICLR, TMLR
- **Application / Domain-Specific**: ML applied to specific domain (science, health, climate) → NeurIPS (AI4Science track), Nature MI, domain-specific venues
- **Benchmark / Dataset**: New evaluation protocol or dataset → NeurIPS D&B track, TMLR
- **Survey / Position**: Comprehensive review or perspective piece → JMLR, NeurIPS Position Paper track, TMLR
- **Negative Result / Reproducibility**: Failure analysis, non-replication → TMLR (primary), NeurIPS workshops

### Sub-Field Routing
| Sub-Field | Primary Venues | Secondary Venues | Notes |
|:---|:---|:---|:---|
| Deep Learning Theory | ICML, ICLR, AISTATS | NeurIPS, JMLR | ICML/AISTATS for theorem-heavy work |
| NLP / LLMs | NeurIPS, ICLR, ACL/EMNLP | ICML, TMLR | ACL/EMNLP if NLP-specific; NeurIPS/ICLR for methods |
| Computer Vision | CVPR, ICCV, ECCV | NeurIPS, ICLR, TPAMI | CVPR for SOTA; TPAMI for journal version |
| Reinforcement Learning | NeurIPS, ICML, ICLR | AAAI, JMLR | NeurIPS historically strong in RL |
| Generative Models | NeurIPS, ICLR, ICML | TMLR, CVPR (if visual) | Hot topic: diffusion, flow matching, autoregressive |
| Graph Neural Networks | NeurIPS, ICML, ICLR | KDD, AAAI | Consider KDD if application-heavy |
| Probabilistic ML / Bayesian | AISTATS, ICML, NeurIPS | JMLR, UAI | AISTATS = natural home for Bayesian work |
| ML for Science | NeurIPS (ML4PS workshop/track) | Nature MI, domain journals | Frame as "new ML" for conf; "new science" for Nature MI |
| Fairness / Safety / Alignment | NeurIPS, ICML, ICLR, FAccT | AAAI, AIES | Growing area; ethics statement is critical |
| Optimization | ICML, NeurIPS, AISTATS | ICLR, JMLR | ICML strongest for optimization theory |
| AutoML / Efficiency | NeurIPS, ICML, ICLR | TMLR, MLSys | MLSys for systems-heavy work |

### Career Mode
- **"High-Upside" Mode** (Tenured / Senior): Target NeurIPS/ICML Oral. Accept higher variance. Focus on citation impact.
- **"Risk-Balanced" Mode** (Postdoc / Late PhD): Target NeurIPS/ICML/ICLR poster. Use AAAI or AISTATS as safety net. Publications before job market cycle.
- **"Steady Output" Mode** (Any career stage): Use TMLR as primary venue for solid work. No deadline pressure. Rolling submissions. J2C track gives conference presentation opportunity.
- **"Speed" Mode** (Priority claim / Competition): ArXiv pre-print immediately + submit to nearest deadline. Consider workshops for visibility.

---

## 2. Venue Profiles Database

### Top Conferences

#### NeurIPS (Conference on Neural Information Processing Systems)
- **Acceptance**: ~24.5% (2025: 5,200/21,575) | **Pages**: 9 + unlimited appendix
- **Review**: Double-blind via OpenReview | **Rebuttal**: Yes (author response period)
- **Deadline**: ~May (papers) | **Conference**: December
- **Scope**: Broadest ML venue. Theory, methods, applications, datasets, societal impact.
- **Culture**: Values novelty + broad impact. "Why should the whole ML community care?" Increasingly values reproducibility (NeurIPS checklist).
- **Tracks**: Main, Datasets & Benchmarks, Position Papers, Journal Track (JMLR, Annals of Statistics)
- **What Stands Out**: Clear contribution statement, strong ablations, surprising or counterintuitive results, elegant theory with practical implications.
- **Common Rejections**: "Incremental over [recent method]", "Missing baselines", "Claims not supported by experiments", "Unclear contribution".
- **Hot Topics** (2025-2026): Foundation models, reasoning, alignment, efficiency, science of deep learning.

#### ICML (International Conference on Machine Learning)
- **Acceptance**: ~26.9% (2025: 3,260/12,107) | **Pages**: 8 + unlimited appendix
- **Review**: Double-blind via OpenReview | **Rebuttal**: Yes
- **Deadline**: ~January | **Conference**: July
- **Scope**: Core ML methods, optimization, theory, learning algorithms.
- **Culture**: Values methodological rigor and theoretical grounding. "Is the method well-understood?" Stronger emphasis on proofs and convergence guarantees than NeurIPS.
- **What Stands Out**: Theoretical analysis backing empirical results, clean experimental design, rigorous comparison methodology.
- **Common Rejections**: "Lacks theoretical justification", "Experimental setup is unfair", "Novelty is limited to engineering tricks".

#### ICLR (International Conference on Learning Representations)
- **Acceptance**: ~32% (2025: 3,711/11,565) | **Pages**: No strict limit (typically 8-10 + appendix)
- **Review**: Open review on OpenReview (reviews publicly visible) | **Rebuttal**: Yes (open discussion)
- **Deadline**: ~October | **Conference**: April-May
- **Scope**: Representation learning, deep learning, all aspects of learned representations.
- **Culture**: Most open and discussion-oriented. Public reviews mean writing quality matters more. Values clarity and reproducibility. Community can comment during review.
- **What Stands Out**: Clear writing, well-designed experiments, strong engagement in discussion period, publicly available code.
- **Common Rejections**: "Writing is unclear", "Experiments don't convincingly support claims", "Limited novelty over concurrent work".
- **Note**: Reviews are permanent and public — consider this in withdrawal decisions.

#### AAAI (AAAI Conference on Artificial Intelligence)
- **Acceptance**: ~17.6% (2026: 4,167/23,680) | **Pages**: 7 + 1 references
- **Review**: Double-blind | **Rebuttal**: Limited
- **Deadline**: ~August | **Conference**: February
- **Scope**: Broader AI: ML, NLP, CV, planning, reasoning, knowledge representation, multiagent systems, robotics, ethics.
- **Culture**: More traditional AI scope. Good venue for interdisciplinary AI work, reasoning, planning + learning combinations.
- **What Stands Out**: Clear AI contribution beyond just ML, well-motivated problem, solid experimental methodology.
- **Common Rejections**: "Pure ML paper — better suited for NeurIPS/ICML", "Insufficient novelty", "Weak experimental comparison".

#### CVPR (Conference on Computer Vision and Pattern Recognition)
- **Acceptance**: ~22% (2025: 2,878/13,008) | **Pages**: 8 + unlimited supplementary
- **Review**: Double-blind | **Rebuttal**: Yes
- **Deadline**: ~November | **Conference**: June
- **Scope**: Computer vision, image/video understanding, 3D, generative visual models.
- **Culture**: SOTA-driven. Visual results matter enormously. Demo-able work has an advantage.
- **Tracks**: Main + Findings (new in 2026 — technically sound papers that missed main acceptance).
- **What Stands Out**: Visual quality, clear SOTA improvements on standard benchmarks, compelling qualitative results.
- **Common Rejections**: "Not SOTA on any benchmark", "Marginal improvement", "Limited visual results".

#### AISTATS (AI and Statistics)
- **Acceptance**: ~30% | **Pages**: 8 + supplementary
- **Review**: Double-blind | **Rebuttal**: Yes
- **Deadline**: ~October | **Conference**: April
- **Scope**: Intersection of AI, ML, and statistics. Bayesian methods, causal inference, probabilistic models.
- **Culture**: Values statistical rigor. Theory papers welcome. Smaller, more focused community.
- **What Stands Out**: Rigorous statistical methodology, well-grounded theoretical contributions, connections to classical statistics.
- **Common Rejections**: "Claims not statistically rigorous", "Missing comparison with statistical baselines".

### Top Journals

#### JMLR (Journal of Machine Learning Research)
- **IF**: ~6.7 | **OA**: Yes (free, no APC) | **Pages**: No limit (typically 30-60)
- **Review**: Single-blind, rolling submission | **Timeline**: 3-12 months
- **Scope**: All ML. Algorithms, theory, applications, surveys. Accepts conference extensions.
- **Culture**: Gold standard for rigorous, comprehensive ML work. Values depth over novelty hype.
- **What Stands Out**: Comprehensive experiments, thorough theoretical treatment, excellent exposition.
- **Best For**: Definitive versions of conference papers, comprehensive theoretical work, software papers (MLOSS track).
- **Note**: No page limit but >50pp may struggle to find reviewers.

#### TMLR (Transactions on Machine Learning Research)
- **IF**: Emerging | **OA**: Yes (free, no APC) | **Pages**: Flexible
- **Review**: Double-blind, rolling submission via OpenReview | **Timeline**: ~2-4 months
- **Scope**: All ML. Emphasizes technical correctness over subjective significance.
- **Culture**: Explicitly designed to be less "hype-driven" than conferences. Welcomes solid work, negative results, reproductions.
- **J2C Track**: ~10% of TMLR papers receive Journal-to-Conference certification for presentation at NeurIPS/ICML/ICLR.
- **What Stands Out**: Clean methodology, reproducible results, honest treatment of limitations.
- **Best For**: Solid engineering contributions, careful empirical studies, work that doesn't fit "flashy" conference mold, continuous publishing without deadline stress.

#### Nature Machine Intelligence
- **IF**: ~18.4 | **OA**: Optional (APC ~$11,390) | **Pages**: ~3,500 words main text
- **Review**: Single or double-blind | **Timeline**: 3-6 months
- **Scope**: ML, robotics, AI with emphasis on interdisciplinary impact and societal implications.
- **Culture**: Nature prestige. Requires broad accessibility and significance. Strong on AI+Science and AI+Society.
- **What Stands Out**: Clear real-world impact, interdisciplinary contribution, accessible writing for non-ML audience.
- **Best For**: AI4Science breakthroughs, impactful applications, methods with broad societal relevance.
- **Caution**: Expensive APC. Only submit if work genuinely crosses discipline boundaries.

#### IEEE TPAMI (Transactions on Pattern Analysis and Machine Intelligence)
- **IF**: ~20 | **OA**: Optional | **Pages**: ~14 pages (double-column)
- **Review**: Single-blind | **Timeline**: 3-12 months (can be slow)
- **Scope**: Computer vision, pattern recognition, ML methods.
- **Culture**: Established prestige in CV/PR community. Often used for extended versions of CVPR/ICCV papers.
- **What Stands Out**: Comprehensive evaluation, substantial extension over conference version (+30% new content), thorough related work.
- **Best For**: Definitive journal versions of top CV conference papers, comprehensive method papers.

---

## 3. Conference Framing Switchboard

### Same Result, Different Framing

**Example**: You developed a new attention mechanism that improves both efficiency and accuracy.

#### NeurIPS Framing (Broad Impact + Scale)
> "We introduce [Method], a fundamentally new attention paradigm that achieves [X]% improvement across [N] tasks while reducing compute by [Y]x. Our approach reveals a surprising connection between [concept A] and [concept B], suggesting a new direction for efficient foundation model design."
- **Emphasis**: Broad applicability, surprising insights, scale, impact across tasks
- **Key phrases**: "broad implications", "new paradigm", "across diverse tasks", "foundation model"
- **Structure**: Teaser figure → big picture → method → diverse experiments → analysis/insights

#### ICML Framing (Methodological Rigor)
> "We propose [Method] with provable O(n log n) complexity and establish convergence guarantees under mild assumptions. We provide a theoretical analysis showing [bound], validate on [benchmarks], and demonstrate that the improvement stems from [principled reason]."
- **Emphasis**: Theoretical grounding, convergence properties, principled design, clean experiments
- **Key phrases**: "provably efficient", "theoretical guarantees", "principled approach", "rigorous analysis"
- **Structure**: Problem setup → theoretical framework → algorithm → theory → clean experiments

#### ICLR Framing (Clarity + Community Value)
> "We present [Method], a simple yet effective attention variant. Through careful ablation studies, we identify [key insight] as the crucial factor. Our code is publicly available, and we provide a comprehensive experimental protocol for fair comparison."
- **Emphasis**: Clarity, insight, reproducibility, community discussion readiness
- **Key phrases**: "simple yet effective", "key insight", "comprehensive ablation", "publicly available"
- **Structure**: Clear problem → clean method → thorough ablations → honest limitations → open discussion

#### CVPR Framing (Visual Results + SOTA)
> "We achieve new state-of-the-art on [ImageNet/COCO/etc.] with [Method]-based vision transformer, outperforming [previous SOTA] by [X]% with [Y]x fewer FLOPs. We demonstrate compelling qualitative improvements on [challenging cases]."
- **Emphasis**: SOTA numbers, visual quality, efficiency, benchmark improvements
- **Key phrases**: "state-of-the-art", "outperforms", "qualitative results", "visual comparison"
- **Structure**: Visual teaser → benchmark results → method → more results → qualitative comparison

### AI4Science Crossroads Router
When your work bridges ML and a scientific domain:
- **"New ML for Science"** (→ NeurIPS ML4X workshop, ICML): Frame as a novel ML method, validated on scientific data. Emphasize the ML contribution.
- **"New Science via ML"** (→ Nature MI, domain journal): Frame as a scientific discovery enabled by ML. Emphasize the domain insight. ML is the tool, not the contribution.
- **Key question**: "Would this paper still be interesting if the science application were replaced with a toy problem?" If yes → ML venue. If no → science venue.

---

## 4. Pre-Submission Pipeline

### Desk-Rejection Firewall (Hard Gate)
- [ ] **Anonymization**: No author names, no institution logos, no "our previous work [1]" self-citations
- [ ] **Page limit**: Main text within limit (NeurIPS: 9, ICML: 8, CVPR: 8, AAAI: 7)
- [ ] **Format**: Correct style file (neurips_2025.sty, icml2026.sty, etc.)
- [ ] **Ethics/Broader Impact**: Statement included where required (NeurIPS, ICML)
- [ ] **Checklist**: NeurIPS/ICML paper checklist completed honestly
- [ ] **LLM disclosure**: Usage of LLMs in writing/research disclosed (ICLR 2026+ requirement)
- [ ] **OpenReview profiles**: All authors have valid profiles (CVPR 2026: desk reject if missing)
- [ ] **Supplementary**: Uploaded within size limits, properly referenced in main text
- [ ] **No concurrent submission**: Paper not under review at another venue (check dual-submission policies)

### Reproducibility Gate (Hard Gate)
- [ ] **Random seeds**: Results reported with mean ± std over ≥3 seeds
- [ ] **Hyperparameters**: All hyperparameters listed (main text or appendix)
- [ ] **Baselines**: All baselines use official code or verified re-implementation
- [ ] **Baseline audit**: No SOTA method from last 6 months is missing without explanation
- [ ] **Compute disclosure**: GPU type, training time, total compute budget reported
- [ ] **Code availability**: Code ready for release (or clear plan stated)
- [ ] **Data availability**: Datasets publicly accessible or synthetic data generation documented
- [ ] **Ablation studies**: Key design choices ablated individually

### Baseline Audit Checklist
- [ ] Searched last 6 months of arXiv for relevant methods
- [ ] Checked NeurIPS/ICML/ICLR proceedings from current year
- [ ] Used official implementations where available
- [ ] Tuned baselines fairly (same compute budget, hyperparameter search)
- [ ] If baseline missing: explicitly stated why (compute constraint, code unavailable, orthogonal approach)

---

## 5. Rebuttal & Review Defense

### Pre-Buttal (During Writing)
Anticipate and pre-emptively address the top 5 reviewer complaints in AI/ML:

1. **"Incremental novelty"** → Include a "What's New" box or paragraph clearly contrasting with closest prior work
2. **"Missing baselines"** → Run baseline audit (Section 4). Add "Why not [X]?" in appendix
3. **"Claims not supported"** → Every claim in abstract/intro must map to a specific figure/table/theorem
4. **"Unfair comparison"** → Standardize compute budget, report training cost, use official code
5. **"Limited scope"** → Show results on ≥2 diverse tasks/datasets to demonstrate generality

### Rebuttal Triage Template (During Review)
When reviews arrive, classify each concern:

| Priority | Type | Action | Template |
|:---|:---|:---|:---|
| **P0 (Decision-flipping)** | Novelty confusion | Clarify with direct comparison table | "We respectfully clarify that our key contribution differs from [X] in [specific way]..." |
| **P0** | Missing critical baseline | Run experiment in rebuttal period | "We have added comparison with [X]. Results in Table R1 show..." |
| **P0** | Invalid claim | Correct or scope down the claim | "We thank the reviewer for identifying this. We have revised our claim to..." |
| **P1 (Strengthening)** | Missing ablation | Add to appendix | "We have added the requested ablation in Appendix R1..." |
| **P1** | Writing clarity | Revise specific sections | "We have revised Section [X] to clarify..." |
| **P2 (Acknowledged)** | Minor concerns | Thank and note | "We thank the reviewer and will address this in the camera-ready version." |

### Reviewer Psychology Guide
- **Confused reviewer**: Be patient, re-explain with different framing. Add a figure.
- **Skeptical reviewer**: Provide additional evidence. Run the exact experiment they suggest.
- **Hostile reviewer**: Stay factual. Address specific points. Do not engage emotionally. Escalate to AC if needed.
- **Lazy reviewer**: (Short, low-effort review) Proactively provide detailed rebuttals to show your work deserves careful consideration.

### OpenReview Engagement Protocol (ICLR, NeurIPS)
- **Phase 1 (Days 1-3)**: Acknowledge all reviews. Ask clarifying questions. Show engagement.
- **Phase 2 (Days 4-10)**: Post evidence-backed responses. Reference specific experiments, figures, equations.
- **Tone**: Professional, grateful, factual. Never defensive. Always start with "We thank the reviewer..."
- **Withdrawal**: If reviews are uniformly negative (all reject) and rebuttal unlikely to flip decisions, consider withdrawing to avoid permanent public rejection stamp on OpenReview.

---

## 6. Conference Cycle Planner

### Annual Calendar (Approximate Deadlines)

```
Jan ──── ICML submission deadline
Feb ──── AAAI conference
Mar ────
Apr ──── ICLR conference / AISTATS conference / ICML notification
May ──── NeurIPS submission deadline
Jun ──── CVPR conference
Jul ──── ICML conference
Aug ──── AAAI submission deadline
Sep ──── NeurIPS notification
Oct ──── ICLR submission deadline / AISTATS submission deadline
Nov ──── CVPR submission deadline
Dec ──── NeurIPS conference / ICLR notification (Jan)
```

### Backward Planning Template
For each target deadline, plan backwards:

| Week | Milestone |
|:---|:---|
| D-8 weeks | Core experiments complete, key results known |
| D-6 weeks | First draft of main text |
| D-4 weeks | Internal review round 1 + additional experiments |
| D-3 weeks | Revision based on internal feedback |
| D-2 weeks | **Experiment freeze** — no new experiments |
| D-1 week | Final polish, format check, anonymization |
| D-3 days | **Writing freeze** — only typo fixes |
| D-1 day | Final submission compliance check (Section 4) |

### Rejection Cascade Paths

```
PRIMARY CASCADE (Theory/Methods):
ICML (Jan) ──reject Apr──→ NeurIPS (May) ──reject Sep──→ ICLR (Oct)
                                                          ↓ reject Jan
                                                    AISTATS (Oct) or TMLR (rolling)

PRIMARY CASCADE (Vision):
CVPR (Nov) ──reject Mar──→ ECCV/ICCV (Mar) ──reject──→ TPAMI (journal, rolling)

PRIMARY CASCADE (Broad AI):
AAAI (Aug) ──reject Nov──→ ICLR (Oct) ──reject Jan──→ ICML (Jan)
                                                       ↓ reject Apr
                                                  NeurIPS (May) or TMLR

STRESS-FREE PATH:
TMLR (any time) ── accept ──→ J2C certification for NeurIPS/ICML/ICLR presentation
```

### Revision Delta Guide
| Transition | Required Changes |
|:---|:---|
| NeurIPS → ICLR | Address NeurIPS reviews, improve writing clarity (ICLR values this), prepare for open review |
| ICML → NeurIPS | Broaden narrative (NeurIPS prefers breadth), add more diverse experiments |
| ICLR → ICML | Add theoretical analysis (ICML values this), tighten experimental methodology |
| Any conf → TMLR | Honest limitations section, remove "hype" language, focus on technical correctness |
| Conference → JMLR/TPAMI | +30% new content minimum, comprehensive related work, thorough experiments |

---

## 7. ArXiv Strategy

### Anonymity Windows by Venue
| Venue | Policy | Safe ArXiv Window |
|:---|:---|:---|
| NeurIPS | No posting 1 month before deadline through notification | Post before silent period or after notification |
| ICML | Anonymous submission; arXiv ok but no social media promotion | Post anytime but don't tweet during review |
| ICLR | Relaxed; arXiv posting allowed | Post anytime |
| CVPR | No arXiv restriction but double-blind | Post anytime but ensure anonymization |
| AAAI | Double-blind, anonymous submission | Check yearly policy |

### Timing Modes
- **Priority Claim**: Post to arXiv 1-2 weeks before conference deadline. Establishes priority. Risk: someone might scoop your framing.
- **Simultaneous**: Post same day as conference submission. Balanced approach.
- **Post-Decision**: Post only after acceptance. No risk, but no early citations.
- **Recommendation**: For competitive topics (LLMs, diffusion models), use **Priority Claim**. For niche topics, **Simultaneous** is sufficient.

### Versioning Standard
- **v1**: Initial submission (matches conference submission)
- **v2**: Post-rebuttal update (if significant changes made)
- **v3**: Camera-ready / accepted version (add "Accepted at [Venue]" to abstract)
- **Tip**: Always update arXiv with the camera-ready version. Many citations come from arXiv, not proceedings.

---

## 8. Figure-First & Appendix Guide

### Figure 1 Protocol (Teaser Figure)
Your teaser figure is the most important element of the paper. Reviewers spend ~30 seconds deciding if they're interested.

**Requirements:**
- Self-contained: Understandable without reading the paper
- Shows the "what" and "why" in one glance
- Includes comparison with baseline (if applicable)
- Clean design, readable at screen zoom

**Common Figure 1 Types in ML:**
1. **Method Overview**: Architecture diagram with data flow (most common)
2. **Result Teaser**: Key result comparison showing your method's advantage
3. **Problem Illustration**: The challenge + your solution side by side
4. **Insight Visualization**: The key finding that makes your method work

### Appendix Structure Guide
With 8-9 page limits, the appendix is where rigor lives:

| Section | Content | Priority |
|:---|:---|:---|
| **A. Proofs** | Full theorem proofs referenced in main text | Critical (theory papers) |
| **B. Experimental Details** | Full hyperparameter tables, training curves | Critical (all papers) |
| **C. Additional Results** | Extended benchmarks, more datasets, edge cases | High |
| **D. Ablation Studies** | Additional ablations beyond main text | High |
| **E. Compute Details** | GPU specs, wall-clock time, CO2 estimate | Medium |
| **F. Broader Impact** | Extended discussion of societal implications | As required |
| **G. Limitations** | Honest assessment of failure cases | High (builds trust) |

---

## Brainstorming Guidance
When planning a venue submission strategy:
- Start with the Strategy Configuration to classify your paper type and sub-field
- Use the Framing Switchboard to draft venue-specific abstracts — if the abstract doesn't work for a venue, the paper won't either
- Complete the full Pre-Submission Pipeline before any submission
- Pre-commit your cascade path and mark "experiment freeze" and "writing freeze" dates
- During writing, run the Pre-Buttal exercise for the top 5 likely reviewer complaints
- Plan your ArXiv timing around anonymity windows

## Implementation Guidance
- Use official LaTeX templates: `neurips_2025.sty`, `icml2026.sty`, `iclr2026_conference.tex`
- Track experiments with `wandb` or `mlflow` — reviewers value organized experiment logs
- Use `texcount` for word/page count verification
- Manage references with Semantic Scholar or Google Scholar BibTeX export
- Code organization: follow the "Papers with Code" conventions for reproducibility
- Use `matplotlib` or `plotly` for clean, publication-quality figures

## Visualization Guidance
- Learning curves (train/val loss) with shaded confidence bands across seeds
- Ablation bar charts with error bars
- Method comparison tables with best results bolded
- Attention maps, feature visualizations, or generated samples (where applicable)
- Parameter sensitivity plots showing robustness
- Computational cost vs. accuracy trade-off plots (Pareto frontiers)
