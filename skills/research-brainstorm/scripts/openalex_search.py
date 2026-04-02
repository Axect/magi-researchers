"""Query the OpenAlex API for academic literature.

Used by the MAGI research-brainstorm skill for pre-flight context
gathering (T9) and evidence anchoring (T11).
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://api.openalex.org/works"
DEFAULT_SELECT = (
    "id,title,authorships,publication_year,cited_by_count,"
    "doi,abstract_inverted_index"
)


def reconstruct_abstract(inverted_index: dict | None, max_sentences: int = 2) -> str:
    if not inverted_index:
        return "N/A"
    size = max(pos for positions in inverted_index.values() for pos in positions) + 1
    tokens: list[str] = [""] * size
    for word, positions in inverted_index.items():
        for pos in positions:
            tokens[pos] = word
    full_text = " ".join(t for t in tokens if t)
    sentences = full_text.split(". ")
    return ". ".join(sentences[:max_sentences]).strip() or "N/A"


def build_url(query: str, sort: str, limit: int, filter_str: str, select: str) -> str:
    params: dict[str, str] = {
        "search": query,
        "sort": sort,
        "per-page": str(limit),
        "select": select,
    }
    if filter_str:
        params["filter"] = filter_str
    return BASE_URL + "?" + urllib.parse.urlencode(params)


def fetch_results(url: str, email: str | None) -> dict:
    headers = {"Accept": "application/json"}
    if email:
        headers["User-Agent"] = f"mailto:{email}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(f"HTTP error {exc.code}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"URL error: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"JSON parse error: {exc}", file=sys.stderr)
        sys.exit(1)


def format_markdown(query: str, filter_str: str, sort: str, data: dict) -> str:
    results = data.get("results", [])
    count = len(results)
    lines = [
        f'## OpenAlex Search Results for: "{query}"',
        f"**Filter**: {filter_str or 'none'} | **Sort**: {sort} | **Results**: {count}",
        "",
    ]
    if not results:
        lines.append("_No results found._")
        return "\n".join(lines)
    for i, work in enumerate(results, 1):
        title = work.get("title") or "Untitled"
        year = work.get("publication_year", "?")
        cited = work.get("cited_by_count", 0)
        doi = work.get("doi") or "N/A"
        authorships = work.get("authorships") or []
        if authorships:
            first_author = (
                (authorships[0].get("author") or {}).get("display_name") or "Unknown"
            )
            author_str = f"{first_author} et al." if len(authorships) > 1 else first_author
        else:
            author_str = "Unknown"
        abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
        lines += [
            f"{i}. **{title}** ({year}, cited: {cited})",
            f"   - Authors: {author_str}",
            f"   - DOI: {doi}",
            f"   - Abstract: {abstract}",
            "",
        ]
    return "\n".join(lines)


def format_json(data: dict) -> str:
    results = data.get("results", [])
    for work in results:
        work["abstract_text"] = reconstruct_abstract(work.get("abstract_inverted_index"))
    return json.dumps(data, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--filter", dest="filter_str", default="",
                        help='OpenAlex filter string (e.g., "publication_year:>2021")')
    parser.add_argument("--sort", default="cited_by_count:desc",
                        help="Sort field (default: cited_by_count:desc)")
    parser.add_argument("--limit", type=int, default=10,
                        help="Number of results (default: 10, max: 50)")
    parser.add_argument("--format", dest="fmt", choices=["json", "md"], default="md",
                        help="Output format: json or md (default: md)")
    parser.add_argument("--email", default=None,
                        help="Email for polite pool (gives 10x rate limit)")
    parser.add_argument("--select", default=DEFAULT_SELECT,
                        help="Comma-separated fields to select from OpenAlex")
    args = parser.parse_args()

    limit = min(max(1, args.limit), 50)
    url = build_url(args.query, args.sort, limit, args.filter_str, args.select)
    data = fetch_results(url, args.email)

    if args.fmt == "json":
        print(format_json(data))
    else:
        print(format_markdown(args.query, args.filter_str, args.sort, data))


if __name__ == "__main__":
    main()
