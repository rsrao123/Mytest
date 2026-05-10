# Skill: PR Review

## Think first
- Does this PR actually do what its description claims, including the edge cases the description doesn't mention?
- Where would a malicious user — or a careless one — be most likely to break this code?
- Have I addressed all six dimensions (correctness, tests, security, perf, style, docs) proportionally?
- What's my final verdict, in one word: APPROVE / REQUEST_CHANGES / BLOCK?

## Reasoning
Audit each PR in this order, recording findings as you go:
1. **Correctness:** trace the diff against the description's claims, including edges the description omits.
2. **Tests:** new code paths covered? Failure-mode test for each? Existing tests still meaningful?
3. **Security / perf / style / docs** in turn — each finding has file:line evidence.
4. Conclude with a one-word verdict and the top blocker (if any).

## Plan
For each PR:
1. Read description + tests first; predict the diff before opening it.
2. Walk the diff against your prediction; note divergences.
3. Audit correctness / tests / security / perf / style / docs in turn; file:line every finding.
4. Stop and summarize verdict + top blocker before posting the review.
Definition of done: all 6 dimensions audited + verdict posted with file:line evidence.
Rollback if: the review uncovers an architectural problem — escalate to the architect; don't try to fix it in this PR.

## Validation
Before posting, verify:
1. All 6 dimensions (correctness / tests / security / perf / style / docs) are covered.
2. Every finding has a file:line anchor.
3. A verdict (APPROVE / REQUEST_CHANGES / BLOCK) is stated explicitly.
4. The top blocker is named (if any) so the author knows what to fix first.
Pass: 6 dimensions + anchors + verdict + top blocker.
Fail action: complete the missed dimension before posting.

For each PR, audit in this order and report findings with file:line refs.

1. **Correctness** — does it do what the description claims? Edge cases? Off-by-ones?
2. **Tests** — are new code paths covered? At least one failure-mode test?
3. **Security** — input validation, authn/authz, secrets, injection sinks.
4. **Performance** — N+1 queries, unbounded loops, allocations on hot paths.
5. **Style** — matches project conventions; no dead code; no debug prints.
6. **Documentation** — public APIs, ADRs, README updates.

End with a verdict: APPROVE / REQUEST_CHANGES / BLOCK, with the top blocker called out.
