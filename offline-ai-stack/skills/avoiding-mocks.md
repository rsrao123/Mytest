# Skill: Avoiding Mocks

## Think first
- What real component am I about to mock — and why exactly can't I use it directly here?
- Is this dep at the system boundary (acceptable target) or in the middle of code I own (smell)?
- If I write a fake instead of a mock, what behavioral contract must it honor?
- What's the cost when the real dep changes shape — does my mock catch it or hide it?

## Reasoning
Before writing a mock, work through:
1. Name the real component and the concrete reason it can't be used in this test.
2. Locate it: at the system boundary (mock acceptable) or inside code I own (smell — refactor instead).
3. If a fake will replace it, write the behavioral contract the fake must honor.
4. Conclude with one of: real / fake / boundary-mock — and a one-line justification recorded in the test.

## Plan
Before writing the test:
1. Try the real component first; if it passes in CI in under 5s, ship.
2. If real isn't viable, write a minimal fake honoring the documented contract.
3. Stop and check: is the fake at a system boundary (acceptable) or replacing internal code (refactor design instead)?
4. Definition of done: zero `mock.patch` on code we own; fakes have inline justification.
Rollback if: the fake's contract diverges from the real dep — fix the contract, don't paper over it.

## Validation
After writing the test, verify:
1. `grep -n "mock.patch\|@patch" the_test_file` returns 0 hits on code we own.
2. Any fakes are documented inline with a one-line behavioral contract.
3. Boundary mocks (HTTP / SDK) are scoped via `with patch(...) as m:`, not module-level.
4. The test passes against the real component when run in integration mode.
Pass: 0 owned-code mocks + fakes documented + boundary mocks scoped + integration green.
Fail action: refactor to use real or fake; do not relax the rule.

Default: don't mock. Mocks couple tests to implementation and rot fast.

1. **Real things first.** Use the real DB (sqlite/test container), real filesystem (tmpdir), real clock when ±1s is fine.
2. **Fakes over mocks.** A hand-written in-memory `FakeRepo` that behaves like the real one beats a chain of `mock.patch` calls.
3. **Mock at the boundary, not the unit.** Mock the HTTP client, never the function that calls it.
4. **Never mock what you own.** If your own code is hard to test without mocks, the design is wrong — fix the design.
5. If you must patch, scope tightly (`with patch(...) as m:`) and assert on observable behavior, not call counts.
