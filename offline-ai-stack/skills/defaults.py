"""Default thinking + reasoning baselines that every workflow agent inherits.

Every agent defined in `crews/*.py` must be wired with `with_defaults(...)`
instead of bare `inject(...)`. Two baselines load unconditionally before any
role-specific skills:

- `BASE_THINKING_SKILLS` — anti-failure metacognition shared across all roles.
- `BASE_REASONING_SKILLS` — universal "figure out what's right" procedures.

Loading order is `thinking → reasoning → deduped role-specific` so role
skills come last and have the final say on conflicts. Duplicates between
role-specific and baseline are dropped silently.

The convention is enforced by `tests/test_default_thinking.py`.
"""
from .loader import inject

BASE_THINKING_SKILLS: tuple[str, ...] = (
    "using-skills-effectively",
    "handling-uncertainty",
)
"""The two thinking skills every workflow agent gets unconditionally.

- ``using-skills-effectively`` — meta-skill on composing other skills:
  name conflicts explicitly, cap at 2-3 loaded, log post-task helpfulness.
- ``handling-uncertainty`` — anti-fabrication: tag every fact as
  known/inferred/guessed; never invent filenames, APIs, or versions.

These cover the failure modes that recur across *every* role: poor skill
composition and silent fabrication.
"""

BASE_REASONING_SKILLS: tuple[str, ...] = (
    "reading-code",
    "systematic-debugging",
)
"""The two reasoning skills every workflow agent gets unconditionally.

- ``reading-code`` — understand before changing: read tests first, trace one
  path end-to-end, match the file's style. Universal because *every* agent
  that touches a repo benefits from understanding the surrounding code
  before producing output, including planner / architect / doc-writer roles
  that don't write production code directly.
- ``systematic-debugging`` — hypothesis-driven thinking: state expected vs
  observed, propose a falsifying experiment, do not speculate without a
  test. Universal because *every* agent occasionally reasons about why
  something isn't behaving as expected — the doc writer chasing stale docs
  reasons the same way as the bug hunter chasing a regression.

These cover the universal reasoning failures: changing what you don't
understand, and jumping to a conclusion without testing it.
"""


def with_defaults(agent, *role_skills: str):
    """Inject thinking baseline → reasoning baseline → deduped role skills.

    The two baselines load first so a role-specific skill listed in the
    call site that duplicates a default is silently dropped (it's already
    loaded). This keeps call sites focused on what's *additional* to the
    baseline and prevents accidental double-loading.

    Order in the final backstory:
        1. BASE_THINKING_SKILLS in declaration order
        2. BASE_REASONING_SKILLS in declaration order
        3. role_skills in declaration order, minus anything in either baseline
    """
    seen = set(BASE_THINKING_SKILLS) | set(BASE_REASONING_SKILLS)
    deduped = [s for s in role_skills if s not in seen]
    return inject(
        agent,
        *BASE_THINKING_SKILLS,
        *BASE_REASONING_SKILLS,
        *deduped,
    )
