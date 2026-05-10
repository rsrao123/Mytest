# Skill: Dispatching Parallel Agents
When subtasks are independent (no shared file writes):
- Dispatch them concurrently via CrewAI Process.parallel or asyncio.gather.
- Set explicit non-overlapping file scopes per agent.
- Merge results; if conflicts, escalate to the architect agent.
