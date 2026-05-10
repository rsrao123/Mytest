# Skill: Memory Management

## Think first
- What in this session is *durable* (project-level, useful next session) vs *task-level* (only matters now)?
- Could the candidate fact contain a secret, credential, or PII? If yes, refuse to persist it.
- Where does this belong: ARCHITECTURE.md (structure), DECISIONS.md (why), CODING_RULES.md, SECURITY_NOTES.md, BUG_HISTORY.md, or SESSION_SUMMARY.md?
- Would a future agent actually query for this fact, or is it noise?

## Reasoning
For each candidate memory write:
1. Classify: durable-fact / task-context / temporary-noise / secret. Persist only the first.
2. Locate the canonical file (PROJECT_MEMORY / ARCHITECTURE / DECISIONS / CODING_RULES / SECURITY_NOTES / BUG_HISTORY / SESSION_SUMMARY).
3. Check for duplicates: would this overwrite or contradict an existing fact? If so, supersede explicitly with a date.
4. Conclude with a one-sentence note framed as a fact a future agent would query for.

## Plan
For each memory cycle:
1. Read the existing memory files for the project before extracting anything new.
2. Extract candidate facts from the current session; classify each.
3. Stop and audit: scan the candidate list for secrets / PII; drop anything that matches.
4. Write the surviving facts to the appropriate files; record a changelog of what was saved.
Definition of done: candidates classified, secrets-scan clean, surviving facts written, changelog updated.
Rollback if: a written fact later proves wrong — supersede with a dated correction, never silently edit.

1. Read existing memory before writing anything new.
2. Persist only durable, project-level facts.
3. Refuse to persist secrets, credentials, or PII.
4. Write each fact to exactly one file; cross-link if needed.
5. Frame facts as future-queryable statements, not narrative.
6. Keep individual fact entries to one to three sentences.
7. Date each fact entry; mark superseded entries explicitly.

## Validation
Before declaring memory updated:
1. `gitleaks detect --no-git --source memory/` returns 0 hits (or equivalent secrets scan).
2. Every new fact appears in exactly one memory file.
3. Each new fact has a date and is one to three sentences.
4. No fact contradicts an existing entry without an explicit "Supersedes <date>" note.
Pass: secrets scan green + per-fact dedupe + size discipline + supersession discipline.
Fail action: remove the offending fact; rewrite the entry or supersede explicitly.

## Agentic capabilities
- **Tools required:** FileReadTool, FileWriteTool (memory files), rg (sensitive-pattern scan), gitleaks for hard validation.
- **Subagents:** Dispatch a secrets-scanner subagent to audit the candidate list before writing.
- **Memory writes:** This skill *is* the memory writer. Targets PROJECT_MEMORY / ARCHITECTURE / DECISIONS / CODING_RULES / SECURITY_NOTES / BUG_HISTORY / SESSION_SUMMARY.
- **Escalate when:** A candidate fact contains a credential, key, or PII — refuse and surface to the user.
- **Autonomy budget:** Project-level fact writes are autonomous. Editing or deleting existing memory entries requires explicit user approval.
