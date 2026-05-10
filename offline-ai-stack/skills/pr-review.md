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

## Agentic capabilities
- **Tools required:** FileReadTool, git, PR comment poster, test runner (to verify diff claims).
- **Subagents:** Dispatch parallel sub-reviewers per dimension (correctness / tests / security / perf / style / docs).
- **Memory writes:** Persist (file → recurring findings) so authors see patterns over time.
- **Escalate when:** Verdict would be BLOCK — copy the architect on the comment.
- **Autonomy budget:** APPROVE / REQUEST_CHANGES autonomously. BLOCK requires architect concurrence.

For each PR, audit in this order and report findings with file:line refs.

1. **Correctness** — does it do what the description claims? Edge cases? Off-by-ones?
2. **Logic errors** — wrong branch, wrong predicate, wrong default, missed `else`.
3. **Edge cases** — empty / zero / negative / max / unicode / race / partial-failure paths.
4. **Tests** — are new code paths covered? At least one failure-mode test? Are existing tests still meaningful or have they been weakened?
5. **Missing tests** — name the untested branches; do not let "tests pass" stand in for "tests cover this".
6. **Duplicated code** — same logic appearing in two places that should converge.
7. **Bad architecture** — coupling across layers, broken abstraction, hidden state.
8. **Over-engineering** — abstractions, options, or flags with no current caller.
9. **Poor naming** — names that don't predict behavior; misleading verbs / nouns.
10. **Error handling** — bare `except:`, swallowed errors, untyped failures.
11. **Project rule violations** — CONVENTIONS.md, CLAUDE.md, lint config, code-owners.
12. **Git diff context** — `git log` / `blame` on touched lines; what was the recent intent?
13. **Security** — input validation, authn/authz, secrets, injection sinks (cross-link to `security-review`).
14. **Performance** — N+1 queries, unbounded loops, allocations on hot paths.
15. **Style** — matches project conventions; no dead code; no debug prints.
16. **Documentation** — public APIs, ADRs, README updates.

End with a verdict: APPROVE / REQUEST_CHANGES / BLOCK, with the top blocker called out.
