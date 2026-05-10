# Skill: QA Validation

## Think first
- What's the *minimum* set of checks that constitutes "ready"? Don't gold-plate; don't undertest.
- Which checks are blocking (PR can't merge) vs informational (must report)?
- For each failing check: is the failure new on this PR, or pre-existing baseline? Don't block on baselines.
- Are the test results deterministic, or could a rerun change the verdict?

## Reasoning
For each release-readiness audit:
1. Inventory checks: unit / integration / build / lint / security / coverage / doc-links.
2. Classify each: blocking (PR can't merge) vs informational (must report).
3. Run every blocking check; record `command + exit_code` for the PR.
4. Conclude: PASS only if every blocking check is green AND not a known flake.

## Plan
For each QA cycle:
1. Generate the inventory of blocking and informational checks for this PR.
2. Run blocking checks first; halt on the first new failure.
3. Stop and triage failures: new vs pre-existing baseline; flake vs deterministic.
4. Run informational checks; collect results.
5. Produce a QA receipt with exact commands, exit codes, and a single PASS / FAIL verdict.
Definition of done: every blocking check executed with recorded exit code + PASS / FAIL verdict written to the PR.
Rollback if: a check that was passing yesterday is failing today and is on the blocking list — block the merge; do not waive.

1. Run the project's documented test command, never an ad-hoc subset.
2. Record the exact command and exit code for every check, blocking or informational.
3. Treat any new flake as blocking until it is deliberately quarantined.
4. Treat security-scanner CRITICAL / HIGH findings as blocking by default.
5. Recommend the next fix per failed check; do not leave findings unactioned.
6. Never declare PASS to unblock a release if any blocking check failed.

## Validation
Before posting the QA verdict:
1. Every blocking check has a recorded `command + exit_code` line in the PR.
2. No blocking check is missing from the report.
3. The verdict (PASS / FAIL) matches the conjunction of blocking-check exit codes.
4. Each failed check has a one-line "next fix" recommendation.
Pass: 4 markers present + verdict matches the evidence.
Fail action: rerun the missing check; do not declare PASS without the evidence row.

## Agentic capabilities
- **Tools required:** test runner (pytest / jest / go test), build runner, linter, security suite (bandit / semgrep / gitleaks / trivy), coverage tool.
- **Subagents:** Dispatch parallel runners (tests + lint + security) to keep wall-clock low.
- **Memory writes:** Persist (PR → blocking checks executed, exit codes, flake quarantine list) for trend analysis.
- **Escalate when:** A blocking check fails on a stable baseline — escalate before declaring FAIL; the failure may be infra, not the PR.
- **Autonomy budget:** PASS / FAIL verdict autonomous when evidence is complete. Waiving a blocking failure requires explicit user approval.
