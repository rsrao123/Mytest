# Skill: Explaining Changes

## Think first
- Why did this change happen — what user/system pain did it relieve?
- What was the alternative I rejected, and what made it worse?
- What's the most surprising thing in this diff that a cold reader would miss?
- What caveats (migrations, deploy order, feature flags, breaking changes) does the reader need *before* reading the diff?

## Reasoning
Build the description in this order:
1. State the user/system pain in one sentence (the *why*).
2. Name the alternative considered + the concrete reason it was rejected.
3. Surface caveats: migrations, deploy ordering, feature flags, breaking changes.
4. Lead the message with the why; close with how the reader can verify locally.

## Plan
Before pushing:
1. Draft the why in one sentence; rewrite if it describes the *what*.
2. List rejected alternatives + caveats (migrations, deploy order, flags).
3. Stop and reread as a cold reader; rewrite if you'd be confused.
4. Land with the issue / spec / ADR link inline.
Definition of done: future-you-at-2am can pick this up cold without scrolling to the diff.
Rollback if: a reviewer asks "why" — the message failed; rewrite it before merging.

## Validation
Before merging, verify:
1. The first sentence states the *why*, not the *what*.
2. Rejected alternatives are named with a reason for each.
3. Caveats (migrations / deploy order / flags / breaking changes) appear under their own header.
4. A cold reader confirms the diff is understandable from the description alone.
Pass: why-first + alternatives + caveats + cold-reader-passed.
Fail action: rewrite description before merge.

## Agentic capabilities
- **Tools required:** git (log, diff, blame), FileReadTool (for issue / spec / ADR context).
- **Subagents:** Dispatch a "cold reader" subagent to validate the description before merge.
- **Memory writes:** Persist (change type → message template) so similar changes get consistent why-statements.
- **Escalate when:** No clear "why" exists — the change shouldn't merge until one does; ask the requester.
- **Autonomy budget:** Author messages autonomously. Final wording on user-facing changelogs requires approval.

The audience for a commit message and PR description is *future-you reading git blame at 2am*. Write for them.

1. Lead with *why*, not *what*. The diff already shows what.
2. Name the user-visible behavior change in the first line. If there isn't one, name the architectural one.
3. Note any non-obvious decisions inline ("chose X over Y because Z"). Don't make readers guess.
4. Call out reverts/rollbacks explicitly with the reverted SHA.
5. If the change has side-effects (migrations, deploy order, feature flags), put them under a "Caveats" header — never in prose.
6. Link the issue/spec/ADR. A commit without context is debt.
