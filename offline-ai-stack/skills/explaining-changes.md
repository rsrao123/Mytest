# Skill: Explaining Changes

## Think first
- Why did this change happen — what user/system pain did it relieve?
- What was the alternative I rejected, and what made it worse?
- What's the most surprising thing in this diff that a cold reader would miss?
- What caveats (migrations, deploy order, feature flags, breaking changes) does the reader need *before* reading the diff?

The audience for a commit message and PR description is *future-you reading git blame at 2am*. Write for them.

1. Lead with *why*, not *what*. The diff already shows what.
2. Name the user-visible behavior change in the first line. If there isn't one, name the architectural one.
3. Note any non-obvious decisions inline ("chose X over Y because Z"). Don't make readers guess.
4. Call out reverts/rollbacks explicitly with the reverted SHA.
5. If the change has side-effects (migrations, deploy order, feature flags), put them under a "Caveats" header — never in prose.
6. Link the issue/spec/ADR. A commit without context is debt.
