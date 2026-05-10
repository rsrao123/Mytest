# Skill: Root Cause Tracing

## Think first
- Why does this bug actually happen? Now ask "why?" of *that* answer. And again.
- Have I gone at least 3 levels deep into the causal chain, or did I stop at the first plausible layer?
- What *other* symptoms would this same root cause produce? Have I searched for them?
- Am I about to fix the cause, or just paper over the symptom where it surfaced?

1. Don't fix at the first plausible layer. Ask "why" until the answer stops surprising you (≥3 levels deep).
2. Reproduce the bug with the smallest possible input. If you can't reproduce, you don't understand it.
3. Stack traces lie about *cause* but tell the truth about *location*. Use them to bisect, not to diagnose.
4. When the cause is clear, ask: what other symptoms would this same cause produce? Search for them.
5. Fix the cause. Add a regression test. If the cause is structural, file a follow-up ticket — don't expand scope mid-fix.
