# Journal & Venue Strategy Templates

MAGI includes domain-specific templates that recommend journals/conferences for your research and provide tailored submission strategies. These templates are automatically loaded as context when you run the research pipeline with a `--domain` flag.

```
/magi-researchers:research "your research topic" --domain physics
```

The `--domain` flag selects both the **research methodology template** and the corresponding **journal strategy template**. The models will:

1. **Brainstorm** with venue-awareness — ideas shaped with publication targets in mind
2. **Plan** with submission strategy — research plan considers framing for target journals
3. **Report** with journal fit — final report includes venue recommendations

You can also reference the strategy templates directly in conversation:

```
Read templates/domains/journal_strategy_physics.md and help me choose
the best journal for my paper on dark matter detection via ML.
```

---

## Particle Physics Phenomenology

Covers PRL, PRD, PRX, JHEP, PLB, EPJC, NPB, JCAP, PRE, CPC, PRX Quantum with:

- **Journal-fit classifier** — Match your paper type and sub-field to the best venue
- **Framing switchboard** — Same result, different framing for PRL vs PRD vs JHEP
- **Referee defense checklist** — Gauge invariance, unitarity, EW precision, vacuum stability...
- **Cover letter templates** — Per-journal templates with acceptance-criteria mapping
- **Cascade submission roadmap** — Pre-planned fallback paths (PRL → PLB/PRD)
- **ArXiv timing strategy** — Category selection, cross-listing, posting schedule

[`journal_strategy_physics.md`](../templates/domains/journal_strategy_physics.md)

---

## AI/ML Conferences & Journals

Covers NeurIPS, ICML, ICLR, AAAI, CVPR, AISTATS, JMLR, TMLR, Nature MI, IEEE TPAMI with:

- **Conference framing switchboard** — NeurIPS (breadth) vs ICML (rigor) vs ICLR (clarity)
- **Pre-submission pipeline** — Desk-rejection firewall + reproducibility gate + baseline audit
- **Rebuttal defense system** — Pre-buttal during writing + triage template for reviews
- **Conference cycle planner** — Annual deadline calendar + rejection cascade paths
- **ArXiv anonymity manager** — Venue-specific safe posting windows
- **Conference-to-journal pipeline** — Extension thresholds for JMLR/TPAMI

[`journal_strategy_ai_ml.md`](../templates/domains/journal_strategy_ai_ml.md)

---

## Interdisciplinary Science (ML + Natural Sciences)

Covers Nature Communications, MLST, PRX Intelligence, PRX Life, PRX Energy, Physical Review Research, SciPost Physics, Science Advances, iScience with:

- **Dual-impact matrix** — 2x2 classifier (ML Novelty vs Domain Significance) for venue selection
- **Sub-field routing** — Physics-informed ML, ML for simulation, scientific discovery, and more
- **Framing switchboard** — Same result framed for Nature Comms vs MLST vs PRX Intelligence vs SciPost
- **Dual rigor checklist** — ML reproducibility + domain validity + interdisciplinary bridge checks
- **Adversarial persona simulation** — Pre-test against ML Purist, Domain Gatekeeper, and Methods Pedant reviewers
- **Figure-first protocol** — Bridge figure requirements for cross-disciplinary readability

[`journal_strategy_interdisciplinary.md`](../templates/domains/journal_strategy_interdisciplinary.md)
