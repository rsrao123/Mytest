# Skill: Systematic Debugging

## Think first
- What's the expected behavior, in one precise sentence?
- What's the observed behavior, in one precise sentence?
- What's my current hypothesis, and what's the cheapest experiment that would *falsify* it?
- If I can't reproduce the bug deterministically, do I actually understand it?

1. State the expected behavior precisely.
2. State the observed behavior precisely.
3. Form a hypothesis. Predict what would prove it wrong.
4. Run the cheapest experiment that would falsify the hypothesis.
5. If falsified, revise. Do not speculate without testing.
6. Bisect when the search space is large (git bisect, binary-search inputs).
7. Fix the cause, not the symptom. Add a regression test.
