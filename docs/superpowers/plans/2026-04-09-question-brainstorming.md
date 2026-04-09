# Replace Step 0c with Research Question Brainstorming — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 3-tier question refinement system (Step 0c) with a human-in-the-loop brainstorming protocol that keeps research direction aligned with user intent.

**Architecture:** Delete Step 0c (lines 334-375) in SKILL.md and replace with a new "Research Question Brainstorming" protocol. Delete Step 0c Tier 3 section (lines 6-30) in depth_max.md. No new files created; only two existing files modified.

**Tech Stack:** Markdown (SKILL.md prompt engineering)

---

### Task 1: Replace Step 0c in SKILL.md

**Files:**
- Modify: `skills/research-brainstorm/SKILL.md:334-375`

- [ ] **Step 1: Read the current Step 0c to confirm exact boundaries**

Run: Read `skills/research-brainstorm/SKILL.md` lines 334-375.
Confirm the section starts with `### Step 0c: Adaptive Question Refinement` and ends just before `### Step 0d: Pre-flight Context Gathering`.

- [ ] **Step 2: Replace Step 0c with the new Research Question Brainstorming protocol**

Delete lines 334-375 (the entire old Step 0c) and insert the following in its place:

```markdown
### Step 0c: Research Question Brainstorming

> **Runs at all depths, unconditionally.** No `--depth` branching. Human-in-the-loop dialogue ensures research direction stays aligned with user intent.

**Phase 1 — Internal Assessment** (not shown to user):

Evaluate the research question on three criteria:

| Criterion | Pass | Marginal/Fail |
|-----------|------|---------------|
| **Specificity** | Narrow enough for actionable directions | Too broad or vague |
| **Clarity** | Key terms unambiguous in domain | Ambiguous or unclear terms |
| **Research-readiness** | Implies measurable outcomes or testable hypotheses | No measurable criteria inferable |

**Decision**:
- **All Pass** → Present to user: "The research question is clear and specific. Proceed directly, or explore research directions further?" If user says proceed → write skip-case `brainstorm/question_refinement.md` (see output format below), go to Step 0d. If user says explore → enter Phase 2.
- **Any Marginal or Fail** → Enter Phase 2.

**Phase 2 — Dialogue Loop**:

Refine the question through interactive dialogue. Rules:
1. **One question per message.** Never ask multiple questions at once.
2. **Multiple choice preferred.** Use open-ended only when the answer space is too wide for options.
3. **Research-specific questions.** Focus on:
   - What methodology scope is intended? (theoretical / computational / experimental / mixed)
   - What would constitute a successful outcome? (measurable criteria)
   - What prior work or approaches should be considered vs. excluded?
   - What is the target audience or application context?
   - What constraints exist? (time, data availability, compute, domain boundaries)
4. **Exit condition**: User signals the question is sufficiently refined (e.g., "that's enough", "looks good", "proceed"). Do not over-question — 2-4 questions is typical. If the question was already Marginal (not Fail), 1-2 questions may suffice.

**Phase 3 — Research Direction Proposals**:

Based on the dialogue, propose **2-3 alternative research directions** for the (now-refined) question. For each direction:
- **Direction name** — concise label
- **Core question** — the specific research question this direction addresses
- **Expected methodology** — how this would be investigated
- **Anticipated outcome** — what results to expect if successful

Present with a **recommendation** and reasoning. User selects one (or provides their own).

**Phase 4 — Scope Level Confirmation**:

Frame the selected direction at three scope levels:
- **Operational** — concrete, mechanism-level
- **Conceptual** — mid-level, framework-focused (default)
- **Philosophical** — abstract, principle-level

If the user already selected a scope level in Question Orientation (Step 0, item 9), use that as default. Present briefly: "Proceeding at Conceptual level. Reply 'operational' or 'philosophical' to adjust." Move on immediately unless user responds.

**Phase 5 — Final Confirmation**:

Present the refined research question as a single sentence. User approves → proceed to Step 0d.

**Output**:

Save `brainstorm/question_refinement.md` with the following format:

```
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

