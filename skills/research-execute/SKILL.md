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
3. **Prefer `execution_manifest.json`**: Check if `execution_manifest.json` exists in the output directory root. If it does, read execution fields from this file instead of the YAML frontmatter:
   ```json
   {
     "schema_version": "1.0.0",
     "languages": ["rust", "python"],
     "ecosystem": ["cargo", "uv"],
     "execution_cmd": "bash run_all.sh",
     "dry_run_cmd": "bash run_all.sh --dry-run",
     "expected_outputs": [
       {"path": "results/metrics.csv", "required": true},
       {"path": "results/checkpoint.pt", "required": false}
     ],
     "estimated_runtime": "~30 minutes"
   }
   ```
   If `execution_manifest.json` exists, it takes precedence over YAML frontmatter fields. If it does not exist, fall back to the YAML frontmatter (backward compatibility).
4. If the frontmatter is **missing or has no `execution_cmd`**: announce the problem to the user and
   ask them to provide the execution command manually. Do not guess. Suggest adding the frontmatter
   to `research_plan.md` following the schema above.
5. Verify `src/` exists and contains at least one file.

### Step 1: Early Exit — results/ Already Populated

Check if `results/` already exists and contains at least one file that is **not** `run_log.txt`,
`pre_execution_status.json`, or `pre_execution_status.md` (legacy):

```
Glob: results/**/*
```

**Exclusion**: Exclude `results/.staging/` from the existence check. Files under `.staging/` are incomplete and must not trigger the 'results already exist' early-exit path.

If populated:
- **Staleness check**: Compute SHA-256 hashes of all files in `src/` and `plan/research_plan.md`. Compare against hashes stored in `results/.source_hashes.json` (if it exists).
  - If hashes match: results are current. Announce: `"results/ already contains artifacts and source code is unchanged. Skipping re-execution."`
  - If hashes differ or `.source_hashes.json` is missing: Announce: `"results/ contains artifacts but source code has changed since they were generated. Re-execution recommended."` Ask the user: "(a) Re-execute with current code, or (b) Keep existing results?"
  - If user chooses (b): proceed to the write below.
- Write `results/pre_execution_status.json` (if not already present) with the canonical EXISTING schema:
  ```json
  {
    "state": "EXISTING",
    "error_class": null,
    "severity": null,
    "retryable": false,
    "downstream_allowed": true,
    "traceback_ref": null,
    "next_action": "proceed"
  }
  ```
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
   - **Fatal / unknown** (segfault, disk full, OOM, novel network error, or any error not matching the above categories): immediately write FAILED status to `results/pre_execution_status.json`. Do NOT attempt auto-fix. Report to user with full traceback and recommend investigating the root cause before retrying.
2. After auto-fix attempt: if dry-run succeeds → continue. If it still fails → stop and report.

If `dry_run_cmd` is **not** specified, skip this step and proceed directly to Step 3.

### Step 3: User Checkpoint — Announce Full Run

Before executing the full run, announce:

```
Ready to execute:
  Command: {execution_cmd}
  Estimated runtime: {estimated_runtime or "unknown"}
  Output will be captured to: results/run_log.txt

Pause for user confirmation before running.
```

If `estimated_runtime` suggests a long job (> 15 minutes), add:

```
⚠ This job may take a long time. If you prefer to run it manually:
  1. Run externally: {execution_cmd}
  2. Copy results to the `results/` directory, then call `/research-execute [output_dir]` — the skill will detect existing results and skip re-execution automatically (Step 1 Early Exit).
```

**Wait for explicit user confirmation before executing.**

### Step 4: Execute Full Run

Create `results/` directory if it does not exist, then run:

**Manifest overrides**: If `execution_manifest.json` was loaded in Step 0:
- If `cwd` is specified, `cd` to that directory before executing the command.
- If `env` is specified (object of key-value pairs), prepend each as environment variable exports to the command (e.g., `FOO=bar BAZ=qux {execution_cmd}`).
- If `timeout_override_ms` is specified, use it instead of the default 30-minute timeout below.

