# Skill: Code Search
1. Start with `rg -n` (ripgrep) at the repo root; prefer it over grep for speed.
2. Search for the symbol's definition before chasing call sites: `rg -n "def <name>|fn <name>|function <name>|class <name>"`.
3. Use word boundaries (`-w`) when names are short or common.
4. Rank results: same module > sibling test files > other modules.
5. When a search returns >50 hits, narrow with `--type` or by directory before reading.
6. Read the surrounding ±20 lines, not just the matched line.
