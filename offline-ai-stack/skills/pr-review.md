# Skill: PR Review
For each PR, audit in this order and report findings with file:line refs.

1. **Correctness** — does it do what the description claims? Edge cases? Off-by-ones?
2. **Tests** — are new code paths covered? At least one failure-mode test?
3. **Security** — input validation, authn/authz, secrets, injection sinks.
4. **Performance** — N+1 queries, unbounded loops, allocations on hot paths.
5. **Style** — matches project conventions; no dead code; no debug prints.
6. **Documentation** — public APIs, ADRs, README updates.

End with a verdict: APPROVE / REQUEST_CHANGES / BLOCK, with the top blocker called out.
