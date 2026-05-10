# Skill: Reading Code

## Think first
- Have I read the test file before the implementation? Tests are the contract.
- Which kind of code is this — orchestration, domain logic, IO, glue — and how should I read each?
- What style does this file commit to (naming, error-handling, layering), and how should new code match it?
- Can I narrate this function as inputs → invariants → outputs, on paper, before changing it?

## Reasoning
Before changing any code, work through:
1. Read the test file first; extract the contract from what the tests assert.
2. Classify the file under test: orchestration / domain / IO / glue. Read each kind differently.
3. Trace one path end-to-end (entry → exit), noting naming and error-handling conventions in flight.
4. Restate the file's commit-to style; commit to matching it in your edit (or, if not, explain why in the PR).

## Plan
Before changing any file:
1. Open the test file first; extract the implicit contract.
2. Trace one entry-to-exit path in the production file; note local conventions.
3. Stop and write a one-line summary of the file's style.
4. Plan the edit so it matches that style; if it shouldn't, that's a refactor commit, not your task.
Definition of done: one-line style summary + ≥ 1 path traced before any edit.
Rollback if: the edit feels foreign to the file when re-read — reread another path; the style was wrong.

## Validation
Before editing, verify:
1. The test file was opened first; one-line summary of the contract recorded.
2. One entry-to-exit path traced; written notes saved.
3. The file's style summarized in one sentence (naming / error-handling / layering).
4. Edit plan committed to matching that style (or PR explains why not).
Pass: tests-first + path-traced + style-named + edit-plan-aligned.
Fail action: re-read another path; the original style read was wrong.

## Agentic capabilities
- **Tools required:** FileReadTool, rg, git (log, blame), test runner (to extract contract).
- **Subagents:** none — reading is single-agent; a second reader is the next agent in the pipeline.
- **Memory writes:** Persist (file → style summary, contract notes) for future edits to the same file.
- **Escalate when:** The file's intent is genuinely unclear — ask the original author or open the design doc.
- **Autonomy budget:** Read-only; no modifications during the understanding phase.

Before you change code, understand it.

1. Read the test file first. Tests document the contract better than docstrings.
2. Trace one path end-to-end before reading the second path. Breadth-first reading produces tourist-level knowledge.
3. Identify the **type of code** before reading: orchestration, domain logic, IO, glue. Read each kind differently.
4. When a function is too big to hold in your head, narrate it on paper: inputs → invariants → outputs.
5. Note the *style* the file is written in. New code in the file should match it; if it shouldn't, that's a refactor commit, not your task.
