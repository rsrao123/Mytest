# Skill: Reading Code

## Think first
- Have I read the test file before the implementation? Tests are the contract.
- Which kind of code is this — orchestration, domain logic, IO, glue — and how should I read each?
- What style does this file commit to (naming, error-handling, layering), and how should new code match it?
- Can I narrate this function as inputs → invariants → outputs, on paper, before changing it?

Before you change code, understand it.

1. Read the test file first. Tests document the contract better than docstrings.
2. Trace one path end-to-end before reading the second path. Breadth-first reading produces tourist-level knowledge.
3. Identify the **type of code** before reading: orchestration, domain logic, IO, glue. Read each kind differently.
4. When a function is too big to hold in your head, narrate it on paper: inputs → invariants → outputs.
5. Note the *style* the file is written in. New code in the file should match it; if it shouldn't, that's a refactor commit, not your task.
