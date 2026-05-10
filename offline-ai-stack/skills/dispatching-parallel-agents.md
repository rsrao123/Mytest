# Skill: Dispatching Parallel Agents

## Think first
- Are these subtasks truly independent, or do they share a write target I missed?
- What file scope does each agent get exclusive write access to, and where's the seam?
- What's the merge step, and who arbitrates if outputs conflict?
- If one subagent fails, does the rest of the work still produce a coherent result?

## Reasoning
Before fanning out, work through:
1. Map each subtask to its write-target files; build the file-scope table.
2. Verify scopes are disjoint; if any overlap, sequence those subtasks instead of paralleling them.
3. Define the merge point and the conflict-arbitration agent (usually the architect).
4. State the failure-recovery plan per subagent: which failures abort the run vs which are isolatable.

## Plan
Before fanning out:
1. Map subtasks to disjoint file scopes; if scopes overlap, sequence those subtasks instead.
2. Define each subagent's prompt + expected output schema (diff + rationale + self-review).
3. Stop and have the architect confirm scope disjointness before dispatch.
4. Dispatch in parallel; collect outputs; merge or escalate conflicts.
Definition of done: all subagent outputs merged + cross-cutting tests green.
Rollback if: a write conflict appears at merge — sequence the conflicting subtasks; do not silently force-merge.

## Validation
After fan-out completes, verify:
1. The file-scope table shows zero overlap between subagents.
2. Each subagent's output passed its self-review check.
3. Cross-cutting integration tests are green post-merge.
4. Any conflicts were arbitrated by the architect, not silent-merged.
Pass: scopes disjoint + self-reviews passed + integration green + conflicts logged.
Fail action: sequence the conflicting subtasks and rerun.

## Agentic capabilities
- **Tools required:** subagent dispatcher (`CrewAI Process.parallel` or `asyncio.gather`), file-scope tracker.
- **Subagents:** This skill *is* subagent dispatch. The architect arbitrates conflicts.
- **Memory writes:** Persist (task → decomposition pattern, file scopes) for similar future tasks.
- **Escalate when:** Scopes can't be made disjoint without restructuring the task — return to architect.
- **Autonomy budget:** Up to N parallel subagents (project policy). Above that, sequence or split the task.

When subtasks are independent (no shared file writes):
- Dispatch them concurrently via CrewAI Process.parallel or asyncio.gather.
- Set explicit non-overlapping file scopes per agent.
- Merge results; if conflicts, escalate to the architect agent.

Standard parallel reviewer catalog (compose 2–7 of these per review):
- **Bug Hunter** — logic bugs, off-by-ones, race conditions, unhandled errors.
- **Security Reviewer** — input handling, auth, secrets, deserialization, OWASP top-10.
- **Performance Reviewer** — N+1 queries, hot-path allocations, unnecessary network round-trips.
- **Code Style Reviewer** — naming, formatting, project-conventions compliance.
- **Test Coverage Reviewer** — missing tests, untested branches, mock-heavy tests.
- **Architecture Reviewer** — module boundaries, hidden coupling, premature abstraction.
- **Git History Reviewer** — context from `git log` / `git blame` on the touched lines.

Rules for the catalog:
- Each reviewer reads the same diff but reports independently in its own dimension.
- Findings are deduplicated across reviewers before merging into the final report.
- Severity ranking (Critical / Major / Minor) is applied at the merge step, not by individual reviewers.
- File paths and function names must appear in every finding; vague comments are rejected.
