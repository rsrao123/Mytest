# Project Conventions

The compliance reviewer in `crews/code_review.py` audits PRs against this file.
Copy it into a project repo as `CONVENTIONS.md` (or `CLAUDE.md`) and edit to fit.

## Code style
- Format with the project's chosen formatter (e.g., black, prettier, gofmt). No exceptions.
- No trailing whitespace, no tabs in Python, LF line endings.
- Imports grouped: stdlib, third-party, local — separated by blank lines.

## Naming
- Modules: `snake_case`. Classes: `PascalCase`. Functions/vars: `snake_case`.
- Tests: `test_<unit>_<scenario>` describes what is being tested and the case.

## Comments
- Default to no comment. Add one only when the WHY is non-obvious.
- No "// removed X" / "# was: ..." breadcrumbs. The history is in git.
- No multi-paragraph docstrings on private functions.

## Errors
- Validate at system boundaries (HTTP, queue, file I/O). Trust internal calls.
- Never silently swallow exceptions. If catching, comment why.
- Use the project's logger; no `print` in committed code.

## Tests
- New code paths get unit tests. Bug fixes get a regression test.
- Tests are fast and deterministic. No real network, no real clock, no sleeps > 100ms.

## Commits & PRs
- Conventional Commits: `type(scope): subject`. Imperative mood. ≤72 chars.
- One logical change per commit. Refactor commits are separate from feature commits.
- PR description has: Summary, Test plan, Rollback.

## Security
- No secrets in source, fixtures, or commit messages.
- All user input crossing a trust boundary is validated.
- See `skills/security-review.md` for the audit checklist.
