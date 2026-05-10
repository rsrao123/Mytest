# Skill: Dispatching Parallel Agents

## Think first
- Are these subtasks truly independent, or do they share a write target I missed?
- What file scope does each agent get exclusive write access to, and where's the seam?
- What's the merge step, and who arbitrates if outputs conflict?
- If one subagent fails, does the rest of the work still produce a coherent result?

When subtasks are independent (no shared file writes):
- Dispatch them concurrently via CrewAI Process.parallel or asyncio.gather.
- Set explicit non-overlapping file scopes per agent.
- Merge results; if conflicts, escalate to the architect agent.
