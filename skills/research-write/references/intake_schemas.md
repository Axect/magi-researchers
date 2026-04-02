# Intake Schemas

Full JSON schemas for the three structured artifacts produced in Phase 0c and Phase 1c.

---

## write_inputs.json Schema

```json
{
  "source_dir": "{source_dir}",
  "mode": "paper|proposal",
  "audience": "{audience}",
  "domain": "{domain}",
  "claims": [
    {
      "id": "claim-1",
      "text": "Our method achieves 15% improvement over baseline",
      "source": "brainstorm/synthesis.md",
      "confidence": "high|medium|low",
      "evidence_ids": ["ev-1", "ev-3"]
    }
  ],
  "evidence": [
    {
      "id": "ev-1",
      "type": "plot|metric|test_result|code|explanation",
      "ref": "plots/fig_convergence.png",
      "description": "Convergence plot showing ...",
      "caption": "Figure 1: ...",
      "section_hint": "results"
    }
  ],
  "definitions": [
    {
      "term": "MAGI architecture",
      "explanation": "Multi-Agent Guided Investigation ...",
      "source": "explain/magi_architecture.md"
    }
  ],
  "key_findings": [
    {
      "id": "finding-1",
      "summary": "...",
      "supporting_claims": ["claim-1", "claim-3"],
      "narrative_weight": "primary|secondary|supporting"
    }
  ],
  "sections_available": ["background", "methodology", "results", "testing"]
}
```

**Extraction guidelines:**
- Extract claims conservatively — only include assertions backed by evidence in the upstream artifacts
- Assign `confidence: "high"` only when a claim has both quantitative data and a supporting plot/test
- Assign `confidence: "low"` to claims inferred from text without direct data support
- Link each claim to its evidence via `evidence_ids`
- Use `section_hint` from `plot_manifest.json` if available; otherwise infer from context
- For definitions, prefer explain outputs; fall back to inline definitions in synthesis/plan

---

## citation_ledger.json Schema

```json
{
  "citations": [
    {
      "id": "ref-1",
      "claim_id": "claim-1",
      "source_type": "upstream_artifact|web_search|assumed",
      "source_path": "brainstorm/synthesis.md",
      "source_detail": "Section 3, Direction 1",
      "resolved": true,
      "needs_verification": false
    }
  ],
  "unresolved_claims": [
    {
      "claim_id": "claim-5",
      "reason": "No supporting data found in upstream artifacts",
      "recommendation": "remove|verify_with_search|mark_as_tentative"
    }
  ]
}
```

---

## section_contracts.json Schema

```json
{
  "global_argument_thread": "This paper argues that ... by showing ... which leads to ...",
  "mode": "paper",
  "audience": "researcher",
  "sections": [
    {
      "id": "introduction",
      "title": "Introduction",
      "purpose": "Motivate the problem and state contributions",
      "narrative_role": "Establish why this problem matters and what we do about it",
      "key_points": ["point 1", "point 2", "point 3"],
      "evidence_ids": ["ev-1", "ev-5"],
      "claim_ids": ["claim-1", "claim-2"],
      "max_words": 1500,
      "style": "Motivate problem, state contributions, outline paper structure.",
      "transition_from_previous": null,
      "transition_to_next": "Having established the problem, we now survey related work.",
      "drafting_order": 3
    }
  ]
}
```

---

## writing_state.json Schema

```json
{
  "status": "complete",
  "mode": "paper",
  "audience": "researcher",
  "source_dir": "{source_dir}",
  "phases_complete": {
    "intake": true,
    "outline": true,
    "draft": true,
    "review": true,
    "finalize": true
  },
  "sections_drafted": ["introduction", "methodology", "results", "..."],
  "output_file": "write/{topic}_paper.md",
  "stats": {
    "total_words": 8500,
    "claims_supported": 12,
    "claims_unresolved": 1,
    "evidence_integrated": 8,
    "review_issues_resolved": 15
  }
}
```
