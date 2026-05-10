# Skill: Incident Response
Stabilize → Diagnose → Fix → Postmortem.

1. **Stabilize first.** Roll back, disable the feature flag, or scale up — whatever stops user pain. Diagnosis comes after.
2. Open a single source of truth (incident channel/doc). Timestamps for every action.
3. **Diagnose** with hypotheses, not vibes. State expected vs observed; bisect deploys/configs.
4. **Fix** the root cause, not just the symptom. Add a regression test or alert.
5. **Postmortem** within 48 hours, blameless. Required sections: timeline, impact, root cause, what worked, what didn't, action items with owners.
