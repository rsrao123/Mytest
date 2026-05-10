# Skill: Prompt Engineering
1. State the task in one sentence at the top.
2. Provide 1–3 positive examples and 1 negative example (what NOT to produce).
3. Specify the output schema explicitly (JSON keys, markdown structure, max length).
4. List hard constraints separately from preferences.
5. Keep instructions monotonic: each rule should be checkable in isolation.
6. When tuning, change one variable at a time and re-run on a fixed eval set.
