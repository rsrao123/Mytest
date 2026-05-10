# Skill: Subagent-Driven Development
For tasks larger than ~50 LOC of changes:
1. Decompose into independent subtasks.
2. Spawn a focused subagent per subtask with a tightly scoped prompt and only the files it needs.
3. Each subagent returns a diff + rationale + self-review.
4. Parent agent integrates and runs cross-cutting tests.
