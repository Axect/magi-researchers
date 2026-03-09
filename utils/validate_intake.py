#!/usr/bin/env python3
"""Validate write_inputs.json and citation_ledger.json schemas.

Maintained utility — NOT generated at runtime by the LLM.
Used by research-write Phase 0c to validate intake artifacts.
"""
import json
import sys


def validate_intake(inputs_path: str, ledger_path: str) -> bool:
    errors: list[str] = []

    # Load and validate write_inputs.json
    try:
        with open(inputs_path) as f:
            inputs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"VALIDATION FAILED: Cannot read {inputs_path}: {e}")
        return False

    if not isinstance(inputs, dict):
        errors.append("write_inputs.json must be a JSON object")
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False

    required_keys = ["source_dir", "mode", "audience", "domain", "claims", "evidence"]
    for key in required_keys:
        if key not in inputs:
            errors.append(f"write_inputs.json missing required key: {key}")

    # Validate claim-evidence links
    evidence_ids: set[str] = set()
    for e in inputs.get("evidence", []):
        if not isinstance(e, dict):
            errors.append(f"Evidence item is not a dict: {e!r}")
            continue
        if "id" in e:
            evidence_ids.add(e["id"])

    for claim in inputs.get("claims", []):
        if not isinstance(claim, dict):
            errors.append(f"Claim item is not a dict: {claim!r}")
            continue
        if "id" not in claim or "text" not in claim:
            errors.append(f"Claim missing required fields (id, text): {claim}")
        for ev_id in claim.get("evidence_ids", []):
            if ev_id not in evidence_ids:
                errors.append(f"Claim {claim.get('id', '?')} references unknown evidence: {ev_id}")

    # Load and validate citation_ledger.json
    try:
        with open(ledger_path) as f:
            ledger = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"VALIDATION FAILED: Cannot read {ledger_path}: {e}")
        return False

    if not isinstance(ledger, dict):
        errors.append("citation_ledger.json must be a JSON object")
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False

    claim_ids: set[str] = set()
    for c in inputs.get("claims", []):
        if isinstance(c, dict) and "id" in c:
            claim_ids.add(c["id"])

    for citation in ledger.get("citations", []):
        if not isinstance(citation, dict):
            errors.append(f"Citation item is not a dict: {citation!r}")
            continue
        cid = citation.get("claim_id")
        if cid and cid not in claim_ids:
            errors.append(f"Citation {citation.get('id', '?')} references unknown claim: {cid}")

        # Validate citation structure when optional fields are present
        if "source_type" in citation:
            if not isinstance(citation["source_type"], str):
                errors.append(f"Citation {citation.get('id', '?')}: 'source_type' must be a string")
        if "resolved" in citation:
            if not isinstance(citation["resolved"], bool):
                errors.append(f"Citation {citation.get('id', '?')}: 'resolved' must be a boolean")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False

    n_claims = len(inputs.get("claims", []))
    n_evidence = len(inputs.get("evidence", []))
    n_citations = len(ledger.get("citations", []))
    print(f"VALIDATION PASSED: {n_claims} claims, {n_evidence} evidence items, {n_citations} citations")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <write_inputs.json> <citation_ledger.json>")
        sys.exit(2)
    success = validate_intake(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
