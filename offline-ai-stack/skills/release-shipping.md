# Skill: Release Shipping

## Think first
- Is anything in this release a behavior change users will notice without warning? If yes, the release plan needs explicit messaging.
- Has every blocking check (`qa-validation`) passed deterministically?
- What's the rollback path if this release breaks something — and have I rehearsed it?
- Have I obtained explicit user / on-call approval for the deploy step?

## Reasoning
For each release decision:
1. Inventory the readiness checklist (git / tests / security / docs / version / changelog / risks / rollback / approval).
2. Mark each item PASS / FAIL / N/A with evidence (command output, link, sign-off name).
3. Identify the riskiest change in this release and the rollback that targets it.
4. Conclude: SHIP only if every blocking item is PASS AND the rollback is rehearsed AND approval is obtained.

## Plan
For each release:
1. Run the readiness checklist; record evidence per item.
2. Rehearse the rollback path on staging; record the commands and outcome.
3. Stop and request explicit deploy approval from the user / on-call by name.
4. Execute the deploy; monitor for the documented post-deploy interval.
5. Record SHIP / DO NOT SHIP decision with reasoning.
Definition of done: checklist evidenced + rollback rehearsed + approval recorded + decision posted to the release record.
Rollback if: any blocking item flips to FAIL, the rollback rehearsal fails, or approval is withheld — DO NOT SHIP and file follow-ups.

1. Never ship with any blocking check (from `qa-validation`) failing.
2. Never push or deploy without explicit user / on-call approval per release.
3. Always rehearse the rollback path on staging before the production deploy.
4. Always update CHANGELOG with the user-visible changes for this release.
5. Always bump the version per the project's scheme (semver / calver).
6. Document known risks in the release notes; do not hide them.
7. Be conservative: when in doubt, do not ship.

## Validation
Before declaring SHIP:
1. `qa-validation` produced PASS within the last hour, with evidence linked.
2. CHANGELOG.md has a section for this release with all user-visible changes.
3. The rollback rehearsal log shows a successful rollback on staging.
4. An explicit approval message exists from the user / on-call (linked in the release record).
Pass: QA + CHANGELOG + rollback-rehearsal + approval all green.
Fail action: DO NOT SHIP; complete the missing artifact and re-validate.

## Agentic capabilities
- **Tools required:** git (status, tag), CI status reader, deploy / rollback runner, CHANGELOG editor, approval-channel reader.
- **Subagents:** Dispatch a rollback-rehearsal subagent on staging in parallel with the readiness audit.
- **Memory writes:** Persist (release tag → checklist evidence, rollback commands, post-deploy observations) for the postmortem trail.
- **Escalate when:** Any blocking item lacks evidence, or the rollback rehearsal fails — page on-call; do not improvise.
- **Autonomy budget:** Audit + report autonomous. Push, deploy, or tag-release actions require explicit user approval per release.
