"""Smoke tests for skills.loader.

These run without vLLM, Chroma, or any service; they only touch the local
markdown skill files and an in-memory dummy agent.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from skills.loader import SKILLS_DIR, inject, load  # noqa: E402


REQUIRED_SKILLS = [
    "architecture-decision-record",
    "brainstorming",
    "code-search",
    "commit-discipline",
    "dependency-hygiene",
    "dispatching-parallel-agents",
    "executing-plans",
    "frontend-design",
    "incident-response",
    "pr-review",
    "prompt-engineering",
    "refactoring",
    "security-review",
    "subagent-driven-development",
    "systematic-debugging",
    "test-driven-development",
    "writing-plans",
]


def test_skills_dir_resolves_inside_package():
    assert SKILLS_DIR.is_dir()
    assert (SKILLS_DIR / "loader.py").is_file()


@pytest.mark.parametrize("name", REQUIRED_SKILLS)
def test_each_required_skill_file_exists(name: str):
    path = SKILLS_DIR / f"{name}.md"
    assert path.is_file(), f"Missing skill file: {path}"
    body = path.read_text()
    assert body.lstrip().startswith("# Skill:"), f"{name}.md should start with '# Skill:'"


def test_load_concatenates_named_skills():
    out = load("brainstorming", "writing-plans")
    assert "# Skill: Brainstorming" in out
    assert "# Skill: Writing Plans" in out
    assert out.index("Brainstorming") < out.index("Writing Plans")


def test_load_raises_on_missing_skill():
    with pytest.raises(FileNotFoundError):
        load("definitely-not-a-real-skill")


def test_inject_appends_skill_text_to_backstory():
    agent = SimpleNamespace(backstory="base")
    returned = inject(agent, "brainstorming")
    assert returned is agent
    assert agent.backstory.startswith("base\n\n")
    assert "# Skill: Brainstorming" in agent.backstory


def test_inject_supports_multiple_skills():
    agent = SimpleNamespace(backstory="x")
    inject(agent, "writing-plans", "executing-plans")
    assert "Writing Plans" in agent.backstory
    assert "Executing Plans" in agent.backstory
