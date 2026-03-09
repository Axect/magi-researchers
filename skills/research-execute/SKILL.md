# Research Execute Skill

## Description
Executes the research code in `src/` to generate result artifacts in `results/`. This is Phase 3.5
of the research pipeline, sitting between Implementation (Phase 3) and Testing & Visualization (Phase 4).

Reads execution commands deterministically from the YAML frontmatter of `plan/research_plan.md` — no
keyword heuristics, no entry-point guessing. The full run command is defined once during planning and
executed here.

## Usage
```
/research-execute [path/to/output/dir]
```

## Arguments
- `$ARGUMENTS` — Optional path to the research output directory. If not provided, uses the most recent `outputs/*/` directory.

## Instructions

### Claude-Only Mode
When `--claude-only` is active, there are no Gemini/Codex calls in this skill. All steps are
performed by Claude directly.

### Step 0: Locate Research Plan & Check Prerequisites

1. Find the active research output directory (from `$ARGUMENTS` or most recent `outputs/*/`).
2. Read `plan/research_plan.md` and parse the YAML frontmatter:
   ```yaml
   ---
   languages: ["rust", "python"]
   ecosystem: ["cargo", "uv"]
   execution_cmd: "bash run_all.sh"
   dry_run_cmd: "bash run_all.sh --dry-run"
   expected_outputs:
     - "results/metrics.csv"
     - "results/checkpoint.pt"
   estimated_runtime: "~30 minutes"
   ---
   ```
3. If the frontmatter is **missing or has no `execution_cmd`**: announce the problem to the user and
   ask them to provide the execution command manually. Do not guess. Suggest adding the frontmatter
   to `research_plan.md` following the schema above.
4. Verify `src/` exists and contains at least one file.

### Step 1: Early Exit — results/ Already Populated

Check if `results/` already exists and contains at least one file that is **not** `run_log.txt` or
`pre_execution_status.md`:

```
Glob: results/**/*
```

If populated:
- Announce: `"results/ already contains artifacts. Skipping re-execution."`
- Write `results/pre_execution_status.md` with status `EXISTING` if not already present.
- Proceed directly to **Step 6 (Summary)**.

### Step 2: Dry-Run Verification

If `dry_run_cmd` is specified in the frontmatter, run it first as a fast sanity check:

```bash
{dry_run_cmd} 2>&1 | tee results/dry_run_log.txt
```

Timeout: **60 seconds**.

| Outcome | Action |
|:--------|:-------|
| Exit 0 | Continue to Step 3 |
| Non-zero exit | Read `results/dry_run_log.txt`, extract the traceback |
| Timeout | Kill process; report to user; ask whether to proceed to full run anyway |

**On dry-run failure:**
1. Classify the error:
   - **Minor** (wrong path, missing directory, missing `results/` subdirectory, simple import): attempt one auto-fix, re-run dry-run.
   - **Logic / Type / Shape error**: report to user with the full traceback. Recommend rolling back to Phase 3 (Implement) to fix the code. Do NOT proceed to full run.
   - **Environment / dependency error** (missing binary, CUDA not found, missing package): report to user with install instructions. Do not attempt auto-fix.
2. After auto-fix attempt: if dry-run succeeds → continue. If it still fails → stop and report.

If `dry_run_cmd` is **not** specified, skip this step and proceed directly to Step 3.

### Step 3: User Checkpoint — Announce Full Run

Before executing the full run, announce:

```
Ready to execute:
  Command: {execution_cmd}
  Estimated runtime: {estimated_runtime or "unknown"}
  Output will be captured to: results/run_log.txt

Proceeding — interrupt with Ctrl+C if needed.
```

If `estimated_runtime` suggests a long job (> 15 minutes), add:

```
⚠ This job may take a long time. If you prefer to run it manually:
  1. Run externally: {execution_cmd}
  2. Then call `/research-execute --resume` to skip re-execution and record results.
```

Pause for user confirmation before running.

### Step 4: Execute Full Run

Create `results/` directory if it does not exist, then run:

```bash
{execution_cmd} 2>&1 | tee results/run_log.txt
```

Timeout: **30 minutes** (adjust based on `estimated_runtime` if provided and > 30 min).

| Outcome | Detection | Action |
|:--------|:----------|:-------|
| Success | Exit code 0 | Continue to Step 5 |
| Runtime error | Non-zero exit | Step 4-FAIL path |
| Timeout | Still running | Kill process → Step 4-TIMEOUT path |

**Step 4-FAIL path** (non-zero exit):
1. Read `results/run_log.txt` and extract the final traceback.
2. Classify the error (same classification as Step 2):
   - **Minor**: attempt one auto-fix, re-run once. Success → Step 5. Failure → Step 4-PARTIAL.
   - **Logic / Environment**: do NOT auto-fix. Write failure status → Step 4-PARTIAL.
3. For logic/environment errors: recommend rolling back to Phase 3 (Implement).

**Step 4-TIMEOUT path**:
1. Append `"EXECUTION TIMED OUT."` to `results/run_log.txt`.
2. Inventory what `results/` contains so far.
3. Ask user: "The job timed out. Would you like to (a) run it externally and then resume, or (b) continue to testing with partial results?"
4. Record the user's choice in `results/pre_execution_status.md` → proceed to Step 4-PARTIAL.

**Step 4-PARTIAL** (failure or timeout):
Write `results/pre_execution_status.md`:
```markdown
# Pre-execution Status: FAILED / PARTIAL

Execution command: {execution_cmd}
Outcome: {FAILED | TIMED_OUT}
Error summary: {one-paragraph description}
Partial artifacts available: {list files in results/ if any}

## Impact on Downstream Steps
- Integration tests that reference results/ should be marked as skipped
- Visualizations will use any partial data available; incomplete sections will be noted
```
Announce clearly to the user. Do NOT block the pipeline — proceed to **Step 6**.

### Step 5: Post-execution Inventory

If execution succeeded:
1. Glob `results/**/*` and categorize by extension.
2. If `expected_outputs` is specified in frontmatter, verify each file exists. Report any missing ones.
3. Write `results/pre_execution_status.md`:
   ```markdown
   # Pre-execution Status: SUCCESS

   Execution command: {execution_cmd}

   ## Generated Artifacts
   | File | Type |
   |:-----|:-----|
   | results/... | csv / npz / pt / ... |

   ## Notes for Downstream Steps
   - Tests should load data from results/ rather than re-running src/
   - Visualizations may read results/ data files directly
   ```
4. Announce success with the artifact summary.

### Step 6: Summary

Present to the user:
- **Execution status**: SUCCESS / FAILED / PARTIAL / SKIPPED (existing) / TIMED_OUT
- **Command used**: `{execution_cmd}`
- **Artifacts generated**: list with file types
- **Issues encountered**: (if any) with recommended next steps
- **Next step**: Proceed to Phase 4 (`/research-test`) when ready

## Notes
- This skill has no Gemini/Codex calls — execution is a deterministic operation.
- If the full run truly requires hours (e.g., multi-GPU training), always recommend running it
  externally and committing `results/` before calling this skill. Step 1 (Early Exit) will detect
  the populated `results/` and skip re-execution automatically.
- Do NOT modify `src/` files during this phase. If errors require code changes, roll back to
  Phase 3 (Implement).
