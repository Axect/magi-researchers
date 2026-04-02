# Phase 3b: Devil's Advocate Adversarial Review (--depth high only)

This step runs only when `--depth high` is specified. Skip entirely for `--depth low` or `--depth medium`.

---

## Selection Criteria

Identify **high-stakes sections**: sections with the most critical/major issues from Step 3a, plus any section tagged as `required: true` in the mode template that has `narrative_role` containing "evidence", "method", or "result".

Apply adversarial review to at most **3 sections**.

---

## Adversarial Review Prompt (per high-stakes section)

```
mcp__gemini-cli__ask-gemini(
  prompt: "You are a hostile but fair reviewer of the '{section_title}' section. Your job is to find fatal flaws that would cause a reviewer to reject this {mode}.

Attack on these dimensions:
1. **Overclaiming**: Does the text promise more than the evidence supports?
2. **Missing counterarguments**: Are obvious objections left unaddressed?
3. **Methodological gaps**: Is the methodology described with sufficient rigor to reproduce?
4. **Evidence cherry-picking**: Are unfavorable results omitted or downplayed?
5. **Logical fallacies**: Are there non sequiturs, false equivalences, or circular reasoning?

For each flaw found, rate severity (Critical/Major/Minor) and provide a concrete fix.

Section text:
@{source_dir}/write/sections/{section_id}.md

Section contract:
[inline the specific section contract from section_contracts.json]

Supporting evidence:
@{source_dir}/write/evidence_blocks/{section_id}.md",
  model: "gemini-3.1-pro-preview"
)
```
Save each result to `write/devils_advocate_{section_id}.md`.

---

## Claude-Only Fallback

> Per §SubagentExec — **Adversarial-Critical** hostile reviewer of '{section_title}': Read `sections/{section_id}.md` + `evidence_blocks/{section_id}.md` + section contract. Attack for overclaiming, missing counterarguments, methodological gaps, evidence cherry-picking, logical fallacies. Per flaw: severity (Critical/Major/Minor) + concrete fix. Save to `write/devils_advocate_{section_id}.md`.

---

## Fix Application Rules

In Step 3c, when consuming devil's advocate findings:
- Apply **all Critical** fixes unconditionally
- Evaluate **Major** fixes on merit — apply where the fix strengthens the argument without expanding scope
- Note **Minor** fixes as optional improvements; surface to user in Phase 4b summary
