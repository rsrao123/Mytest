# Skill: Code Search

## Think first
- What am I really looking for — the symbol's definition, its call sites, or its tests?
- What naming conventions does this codebase use (snake_case, camelCase, kebab-case)?
- How many hits is "too many" before I stop and narrow by file type or directory?
- What ±20-line context will I need around each hit to interpret it?

## Reasoning
Plan each search before running it:
1. State the target precisely: definition, call sites, tests, or all three?
2. Pick the right filters: word boundaries (`-w`), file types (`--type`), path scope.
3. Predict rough hit count; if > ~50, narrow further before reading any.
4. Rank results by likely relevance (same module > sibling tests > elsewhere) before opening files.

1. Start with `rg -n` (ripgrep) at the repo root; prefer it over grep for speed.
2. Search for the symbol's definition before chasing call sites: `rg -n "def <name>|fn <name>|function <name>|class <name>"`.
3. Use word boundaries (`-w`) when names are short or common.
4. Rank results: same module > sibling test files > other modules.
5. When a search returns >50 hits, narrow with `--type` or by directory before reading.
6. Read the surrounding ±20 lines, not just the matched line.
