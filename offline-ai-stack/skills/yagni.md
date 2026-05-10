# Skill: YAGNI (You Aren't Gonna Need It)

## Think first
- Is there a *current* caller for this option, flag, abstraction, or extension point? If not, delete it.
- Have I seen this pattern at least three times, or am I extracting a helper after the second occurrence?
- Could I delete a branch entirely instead of generalizing it?
- Am I designing for next quarter when I should be shipping this week?

## Reasoning
Before adding any abstraction / option / flag, work through:
1. Name the *current* caller; if there isn't one, delete instead of generalizing.
2. Count occurrences of the pattern; if < 3, inline rather than extract.
3. Compare cost of adding the abstraction now vs adding it when the third real caller appears.
4. Conclude: ship the simple form; defer abstraction with a note explaining when it would unlock.

## Plan
Before adding any abstraction / option / flag:
1. Name the *current* real caller; if there isn't one, stop and delete instead.
2. Count occurrences of the pattern; if < 3, inline rather than extract.
3. Stop and weigh: cost-of-adding-now vs cost-of-adding-when-third-real-caller-appears.
4. Default: ship the simple form; leave a deferred-extraction note explaining when it would unlock.
Definition of done: simple form shipped + deferred-extraction note present (if applicable).
Rollback if: an abstraction got added without a current real caller — inline immediately and file the lesson.

## Validation
Before merging, verify:
1. No abstraction / option / flag landed without a current real caller.
2. No helper extracted with < 3 occurrences in the codebase.
3. Deferred-extraction notes (where applicable) name the unlock condition.
4. The diff is no larger than the smallest implementation that satisfies the requirement.
Pass: no caller-less abstractions + no premature extracts + notes present + minimal diff.
Fail action: inline the abstraction; ship the simple form.

1. Build for the requirement in front of you. Not the one you're imagining for next quarter.
2. Three similar lines beat a premature abstraction. Wait for the fourth before extracting.
3. No options, flags, or knobs without a current caller that needs them.
4. Don't add validation or error handling for cases that can't happen given current callers.
5. Delete dead branches as soon as you spot them — they accumulate maintenance cost without paying any.
6. The cost of removing a feature later is almost always lower than the cost of carrying an unused one.
