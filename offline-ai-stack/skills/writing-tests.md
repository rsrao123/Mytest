# Skill: Writing Tests
1. One concept per test. Name describes the case: `test_<unit>_<scenario>_<expected>`.
2. Arrange / Act / Assert, in that order, with blank lines between. No surprises hidden in fixtures.
3. Test behavior, not implementation. Asserting "method foo was called twice" is a smell.
4. Cover the happy path, the boundary, and one failure mode each — minimum.
5. Tests must be deterministic: no real network, no real clock, no sleeps > 100 ms, no order-dependence.
6. A test that doesn't fail when the code is broken is worse than no test. Mutate the code to confirm the test fails.
