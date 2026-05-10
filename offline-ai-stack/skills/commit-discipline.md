# Skill: Commit Discipline

## Think first
- Could I describe this commit's purpose with the word "and"? If yes, where does it split?
- Is anything in this diff a refactor masquerading as a feature change?
- What's the one-line subject that captures *intent*, not just the file or function changed?
- Are there debug prints, .env edits, or unintended secrets I haven't reviewed?

## Reasoning
Before each commit, work through:
1. State the commit's intent in one sentence; if "and" appears, mark a split point.
2. Classify each chunk in the diff: feature / fix / refactor / docs / test.
3. Confirm exactly one chunk type is present; isolate the rest into separate commits.
4. Draft the conventional-commits subject line: `type(scope): subject` (imperative, ≤ 72 chars).

## Plan
Before each commit:
1. Review the staged diff; tag chunks (feature / fix / refactor / docs / test).
2. If multiple tags appear, unstage and split into separate commits.
3. Stop and run pre-commit hooks (linters, formatters, tests); resolve all failures.
4. Definition of done: one tag per commit + green hooks + conventional subject line.
Rollback if: a hook fails — fix and create a NEW commit. Never `--amend` already-pushed commits.

## Validation
Before pushing, verify:
1. `git log --oneline @{push}..HEAD` shows one tag per commit.
2. No commit subject contains " and "; none exceeds 72 chars.
3. Pre-commit hooks pass on each commit individually.
4. No `--amend` of any already-pushed commit.
Pass: all 4 checks green.
Fail action: rebase to split offending commits; rerun hooks.

1. Atomic commits: one logical change per commit. If you'd describe it with "and", split it.
2. Conventional Commits format: `type(scope): subject` where type ∈ {feat, fix, refactor, perf, test, docs, chore, build, ci}.
3. Subject in imperative mood, ≤72 chars, no trailing period.
4. Body explains the WHY, not the WHAT.
5. Never commit commented-out code, debug prints, or `.env` files.
6. Don't `--amend` published commits. Add a fix commit instead.
7. Refactor commits and feature commits never share a commit.
