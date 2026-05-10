"""Skill loader: inject markdown skill prompts into CrewAI agent backstories."""
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent


def load(*names: str) -> str:
    """Concatenate the named skill files."""
    return "\n\n".join((SKILLS_DIR / f"{n}.md").read_text() for n in names)


def inject(agent, *names: str):
    """Append skill prompts to a CrewAI agent's backstory."""
    agent.backstory = f"{agent.backstory}\n\n{load(*names)}"
    return agent
