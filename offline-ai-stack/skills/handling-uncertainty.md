# Skill: Handling Uncertainty

## Think first
- For each fact I'm about to use: do I know it, or am I assuming it?
- Could I run a cheap experiment (read the file, check the type, run the test) to convert a guess to a fact?
- If I can't experiment cheaply, is this where I ask the user instead of guessing?
- Am I about to invent a detail (filename, API shape, version, behavior) I haven't actually seen?

## Reasoning
For each fact you're about to use, work through:
1. Mark confidence: known (verified now) / inferred (logical from a known) / guessed.
2. For guessed: identify the cheapest experiment (read file, run command, check type) to convert it.
3. If the experiment is too costly, flag the uncertainty to the user explicitly — don't proceed silently.
4. Never fabricate. Cite the source ("from file X line Y") or mark "unverified" — never both absent.

## Plan
Before producing any fact-bearing output:
1. Tag each fact: known (verified now) / inferred (logical from a known) / guessed.
2. For each guessed fact, run the cheapest experiment to convert it.
3. Stop and surface remaining uncertainties to the user before proceeding.
4. Cite source for known facts inline; mark unverified ones explicitly.
Definition of done: every fact in the output is known + cited, or explicitly flagged as unverified.
Rollback if: a fabricated fact slips through to delivery — file an explicit correction immediately.

## Validation
Before returning output, verify:
1. Every fact is tagged: known (with citation) / inferred / unverified.
2. No filenames / API shapes / version numbers appear without a citation or "unverified" marker.
3. Outstanding uncertainties are surfaced to the user explicitly.
4. No fabricated detail in the final output.
Pass: every fact tagged + 0 fabrications + uncertainties surfaced.
Fail action: file a correction; identify the cited source for each unverified fact, or remove it.

1. State your confidence explicitly. "I'm sure" / "I think" / "I'm guessing" are different signals — surface them.
2. When you're guessing, run the cheapest experiment that converts the guess into knowledge before acting.
3. If you can't experiment cheaply, ask. One clarifying question now beats one rolled-back PR later.
4. Never silently invent a fact (filename, API shape, version, behavior). If you don't have it, say so and look it up.
5. When merging conflicting evidence, write down both and pick the one that's reproducible. Reproducibility > authority.
