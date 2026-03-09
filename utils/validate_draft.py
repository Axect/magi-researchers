#!/usr/bin/env python3
"""Validate draft.md against section_contracts.json.

Maintained utility — NOT generated at runtime by the LLM.
Used by research-write Phase 4 (DocCI) to validate draft integrity.
"""
import json
import re
import sys
from pathlib import Path


def validate_draft_full(draft_path: str, contracts_path: str, inputs_path: str) -> dict:
    """Validate draft and return structured results dict.

    Returns dict with keys: status, errors, warnings, stats.
    """
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict[str, int] = {}

    # Load files
    try:
        draft_text = Path(draft_path).read_text()
    except FileNotFoundError:
        return {
            "status": "FAILED",
            "errors": [f"Draft not found: {draft_path}"],
            "warnings": [],
            "stats": {},
        }

    try:
        with open(contracts_path) as f:
            contracts = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {
            "status": "FAILED",
            "errors": [f"Cannot read contracts: {e}"],
            "warnings": [],
            "stats": {},
        }

    if not isinstance(contracts, dict):
        return {
            "status": "FAILED",
            "errors": ["section_contracts.json must be a JSON object"],
            "warnings": [],
            "stats": {},
        }

    try:
        with open(inputs_path) as f:
            inputs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {
            "status": "FAILED",
            "errors": [f"Cannot read inputs: {e}"],
            "warnings": [],
            "stats": {},
        }

    if not isinstance(inputs, dict):
        return {
            "status": "FAILED",
            "errors": ["write_inputs.json must be a JSON object"],
            "warnings": [],
            "stats": {},
        }

    # Check evidence block presence
    evidence_blocks_found = set(re.findall(r'<!-- EVIDENCE BLOCK: (ev-\d+) -->', draft_text))
    all_evidence_ids: set[str] = set()
    for e in inputs.get("evidence", []):
        if not isinstance(e, dict):
            warnings.append(f"Evidence item is not a dict, skipping: {e!r}")
            continue
        if "id" in e:
            all_evidence_ids.add(e["id"])

    for section in contracts.get("sections", []):
        if not isinstance(section, dict):
            warnings.append(f"Section contract item is not a dict, skipping: {section!r}")
            continue
        section_id = section.get("id", "unknown")
        for ev_id in section.get("evidence_ids", []):
            if ev_id not in evidence_blocks_found:
                errors.append(f"Section '{section_id}' missing evidence block: {ev_id}")

    # Check for orphaned evidence
    orphaned = all_evidence_ids - evidence_blocks_found
    if orphaned:
        warnings.append(f"Orphaned evidence (not referenced in draft): {', '.join(sorted(orphaned))}")

    # Check LaTeX formatting
    bad_display_math = re.findall(r'\$\$[^\n]+\$\$', draft_text)
    if bad_display_math:
        errors.append(f"Display equations on single line (should use line breaks): {len(bad_display_math)} found")

    # Check required sections exist in draft and word budget (approximate)
    sections_found = 0
    sections_required = 0
    for section in contracts.get("sections", []):
        if not isinstance(section, dict):
            continue
        section_id = section.get("id", "unknown")
        title = section.get("title", section_id)
        sections_required += 1
        pattern = rf'#+\s+{re.escape(title)}.*?\n(.*?)(?=\n#+\s|\Z)'
        match = re.search(pattern, draft_text, re.DOTALL)
        if not match:
            errors.append(f"Required section not found in draft: '{title}' (id: {section_id})")
            continue
        sections_found += 1

        # Check word budget
        max_words = section.get("max_words", 0)
        if max_words == 0:
            continue
        word_count = len(match.group(1).split())
        if word_count > max_words * 1.1:
            warnings.append(f"Section '{section_id}' exceeds budget: {word_count}/{max_words} words")

    stats["sections_found"] = sections_found
    stats["sections_required"] = sections_required
    stats["evidence_blocks"] = len(evidence_blocks_found)
    stats["total_evidence"] = len(all_evidence_ids)

    status = "FAILED" if errors else "PASSED"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }


def validate_draft(draft_path: str, contracts_path: str, inputs_path: str) -> bool:
    """Validate draft and print human-readable results. Returns True on pass."""
    result = validate_draft_full(draft_path, contracts_path, inputs_path)

    if result["status"] == "FAILED":
        print("VALIDATION FAILED:")
        for e in result["errors"]:
            print(f"  - {e}")
        for w in result["warnings"]:
            print(f"  [warning] {w}")
        return False

    if result["warnings"]:
        print("VALIDATION PASSED (with warnings):")
        for w in result["warnings"]:
            print(f"  [warning] {w}")
    else:
        print("VALIDATION PASSED")
    return True


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--json"]
    use_json = "--json" in sys.argv[1:]

    if len(args) != 3:
        print(f"Usage: {sys.argv[0]} [--json] <draft.md> <section_contracts.json> <write_inputs.json>")
        sys.exit(2)

    if use_json:
        result = validate_draft_full(args[0], args[1], args[2])
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] == "PASSED" else 1)
    else:
        success = validate_draft(args[0], args[1], args[2])
        sys.exit(0 if success else 1)
