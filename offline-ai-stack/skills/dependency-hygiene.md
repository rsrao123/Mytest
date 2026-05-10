# Skill: Dependency Hygiene

## Think first
- Why this dep over the standard library or an existing project dep?
- What's its license, last-release date, maintainer count, and CVE history?
- What surface area does it expose that I don't actually need?
- If this dep disappeared in a year, how hard would the rip-and-replace be?

## Reasoning
Before adding any dep, work through:
1. Compare against stdlib + existing project deps; name the concrete capability missing.
2. Audit license, last release date, maintainer count, open-CVE count.
3. Catalog the surface used vs total surface offered; flag if usage < 10%.
4. Conclude: add (with one-line justification) / use stdlib / use existing / hand-roll.

1. **Pin** every direct dependency to an exact version; let the lockfile pin transitives.
2. **Audit** weekly: `pip-audit`, `npm audit`, `safety check`, `trivy fs`.
3. **Update on a schedule**, not in panic. One dependency per PR; run the full test suite.
4. Prefer the standard library or a single well-maintained dep over many small ones.
5. Remove unused deps immediately; they expand the attack surface.
6. New deps need a one-liner justification in the PR (why this, why not stdlib, license).
