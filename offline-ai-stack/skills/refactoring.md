# Skill: Refactoring

## Think first
- Is this commit purely behavior-preserving? If not, it's two commits.
- Did I run the full test suite *before* I started, and is it green right now?
- Am I tempted to "fix" something the task doesn't require? Note it as follow-up; don't expand scope.
- Is there a prematurely-extracted helper here that I could *inline* rather than refactor further?

## Reasoning
For each refactor, work through:
1. Run the full test suite *before* starting; confirm green. (No green, no refactor.)
2. State the structural change in one sentence; verify it's behavior-preserving by construction.
3. Apply the smallest single structural change; re-run all tests; confirm green again.
4. Commit alone — never bundle with feature work or unrelated cleanups.

## Plan
For each refactor:
1. Confirm full test suite green pre-change. (No green, no refactor.)
2. Apply a single structural change.
3. Stop and re-run the full suite; confirm green.
4. Commit alone with a `refactor:` subject; never bundle with feature work.
Definition of done: green-pre + green-post + isolated commit.
Rollback if: tests fail post-change — revert the structural change; the refactor wasn't behavior-preserving.

## Validation
Before pushing, verify:
1. Test suite was green pre-change (recorded in PR description).
2. Test suite is green post-change.
3. Commit subject prefixed `refactor:`; no behavior changes appear in the diff.
4. The commit stands alone — no feature / fix / docs work bundled.
Pass: green-pre + green-post + isolated + behavior-preserving.
Fail action: revert; the refactor wasn't safe.

## Agentic capabilities
- **Tools required:** test runner (pre + post), git (commit, diff), language-aware refactor tools where available.
- **Subagents:** Dispatch a test-runner subagent for full-suite verification at each step.
- **Memory writes:** Persist (file → safe-refactor patterns) for future refactors of similar code.
- **Escalate when:** A refactor reveals a behavior bug — file a separate fix; do not bundle.
- **Autonomy budget:** Pure refactors autonomous. Refactors touching > 5 files require architect review.

Tidy First. Behavior-preserving changes only.

1. Separate refactor commits from feature commits. Never mix.
2. Run the full test suite before and after each refactor; both must be green.
3. Make one structural change per commit (rename, extract, inline, move).
4. Don't refactor what you don't need to touch for the task at hand.
5. If a refactor uncovers a bug, stop, commit the refactor as-is, then fix in a separate commit.
6. Prefer deleting code over abstracting it. Three similar lines beat a premature helper.
