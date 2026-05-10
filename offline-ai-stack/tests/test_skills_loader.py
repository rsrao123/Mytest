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
    "avoiding-flaky-tests",
    "avoiding-mocks",
    "brainstorming",
    "code-search",
    "commit-discipline",
    "defensive-programming-discipline",
    "dependency-hygiene",
    "dispatching-parallel-agents",
    "executing-plans",
    "explaining-changes",
    "frontend-design",
    "giving-code-review",
    "handling-failures-and-retries",
    "handling-uncertainty",
    "incident-response",
    "making-changes-incrementally",
    "pr-review",
    "prompt-engineering",
    "reading-code",
    "refactoring",
    "requesting-code-review",
    "root-cause-tracing",
    "security-review",
    "subagent-driven-development",
    "systematic-debugging",
    "test-driven-development",
    "using-skills-effectively",
    "working-with-legacy-code",
    "writing-plans",
    "writing-tests",
    "yagni",
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


@pytest.mark.parametrize("name", REQUIRED_SKILLS)
def test_each_skill_has_think_first_section(name: str):
    """Every skill must include a `## Think first` section with at least 3 reflective prompts.

    The thinking section forces deliberation before the agent applies the imperative rules.
    See docs/SUPERPOWERS.md §5 for the authoring contract.
    """
    body = (SKILLS_DIR / f"{name}.md").read_text()
    assert "## Think first" in body, f"{name}.md is missing the '## Think first' section"
    section = body.split("## Think first", 1)[1]
    # Stop at the next H2 or numbered list start, whichever comes first.
    end_markers = ["\n## ", "\n1. "]
    end_idx = min(
        (section.find(m) for m in end_markers if section.find(m) >= 0),
        default=len(section),
    )
    bullets = [
        line for line in section[:end_idx].splitlines()
        if line.strip().startswith("- ") and len(line.strip()) > 4
    ]
    assert len(bullets) >= 3, (
        f"{name}.md '## Think first' section has only {len(bullets)} prompts; need ≥ 3"
    )


@pytest.mark.parametrize("name", REQUIRED_SKILLS)
def test_each_skill_has_reasoning_section(name: str):
    """Every skill must include a `## Reasoning` section with a numbered inference procedure.

    The reasoning section is a domain-specific inference chain the agent produces as written
    output before applying the rules. It must list at least 3 numbered steps. See
    docs/SUPERPOWERS.md §5 for the authoring contract.
    """
    body = (SKILLS_DIR / f"{name}.md").read_text()
    assert "## Reasoning" in body, f"{name}.md is missing the '## Reasoning' section"
    section = body.split("## Reasoning", 1)[1]
    # Stop at the next H2 or end-of-file.
    end_idx = section.find("\n## ")
    if end_idx < 0:
        end_idx = len(section)
    numbered = [
        line for line in section[:end_idx].splitlines()
        if line.strip()[:2].rstrip(".").isdigit() and "." in line.strip()[:3]
    ]
    assert len(numbered) >= 3, (
        f"{name}.md '## Reasoning' section has only {len(numbered)} numbered steps; need ≥ 3"
    )


@pytest.mark.parametrize("name", REQUIRED_SKILLS)
def test_each_skill_has_plan_section(name: str):
    """Every skill must include a `## Plan` section: a domain-specific work program.

    The plan layer turns the reasoning verdict into an executable sequence with stop-gates,
    a definition of done, and a rollback condition. See docs/SUPERPOWERS.md §5 for the
    authoring contract.
    """
    body = (SKILLS_DIR / f"{name}.md").read_text()
    assert "## Plan" in body, f"{name}.md is missing the '## Plan' section"
    section = body.split("## Plan", 1)[1]
    end_idx = section.find("\n## ")
    if end_idx < 0:
        end_idx = len(section)
    plan_text = section[:end_idx]
    numbered = [
        line for line in plan_text.splitlines()
        if line.strip()[:2].rstrip(".").isdigit() and "." in line.strip()[:3]
    ]
    assert len(numbered) >= 3, (
        f"{name}.md '## Plan' has only {len(numbered)} numbered actions; need ≥ 3"
    )
    lower = plan_text.lower()
    assert "definition of done" in lower, (
        f"{name}.md '## Plan' is missing 'Definition of done'"
    )
    assert "rollback if" in lower, (
        f"{name}.md '## Plan' is missing 'Rollback if'"
    )


@pytest.mark.parametrize("name", REQUIRED_SKILLS)
def test_each_skill_has_validation_section(name: str):
    """Every skill must include a `## Validation` section: post-action evidence checks.

    The validation layer collects observable evidence that the work product meets the
    Plan's Definition of done. It must list at least 3 numbered checks, plus explicit
    'Pass:' criteria and a 'Fail action:' recovery. See docs/SUPERPOWERS.md §5 for the
    authoring contract.
    """
    body = (SKILLS_DIR / f"{name}.md").read_text()
    assert "## Validation" in body, f"{name}.md is missing the '## Validation' section"
    section = body.split("## Validation", 1)[1]
    end_idx = section.find("\n## ")
    if end_idx < 0:
        end_idx = len(section)
    val_text = section[:end_idx]
    numbered = [
        line for line in val_text.splitlines()
        if line.strip()[:2].rstrip(".").isdigit() and "." in line.strip()[:3]
    ]
    assert len(numbered) >= 3, (
        f"{name}.md '## Validation' has only {len(numbered)} numbered checks; need ≥ 3"
    )
    lower = val_text.lower()
    assert "pass:" in lower, f"{name}.md '## Validation' is missing 'Pass:' criteria"
    assert "fail action:" in lower, (
        f"{name}.md '## Validation' is missing 'Fail action:' recovery"
    )


@pytest.mark.parametrize("name", REQUIRED_SKILLS)
def test_skill_section_order(name: str):
    """`## Think first` → `## Reasoning` → `## Plan` → `## Validation` is the required order.

    The five layers are sequential: deliberate (Think first) → reason (Reasoning) →
    plan (Plan) → act (numbered rules) → validate (Validation, post-action evidence).
    """
    body = (SKILLS_DIR / f"{name}.md").read_text()
    think_idx = body.find("## Think first")
    reason_idx = body.find("## Reasoning")
    plan_idx = body.find("## Plan")
    val_idx = body.find("## Validation")
    assert all(i >= 0 for i in (think_idx, reason_idx, plan_idx, val_idx))
    assert think_idx < reason_idx < plan_idx < val_idx, (
        f"{name}.md: section order must be Think first → Reasoning → Plan → Validation"
    )


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
