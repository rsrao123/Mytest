# Skill: Subagent-Driven Development

## Think first
- Is this task genuinely > ~50 LOC of changes, or am I over-decomposing a small one?
- What's the smallest set of files each subagent needs to do its job — nothing more?
- What do I want each subagent to *return*: a diff, a rationale, a self-review, all three?
- Once I have the outputs, what's the integration step and the cross-cutting test that proves it works?

## Reasoning
For each task > ~50 LOC, work through:
1. Decompose into independent subtasks; name file scopes so they don't overlap.
2. Define each subagent's prompt: minimum context, expected output (diff + rationale + self-review).
3. Define the integration step + the cross-cutting test that proves the parts compose.
4. Plan failure handling: which subagent failures abort the run vs which are isolatable and recoverable.

## Plan
For tasks > ~50 LOC:
1. Decompose into independent subtasks; map each to disjoint file scopes.
2. Define each subagent's prompt + expected output schema (diff + rationale + self-review).
3. Stop and have the architect confirm decomposition before dispatch.
4. Run the subagents; integrate outputs; verify cross-cutting tests green.
Definition of done: all subagent outputs integrated + cross-cutting tests green.
Rollback if: subagent outputs conflict at merge — escalate to architect; do not silently force-merge.

## Validation
After integration, verify:
1. The file-scope table for subagents shows 0 overlaps.
2. Each subagent returned diff + rationale + self-review.
3. Cross-cutting integration tests are green.
4. Architect approved the decomposition (decision recorded).
Pass: scopes + outputs + tests + architect sign-off.
Fail action: sequence overlapping subagents; rerun with the architect's revised decomposition.

## Agentic capabilities
- **Tools required:** subagent dispatcher, file-scope tracker, integration-test runner.
- **Subagents:** This skill *is* subagent-driven development; the architect arbitrates conflicts.
- **Memory writes:** Persist (task → decomposition pattern, file scopes, integration test) for similar future tasks.
- **Escalate when:** Subagent outputs conflict structurally — escalate to architect; never silent-merge.
- **Autonomy budget:** Up to N parallel subagents (project policy). Cross-cutting integration is single-agent.

For tasks larger than ~50 LOC of changes:
1. Decompose into independent subtasks.
2. Spawn a focused subagent per subtask with a tightly scoped prompt and only the files it needs.
3. Each subagent returns a diff + rationale + self-review.
4. Parent agent integrates and runs cross-cutting tests.
