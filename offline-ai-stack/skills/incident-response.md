# Skill: Incident Response

## Think first
- Is user pain still active right now? If yes, stabilize before anything else.
- Where's the source-of-truth doc/channel, and have I started a timestamped timeline?
- Am I forming hypotheses, or am I just pattern-matching on past incidents?
- What's my rollback plan if my fix makes the incident worse?

## Reasoning
Work through these phases in order:
1. **Stabilize.** Pick the cheapest mitigation (rollback / flag flip / scale up); record the action with timestamp.
2. **Diagnose.** State expected vs observed; form a falsifiable hypothesis; bisect deploys/configs.
3. **Fix.** Target the root cause + add a regression test or alert that would have caught it.
4. **Postmortem.** Within 48h, blameless: timeline / impact / root cause / what worked / what didn't / actions with owners.

## Plan
Run these phases in order:
1. Stabilize — pick the cheapest mitigation (rollback / flag / scale); record action + timestamp in the incident channel.
2. Diagnose — falsifiable hypothesis; bisect deploys/configs; record findings in the timeline.
3. Stop and write the timeline so far before applying any fix.
4. Fix the root cause + add a regression alert; verify in staging where possible.
5. Postmortem within 48h; assign action items with owners and due dates.
Definition of done: incident closed + postmortem published + action items tracked.
Rollback if: the fix worsens the incident — invoke the stabilize-action recorded in step 1; resume diagnosis.

Stabilize → Diagnose → Fix → Postmortem.

1. **Stabilize first.** Roll back, disable the feature flag, or scale up — whatever stops user pain. Diagnosis comes after.
2. Open a single source of truth (incident channel/doc). Timestamps for every action.
3. **Diagnose** with hypotheses, not vibes. State expected vs observed; bisect deploys/configs.
4. **Fix** the root cause, not just the symptom. Add a regression test or alert.
5. **Postmortem** within 48 hours, blameless. Required sections: timeline, impact, root cause, what worked, what didn't, action items with owners.
