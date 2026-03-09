---
mode: paper
description: "Academic research paper with standard structure"
sections:
  - id: abstract
    required: true
    max_words: 250
    evidence_slots: []
    style: "Concise. State problem, method, key result. No citations."
    narrative_role: "Hook the reader with the core contribution"
  - id: introduction
    required: true
    max_words: 1500
    evidence_slots: ["claims[]", "citations[]"]
    style: "Motivate problem, state contributions, outline paper structure."
    narrative_role: "Establish why this problem matters and what we do about it"
  - id: related_work
    required: true
    max_words: 1000
    evidence_slots: ["citations[]"]
    style: "Compare and contrast with prior work. Position contribution clearly."
    narrative_role: "Show the gap this work fills"
  - id: methodology
    required: true
    max_words: 2000
    evidence_slots: ["claims[]", "figures[]", "citations[]"]
    style: "Precise, reproducible. Include equations with LaTeX. Specify assumptions."
    narrative_role: "Explain how the problem is solved"
  - id: experiments
    required: true
    max_words: 2000
    evidence_slots: ["figures[]", "metrics[]", "citations[]"]
    style: "Baselines, ablations, quantitative results. Reference all figures."
    narrative_role: "Demonstrate that the method works"
  - id: results
    required: true
    max_words: 1500
    evidence_slots: ["figures[]", "metrics[]"]
    style: "Concrete observations with specific numbers. Interpret what data shows."
    narrative_role: "Present the evidence for the contribution"
  - id: discussion
    required: false
    max_words: 1000
    evidence_slots: ["claims[]"]
    style: "Interpret results in broader context. Connect to related work."
    narrative_role: "Explain what the results mean beyond the immediate experiment"
  - id: limitations
    required: true
    max_words: 500
    evidence_slots: []
    style: "Honest, specific, grounded in methodology. Not generic disclaimers."
    narrative_role: "Acknowledge what the work does NOT show"
  - id: conclusion
    required: true
    max_words: 500
    evidence_slots: []
    style: "Summarize contributions. Suggest future work. No new claims."
    narrative_role: "Leave the reader with a clear takeaway"
  - id: references
    required: true
    max_words: 0
    evidence_slots: ["citations[]"]
    style: "Complete, correctly formatted."
    narrative_role: "Support all claims"
export:
  - markdown
  - latex
total_max_words: 10250
tone: "Academic, precise, third-person. Avoid hedging language."
jargon_budget: high
formality: high
---

# Academic Paper Mode

This template guides the write pipeline to produce a standard academic research paper.

## Section Dependencies
- `abstract` depends on all other sections (write last)
- `introduction` depends on `methodology` and `results` (for contribution claims)
- `related_work` is independent (can be drafted early)
- `methodology` depends on `introduction` (for problem statement)
- `experiments` depends on `methodology`
- `results` depends on `experiments`
- `discussion` depends on `results` and `related_work`
- `limitations` depends on `methodology` and `results`
- `conclusion` depends on all preceding sections

## Evidence Integration Guidelines
- Every quantitative claim must reference a figure, table, or metric from `write_inputs.json`
- Figures are pre-inserted by the orchestrator; write prose around them
- Use LaTeX for all mathematical expressions
- Display equations use `$$` on separate lines; inline math uses `$...$`
