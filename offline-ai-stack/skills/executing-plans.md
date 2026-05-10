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

## Plan
For each step:
1. Restate the step's intent + acceptance check before starting it.
2. Verify preconditions; if reality has drifted, halt and update the plan rather than improvise.
3. Execute the step; capture state at each substep.
4. Stop and run the verify check; on failure, invoke the rollback path documented for this step.
Definition of done: every step's verify check has passed; plan markers updated.
Rollback if: any step fails its verify — execute the documented rollback; do not improvise a fix.

## Validation
At each step boundary, verify:
1. The step's verify check ran and returned green.
2. The actual outcome matches the plan's expected outcome (no silent drift).
3. Plan markers (todo / done / blocked) are updated for this step.
4. On any failure, the rollback path was executed (not improvised).
Pass: verify green + outcomes match + markers current + no improvisation.
Fail action: halt; surface state to the user; do not advance to the next step.

1. Read the entire plan before touching anything.
2. Execute one step at a time; verify before proceeding.
3. If a step fails, do NOT improvise — report the failure with state and ask.
4. Update the plan in place when reality diverges; never silently deviate.
