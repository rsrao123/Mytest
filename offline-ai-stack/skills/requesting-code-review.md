# Skill: Requesting Code Review

## Think first
- Have I run linters, formatters, and the full test suite myself before asking anyone to look?
- Can a reviewer pick this up cold from the description alone — what + why + how to verify?
- What questions would I ask if I were reviewing this? Are they pre-empted in the description?
- Is this one PR per concern, or have I sneaked in a refactor / unrelated cleanup?

## Reasoning
Before requesting review, work through:
1. Run linters / formatters / full test suite yourself; resolve everything cleanly first.
2. Predict the reviewer's first three questions; pre-empt each in the PR description.
3. Confirm one PR per concern; if not, split before pushing.
4. If any path isn't ready for behavior review, mark the PR as draft — don't burn reviewer time.

## Plan
Before pinging a reviewer:
1. Run linters / formatters / full test suite yourself; resolve everything.
2. Predict the reviewer's first 3 questions; pre-empt each in the description.
3. Confirm one PR per concern; split if not.
4. Stop and self-review the diff one more pass before requesting review.
Definition of done: clean self-review + answered-in-advance description + one PR per concern.
Rollback if: the reviewer asks something obvious — the description failed; rewrite it before resuming review.

## Validation
Before pinging the reviewer, verify:
1. Linters + formatters + full test suite all green locally.
2. The description pre-empts the obvious questions; "I considered X but…" present where relevant.
3. The PR contains exactly one concern; no hidden refactors / cleanups.
4. Draft status is used if any path isn't ready for behavior review.
Pass: green + pre-emptive + single concern + draft-state-correct.
Fail action: fix locally and rewrite description; don't burn reviewer time.

1. Self-review first. Run the diff through your own eyes and the linters before paging anyone.
2. Write the description so the reviewer can pick it up cold: what + why + how to verify.
3. Pre-empt the obvious questions in the description ("I considered X but chose Y because…").
4. Mark draft if the diff isn't ready for behavior review. Don't ask for time you'll waste.
5. One PR per concern. If you have a refactor and a feature, that's two PRs.
6. When you push fixups, summarize what changed since the last round so the reviewer doesn't re-read everything.
