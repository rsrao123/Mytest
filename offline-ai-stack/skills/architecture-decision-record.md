# Skill: Architecture Decision Record (ADR)

## Think first
- What's the actual problem this decision is responding to — not the symptom?
- Which constraints (technical, organizational, time) are non-negotiable, and which are preferences?
- What would I regret in 6 months if I pick wrong, and which option minimizes that regret?
- Is this decision reversible, and at what cost?

## Reasoning
Produce this trace before drafting the ADR:
1. Inventory hard constraints (must-have) and soft preferences; mark each.
2. For each candidate option, mark which hard constraints it satisfies / violates.
3. Identify the single tradeoff axis on which the surviving options differ.
4. State the chosen option + the constraint or tradeoff it optimizes; name what you give up.

Use this template for every non-trivial architectural choice. File it under `docs/adr/NNNN-title.md`.

```
# NNNN. <Decision title>

Date: YYYY-MM-DD
Status: Proposed | Accepted | Deprecated | Superseded by NNNN

## Context
What is the problem? What constraints exist (technical, organizational, time)?

## Decision
What did we choose? State it as an imperative.

## Consequences
- Positive: ...
- Negative: ...
- Neutral: ...

## Alternatives considered
- Option A — why not.
- Option B — why not.
```

Rules:
1. One decision per ADR. Don't bundle.
2. ADRs are append-only; supersede with a new ADR rather than editing.
3. Link the ADR from the PR that implements it.
