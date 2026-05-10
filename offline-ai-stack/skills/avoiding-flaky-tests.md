# Skill: Avoiding Flaky Tests

## Think first
- What sources of nondeterminism does this code touch (time, randomness, threads, network, FS, ordering)?
- Which of those are inputs I can control, and which are outputs I have to assert against?
- Where does shared mutable state live, and could a previous test have left it in an unexpected state?
- What would I have to change to make this test fail reliably 100/100 times?

## Reasoning
For each test under suspicion, walk through:
1. Enumerate every nondeterministic source the code touches (time, RNG, threads, network, FS, ordering).
2. Classify each: input I can pin (control) vs output I must assert against.
3. Locate shared mutable state and any prior-test mutation paths.
4. Conclude with a fixture/seeding/freezing plan that makes the test 100/100 reliable.

## Plan
Before merging the test:
1. Apply the fixture/freezing strategy from Reasoning step 4.
2. Run the test 100× locally (or in a CI matrix); confirm 100% pass.
3. Stop and re-read the diff for residual sleeps > 100ms, unseeded randomness, or shared module state.
4. Definition of done: 100/100 passes locally + zero unseeded RNG + zero `time.sleep > 100ms`.
Rollback if: any single flake post-merge — quarantine within 24h and reopen the trace.

## Validation
After landing the test, verify:
1. CI pass rate ≥ 100/100 over a forced rerun matrix.
2. `grep -n "time.sleep" the_test_file` returns 0 hits, or every hit is < 100ms.
3. Every random source has an explicit seed; every clock is frozen via fixture.
4. The test name encodes the scenario it pins down.
Pass: 100/100 + no unbounded sleep + seeded RNG + frozen clock.
Fail action: quarantine immediately; return to Plan step 1 with the residual nondeterminism named.

A flaky test is worse than no test — it trains the team to ignore failures.

Sources of flakiness, in order of frequency:
1. **Time.** `datetime.now()` in production code; freeze it in tests (`freezegun`, fake clock).
2. **Order.** Tests that depend on shared mutable state. Use fresh fixtures per test; don't mutate module-level globals.
3. **Concurrency.** Real threads/async with no synchronization. Use deterministic schedulers or assert on reachable states.
4. **Floating point.** `assertEqual(0.1 + 0.2, 0.3)` is flaky. Use `pytest.approx`.
5. **External services.** No real network in unit tests. Period.
6. **Random.** Seed it (`random.seed(0)`); never use unseeded randomness in tests.

When a test fails intermittently, **quarantine it on first occurrence** and fix the cause within a week — don't normalize it.
