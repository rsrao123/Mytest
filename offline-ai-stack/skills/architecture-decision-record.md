# Skill: Architecture Decision Record (ADR)
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
