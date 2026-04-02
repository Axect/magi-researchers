# Phase 4a: Macro Resolution Fallback Script

This script is written by Claude to `write/resolve_macros.py` and executed only when `{{fig:id}}` or `{{ref:id}}` patterns are found in `write/revised_draft.md`. If no such patterns exist, skip Phase 4a entirely.

---

## Script Source

```python
# Claude writes this script to write/resolve_macros.py, then executes it
import json
import re
import sys

def resolve_macros(draft_path, inputs_path, ledger_path):
    """Resolve any remaining macros in the draft."""
    with open(draft_path) as f:
        draft = f.read()
    with open(inputs_path) as f:
        inputs = json.load(f)
    with open(ledger_path) as f:
        ledger = json.load(f)

    # Build lookup tables
    evidence_map = {e["id"]: e for e in inputs.get("evidence", [])}
    citation_map = {c["id"]: c for c in ledger.get("citations", [])}

    unresolved = []

    # Resolve {{fig:id}} → markdown image embed
    def resolve_fig(match):
        fig_id = match.group(1)
        if fig_id in evidence_map:
            ev = evidence_map[fig_id]
            return f'![{ev.get("caption", fig_id)}]({ev["ref"]})\n*{ev.get("caption", "")}*'
        unresolved.append(f"{{{{fig:{fig_id}}}}}")
        return match.group(0)

    # Resolve {{ref:id}} → citation text
    def resolve_ref(match):
        ref_id = match.group(1)
        if ref_id in citation_map:
            cit = citation_map[ref_id]
            return f'[{cit.get("source_detail", ref_id)}]'
        unresolved.append(f"{{{{ref:{ref_id}}}}}")
        return match.group(0)

    draft = re.sub(r'\{\{fig:([\w-]+)\}\}', resolve_fig, draft)
    draft = re.sub(r'\{\{ref:([\w-]+)\}\}', resolve_ref, draft)

    with open(draft_path, 'w') as f:
        f.write(draft)

    if unresolved:
        print(f"WARNING: {len(unresolved)} unresolved macros: {', '.join(unresolved)}")
        sys.exit(1)
    else:
        print("All macros resolved (or none found).")

if __name__ == "__main__":
    resolve_macros(sys.argv[1], sys.argv[2], sys.argv[3])
```

---

## Execution

Run with:
```bash
uv run python write/resolve_macros.py write/revised_draft.md write/write_inputs.json write/citation_ledger.json
```

If unresolved macros remain after script execution, Claude manually resolves them by reading the intake data and making inline replacements.

> **Note**: This is a fallback only. The primary evidence integration happens in Phase 2a via pre-inserted evidence blocks. The macro pattern should rarely appear if Phase 2a ran correctly.
