# Skill: Defensive Programming Discipline

## Think first
- Where exactly is the trust boundary for this input — and am I on the inside or the outside?
- Has this value already been validated upstream by code I control?
- If I removed this check, what observable failure would appear, and where in the stack?
- Am I asserting an invariant (must always hold) or validating user input (might be wrong)? They want different tools.

## Reasoning
For each defensive check, work through:
1. Locate the trust boundary; place the check just on the inside.
2. Walk the call graph: has upstream code in this codebase already validated this value?
3. Predict the observable failure mode if the check is removed (typed exception, traceback, silent corruption).
4. Conclude: keep at boundary / drop redundant / convert to assertion documenting an invariant.

## Plan
For each candidate check:
1. Locate the trust boundary; place the check just on the inside.
2. Walk callers and remove redundant downstream checks.
3. Stop and add an adversarial-input fixture test against the boundary check.
4. Definition of done: one validation per boundary; no duplicate upstream/downstream checks.
Rollback if: a redundant check gets re-added in review — escalate to the architect for a project-wide policy decision.

Defensive checks have a cost: they hide bugs and inflate code. Use them where they earn their keep.

1. **Validate at boundaries** (HTTP, queue, file I/O, FFI). Trust internal calls.
2. **Fail fast.** A bad input should produce a typed error at the boundary, not a confused state three layers deep.
3. **No defensive `try/except`** around code that can't actually fail. If you can't name the exception, don't catch it.
4. **No `is None` guards** on values your own caller already validated. Duplicate checks rot out of sync.
5. **Assert invariants**, not inputs. Assertions document what *must* be true at this point — they're not user input validation.
6. When in doubt, prefer crashing loudly to limping silently. A traceback is a feature.
