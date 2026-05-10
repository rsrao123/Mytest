# Skill: Handling Failures & Retries
1. **Classify before retrying.** Transient (network blip, 503) → retry. Permanent (400, 401, 422) → don't.
2. Every retry needs a budget: max attempts AND max total time. Unbounded retries are an outage.
3. Exponential backoff with full jitter (`random.uniform(0, base * 2**n)`) — fixed sleeps cause thundering herds.
4. Make retries idempotent. If the operation isn't idempotent, add an idempotency key before adding retries.
5. On giving up, surface a typed error with the underlying cause attached. Don't swallow.
6. Log every retry decision (attempt #, delay, reason). Silent retries hide outages.
