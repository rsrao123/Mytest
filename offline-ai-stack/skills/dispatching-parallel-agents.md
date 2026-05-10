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

When subtasks are independent (no shared file writes):
- Dispatch them concurrently via CrewAI Process.parallel or asyncio.gather.
- Set explicit non-overlapping file scopes per agent.
- Merge results; if conflicts, escalate to the architect agent.
