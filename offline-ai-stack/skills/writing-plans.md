# Skill: Writing Plans

## Think first
- Is the goal one outcome-shaped sentence, or am I still describing the activity?
- Are the acceptance criteria testable as written, or do they need restating?
- Does every step have *both* a verify step and a rollback?
- What's explicitly out-of-scope, to pre-empt scope creep mid-execution?

## Reasoning
Build the plan in this order:
1. Write the goal as a single outcome-shaped sentence.
2. Write acceptance criteria as testable items, not aspirations.
3. List ordered steps; each step gets a verify check, a rollback, and a time estimate.
4. List out-of-scope explicitly to pre-empt scope creep during execution.

## Plan
When writing the plan itself:
1. Goal — one outcome-shaped sentence.
2. Acceptance criteria — testable, listed.
3. Steps — each with verify check, rollback path, time estimate.
4. Stop and have an executor agent (or human) confirm the plan is executable without questions before approval.
5. Out-of-scope — explicit list to pre-empt scope creep.
Definition of done: every step has verify + rollback + estimate; an executor confirmed executability.
Rollback if: an executor cannot follow a step without asking — the plan needs more detail; rewrite it.

## Validation
Before approval, verify:
1. The goal is one outcome-shaped sentence.
2. Each step has verify + rollback + estimate.
3. Out-of-scope is listed explicitly.
4. An executor confirmed they could follow the plan without questions.
Pass: goal + per-step trio + out-of-scope + executor sign-off.
Fail action: rewrite the failing step; the plan isn't ready for execution.

## Agentic capabilities
- **Tools required:** FileWriteTool (plan file), executor simulator.
- **Subagents:** Dispatch an executor-simulator subagent to test the plan's executability before approval.
- **Memory writes:** Persist (project → plan template, common steps) so future plans reuse known-good structure.
- **Escalate when:** A step can't have a rollback (irreversible) — design the plan around the irreversibility, with the user.
- **Autonomy budget:** Draft + iterate autonomous. Final approval requires the executor agent or a human to sign off.

A plan must contain:
- **Goal** (one sentence, outcome-shaped)
- **Scope** (what is explicitly in)
- **Non-scope** (what is explicitly out, to pre-empt creep)
- **Requirements** (functional + non-functional, testable)
- **Acceptance criteria** (testable, derived from requirements)
- **Architecture** (components touched, new interfaces, data flow)
- **Files to create or change** (path + brief intent per file)
- **Step-by-step implementation plan** (ordered, each step independently executable)
- **Test plan** (unit + integration + manual cases per step)
- **Security considerations** (input handling, secrets, auth, deserialization for the touched code)
- **Risks and mitigations** (per risk: likelihood, impact, mitigation)
- **Rollback plan** (per step: the exact reverse action)
- **Time estimate** (per step)
- **Success criteria** (observable end-state — what proves the plan worked)
- **Handoff to executing-plans** (one-paragraph packet with goal, plan link, prerequisites)

Reject any plan missing acceptance criteria, rollback, security considerations, or success criteria. Save the final plan as `PLAN.md` (or under `plans/<id>.md`) when file editing is available.
