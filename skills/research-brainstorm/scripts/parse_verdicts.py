"""Parse MAGI T2 review .md files to extract and count verdict annotations."""

import re
import json
import argparse
import sys
import pathlib

VERDICT_PATTERN = re.compile(r'\*\*(AGREE|DISAGREE|INSUFFICIENT)\*\*')
IDEA_PATTERN = re.compile(r'\(0\)\s*\*\*Identity check\*\*:\s*(.+)', re.IGNORECASE)


def parse_file(path: pathlib.Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    results = []
    current_idea = None

    for line in lines:
        idea_match = IDEA_PATTERN.search(line)
        if idea_match:
            current_idea = idea_match.group(1).strip()

        verdict_match = VERDICT_PATTERN.search(line)
        if verdict_match:
            results.append({
                "idea": current_idea,
                "verdict": verdict_match.group(1),
                "source_file": path.name,
            })
            current_idea = None  # reset after consuming

    return results


def compute_summary(verdicts: list[dict]) -> dict:
    n_agree = sum(1 for v in verdicts if v["verdict"] == "AGREE")
    n_disagree = sum(1 for v in verdicts if v["verdict"] == "DISAGREE")
    n_insufficient = sum(1 for v in verdicts if v["verdict"] == "INSUFFICIENT")
    n_total = len(verdicts)
    contention_score = (n_disagree + n_insufficient) / n_total if n_total > 0 else 0.0
    return {
        "n_agree": n_agree,
        "n_disagree": n_disagree,
        "n_insufficient": n_insufficient,
        "n_total": n_total,
        "contention_score": round(contention_score, 4),
        "verdicts": verdicts,
    }


def format_json(summary: dict) -> str:
    return json.dumps(summary, indent=2, ensure_ascii=False)


def format_markdown(summary: dict) -> str:
    lines = [
        "## Verdict Analysis",
        "",
        f"**Verdict counts**: AGREE={summary['n_agree']}, DISAGREE={summary['n_disagree']}, "
        f"INSUFFICIENT={summary['n_insufficient']}, Total={summary['n_total']}",
        f"**Contention score**: {summary['contention_score']:.2f}",
        "",
        "### Per-idea verdicts",
        "| # | Idea | Verdict | Source |",
        "|---|------|---------|--------|",
    ]
    for i, v in enumerate(summary["verdicts"], 1):
        idea = v["idea"] or "—"
        lines.append(f"| {i} | {idea} | {v['verdict']} | {v['source_file']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=pathlib.Path, help="Review .md file(s) to parse")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Output format (default: json)")
    args = parser.parse_args()

    all_verdicts = []
    for path in args.files:
        if not path.exists():
            print(f"Warning: file not found: {path}", file=sys.stderr)
            continue
        all_verdicts.extend(parse_file(path))

    summary = compute_summary(all_verdicts)

    if args.format == "md":
        print(format_markdown(summary))
    else:
        print(format_json(summary))


if __name__ == "__main__":
    main()
