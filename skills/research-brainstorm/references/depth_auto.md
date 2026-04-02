# Depth Auto: Escalation & Deep Investigation Steps

> This file contains the `--depth auto`-specific steps. Read this file when `--depth auto` is active.
> Steps 1b-ev and 1b+ are shared with `--depth high` and remain in the main SKILL.md.

### Step 1b-esc: Depth Escalation Check (`--depth auto` only)

> **Skip unless `--depth auto`**: This step only runs for adaptive depth mode.

Analyze T2 verdict distribution per **T12** (see `references/templates.md`) to decide whether to escalate depth:

1. **Parse both review files** — run the bundled verdict parser:
   ```bash
   uv run python ${CLAUDE_PLUGIN_ROOT}/skills/research-brainstorm/scripts/parse_verdicts.py \
     {output_dir}/brainstorm/gemini_review_of_codex.md \
     {output_dir}/brainstorm/codex_review_of_gemini.md
   ```
   This outputs JSON with `n_agree`, `n_disagree`, `n_insufficient`, `n_total`, `contention_score`.

2. **Make escalation decision** per **T12** decision matrix:
   - `contention_score < 0.30` → Stay at **medium**, proceed to Step 1c (MELCHIOR as Critical Editor)
   - `0.30 ≤ contention_score < 0.50` → Escalate to **high**, proceed to Step 1b-ev → Step 1b+ → Step 1c (MELCHIOR as Adversarial Critic)
   - `contention_score ≥ 0.50` → Escalate to **deep**, proceed to Step 1b-ev → Step 1b+ → Step 1b-deep → Step 1c (MELCHIOR as Adversarial Critic Enhanced)

3. **Save decision** to `brainstorm/escalation_analysis.md` per **T12** format.

4. **Announce escalation** to the user: "Depth auto-escalation: contention score {score:.2f} → escalating to {level}" (or "remaining at medium" if no escalation).

> **Reuse guarantee**: All existing artifacts from Steps 1a and 1b are preserved. Escalation only adds downstream steps.

---

### Step 1b-deep: Focused Deep Investigation (`--depth auto`, escalation to deep only)

> **Skip unless `--depth auto` escalated to deep** (contention_score >= 0.50).

For the top 3 most contested ideas (highest combined DISAGREE + INSUFFICIENT count from Step 1b-esc analysis):

1. **Extract contested ideas** from `brainstorm/escalation_analysis.md` — take the "Top contested ideas" list.

2. **For each contested idea**, execute two focused argument calls **simultaneously**:
   - **Pro argument** (one model): "Present the strongest possible case FOR this research direction: [idea]. {If `brainstorm/claim_evidence.md` exists: 'Cite evidence from `@{output_dir}/brainstorm/claim_evidence.md` where available.'} Write exactly 300 words. Focus on: mechanism validity, supporting precedents, and conditions under which this idea succeeds."
   - **Con argument** (other model): "Present the strongest possible case AGAINST this research direction: [idea]. {If `brainstorm/claim_evidence.md` exists: 'Cite evidence from `@{output_dir}/brainstorm/claim_evidence.md` where available.'} Write exactly 300 words. Focus on: mechanism flaws, contradicting evidence, and conditions under which this idea fails."

   **Role alternation**: Alternate which model argues Pro vs. Con across the 3 ideas to prevent positional bias:
   - Idea 1: Gemini = Pro, Codex = Con
   - Idea 2: Codex = Pro, Gemini = Con
   - Idea 3: Gemini = Pro, Codex = Con

   > **If `--claude-only`**: Replace with Agent subagents per **T6**:
   > - Subagent A (T1-CD) takes Pro for odd-numbered ideas, Subagent B (T1-AC) takes Pro for even-numbered ideas (and vice versa for Con).
   > - Each subagent reads: `brainstorm/escalation_analysis.md`, (if exists) `brainstorm/claim_evidence.md`, and the relevant brainstorm/review files.
   > - Save to `brainstorm/deep_investigation_{i}_pro.md` and `brainstorm/deep_investigation_{i}_con.md` per **T5**.

3. **Save** to `brainstorm/deep_investigation_{i}_pro.md` and `brainstorm/deep_investigation_{i}_con.md` for each contested idea.

4. These files are referenced in Step 1c synthesis. When `--depth auto` escalated to deep, Step 1c must include a **"Deep Investigation Results"** section summarizing the pro/con analysis for each contested idea and its effect on ranking.
