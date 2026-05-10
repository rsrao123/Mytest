# Skill: Giving Code Review

## Think first
- What did the author do well that's worth naming explicitly?
- For each comment I'm about to leave: is it blocking, a nit, or a question? Mark it.
- Am I reviewing the *change*, or am I drifting into pre-existing code that the diff merely touches?
- If this review takes me more than 30 minutes, is the diff too big to review well?

1. Lead with what's good. Reviewers who only flag faults get tuned out.
2. Distinguish blocking from non-blocking comments explicitly: prefix with `nit:`, `q:`, or `BLOCKER:`.
3. Suggest, don't dictate. "Consider X because Y" beats "do X".
4. Pull-requests are conversations. Don't pile on after the third unanswered comment — pick up the call.
5. Review the *change*, not the file. Don't ask the author to fix pre-existing problems unless the change makes them worse.
6. If a review takes more than 30 minutes, the diff is too big. Ask for a split.
