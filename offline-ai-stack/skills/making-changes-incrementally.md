# Skill: Making Changes Incrementally
1. Aim for small, reviewable diffs (≤ ~200 lines net). Bigger diffs hide mistakes and stall reviews.
2. Land structural changes first (renames, extracts, moves), then behavior changes — never bundle them.
3. Each commit must compile and pass tests. The chain should be `git bisect`-able.
4. If a change requires a flag, ship the flag-off path first; flip the flag in a follow-up.
5. When a refactor balloons, stop. Commit what works, open a new branch for the rest.
6. Prefer reversible changes when uncertain. Reversibility buys you time to learn.
