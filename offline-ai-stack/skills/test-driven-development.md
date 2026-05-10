# Skill: TDD

## Think first
- Have I written the failing test *before* any production-code change?
- Is the test failing for the *right* reason — not an import error or typo?
- What's the *minimum* implementation that turns this test green?
- Has the full suite stayed green after my refactor step?

## Reasoning
For each behavior change, follow the cycle:
1. Write the failing test; run it; confirm it fails for the *right* reason (not import / typo).
2. Write the minimum production code that makes it pass; run; confirm green.
3. Run the full suite to catch regressions; confirm green.
4. Refactor under the test net; commit at green.

1. Write the failing test first; do not write implementation code yet.
2. Run the test and confirm it fails for the expected reason (not import error).
3. Write the minimum code to make it pass.
4. Run the full suite to catch regressions.
5. Refactor with the test as a safety net.
6. Commit at green.
