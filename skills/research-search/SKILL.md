# Research Search Skill

## Description
Searches academic literature via OpenAlex (240M+ works) and optionally web sources. Standalone skill for quick literature discovery without the full brainstorm pipeline.

## Usage
```
/research-search "topic" [--filter "..."] [--sort cited_by_count:desc|relevance_score:desc|publication_year:desc] [--limit N] [--web] [--save path/to/output.md]
```

## Arguments
- `$ARGUMENTS` — The search topic (required) and optional flags:
  - `--filter` — OpenAlex filter string (default: `"publication_year:>2021,type:article|review"`). Valid types: article, review, preprint, book-chapter, book, dataset, dissertation, report.
  - `--sort` — Sort order (default: `relevance_score:desc`). Options: `relevance_score:desc`, `cited_by_count:desc`, `publication_year:desc`.
  - `--limit` — Number of results (default: 10, max: 50).
  - `--web` — Also run a WebSearch for recent developments (default: false).
  - `--save` — Save results to a file instead of displaying inline. Accepts a relative or absolute path.

## Instructions

> **Shared rules**: Read `${CLAUDE_PLUGIN_ROOT}/shared/rules.md` before starting. §LaTeX applies to this skill.

When this skill is invoked, follow these steps:

### Step 1: Parse Arguments

1. Extract the search topic from `$ARGUMENTS`.
2. Parse optional flags with defaults:
   - `filter`: `"publication_year:>2021,type:article|review"`
   - `sort`: `relevance_score:desc`
   - `limit`: `10`
   - `web`: `false`
   - `save`: `null` (display inline)

### Step 2: Academic Literature Search (OpenAlex)

Run the bundled OpenAlex search script:
```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/research-brainstorm/scripts/openalex_search.py "{topic}" --filter "{filter}" --sort "{sort}" --limit {limit} --format md
```

If results are sparse (< 3 papers):
1. Simplify the query: drop domain-specific jargon, keep core concepts.
2. Retry with broader filter: `--filter "publication_year:>2019,type:article|review|preprint"`.
3. If still sparse, retry without type filter: `--filter "publication_year:>2019"`.

### Step 3: Web Search (optional)

If `--web` is specified:
```
WebSearch(query: "{topic} recent advances 2024 2025 2026")
```

Extract the top 5 web results with source URLs.

### Step 4: Format and Present Results

Combine results into a structured output:

```markdown
## Literature Search: "{topic}"

### Academic Papers (OpenAlex)
**Filter**: {filter} | **Sort**: {sort} | **Results**: {count}

[numbered list from openalex_search.py output]

### Recent Developments (Web)
[key findings with source URLs — only if --web]

### Summary
- Total academic papers found: {N}
- Most cited: "{title}" ({year}, {citations} citations)
- Year range: {min_year}–{max_year}
- Dominant themes: [2-3 key themes from abstracts]
```

### Step 5: Save or Display

- If `--save` is specified: write the formatted output to the given path.
- Otherwise: display inline in the conversation.
