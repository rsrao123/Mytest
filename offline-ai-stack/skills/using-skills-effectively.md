# Skill: Using Skills Effectively

## Think first
- Which 2-3 skills genuinely match this task? Name them out loud before starting.
- Are any of those skills in conflict (e.g., `defensive-programming-discipline` vs `security-review`)? Resolve before acting.
- Which skill should I draw on first, and which is supporting?
- Am I composing too many skills and just adding noise?

## Reasoning
Before each task, work through:
1. List the 2-3 skills that genuinely match this task's failure modes; reject the rest.
2. Detect conflicts among loaded skills (e.g., `defensive-programming` vs `security-review`); name and resolve before acting.
3. Pick a primary skill — the others are supporting voices, not co-equal.
4. After execution, log which skill helped and which didn't; that feedback compounds across tasks.

## Plan
At task start:
1. List the 2-3 skills matching this task's failure modes.
2. Detect conflicts among loaded skills; resolve and announce which takes precedence.
3. Stop and name the primary skill before acting.
4. After the task, log which skill helped and which didn't.
Definition of done: primary skill named at start + post-task log entry.
Rollback if: a loaded skill conflicts mid-task — pause, resolve at the meta level, restart from step 1.

## Validation
After the task, verify:
1. Primary skill named at task start (recorded in the agent's own log).
2. ≤ 3 skills loaded total; conflicts (if any) were resolved.
3. Post-task entry recorded which skill helped and which didn't.
4. New skill needs (if any) filed as proposals for the next round.
Pass: primary + cap + log + proposals filed.
Fail action: trim the loaded skill set next time; over-composition is the default failure mode.

## Agentic capabilities
- **Tools required:** `skills.loader` (inject), the skill catalog reader.
- **Subagents:** Meta-skill — applies to dispatcher decisions about which skills each subagent loads.
- **Memory writes:** Per task: (skills loaded, primary, helped, hindered) — feeds the sunset rule.
- **Escalate when:** Two loaded skills contradict and the conflict can't be resolved at the task level.
- **Autonomy budget:** Loading 2-3 skills autonomous. Loading > 5 requires architect; usually the role is too broad.

1. Load skills *before* you start the task, not mid-stream — the skill changes how you'd plan.
2. Compose narrowly: pick the 2–3 skills that match the task, not all of them. Noise drowns signal.
3. Skills override defaults; if a skill conflicts with another instruction, name the conflict explicitly and pick one.
4. If you find yourself re-deriving a rule from first principles, that rule belongs in a skill — propose it.
5. After the task, write a one-liner about what the skill did or didn't help with. That feedback compounds.
