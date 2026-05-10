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

## Plan
For each test:
1. Name encodes (unit, scenario, expected); commit to it before writing the body.
2. Arrange / Act / Assert sections are visually separated by blank lines.
3. Stop and mentally mutate the production code; confirm the test would fail under the mutation.
4. Run the test; commit at green.
Definition of done: AAA visible + name encodes the case + mental-mutation test passed.
Rollback if: mutation doesn't fail the test — the test is decorative; rewrite before merging.

## Validation
Before merging, verify:
1. The test name encodes (unit, scenario, expected).
2. AAA sections are visually separated.
3. Mental-mutation: a deliberate bug in the production code would fail this test.
4. No assertion on call counts / private methods / implementation details.
Pass: name + AAA + mutation-test passed + behavior-only assertions.
Fail action: rewrite the test; if it can't catch a deliberate bug, it's decorative.

## Agentic capabilities
- **Tools required:** test runner, coverage tool, mutation-test runner (mutmut / cosmic-ray) when available.
- **Subagents:** Dispatch a mutation-test subagent to verify the test catches deliberate bugs.
- **Memory writes:** Persist (unit → test patterns, edge cases covered) for future unit-test consistency.
- **Escalate when:** The unit can't be tested without mocks on owned code — the unit's design is wrong; refactor first.
- **Autonomy budget:** Test authoring autonomous. Skipping coverage targets requires PR-level justification.

1. One concept per test. Name describes the case: `test_<unit>_<scenario>_<expected>`.
2. Arrange / Act / Assert, in that order, with blank lines between. No surprises hidden in fixtures.
3. Test behavior, not implementation. Asserting "method foo was called twice" is a smell.
4. Cover the happy path, the boundary, and one failure mode each — minimum.
5. Tests must be deterministic: no real network, no real clock, no sleeps > 100 ms, no order-dependence.
6. A test that doesn't fail when the code is broken is worse than no test. Mutate the code to confirm the test fails.
