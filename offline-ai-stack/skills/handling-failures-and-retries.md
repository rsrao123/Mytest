# Skill: Handling Failures & Retries

## Think first
- Is this failure transient (worth retrying) or permanent (fail fast)?
- What's my retry budget — both attempt count AND wall-clock total?
- Is the underlying operation idempotent? If not, what idempotency key makes it so?
- On final failure, what *typed* error do I surface, and does the caller have enough context to react?

## Reasoning
For each fallible call, work through:
1. Classify each failure mode: transient (retry) / permanent (fail fast) / ambiguous (treat as transient with cap).
2. Set a budget: max attempts AND max wall-clock — both required.
3. Verify or impose idempotency (idempotency key, dedupe table, natural primary key).
4. Define the typed final-error and the per-retry log signal (attempt #, delay, reason).

## Plan
For each fallible call:
1. Define classifier (transient/permanent), budget (attempts AND wall-clock), and idempotency key.
2. Implement with exponential backoff + full jitter.
3. Stop and add tests for: success, permanent failure, eventual success after retries, exhausted budget.
4. Wire metrics + logs at each retry; surface a typed final error with cause attached.
Definition of done: 4 paths covered (success / permanent / transient-eventual / budget-exhausted) + typed final error.
Rollback if: retries cause duplicate side-effects in production — make the operation idempotent first, then re-enable retries.

1. **Classify before retrying.** Transient (network blip, 503) → retry. Permanent (400, 401, 422) → don't.
2. Every retry needs a budget: max attempts AND max total time. Unbounded retries are an outage.
3. Exponential backoff with full jitter (`random.uniform(0, base * 2**n)`) — fixed sleeps cause thundering herds.
4. Make retries idempotent. If the operation isn't idempotent, add an idempotency key before adding retries.
5. On giving up, surface a typed error with the underlying cause attached. Don't swallow.
6. Log every retry decision (attempt #, delay, reason). Silent retries hide outages.
