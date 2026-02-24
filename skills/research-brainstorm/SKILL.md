# Research Brainstorm Skill

## Description
Generates and cross-validates research ideas using Gemini and Codex in parallel, then synthesizes results with Claude.

## Usage
```
/research-brainstorm "research topic" [--domain physics|ai_ml|statistics|mathematics|paper]
```

## Arguments
- `$ARGUMENTS` — The research topic and optional domain flag

## Instructions

### MCP Tool Rules
- **Gemini**: Use the following model fallback chain. Try each model in order; if a call fails (error, timeout, or model-not-found), retry with the next model:
  1. `model: "gemini-3.1-pro-preview"` (preferred)
  2. `model: "gemini-3-pro-preview"` (fallback)
  3. `model: "gemini-2.5-pro"` (last resort)
- **Codex**: Use `mcp__codex-cli__brainstorm` for ideation, `mcp__codex-cli__ask-codex` for analysis/review.

When this skill is invoked, follow these steps exactly:

### Step 0: Setup

1. Parse the research topic from `$ARGUMENTS`. If a `--domain` flag is provided, note the domain (physics, ai_ml, statistics, mathematics, paper). Otherwise, infer the domain from the topic.
2. Create the output directory: `outputs/{sanitized_topic}_{YYYYMMDD}_v{N}/brainstorm/`
   - Sanitize the topic: lowercase, replace spaces with underscores, remove special characters, truncate to 50 chars.
   - Use today's date in YYYYMMDD format.
   - Version: Glob for `outputs/{sanitized_topic}_{YYYYMMDD}_v*/` and set N = max existing + 1 (start at v1).
3. If a domain template exists at `${CLAUDE_PLUGIN_ROOT}/templates/domains/{domain}.md`, read it for context.

### Step 1a: Parallel Independent Brainstorming

Execute these two calls **simultaneously** (in the same message):

**Gemini Brainstorming:**
```
mcp__gemini-cli__brainstorm(
  prompt: "{topic} — Generate diverse, creative research ideas. Consider theoretical foundations, practical applications, novel approaches, and potential breakthroughs.",
  model: "gemini-3.1-pro-preview",  // fallback: "gemini-3-pro-preview" → "gemini-2.5-pro"
  domain: "{domain}",
  methodology: "auto",
  ideaCount: 12,
  includeAnalysis: true,
  existingContext: "{domain template content if available}"
)
```

**Codex Brainstorming:**
```
mcp__codex-cli__brainstorm(
  prompt: "{topic} — Generate implementation-focused research ideas. Consider feasibility, existing tools/libraries, computational requirements, and step-by-step approaches.",
  domain: "{domain}",
  methodology: "auto",
  ideaCount: 12,
  includeAnalysis: true,
  existingContext: "{domain template content if available}"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__brainstorm` with the Gemini fallback chain and implementation-focused framing.

Save results to:
- `brainstorm/gemini_ideas.md` — Gemini's raw output with header noting source and timestamp
- `brainstorm/codex_ideas.md` — Codex's raw output with header noting source and timestamp

### Step 1b: Cross-Check

After both brainstorming results are saved, execute these two calls **simultaneously**:

**Gemini reviews Codex ideas:**
```
mcp__gemini-cli__ask-gemini(
  prompt: "Review the following research ideas for technical feasibility, scientific rigor, novelty, and potential impact. Identify strengths, weaknesses, and suggest improvements for each idea.\n\n{codex_ideas content}",
  model: "gemini-3.1-pro-preview"  // fallback: "gemini-3-pro-preview" → "gemini-2.5-pro"
)
```

**Codex reviews Gemini ideas:**
```
mcp__codex-cli__ask-codex(
  prompt: "Review the following research ideas for implementation feasibility, computational practicality, available tools/datasets, and timeline realism. Identify strengths, weaknesses, and suggest improvements for each idea.\n\n{gemini_ideas content}"
)
```

> Note: If Codex MCP is unavailable, fall back to `mcp__gemini-cli__ask-gemini` with the Gemini fallback chain.

Save results to:
- `brainstorm/gemini_review_of_codex.md`
- `brainstorm/codex_review_of_gemini.md`

### Step 1c: Claude Synthesis

1. Read all 4 documents (gemini_ideas, codex_ideas, gemini_review_of_codex, codex_review_of_gemini).
2. Synthesize into a coherent research direction document that includes:
   - **Top Research Directions** (ranked by combined novelty + feasibility + impact)
   - **Key Technical Approaches** for each direction
   - **Consensus Points** — ideas both models agreed on
   - **Divergence Points** — areas of disagreement and how to resolve them
   - **Recommended Path Forward** — Claude's recommendation with reasoning
3. Save to `brainstorm/synthesis.md`.

### Step 2: User Feedback

Present the synthesis to the user with:
- A concise summary of the top 3-5 research directions
- Clear options for the user to choose, modify, or combine directions
- Ask for any additional constraints or preferences

Wait for user input before proceeding.

## Output Files
```
brainstorm/
├── gemini_ideas.md
├── codex_ideas.md
├── gemini_review_of_codex.md
├── codex_review_of_gemini.md
└── synthesis.md
```
