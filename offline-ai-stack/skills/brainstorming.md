# Skill: Brainstorming

## Think first
- What constraints am I implicitly assuming that aren't actually fixed?
- Whose perspective am I missing (user, operator, future maintainer, attacker)?
- What would the contrarian / minimalist / most-ambitious option look like?
- On which axis (effort, impact, reversibility) does each candidate genuinely differ?

## Reasoning
For each open problem, produce a divergence trace:
1. List ≥ 5 distinct directions; explicitly include the obvious, the contrarian, the simplest viable, the most ambitious.
2. Score each on (effort, impact, reversibility); use coarse buckets (low/med/high), not false precision.
3. Identify the single axis on which the candidates meaningfully differ — eliminate dominated options.
4. Surface the strongest two with comparable tradeoffs; do not collapse to one until forced.

## Plan
Before recommending:
1. Generate ≥ 5 directions in one uninterrupted sweep — no evaluation yet.
2. Score each (effort/impact/reversibility); strike dominated options.
3. Stop and present the top two with their differing axis; do not collapse to one.
4. Decide only after the user (or architect) picks the axis they care about.
Definition of done: top-two surfaced with one named tradeoff axis between them.
Rollback if: the user's chosen axis isn't on the matrix — restart at step 1 with that axis explicit.

1. Generate at least 5 distinct directions before evaluating any.
2. Force variety: include the obvious, the contrarian, the simplest viable, and the most ambitious.
3. Score each on (a) effort, (b) impact, (c) reversibility.
4. Surface the strongest two with explicit tradeoffs; do not collapse to a single recommendation prematurely.
