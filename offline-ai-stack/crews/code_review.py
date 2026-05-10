"""Four parallel review agents — replacement for /code-review."""
import subprocess
import sys
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI

# skills/loader.py lives in a sibling directory — make it importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from skills import with_defaults  # noqa: E402

llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",
    api_key="local",
    model="mistralai/Devstral-Small-2-24B-Instruct-2512",
    temperature=0.0,
)


class GitTool:
    name = "git"
    description = "Run a git read-only command and return the output."

    def run(self, cmd: str) -> str:
        # Whitelist read-only commands
        allowed = ("log", "blame", "diff", "show", "status", "rev-parse")
        parts = cmd.split()
        if not parts or parts[0] not in allowed:
            return f"Refused: {cmd}"
        return subprocess.check_output(["git"] + parts, text=True)[:4000]


file_tool = FileReadTool()
git_tool = GitTool()

# ---- Four reviewers, run in parallel ----

claude_md_compliance = with_defaults(
    Agent(
        role="Project Conventions Compliance Checker",
        goal="Verify the diff follows CONVENTIONS.md / CLAUDE.md / project rules.",
        backstory=(
            "Reads the project's rule files first, then audits the diff for violations. "
            "Reports each violation as (rule, file:line, evidence)."
        ),
        llm=llm, tools=[file_tool], allow_delegation=False,
    ),
    "pr-review",
)

redundancy_checker = with_defaults(
    Agent(
        role="Redundancy Detector",
        goal="Find duplicated logic, redundant rules, and dead code in the diff.",
        backstory=(
            "Loves DRY but understands when it harms clarity. "
            "Reports duplications with concrete refactor suggestions."
        ),
        llm=llm, tools=[file_tool], allow_delegation=False,
    ),
    "refactoring",
)

bug_detector = with_defaults(
    Agent(
        role="Bug Detector",
        goal="Find logic bugs, off-by-ones, race conditions, and unhandled errors.",
        backstory="Adversarial reader. Treats every branch as guilty until proven correct.",
        llm=llm, tools=[file_tool], allow_delegation=False,
    ),
    # systematic-debugging is in the reasoning baseline; layer root-cause on top.
    "root-cause-tracing",
)

git_history_reviewer = with_defaults(
    Agent(
        role="Git History Context Reviewer",
        goal="Use git log/blame to find why touched code was last changed and surface relevant prior context.",
        backstory=(
            "Always asks 'why was this written this way?' before suggesting changes. "
            "Uses git blame and log to recover institutional memory."
        ),
        llm=llm, tools=[file_tool, git_tool], allow_delegation=False,
    ),
    "code-search",
)


def build(diff_path: str):
    diff = Path(diff_path).read_text()
    common = f"\n\nDiff under review:\n```diff\n{diff[:8000]}\n```"
    tasks = [
        Task(
            agent=claude_md_compliance,
            description="Audit the diff against project conventions." + common,
            expected_output="A list of violations (rule, file:line, evidence) or 'no violations'.",
        ),
        Task(
            agent=redundancy_checker,
            description="Find redundancy and dead code in the diff." + common,
            expected_output="A redundancy list with refactor suggestions.",
        ),
        Task(
            agent=bug_detector,
            description="Find bugs in the diff." + common,
            expected_output="A bug list (severity, file:line, scenario, fix).",
        ),
        Task(
            agent=git_history_reviewer,
            description="Use git log/blame on the touched files; surface relevant historical context." + common,
            expected_output="Per-file historical context that affects the review.",
        ),
    ]
    return Crew(
        agents=[claude_md_compliance, redundancy_checker, bug_detector, git_history_reviewer],
        tasks=tasks,
        process=Process.parallel,  # all four run concurrently
        verbose=True,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: code_review.py <change.diff>", file=sys.stderr)
        sys.exit(2)
    crew = build(sys.argv[1])
    print(crew.kickoff())
