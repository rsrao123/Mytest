# Skill: YAGNI (You Aren't Gonna Need It)
1. Build for the requirement in front of you. Not the one you're imagining for next quarter.
2. Three similar lines beat a premature abstraction. Wait for the fourth before extracting.
3. No options, flags, or knobs without a current caller that needs them.
4. Don't add validation or error handling for cases that can't happen given current callers.
5. Delete dead branches as soon as you spot them — they accumulate maintenance cost without paying any.
6. The cost of removing a feature later is almost always lower than the cost of carrying an unused one.
