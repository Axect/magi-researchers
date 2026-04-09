# Design: Replace Step 0c with Research Question Brainstorming

**Date**: 2026-04-09
**Status**: Approved
**Scope**: Step 0c (Adaptive Question Refinement) in `skills/research-brainstorm/SKILL.md`

## Problem

The current 3-tier question refinement system (Tier 1: Claude auto-assessment, Tier 2: user choice from suggestions, Tier 3: MAGI multi-model discussion) has a fundamental issue: AI-only discussion (especially Tier 3) drifts away from the user's actual research intent. The user wants a human-in-the-loop approach inspired by `superpowers:brainstorming` — one question at a time, user confirms at each step.

## Approach

Inline rewrite of Step 0c in SKILL.md. Encode the brainstorming skill's core principles (1-question-at-a-time, approach proposals, user confirmation) directly into the research pipeline, specialized for research question refinement. No external skill invocation.

## Design

### Execution

- Runs at **all depths**, unconditionally. No `--depth` branching in Step 0c.
- Pipeline order unchanged: `0 → Orientation → 0a → 0b → 0c(brainstorming) → 0d → 1...`

### Protocol Flow

```
1. Initial Assessment (internal, not shown to user)
   - Evaluate Specificity / Clarity / Research-readiness
   - All Pass → offer skip: "질문이 충분히 명확합니다. 바로 진행할까요, 
     아니면 연구 방향을 더 탐색할까요?"
     - User says proceed → write minimal refinement doc, go to Step 0d
     - User says explore → enter dialogue loop
   - Any Marginal/Fail → enter dialogue loop

2. Dialogue Loop (1 question at a time)
   - Multiple choice preferred, open-ended when needed
   - Research-specific questions: methodology scope, measurable criteria,
     prior work boundaries, target audience, etc.
   - Loop until user signals satisfaction

3. Research Direction Proposals (2-3 options)
   - Each direction: core question, expected methodology, anticipated outcome
   - Claude recommendation with reasoning
   - User selects one

4. Scope Level Confirmation
   - Frame selected direction as Operational / Conceptual / Philosophical
   - Default to level chosen in Question Orientation (Step 0, item 9)
   - User confirms or adjusts

5. Final Confirmation
   - Present refined question as a single sentence
   - User approves → proceed to Step 0d
```

### Output Artifacts

**`brainstorm/question_refinement.md`** — full trace of the refinement process:

```markdown
# Research Question Refinement

## Original Question
{user's original input}

## Refinement Dialogue
### Q1: {Claude's question}
**A**: {user's response}

### Q2: {Claude's question}
**A**: {user's response}
...

## Research Directions Proposed
| # | Direction | Core Question | Methodology | Expected Outcome |
|---|-----------|--------------|-------------|-----------------|
| 1 | {name} | {question} | {method} | {outcome} |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |

**Recommended**: #{N} — {reasoning}
**Selected**: #{user's choice}

## Scope Level
{Operational / Conceptual / Philosophical} — {one-line explanation}

## Final Research Question
> {refined question}

## Changes from Original
- {summary of what changed and why}
```

**Skip case** (All Pass, user chose to proceed):

```markdown
# Research Question Refinement

## Original Question
{original}

## Assessment
Question assessed as clear and specific. User confirmed to proceed without refinement.

## Final Research Question
> {original, unchanged}
```

**`.workspace.json`**: Update `topic` field to refined question. If changed, preserve `original_topic`.

## Files Changed

### `skills/research-brainstorm/SKILL.md`
- **Delete**: Step 0c (lines 334-375) — entire 3-tier system
- **Insert**: New Step 0c "Research Question Brainstorming" protocol as described above
- **Modify**: Remove depth-conditional language referencing old tiers
- **Keep**: Question Orientation (lines 215-232), add note that scope level chosen here is the default for Step 0c.4

### `skills/research-brainstorm/references/depth_max.md`
- **Delete**: Step 0c Tier 3 section (MAGI question refinement discussion)
- **Keep**: Everything else (Step 1+ MAGI-in-MAGI pipeline)

### No changes
- `references/depth_auto.md` (Step 1b+ escalation only)
- `scripts/openalex_search.py` (Step 0d)
- `scripts/parse_verdicts.py` (Step 1b)
- `templates/`, `shared/rules.md`, `config/flags.yaml`
