# Skill: Systematic Debugging

## Think first
- What's the expected behavior, in one precise sentence?
- What's the observed behavior, in one precise sentence?
- What's my current hypothesis, and what's the cheapest experiment that would *falsify* it?
- If I can't reproduce the bug deterministically, do I actually understand it?

## Reasoning
Run this loop until the bug is fixed:
1. State expected and observed behavior precisely, in one sentence each.
2. Form one hypothesis + the cheapest experiment whose outcome would falsify it.
3. Run the experiment; if falsified, revise the hypothesis (do not speculate further without a test).
4. Loop until the bug is reproduced deterministically; then fix the cause and add a regression test.

## Plan
Loop until reproduced and fixed:
1. State expected/observed behavior precisely.
2. Hypothesize + define the cheapest falsifying experiment.
3. Stop and run the experiment; record outcome in the bug's notes.
4. If falsified, revise the hypothesis; if confirmed, fix the cause and add a regression test.
Definition of done: deterministic reproduction + fix + regression test landed.
Rollback if: 3 hypotheses fail in a row — re-read the relevant code; speculation isn't working.

## Validation
Before declaring fixed, verify:
1. Reproducer runs deterministically on the failing input.
2. Hypotheses + falsification outcomes are recorded in the bug notes.
3. The fix targets the root cause; any symptom-level fix is marked as tactical.
4. Regression test added.
5. Prevention advice recorded for the bug class: lint rule, fixture, alert, or convention that would have caught this earlier.
Pass: deterministic repro + record + cause-targeted fix + regression test + prevention note.
Fail action: re-read the relevant code; speculation needs another reset before the next attempt.

## Agentic capabilities
- **Tools required:** debugger or strategic logger, test runner (deterministic repro), `git bisect`.
- **Subagents:** Dispatch experiment-runner subagents for parallel falsification of multiple hypotheses.
- **Memory writes:** Persist (bug → hypothesis chain, falsification outcomes) — accumulates debugging wisdom.
- **Escalate when:** 3 hypotheses fail in a row — pause, re-read code; speculation isn't working.
- **Autonomy budget:** Trace + fix autonomously. Debugging in production requires explicit user approval.

1. State the expected behavior precisely.
2. State the observed behavior precisely.
3. Form a hypothesis. Predict what would prove it wrong.
4. Run the cheapest experiment that would falsify the hypothesis.
5. If falsified, revise. Do not speculate without testing.
6. Bisect when the search space is large (git bisect, binary-search inputs).
7. Fix the cause, not the symptom. Add a regression test.
8. Record prevention advice: name the lint rule, fixture, alert, or convention that would have caught this bug class earlier.
