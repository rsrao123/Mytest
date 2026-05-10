# Skill: Giving Code Review

## Think first
- What did the author do well that's worth naming explicitly?
- For each comment I'm about to leave: is it blocking, a nit, or a question? Mark it.
- Am I reviewing the *change*, or am I drifting into pre-existing code that the diff merely touches?
- If this review takes me more than 30 minutes, is the diff too big to review well?

## Reasoning
For each PR review, work through:
1. Note one concrete thing the author did well; lead the review with it.
2. For each comment, tag explicitly: BLOCKER / nit / question.
3. Verify each comment targets *the change*, not pre-existing code that the diff merely touches.
4. State a single verdict — APPROVE / REQUEST_CHANGES / BLOCK — with the top blocker named.

## Plan
Before posting:
1. Read the diff once end-to-end without commenting.
2. Note one concrete thing the author did well; lead with it.
3. Tag each pending comment as BLOCKER / nit / question; cut anything not about *this change*.
4. Stop and post a single APPROVE / REQUEST_CHANGES / BLOCK verdict + the top blocker.
Definition of done: verdict + tagged comments + lead-with-good present.
Rollback if: review takes > 30 minutes — the diff is too big; ask for a split rather than continuing.

## Validation
Before posting, verify:
1. One concrete "what's good" comment leads the review.
2. Every comment tagged BLOCKER / nit / question.
3. No comment targets pre-existing code untouched by the diff.
4. Single verdict (APPROVE / REQUEST_CHANGES / BLOCK) at the bottom; top blocker named if any.
Pass: lead-with-good + tags + scope + verdict.
Fail action: trim to in-scope comments; restate the verdict; post.

1. Lead with what's good. Reviewers who only flag faults get tuned out.
2. Distinguish blocking from non-blocking comments explicitly: prefix with `nit:`, `q:`, or `BLOCKER:`.
3. Suggest, don't dictate. "Consider X because Y" beats "do X".
4. Pull-requests are conversations. Don't pile on after the third unanswered comment — pick up the call.
5. Review the *change*, not the file. Don't ask the author to fix pre-existing problems unless the change makes them worse.
6. If a review takes more than 30 minutes, the diff is too big. Ask for a split.
