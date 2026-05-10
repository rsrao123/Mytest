# Skill: Root Cause Tracing
1. Don't fix at the first plausible layer. Ask "why" until the answer stops surprising you (≥3 levels deep).
2. Reproduce the bug with the smallest possible input. If you can't reproduce, you don't understand it.
3. Stack traces lie about *cause* but tell the truth about *location*. Use them to bisect, not to diagnose.
4. When the cause is clear, ask: what other symptoms would this same cause produce? Search for them.
5. Fix the cause. Add a regression test. If the cause is structural, file a follow-up ticket — don't expand scope mid-fix.
