# Skill: Brainstorming

## Think first
- What constraints am I implicitly assuming that aren't actually fixed?
- Whose perspective am I missing (user, operator, future maintainer, attacker)?
- Have I covered all 7 archetypes (simple / robust / low-cost / fastest / scalable / unconventional / safest), or am I clustering on one mode?
- Among the 7 comparison axes (feasibility, cost, complexity, time, maintainability, security, long-term value), which one will actually decide the answer?

## Reasoning
For each open problem, produce a divergence trace:
1. Restate the user's goal in one sentence; list known facts, missing facts, and assumptions.
2. Generate ≥ 7 ideas, one per archetype: **simple**, **robust**, **low-cost**, **fastest**, **scalable**, **unconventional**, **safest**.
3. For each idea, capture: what it is / how it works / advantages / disadvantages / risks / required tools or resources.
4. Compare across the 7 axes (feasibility, cost, complexity, time, maintainability, security, long-term value); strike dominated options.
5. Conclude with a recommendation + one-line "why other options were rejected" + a handoff packet for the writing-plans skill.

## Plan
Before recommending:
1. Restate the goal; capture known facts, missing facts, assumptions, and any blocking clarifications.
2. Generate the 7 archetype ideas in one uninterrupted sweep — no evaluation yet.
3. Stop and build the per-idea analysis (what / how / advantages / disadvantages / risks / required tools) and the comparison table across all 7 axes.
4. Surface the recommendation, the rejected alternatives with reasons, and a handoff packet for the writing-plans skill.
Definition of done: 7 ideas + per-idea analysis + comparison table + recommendation + rejected list + writing-plans handoff packet.
Rollback if: the user signals an unstated constraint after the recommendation — restart at step 1 with that constraint explicit.

1. Restate the user's goal in one sentence before generating any ideas.
2. List known facts, missing facts, and assumptions explicitly.
3. Ask clarification questions only when the task cannot proceed without them.
4. Generate at least 7 ideas — one per archetype: simple, robust, low-cost, fastest, scalable, unconventional, safest.
5. For each idea, document what it is, how it works, advantages, disadvantages, risks, and required tools or resources.
6. Compare all ideas on feasibility, cost, complexity, implementation time, maintainability, security, and long-term value.
7. Identify hidden risks and failure modes per idea before recommending.
8. Recommend the best option and explain why each rejected option was rejected.
9. Convert the recommendation into a handoff packet for the writing-plans skill (goal, chosen approach, constraints, open questions).
10. Prefer practical offline / local / open-source solutions when relevant; be specific, not generic; never write code at this stage.

## Validation
Before recommending, verify:
1. ≥ 7 ideas generated, each labeled with one of the named archetypes.
2. Per-idea analysis present (what / how / advantages / disadvantages / risks / required tools) for every idea.
3. Comparison table present with all 7 axes as columns.
4. Recommendation + rejected-alternatives-with-reasons + writing-plans handoff packet all present.
Pass: 7-archetype coverage + per-idea analysis + 7-axis comparison + recommendation + handoff packet.
Fail action: return to Plan step 2; the divergence sweep was incomplete.

## Agentic capabilities
- **Tools required:** none — pure ideation. FileReadTool optional for project-context inputs.
- **Subagents:** Dispatch a contrarian subagent (higher temperature) to challenge the obvious direction; dispatch a missing-perspective subagent (user / operator / attacker viewpoints).
- **Memory writes:** Persist (problem, 7 ideas considered, recommended approach, rejected alternatives with reasons, handoff packet) for future similar problems.
- **Escalate when:** A blocking clarification is required (the task cannot proceed without it) — surface to the user before generating ideas.
- **Autonomy budget:** Surface recommendation + handoff packet. Final selection and promotion to writing-plans require user or architect sign-off; never auto-promote to implementation.
