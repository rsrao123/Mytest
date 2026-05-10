# Skill: Incident Response

## Think first
- Is user pain still active right now? If yes, stabilize before anything else.
- Where's the source-of-truth doc/channel, and have I started a timestamped timeline?
- Am I forming hypotheses, or am I just pattern-matching on past incidents?
- What's my rollback plan if my fix makes the incident worse?

Stabilize → Diagnose → Fix → Postmortem.

1. **Stabilize first.** Roll back, disable the feature flag, or scale up — whatever stops user pain. Diagnosis comes after.
2. Open a single source of truth (incident channel/doc). Timestamps for every action.
3. **Diagnose** with hypotheses, not vibes. State expected vs observed; bisect deploys/configs.
4. **Fix** the root cause, not just the symptom. Add a regression test or alert.
5. **Postmortem** within 48 hours, blameless. Required sections: timeline, impact, root cause, what worked, what didn't, action items with owners.
