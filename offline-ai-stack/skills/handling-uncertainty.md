# Skill: Handling Uncertainty

## Think first
- For each fact I'm about to use: do I know it, or am I assuming it?
- Could I run a cheap experiment (read the file, check the type, run the test) to convert a guess to a fact?
- If I can't experiment cheaply, is this where I ask the user instead of guessing?
- Am I about to invent a detail (filename, API shape, version, behavior) I haven't actually seen?

1. State your confidence explicitly. "I'm sure" / "I think" / "I'm guessing" are different signals — surface them.
2. When you're guessing, run the cheapest experiment that converts the guess into knowledge before acting.
3. If you can't experiment cheaply, ask. One clarifying question now beats one rolled-back PR later.
4. Never silently invent a fact (filename, API shape, version, behavior). If you don't have it, say so and look it up.
5. When merging conflicting evidence, write down both and pick the one that's reproducible. Reproducibility > authority.
