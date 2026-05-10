# Skill: Executing Plans

## Think first
- Have I read the *entire* plan end-to-end before touching anything?
- For the current step, what does "verified" concretely look like?
- If this step fails partway through, what state am I leaving the system in?
- Has reality diverged from the plan since it was written? Where, and does that change the next step?

## Reasoning
For each step in the plan, work through:
1. Restate the step's intent and the concrete acceptance check it must satisfy.
2. Verify preconditions hold; if reality has diverged, halt and update the plan rather than improvise.
3. Execute, capture state at each substep, run the verify check.
4. On failure: stop. Do not improvise. Report state + invoke the documented rollback path.

1. Read the entire plan before touching anything.
2. Execute one step at a time; verify before proceeding.
3. If a step fails, do NOT improvise — report the failure with state and ask.
4. Update the plan in place when reality diverges; never silently deviate.
