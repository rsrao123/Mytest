# Skill: Requesting Code Review

## Think first
- Have I run linters, formatters, and the full test suite myself before asking anyone to look?
- Can a reviewer pick this up cold from the description alone — what + why + how to verify?
- What questions would I ask if I were reviewing this? Are they pre-empted in the description?
- Is this one PR per concern, or have I sneaked in a refactor / unrelated cleanup?

1. Self-review first. Run the diff through your own eyes and the linters before paging anyone.
2. Write the description so the reviewer can pick it up cold: what + why + how to verify.
3. Pre-empt the obvious questions in the description ("I considered X but chose Y because…").
4. Mark draft if the diff isn't ready for behavior review. Don't ask for time you'll waste.
5. One PR per concern. If you have a refactor and a feature, that's two PRs.
6. When you push fixups, summarize what changed since the last round so the reviewer doesn't re-read everything.
