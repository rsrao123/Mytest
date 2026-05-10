# Skill: Making Changes Incrementally

## Think first
- Is this diff under ~200 net lines? If not, where can I split it without breaking the build?
- Are structural changes (rename, extract, move) mixed in with behavior changes? They want to be sequenced, not bundled.
- Will every commit on this branch compile and pass tests in isolation? Is the chain `git bisect`-able?
- Is there a feature-flag-off path I should ship first, then flip in a follow-up?

## Reasoning
For each branch, work through:
1. Estimate net diff size; if > ~200 lines, list concrete split points before starting.
2. Order the splits: structural first (rename, extract, move), then behavior — never bundled.
3. Verify each commit compiles and passes tests in isolation; chain must be `git bisect`-able.
4. Plan the flag-off + flip sequence for risky behavior changes; ship the off path first.

## Plan
Before pushing the branch:
1. Estimate net diff size; if > 200 lines, list concrete split points and split.
2. Sequence: structural commits first (rename/extract/move), then behavior commits.
3. Stop after each commit; verify build + tests green in isolation before continuing.
4. For risky behavior, ship the flag-off path first; flip in a follow-up PR.
Definition of done: every commit compiles + tests green + total diff < 200 lines net.
Rollback if: a commit breaks `git bisect` — revert it before continuing the chain.

## Validation
Before requesting review, verify:
1. `git log --oneline base..HEAD` shows commits in structural-then-behavior order.
2. Net diff < 200 lines; if larger, the description justifies it.
3. `git bisect run` succeeds across the chain; every commit compiles + tests green.
4. For risky behavior changes, the flag-off path is in a separate landed PR.
Pass: order + size + bisectable + flag-off-first.
Fail action: rebase to split; rerun bisect.

1. Aim for small, reviewable diffs (≤ ~200 lines net). Bigger diffs hide mistakes and stall reviews.
2. Land structural changes first (renames, extracts, moves), then behavior changes — never bundle them.
3. Each commit must compile and pass tests. The chain should be `git bisect`-able.
4. If a change requires a flag, ship the flag-off path first; flip the flag in a follow-up.
5. When a refactor balloons, stop. Commit what works, open a new branch for the rest.
6. Prefer reversible changes when uncertain. Reversibility buys you time to learn.
