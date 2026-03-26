#!/usr/bin/env python3
"""Validate JSON artifacts against their JSON Schema definitions.

Maintained utility — NOT generated at runtime by the LLM.
Used at phase transitions to enforce data contracts between pipeline phases.

Supports auto-detection of the correct schema based on filename, or explicit
schema specification via --schema flag.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema.validators import validator_for
except ImportError:
    print(
        "ERROR: jsonschema is required. Install with: uv add jsonschema",
        file=sys.stderr,
    )
    sys.exit(2)

# Schema directory relative to this script
SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

# Filename pattern → schema file mapping
# Keys are matched against the artifact filename (not path)
SCHEMA_MAP: dict[str, str] = {
    "weights.json": "weights.schema.json",
    "plot_manifest.json": "plot_manifest.schema.json",
    "execution_manifest.json": "execution_manifest.schema.json",
    "report_versions.json": "report_versions.schema.json",
    "write_inputs.json": "write_inputs.schema.json",
    "citation_ledger.json": "citation_ledger.schema.json",
    "section_contracts.json": "section_contracts.schema.json",
}

# Suffix patterns for checkpoint files (brainstorm_checkpoint.json, plan_checkpoint.json, etc.)
CHECKPOINT_SUFFIX = "_checkpoint.json"


def detect_schema(artifact_path: str) -> Path | None:
    """Auto-detect the correct schema for a given artifact filename.

    Returns the schema Path, or None if no matching schema is found.
    """
    filename = Path(artifact_path).name

    # Direct match
    if filename in SCHEMA_MAP:
        return SCHEMAS_DIR / SCHEMA_MAP[filename]

    # Checkpoint pattern: *_checkpoint.json
    if filename.endswith(CHECKPOINT_SUFFIX):
        return SCHEMAS_DIR / "checkpoint.schema.json"

    return None


def load_json_file(path: str) -> Any:
    """Load a JSON file. Raises on error."""
    with open(path) as f:
        return json.load(f)


def validate_one(data_path: str, schema_path: str | None = None) -> dict:
    """Validate a single JSON artifact against its schema.

    Args:
        data_path: Path to the JSON artifact to validate.
        schema_path: Explicit schema path. If None, auto-detected from filename.

    Returns:
        dict with keys: status, errors, warnings, artifact, schema.
    """
    result: dict = {
        "status": "fail",
        "errors": [],
        "warnings": [],
        "artifact": str(data_path),
        "schema": None,
    }

    # Resolve schema
    if schema_path:
        resolved_schema = Path(schema_path)
    else:
        resolved_schema = detect_schema(data_path)

    if resolved_schema is None:
        result["errors"].append(
            f"No schema found for '{Path(data_path).name}'. "
            f"Use --schema to specify explicitly."
        )
        return result

    if not resolved_schema.exists():
        result["errors"].append(f"Schema file not found: {resolved_schema}")
        return result

    result["schema"] = str(resolved_schema)

    # Load artifact
    try:
        data: Any = load_json_file(data_path)
    except FileNotFoundError:
        result["errors"].append(f"File not found: {data_path}")
        return result
    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON in {data_path}: {e}")
        return result

    # Load schema
    try:
        schema_obj = load_json_file(str(resolved_schema))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        result["errors"].append(f"Cannot read schema: {e}")
        return result

    if not isinstance(schema_obj, dict):
        result["errors"].append(f"Schema must be a JSON object: {resolved_schema}")
        return result

    schema: dict = schema_obj  # type-narrowed

    # Validate
    cls = validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema)

    validation_errors = sorted(
        validator.iter_errors(data), key=lambda e: list(e.path)
    )
    for error in validation_errors:
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        result["errors"].append(f"[{path}] {error.message}")

    if not result["errors"]:
        result["status"] = "pass"

    return result


def validate_directory(output_dir: str) -> dict:
    """Scan an output directory and validate all recognized JSON artifacts.

    Returns:
        dict with keys: status, total, passed, failed, results.
    """
    output_path = Path(output_dir)
    if not output_path.is_dir():
        return {
            "status": "fail",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "results": [],
            "errors": [f"Not a directory: {output_dir}"],
        }

    results = []
    for json_file in sorted(output_path.rglob("*.json")):
        # Skip workspace anchor and hidden files
        if json_file.name.startswith("."):
            continue

        # Only validate files that have a matching schema
        schema = detect_schema(str(json_file))
        if schema is None:
            continue

        result = validate_one(str(json_file))
        results.append(result)

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")

    return {
        "status": "pass" if failed == 0 else "fail",
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": results,
    }


def print_result(result: dict) -> None:
    """Print a single validation result in human-readable format."""
    artifact = result["artifact"]
    status = result["status"].upper()
    schema_name = Path(result["schema"]).name if result["schema"] else "unknown"

    if status == "PASS":
        print(f"  PASS  {artifact} (against {schema_name})")
    else:
        print(f"  FAIL  {artifact} (against {schema_name})")
        for err in result["errors"]:
            print(f"        - {err}")

    for warn in result.get("warnings", []):
        print(f"        [warning] {warn}")


def print_summary(batch: dict) -> None:
    """Print batch validation summary."""
    for result in batch["results"]:
        print_result(result)

    total = batch["total"]
    passed = batch["passed"]
    failed = batch["failed"]
    status = "PASSED" if failed == 0 else "FAILED"

    print(f"\nSCHEMA VALIDATION {status}: {passed}/{total} artifacts valid")
    if failed > 0:
        print(f"  {failed} artifact(s) failed validation")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    use_json = "--json" in sys.argv[1:]
    schema_flag = None

    # Parse --schema flag
    for i, a in enumerate(sys.argv[1:], 1):
        if a == "--schema" and i < len(sys.argv) - 1:
            schema_flag = sys.argv[i + 1]
            args = [a for a in args if a != schema_flag]
            break

    if len(args) == 0:
        print(
            f"Usage: {sys.argv[0]} [--json] [--schema <schema.json>] <artifact.json|output_dir> [...]",
            file=sys.stderr,
        )
        print(
            "\nValidate JSON artifacts against their JSON Schema definitions.",
            file=sys.stderr,
        )
        print(
            "\nIf a directory is given, recursively scans for all recognized artifacts.",
            file=sys.stderr,
        )
        print(
            f"\nAuto-detected schemas: {', '.join(sorted(SCHEMA_MAP.keys()))}, *{CHECKPOINT_SUFFIX}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Single directory mode
    if len(args) == 1 and Path(args[0]).is_dir():
        batch = validate_directory(args[0])
        if use_json:
            print(json.dumps(batch, indent=2))
        else:
            if batch["total"] == 0:
                print(f"No recognized JSON artifacts found in {args[0]}")
            else:
                print_summary(batch)
        sys.exit(0 if batch["status"] == "pass" else 1)

    # Multiple files mode
    all_results = []
    for artifact in args:
        result = validate_one(artifact, schema_path=schema_flag)
        all_results.append(result)

    passed = sum(1 for r in all_results if r["status"] == "pass")
    failed = sum(1 for r in all_results if r["status"] == "fail")
    batch = {
        "status": "pass" if failed == 0 else "fail",
        "total": len(all_results),
        "passed": passed,
        "failed": failed,
        "results": all_results,
    }

    if use_json:
        print(json.dumps(batch, indent=2))
    else:
        print_summary(batch)

    sys.exit(0 if batch["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
