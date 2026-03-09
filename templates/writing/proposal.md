---
mode: proposal
description: "Grant or funding proposal with persuasive structure"
sections:
  - id: executive_summary
    required: true
    max_words: 300
    evidence_slots: []
    style: "Persuasive, concise. State problem, approach, expected impact."
    narrative_role: "Sell the idea in 30 seconds"
  - id: problem_statement
    required: true
    max_words: 1000
    evidence_slots: ["claims[]", "citations[]"]
    style: "Establish urgency and significance. Use concrete data."
    narrative_role: "Make the reader care about the problem"
  - id: proposed_approach
    required: true
    max_words: 2000
    evidence_slots: ["claims[]", "figures[]", "citations[]"]
    style: "Clear methodology. Highlight innovation. Show feasibility."
    narrative_role: "Present a credible solution"
  - id: preliminary_results
    required: false
    max_words: 1500
    evidence_slots: ["figures[]", "metrics[]"]
    style: "Show proof of concept. Reference existing data/plots."
    narrative_role: "Demonstrate that the approach is not speculative"
  - id: timeline_milestones
    required: true
    max_words: 800
    evidence_slots: []
    style: "Specific milestones with dates. Deliverables per phase."
    narrative_role: "Show the work is plannable and manageable"
  - id: budget_justification
    required: true
    max_words: 500
    evidence_slots: []
    style: "Line items with rationale. Connect costs to milestones."
    narrative_role: "Justify the investment"
  - id: broader_impact
    required: true
    max_words: 500
    evidence_slots: ["claims[]"]
    style: "Societal benefits, training opportunities, open-source plans."
    narrative_role: "Show value beyond the immediate research"
  - id: references
    required: true
    max_words: 0
    evidence_slots: ["citations[]"]
    style: "Complete, correctly formatted."
    narrative_role: "Support all claims"
export:
  - markdown
total_max_words: 6600
tone: "Professional, persuasive, confident but not overclaiming."
jargon_budget: medium
formality: high
---

# Grant Proposal Mode

This template guides the write pipeline to produce a funding proposal.

## Section Dependencies
- `executive_summary` depends on all other sections (write last)
- `problem_statement` is independent (draft first)
- `proposed_approach` depends on `problem_statement`
- `preliminary_results` depends on `proposed_approach` (optional)
- `timeline_milestones` depends on `proposed_approach`
- `budget_justification` depends on `timeline_milestones`
- `broader_impact` depends on `proposed_approach`

## Evidence Integration Guidelines
- Preliminary results should reference figures/metrics from upstream research outputs
- Problem statement should cite recent literature to establish urgency
- Budget items should be realistic and justified by the timeline
- Avoid speculative claims without evidence qualification
