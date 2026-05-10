# Skill: Defensive Programming Discipline

## Think first
- Where exactly is the trust boundary for this input — and am I on the inside or the outside?
- Has this value already been validated upstream by code I control?
- If I removed this check, what observable failure would appear, and where in the stack?
- Am I asserting an invariant (must always hold) or validating user input (might be wrong)? They want different tools.

Defensive checks have a cost: they hide bugs and inflate code. Use them where they earn their keep.

1. **Validate at boundaries** (HTTP, queue, file I/O, FFI). Trust internal calls.
2. **Fail fast.** A bad input should produce a typed error at the boundary, not a confused state three layers deep.
3. **No defensive `try/except`** around code that can't actually fail. If you can't name the exception, don't catch it.
4. **No `is None` guards** on values your own caller already validated. Duplicate checks rot out of sync.
5. **Assert invariants**, not inputs. Assertions document what *must* be true at this point — they're not user input validation.
6. When in doubt, prefer crashing loudly to limping silently. A traceback is a feature.
