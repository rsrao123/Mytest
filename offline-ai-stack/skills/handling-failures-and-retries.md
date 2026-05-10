# Skill: Handling Failures & Retries

## Think first
- Is this failure transient (worth retrying) or permanent (fail fast)?
- What's my retry budget — both attempt count AND wall-clock total?
- Is the underlying operation idempotent? If not, what idempotency key makes it so?
- On final failure, what *typed* error do I surface, and does the caller have enough context to react?

1. **Classify before retrying.** Transient (network blip, 503) → retry. Permanent (400, 401, 422) → don't.
2. Every retry needs a budget: max attempts AND max total time. Unbounded retries are an outage.
3. Exponential backoff with full jitter (`random.uniform(0, base * 2**n)`) — fixed sleeps cause thundering herds.
4. Make retries idempotent. If the operation isn't idempotent, add an idempotency key before adding retries.
5. On giving up, surface a typed error with the underlying cause attached. Don't swallow.
6. Log every retry decision (attempt #, delay, reason). Silent retries hide outages.