**Command validation**: Before executing, inspect `execution_cmd` for shell metacharacters (`;`, `&&`, `||`, `|`, `$(`, `` ` ``, `>`, `<`, `&`). If any are found beyond simple pipes to `tee`, warn the user and require explicit confirmation before proceeding. Validate that the `cwd` field (if present) is a relative subdirectory path with no `..` traversal and that the directory exists.

Execute in an isolated process group to prevent orphaned child processes on timeout:

```bash
setsid bash -c '{execution_cmd} 2>&1 | tee results/run_log.txt'
```

Timeout: **30 minutes** (adjust based on `estimated_runtime` if provided and > 30 min, or `timeout_override_ms` from manifest).

**On timeout — staggered teardown:**
1. Send SIGTERM to the entire process group: `kill -TERM -$PGID`
2. Wait 10 seconds for graceful shutdown
3. If processes remain, send SIGKILL: `kill -KILL -$PGID`
4. Check for and release any lock files or temporary resources
5. Append `"EXECUTION TIMED OUT. Process group terminated."` to `results/run_log.txt`

**Atomic results staging:**
To prevent half-written results from triggering false early-exit on subsequent runs:
1. Create staging directory: `mkdir -p results/.staging/`
2. Set environment variable `RESULTS_DIR=results/.staging/` (if the execution script respects it) or configure output paths to write to `results/.staging/`
3. After execution completes successfully (exit code 0):
   - Move all files from `results/.staging/` to `results/`: `mv results/.staging/* results/`
   - Remove staging directory: `rmdir results/.staging/`
4. If execution fails:
   - Leave files in `results/.staging/` (they will not trigger early-exit in Step 1)
   - Note in `pre_execution_status.json` that partial results are in `.staging/`

> Note: If the execution script writes directly to paths that cannot be redirected, skip atomic staging and document this in the run log.

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
   - **Fatal / unknown** (segfault, disk full, OOM, novel network error, or any error not matching the above categories): immediately write FAILED status to `results/pre_execution_status.json`. Do NOT attempt auto-fix. Report to user with full traceback and recommend investigating the root cause before retrying.
3. For logic/environment errors: recommend rolling back to Phase 3 (Implement).

**Step 4-TIMEOUT path**:
1. Append `"EXECUTION TIMED OUT."` to `results/run_log.txt`.
2. Inventory what `results/` contains so far.
   Also check `results/.staging/` — if atomic staging was active, partial artifacts may be there instead of `results/`. Include both locations in the inventory presented to the user.
3. Ask user: "The job timed out. Would you like to (a) run it externally and then resume, or (b) continue to testing with partial results?"
4. Record the user's choice in `results/pre_execution_status.json` → proceed to Step 4-PARTIAL.

**Step 4-PARTIAL** (failure or timeout):
Write `results/pre_execution_status.json`:
```json
{
  "state": "FAILED | PARTIAL",
  "error_class": "dependency|compilation|runtime|timeout|resource|fatal|unknown",
  "severity": "recoverable|blocking|fatal",
  "retryable": true,
  "downstream_allowed": true | false,
  "traceback_ref": "results/run_log.txt",
  "next_action": "retry|abort|user_decision"
}
```
Choose the appropriate `state`, `error_class`, and `severity` based on the failure mode:
- **Timeouts**: `"state": "PARTIAL"`, `"error_class": "timeout"`
- **Non-zero exit with partial artifacts**: `"state": "PARTIAL"`
- **Non-zero exit with no usable output**: `"state": "FAILED"`
Set `"downstream_allowed": true` if partial artifacts exist that downstream phases can use, `false` if nothing usable was produced. Set `"retryable": true` for transient failures (timeout, resource), `false` for deterministic failures (compilation, logic).

Announce clearly to the user. Do NOT block the pipeline — proceed to **Step 6**.

### Step 5: Post-execution Inventory

If execution succeeded:
1. Glob `results/**/*` and categorize by extension.
2. If `expected_outputs` is specified in frontmatter, verify each file exists. Report any missing ones.
3. **Silent failure detection**: If exit code was 0 but one or more `required: true` expected outputs are missing, treat this as state `PARTIAL` (not `SUCCESS`). Write `pre_execution_status.json` with `"state": "PARTIAL"`, `"error_class": "silent_failure"`, `"severity": "recoverable"`, and `"downstream_allowed": true`. Announce the discrepancy to the user.
4. Write `results/pre_execution_status.json`:
   ```json
   {
     "state": "SUCCESS",
     "error_class": null,
     "severity": null,
     "retryable": false,
     "downstream_allowed": true,
     "traceback_ref": "results/run_log.txt",
     "next_action": "proceed"
   }
   ```

   > **Note for downstream consumers:** When reading `pre_execution_status.json`, always check the `state` field value — do not treat file existence alone as an indicator of success. See `research-test` Step 0 for the correct guard logic.

   > **Legacy fallback**: If `pre_execution_status.md` exists (legacy v0.8.x workspace), read it and treat any line containing SUCCESS/FAILED/PARTIAL/EXISTING as the state. New runs always write `.json`.
5. **Save source fingerprints** for future staleness detection:
   - Compute SHA-256 hashes of all files in `src/` and `plan/research_plan.md`
   - Save to `results/.source_hashes.json`:
     ```json
     {
       "generated_at": "ISO-8601 timestamp",
       "execution_cmd": "{execution_cmd}",
       "hashes": {
         "src/main.py": "sha256:abc123...",
         "plan/research_plan.md": "sha256:def456..."
       }
     }
     ```
6. Announce success with the artifact summary.

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
