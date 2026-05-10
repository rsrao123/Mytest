# Skill: Prompt Engineering

## Think first
- Can I state the task in *one* sentence? If not, the prompt isn't ready to write.
- Do I have at least one positive example, and one negative example showing what NOT to produce?
- Is the output schema explicit (JSON keys, markdown headers, max length)?
- Are constraints separated from preferences, so the consumer can tell which are hard?

## Reasoning
For each prompt you author, work through:
1. State the task in *one* sentence; if you can't, the prompt isn't ready — refuse to ship.
2. Provide ≥ 1 positive example and ≥ 1 negative example (what NOT to produce).
3. Lock the output schema: keys, structure, max length, examples.
4. Separate hard constraints (must) from preferences (nice-to-have); list each under its own header.

## Plan
Before shipping any prompt:
1. Write the task in one sentence; refuse to continue if you can't.
2. Add ≥ 1 positive + 1 negative example of expected output.
3. Lock the output schema; specify keys, structure, max length.
4. Stop and run the prompt against the eval set before merging; compare to the prior baseline.
Definition of done: eval pass-rate ≥ baseline + schema validated against examples.
Rollback if: eval regresses on the existing test set — revert the prompt change; do not ship.

## Validation
Before merging the prompt, verify:
1. Eval pass-rate ≥ baseline on the existing test set.
2. Output schema validated against the example outputs.
3. Hard constraints separated from preferences in the prompt body.
4. Negative example present (what NOT to produce).
Pass: ≥ baseline + schema valid + constraints separated + negative example present.
Fail action: revert; iterate offline before re-merging.

1. State the task in one sentence at the top.
2. Provide 1–3 positive examples and 1 negative example (what NOT to produce).
3. Specify the output schema explicitly (JSON keys, markdown structure, max length).
4. List hard constraints separately from preferences.
5. Keep instructions monotonic: each rule should be checkable in isolation.
6. When tuning, change one variable at a time and re-run on a fixed eval set.