**Skip case** (All Pass, user chose to proceed directly):
```
# Research Question Refinement

## Original Question
{original}

## Assessment
Question assessed as clear and specific. User confirmed to proceed without refinement.

## Final Research Question
> {original, unchanged}
```

Update `.workspace.json`: set `topic` to the final refined question. If different from original, preserve original as `original_topic`.
```

- [ ] **Step 3: Verify the transition to Step 0d is intact**

Read 5 lines above and below the edit boundary. Confirm:
- New Step 0c ends cleanly
- `### Step 0d: Pre-flight Context Gathering` follows immediately after
- No orphaned references to old tiers

Run: Read `skills/research-brainstorm/SKILL.md` around the boundary.

- [ ] **Step 4: Commit**

```bash
git add skills/research-brainstorm/SKILL.md
git commit -m "feat: replace Step 0c 3-tier system with research question brainstorming"
```

---

### Task 2: Remove Step 0c Tier 3 from depth_max.md

**Files:**
- Modify: `skills/research-brainstorm/references/depth_max.md:1-31`

- [ ] **Step 1: Read depth_max.md to confirm boundaries**

Run: Read `skills/research-brainstorm/references/depth_max.md` lines 1-35.
Confirm the Tier 3 section spans lines 6-30, followed by `---` separator and then `### Step 1-max-a`.

- [ ] **Step 2: Delete the Step 0c Tier 3 section**

Delete lines 6-31 (from `### Step 0c Tier 3:` through the `---` separator). Keep lines 1-4 (file header) and everything from `### Step 1-max-a` onward.

The file should now read:

```markdown
# Depth Max: MAGI-in-MAGI Pipeline

> This file contains the `--depth max`-specific steps. Read this file when `--depth max` is active.
> These steps (1-max-a through 1-max-d) replace Steps 1a/1b/1b+/1c from the main SKILL.md.

### Step 1-max-a: Layer 1 — Parallel Persona Subagents
...
```

Note: Update line 4 to remove `0c,` from the step list: change `(0c, 1-max-a through 1-max-d)` to `(1-max-a through 1-max-d)`.

- [ ] **Step 3: Verify depth_max.md integrity**

Run: Read `skills/research-brainstorm/references/depth_max.md` lines 1-40.
Confirm: no orphaned Tier references, Step 1-max-a starts cleanly, no broken formatting.

- [ ] **Step 4: Commit**

```bash
git add skills/research-brainstorm/references/depth_max.md
git commit -m "refactor: remove Step 0c Tier 3 MAGI question refinement from depth_max.md"
```

---

### Task 3: Verify no broken cross-references

**Files:**
- Read-only scan across `skills/research-brainstorm/`

- [ ] **Step 1: Grep for stale references**

Search the entire `skills/research-brainstorm/` directory for references to the removed content:

```bash
grep -rn "Tier 3.*question\|Step 0c Tier 3\|Tier 2.*clarification\|3-tier" skills/research-brainstorm/
```

Expected: No matches (aside from the already-removed content). If any remain, fix them.

- [ ] **Step 2: Grep for "Tier 1 finding" (should be kept)**

Verify that references to "Tier 1 finding" in the synthesis/templates context (meaning top-ranked findings, not question refinement tiers) are untouched:

```bash
grep -rn "Tier 1 finding\|Tier 2 finding\|Tier 3.*speculative" skills/research-brainstorm/references/templates.md
```

Expected: These should still exist — they refer to finding ranking tiers, not question refinement.

- [ ] **Step 3: Commit (if any fixes were needed)**

```bash
git add -A skills/research-brainstorm/
git commit -m "fix: clean up stale Tier references after Step 0c replacement"
```

Skip this commit if no changes were needed.
