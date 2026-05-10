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

from skills import BASE_THINKING_SKILLS, with_defaults  # noqa: E402


# ----- Unit tests for the helper itself --------------------------------

def test_base_thinking_skills_are_named():
    """The baseline must include the two universal-default skills."""
    assert BASE_THINKING_SKILLS == ("using-skills-effectively", "handling-uncertainty")


def test_with_defaults_prepends_base_skills():
    """`with_defaults` must load BASE_THINKING_SKILLS *before* role skills."""
    agent = SimpleNamespace(backstory="base")
    returned = with_defaults(agent, "writing-plans")
    assert returned is agent
    body = agent.backstory
    # All three skills present.
    assert "# Skill: Using Skills Effectively" in body
    assert "# Skill: Handling Uncertainty" in body
    assert "# Skill: Writing Plans" in body
    # Order: defaults precede the role skill.
    base_idx = body.index("# Skill: Using Skills Effectively")
    uncert_idx = body.index("# Skill: Handling Uncertainty")
    role_idx = body.index("# Skill: Writing Plans")
    assert base_idx < uncert_idx < role_idx


def test_with_defaults_works_with_no_role_skills():
    """An agent with only the baseline must still get both default skills."""
    agent = SimpleNamespace(backstory="")
    with_defaults(agent)
    assert "# Skill: Using Skills Effectively" in agent.backstory
    assert "# Skill: Handling Uncertainty" in agent.backstory


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
