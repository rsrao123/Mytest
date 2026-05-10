# Skill: Avoiding Mocks

## Think first
- What real component am I about to mock — and why exactly can't I use it directly here?
- Is this dep at the system boundary (acceptable target) or in the middle of code I own (smell)?
- If I write a fake instead of a mock, what behavioral contract must it honor?
- What's the cost when the real dep changes shape — does my mock catch it or hide it?

Default: don't mock. Mocks couple tests to implementation and rot fast.

1. **Real things first.** Use the real DB (sqlite/test container), real filesystem (tmpdir), real clock when ±1s is fine.
2. **Fakes over mocks.** A hand-written in-memory `FakeRepo` that behaves like the real one beats a chain of `mock.patch` calls.
3. **Mock at the boundary, not the unit.** Mock the HTTP client, never the function that calls it.
4. **Never mock what you own.** If your own code is hard to test without mocks, the design is wrong — fix the design.
5. If you must patch, scope tightly (`with patch(...) as m:`) and assert on observable behavior, not call counts.
