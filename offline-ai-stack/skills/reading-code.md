# Skill: Reading Code
Before you change code, understand it.

1. Read the test file first. Tests document the contract better than docstrings.
2. Trace one path end-to-end before reading the second path. Breadth-first reading produces tourist-level knowledge.
3. Identify the **type of code** before reading: orchestration, domain logic, IO, glue. Read each kind differently.
4. When a function is too big to hold in your head, narrate it on paper: inputs → invariants → outputs.
5. Note the *style* the file is written in. New code in the file should match it; if it shouldn't, that's a refactor commit, not your task.
