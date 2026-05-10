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

## Plan
For each behavior change:
1. Write the failing test; run it; confirm it fails for the *right* reason.
2. Write the minimum production code to pass; run; confirm green.
3. Stop and run the *full* suite; confirm no regressions.
4. Refactor under the green test; commit at green.
Definition of done: red → green → full-suite-green → refactor-green → commit, in order.
Rollback if: full suite goes red after step 2 — revert your change; the test alone didn't catch a regression.

## Validation
Before committing, verify:
1. The failing test was committed before the production code (or the order is captured in the PR).
2. The failing test failed for the right reason (recorded reproduction line).
3. The full test suite is green post-change.
4. The refactor commit is separate from the green commit.
Pass: TDD order + right-reason fail + full-green + isolated refactor commit.
Fail action: rebase to restore the order; or, if order isn't recoverable, rewrite the PR description.

## Agentic capabilities
- **Tools required:** test runner, git (commit ordering), coverage tool.
- **Subagents:** Dispatch a test-writer subagent if the test design is non-trivial (parameterization, property-based, etc.).
- **Memory writes:** Persist (feature → test pattern, naming) so similar features get consistent coverage.
- **Escalate when:** A test can't be written for the change (architecture forbids it) — refactor first.
- **Autonomy budget:** TDD cycle autonomous. Skipping the failing-test step requires explicit override + justification.

1. Write the failing test first; do not write implementation code yet.
2. Run the test and confirm it fails for the expected reason (not import error).
3. Write the minimum code to make it pass.
4. Run the full suite to catch regressions.
5. Refactor with the test as a safety net.
6. Commit at green.
