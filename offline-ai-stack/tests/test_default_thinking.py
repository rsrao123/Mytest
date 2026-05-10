"""Enforcement tests for the default-thinking baseline.

Every workflow agent in `crews/*.py` must be wired with `with_defaults(...)`
rather than bare `inject(...)`. The two `BASE_THINKING_SKILLS` then load
unconditionally before any role-specific skills. See
`skills/defaults.py` and `docs/SUPERPOWERS.md` §4.
"""
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from skills import (  # noqa: E402
    BASE_PLANNING_SKILLS,
    BASE_REASONING_SKILLS,
    BASE_THINKING_SKILLS,
    with_defaults,
)


# ----- Unit tests for the helper itself --------------------------------

def test_base_thinking_skills_are_named():
    """The thinking baseline must include the two universal-default skills."""
    assert BASE_THINKING_SKILLS == ("using-skills-effectively", "handling-uncertainty")


def test_base_reasoning_skills_are_named():
    """The reasoning baseline must include the two universal-default skills."""
    assert BASE_REASONING_SKILLS == ("reading-code", "systematic-debugging")


def test_base_planning_skills_are_named():
    """The planning baseline must include the two universal-default skills."""
    assert BASE_PLANNING_SKILLS == ("writing-plans", "executing-plans")


def test_baselines_do_not_overlap():
    """A skill appearing in two baselines would be a redundancy bug."""
    thinking, reasoning, planning = (
        set(BASE_THINKING_SKILLS),
        set(BASE_REASONING_SKILLS),
        set(BASE_PLANNING_SKILLS),
    )
    assert thinking.isdisjoint(reasoning)
    assert thinking.isdisjoint(planning)
    assert reasoning.isdisjoint(planning)


def test_with_defaults_loads_thinking_then_reasoning_then_planning_then_role():
    """`with_defaults` must load thinking → reasoning → planning → role in that order."""
    agent = SimpleNamespace(backstory="base")
    returned = with_defaults(agent, "yagni")
    assert returned is agent
    body = agent.backstory
    # All seven skills present (6 baseline + 1 role).
    for marker in (
        "# Skill: Using Skills Effectively",
        "# Skill: Handling Uncertainty",
        "# Skill: Reading Code",
        "# Skill: Systematic Debugging",
        "# Skill: Writing Plans",
        "# Skill: Executing Plans",
        "# Skill: YAGNI",
    ):
        assert marker in body, f"Missing skill marker: {marker}"
    # Order: thinking → reasoning → planning → role.
    indexes = [
        body.index("# Skill: Using Skills Effectively"),
        body.index("# Skill: Handling Uncertainty"),
        body.index("# Skill: Reading Code"),
        body.index("# Skill: Systematic Debugging"),
        body.index("# Skill: Writing Plans"),
        body.index("# Skill: Executing Plans"),
        body.index("# Skill: YAGNI"),
    ]
    assert indexes == sorted(indexes), f"Skills out of order: {indexes}"


def test_with_defaults_works_with_no_role_skills():
    """An agent with only the baseline must still get all six default skills."""
    agent = SimpleNamespace(backstory="")
    with_defaults(agent)
    for marker in (
        "# Skill: Using Skills Effectively",
        "# Skill: Handling Uncertainty",
        "# Skill: Reading Code",
        "# Skill: Systematic Debugging",
        "# Skill: Writing Plans",
        "# Skill: Executing Plans",
    ):
        assert marker in agent.backstory


def test_with_defaults_dedupes_role_against_thinking_baseline():
    """A role skill that's already in the thinking baseline must be dropped silently."""
    agent = SimpleNamespace(backstory="")
    with_defaults(agent, "using-skills-effectively", "yagni")
    # Should appear exactly once (from the baseline), not twice.
    assert agent.backstory.count("# Skill: Using Skills Effectively") == 1
    assert agent.backstory.count("# Skill: YAGNI") == 1


def test_with_defaults_dedupes_role_against_reasoning_baseline():
    """A role skill that's already in the reasoning baseline must be dropped silently."""
    agent = SimpleNamespace(backstory="")
    with_defaults(agent, "systematic-debugging", "code-search")
    assert agent.backstory.count("# Skill: Systematic Debugging") == 1
    assert agent.backstory.count("# Skill: Code Search") == 1


def test_with_defaults_dedupes_role_against_planning_baseline():
    """A role skill that's already in the planning baseline must be dropped silently."""
    agent = SimpleNamespace(backstory="")
    with_defaults(agent, "writing-plans", "executing-plans", "yagni")
    assert agent.backstory.count("# Skill: Writing Plans") == 1
    assert agent.backstory.count("# Skill: Executing Plans") == 1
    assert agent.backstory.count("# Skill: YAGNI") == 1


# ----- Enforcement: every crew uses with_defaults ----------------------

CREW_FILES = [
    "crews/dev_team.py",
    "crews/code_review.py",
    "crews/exec_review.py",
    "crews/security_review.py",
]


@pytest.mark.parametrize("crew_path", CREW_FILES)
def test_crew_imports_with_defaults(crew_path: str):
    """Each crew file must import `with_defaults` from skills."""
    text = (ROOT / crew_path).read_text()
    assert re.search(r"from\s+skills\s+import\s+.*\bwith_defaults\b", text), (
        f"{crew_path} must `from skills import with_defaults`"
    )


@pytest.mark.parametrize("crew_path", CREW_FILES)
def test_crew_does_not_use_bare_inject(crew_path: str):
    """Crews must use `with_defaults`, not bare `inject`.

    Bare `inject(agent, *role_skills)` would skip the baseline; the
    enforcement is at the source level rather than runtime because
    constructing the agents requires PROJECT_DIR + vLLM endpoints.
    """
    text = (ROOT / crew_path).read_text()
    # Allow imports of inject (some files may import both); only ban the call form.
    bad = re.findall(r"(?<!_)\binject\s*\(\s*Agent", text)
    assert not bad, (
        f"{crew_path} uses bare `inject(Agent(...))`; use `with_defaults(Agent(...), ...)` instead"
    )


@pytest.mark.parametrize("crew_path", CREW_FILES)
def test_every_agent_in_crew_is_wrapped(crew_path: str):
    """Every `Agent(...)` constructor in a crew must be wrapped in `with_defaults(...)`.

    Detection: count top-level `Agent(` calls (excluding the import line and
    excluding occurrences immediately preceded by `with_defaults(`). Then
    count `with_defaults(` calls. They must match.
    """
    text = (ROOT / crew_path).read_text()
    # All Agent constructor calls (heuristic: `Agent(` preceded by `=` or `(` or whitespace).
    agent_calls = len(re.findall(r"(?<![A-Za-z_])Agent\s*\(", text))
    # `with_defaults(` calls (each wraps one Agent).
    with_defaults_calls = len(re.findall(r"with_defaults\s*\(", text))
    assert agent_calls > 0, f"{crew_path} has no Agent() calls — is the file empty?"
    assert with_defaults_calls >= agent_calls, (
        f"{crew_path} has {agent_calls} Agent() calls but only {with_defaults_calls} "
        f"with_defaults(...) wrappers; every agent must be wrapped"
    )
