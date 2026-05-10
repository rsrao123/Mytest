# Skill: Writing Tests

## Think first
- What is the *one* concept this test covers, and does the name encode it?
- Are the AAA sections (Arrange / Act / Assert) clearly separated and free of fixture surprises?
- Am I testing behavior, or am I drifting into asserting on implementation (call counts, internal calls)?
- If I mutated the production code to be wrong, would this test fail? If not, the test is decorative.

## Reasoning
For each test, design in this order:
1. State the one concept under test; encode it in the name (`test_<unit>_<scenario>_<expected>`).
2. **Arrange** — inputs and fixtures, no surprises hidden in setup.
3. **Act** — the single behavior under test.
4. **Assert** on observable behavior, not implementation; mentally mutate the production code and confirm the test would fail.

1. One concept per test. Name describes the case: `test_<unit>_<scenario>_<expected>`.
2. Arrange / Act / Assert, in that order, with blank lines between. No surprises hidden in fixtures.
3. Test behavior, not implementation. Asserting "method foo was called twice" is a smell.
4. Cover the happy path, the boundary, and one failure mode each — minimum.
5. Tests must be deterministic: no real network, no real clock, no sleeps > 100 ms, no order-dependence.
6. A test that doesn't fail when the code is broken is worse than no test. Mutate the code to confirm the test fails.
