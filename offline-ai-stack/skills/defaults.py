"""Default thinking baseline that every workflow agent inherits.

Every agent defined in `crews/*.py` must be wired with `with_defaults(...)`
instead of bare `inject(...)`. The two `BASE_THINKING_SKILLS` are the
universal anti-failure defaults named in `docs/SUPERPOWERS.md` §4 — they
load *before* role-specific skills so role conflicts can be resolved
inside the meta-skill rather than at runtime.

The convention is enforced by:
- `tests/test_default_thinking.py::test_with_defaults_prepends_base_skills`
- `tests/test_default_thinking.py::test_each_crew_uses_with_defaults`
"""
from .loader import inject

BASE_THINKING_SKILLS: tuple[str, ...] = (
    "using-skills-effectively",
    "handling-uncertainty",
)
"""The two skills every workflow agent gets unconditionally.

- ``using-skills-effectively`` — meta-skill on composing other skills:
  name conflicts explicitly, cap at 2-3 loaded, log post-task helpfulness.
- ``handling-uncertainty`` — anti-fabrication: tag every fact as
  known/inferred/guessed; never invent filenames, APIs, or versions.

These two cover the failure modes that recur across *every* role: poor
skill composition and silent fabrication. Everything else is
role-specific and lives in the per-agent skill list.
"""


def with_defaults(agent, *role_skills: str):
    """Inject BASE_THINKING_SKILLS, then role-specific skills, onto ``agent``.

    Equivalent to ``inject(agent, *BASE_THINKING_SKILLS, *role_skills)``.
    Use this wrapper for every agent defined in ``crews/`` so the
    thinking baseline is impossible to forget. The defaults are loaded
    first so a role-specific skill that overrides them has the final say.
    """
    return inject(agent, *BASE_THINKING_SKILLS, *role_skills)
