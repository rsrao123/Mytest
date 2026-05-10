"""Standalone security-review agent — replacement for /security-review.

Wraps the security-review skill prompt and audits a diff in isolation.
Pair with scripts/security_scan.sh (static scanners) for full coverage.
"""
import sys
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from skills.loader import inject  # noqa: E402

llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",
    api_key="local",
    model="mistralai/Devstral-Small-2-24B-Instruct-2512",
    temperature=0.0,
)

security_reviewer = inject(
    Agent(
        role="Security Reviewer",
        goal=(
            "Find injections, auth holes, secrets, unsafe deserialization, "
            "and OWASP top-10 issues in the diff."
        ),
        backstory="Treats every input as hostile until proven otherwise.",
        llm=llm, tools=[FileReadTool()], allow_delegation=False,
    ),
    "security-review",
)


def build(diff_path: str) -> Crew:
    diff = Path(diff_path).read_text()
    task = Task(
        agent=security_reviewer,
        description=(
            "Audit the following diff against the security-review checklist. "
            "Report findings in the prescribed schema and end with a triage "
            "recommendation.\n\n"
            f"```diff\n{diff[:8000]}\n```"
        ),
        expected_output=(
            "A list of findings (SEVERITY, FILE:LINE, EXPLOIT, FIX) followed "
            "by a triage recommendation."
        ),
    )
    return Crew(
        agents=[security_reviewer],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: security_review.py <change.diff>", file=sys.stderr)
        sys.exit(2)
    crew = build(sys.argv[1])
    print(crew.kickoff())
