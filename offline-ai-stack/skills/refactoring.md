# Skill: Refactoring

## Think first
- Is this commit purely behavior-preserving? If not, it's two commits.
- Did I run the full test suite *before* I started, and is it green right now?
- Am I tempted to "fix" something the task doesn't require? Note it as follow-up; don't expand scope.
- Is there a prematurely-extracted helper here that I could *inline* rather than refactor further?

Tidy First. Behavior-preserving changes only.

1. Separate refactor commits from feature commits. Never mix.
2. Run the full test suite before and after each refactor; both must be green.
3. Make one structural change per commit (rename, extract, inline, move).
4. Don't refactor what you don't need to touch for the task at hand.
5. If a refactor uncovers a bug, stop, commit the refactor as-is, then fix in a separate commit.
6. Prefer deleting code over abstracting it. Three similar lines beat a premature helper.
