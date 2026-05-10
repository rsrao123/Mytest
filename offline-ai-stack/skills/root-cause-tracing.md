# Skill: Root Cause Tracing

## Think first
- Why does this bug actually happen? Now ask "why?" of *that* answer. And again.
- Have I gone at least 3 levels deep into the causal chain, or did I stop at the first plausible layer?
- What *other* symptoms would this same root cause produce? Have I searched for them?
- Am I about to fix the cause, or just paper over the symptom where it surfaced?

## Reasoning
For each bug, dig down with this loop:
1. State the symptom precisely; ask "why?" of it.
2. Ask "why?" of each answer in turn; recurse until the answer stops surprising you (≥ 3 levels).
3. Predict at least one *other* symptom the same root cause would produce; search the codebase for it.
4. Fix the root cause + add a regression test that pins it; file follow-ups for any structural issues.

## Plan
For each bug:
1. Reproduce deterministically with the smallest possible input. If you can't reproduce it, you don't understand it.
2. Drill ≥ 3 levels of "why" past the first plausible answer.
3. Stop and search for other symptoms the same root cause would produce.
4. Fix the root cause + add the regression test that pins it; file structural follow-ups separately.
Definition of done: cause named + ≥ 3 "why" levels documented + regression test landed.
Rollback if: another instance of the same cause appears post-fix — the fix was at the wrong layer; redo the trace.

## Validation
Before declaring fixed, verify:
1. The reproducer is deterministic (100/100 on the failing input).
2. ≥ 3 levels of "why" recorded in the bug notes.
3. At least one search for sibling symptoms attempted and findings noted.
4. Regression test pins the *cause*, not just the symptom location.
Pass: deterministic repro + 3+ whys + sibling search + cause-pinning test.
Fail action: redo the trace; the fix was at the wrong layer.

## Agentic capabilities
- **Tools required:** test runner (deterministic repro), debugger or logger, `git bisect`, rg (sibling-symptom search).
- **Subagents:** Dispatch a sibling-symptom search subagent in parallel with the why-trace.
- **Memory writes:** Persist (bug → cause, level depth, regression test path) for sibling-symptom search reuse.
- **Escalate when:** ≥ 5 levels of "why" with no convergence — design issue, not a bug; escalate to architect.
- **Autonomy budget:** Trace + fix + regression test autonomous. Architectural fixes require architect approval + ADR.

1. Don't fix at the first plausible layer. Ask "why" until the answer stops surprising you (≥3 levels deep).
2. Reproduce the bug with the smallest possible input. If you can't reproduce, you don't understand it.
3. Stack traces lie about *cause* but tell the truth about *location*. Use them to bisect, not to diagnose.
4. When the cause is clear, ask: what other symptoms would this same cause produce? Search for them.
5. Fix the cause. Add a regression test. If the cause is structural, file a follow-up ticket — don't expand scope mid-fix.
