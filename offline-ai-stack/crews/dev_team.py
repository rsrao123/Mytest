"""Role-based dev crew that runs a full plan → design → implement → review → ship pipeline.

Usage:
    PROJECT_DIR=~/offline-ai-stack/projects/myapp \
        python ~/offline-ai-stack/crews/dev_team.py "Add SSO via OIDC to the admin panel."
"""
import os
import sys
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai_tools import DirectoryReadTool, FileReadTool
from langchain_openai import ChatOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from skills import with_defaults  # noqa: E402

# Two endpoints, different temperatures per role
primary = ChatOpenAI(
    model="Qwen/Qwen3-Coder-Next",
    base_url="http://localhost:8000/v1",
    api_key="local",
    temperature=0.2,
)
specialist = ChatOpenAI(
    model="mistralai/Devstral-Small-2-24B-Instruct-2512",
    base_url="http://localhost:8001/v1",
    api_key="local",
    temperature=0.1,
)
reasoner = ChatOpenAI(
    model="Qwen/Qwen3-Coder-Next",
    base_url="http://localhost:8000/v1",
    api_key="local",
    temperature=0.4,  # higher for ideation
)

PROJECT = os.environ["PROJECT_DIR"]
file_tool = FileReadTool()
dir_tool = DirectoryReadTool(directory=PROJECT)

# --- Roles -----------------------------------------------------------

product_planner = with_defaults(
    Agent(
        role="Product Planner",
        goal="Convert vague user requests into precise, testable specs.",
        backstory="Senior PM who refuses to let work start without acceptance criteria.",
        llm=reasoner,
        tools=[dir_tool],
        allow_delegation=False,
        verbose=True,
    ),
    "brainstorming", "writing-plans",
)

architect = with_defaults(
    Agent(
        role="System Architect",
        goal="Design modular, maintainable architecture; flag risk early.",
        backstory="Has rebuilt three legacy monoliths and learned to prefer boring choices.",
        llm=reasoner,
        tools=[dir_tool, file_tool],
        allow_delegation=True,
    ),
    "writing-plans", "architecture-decision-record", "subagent-driven-development",
)

backend_dev = with_defaults(
    Agent(
        role="Backend Developer",
        goal="Implement backend changes with tests, idiomatic to the existing codebase.",
        backstory="Reads the surrounding code before writing new code.",
        llm=primary,
        tools=[dir_tool, file_tool],
        allow_delegation=False,
    ),
    "test-driven-development", "yagni", "commit-discipline",
)

frontend_dev = with_defaults(
    Agent(
        role="Frontend Developer",
        goal="Ship accessible, fast UI using the project's existing component system.",
        backstory="Hates re-inventing components; reaches for shadcn/Tailwind first.",
        llm=primary,
        tools=[dir_tool, file_tool],
        allow_delegation=False,
    ),
    "frontend-design", "yagni", "commit-discipline",
)

bug_hunter = with_defaults(
    Agent(
        role="Bug Hunter",
        goal="Find regressions, edge cases, and silent failures in proposed diffs.",
        backstory="Obsessed with off-by-one errors and unhandled error paths.",
        llm=specialist,
        tools=[file_tool],
        allow_delegation=False,
    ),
    # systematic-debugging is in the reasoning baseline.
    "root-cause-tracing", "code-search", "pr-review",
)

security_reviewer = with_defaults(
    Agent(
        role="Security Reviewer",
        goal="Find injections, auth holes, secrets, unsafe deserialization, OWASP top-10.",
        backstory="Treats every input as hostile until proven otherwise.",
        llm=specialist,
        tools=[file_tool],
        allow_delegation=False,
    ),
    "security-review", "pr-review", "defensive-programming-discipline",
)

perf_reviewer = with_defaults(
    Agent(
        role="Performance Reviewer",
        goal="Spot N+1 queries, hot-path allocations, and unnecessary network round-trips.",
        backstory="Has a profiler open at all times.",
        llm=specialist,
        tools=[file_tool],
        allow_delegation=False,
    ),
    # systematic-debugging is in the reasoning baseline.
    "pr-review", "code-search", "root-cause-tracing",
)

qa_engineer = with_defaults(
    Agent(
        role="QA Engineer",
        goal="Write unit + integration tests; identify untested branches.",
        backstory="Coverage report is their love language.",
        llm=primary,
        tools=[dir_tool, file_tool],
        allow_delegation=False,
    ),
    "writing-tests", "avoiding-mocks", "avoiding-flaky-tests",
)

release_manager = with_defaults(
    Agent(
        role="Release Manager",
        goal="Produce changelog, migration notes, deploy plan; gate the merge.",
        backstory="Has rolled back enough Friday deploys to be cautious.",
        llm=reasoner,
        tools=[file_tool],
        allow_delegation=False,
    ),
    "writing-plans", "incident-response", "explaining-changes",
)

doc_writer = with_defaults(
    Agent(
        role="Documentation Writer",
        goal="Update README/docs/ADRs to match the actual change.",
        backstory="Believes undocumented code is a half-finished change.",
        llm=primary,
        tools=[dir_tool, file_tool],
        allow_delegation=False,
    ),
    # reading-code is in the reasoning baseline.
    "explaining-changes", "architecture-decision-record", "writing-plans",
)


def build_crew(ticket: str) -> Crew:
    plan = Task(
        description=f"Turn this request into a spec with acceptance criteria:\n\n{ticket}",
        expected_output="A markdown spec: goals, constraints, acceptance tests, out-of-scope.",
        agent=product_planner,
    )
    design = Task(
        description="Propose architecture for the spec; list modules touched, new interfaces, migration risks.",
        expected_output="An architecture note + risk list.",
        agent=architect,
        context=[plan],
    )
    implement_be = Task(
        description="Implement backend changes per the architecture.",
        expected_output="A unified diff plus brief rationale.",
        agent=backend_dev,
        context=[plan, design],
    )
    implement_fe = Task(
        description="Implement frontend changes if applicable; otherwise return 'no UI changes'.",
        expected_output="A unified diff or 'no UI changes'.",
        agent=frontend_dev,
        context=[plan, design],
    )
    review_bugs = Task(
        description="Review the diffs above for bugs, edge cases, silent failures.",
        expected_output="A list of issues by severity, with file:line refs.",
        agent=bug_hunter,
        context=[implement_be, implement_fe],
    )
    review_sec = Task(
        description="Review the diffs for security issues (OWASP, secrets, injection, auth).",
        expected_output="A security finding list with severity and remediation.",
        agent=security_reviewer,
        context=[implement_be, implement_fe],
    )
    review_perf = Task(
        description="Review the diffs for performance regressions.",
        expected_output="A perf-issue list with measured/estimated impact.",
        agent=perf_reviewer,
        context=[implement_be, implement_fe],
    )
    test = Task(
        description="Write unit + integration tests covering the new code paths and one failure mode each.",
        expected_output="A test diff and a coverage rationale.",
        agent=qa_engineer,
        context=[implement_be, implement_fe, review_bugs],
    )
    docs = Task(
        description="Update docs and ADR for this change.",
        expected_output="A docs diff.",
        agent=doc_writer,
        context=[plan, design, implement_be, implement_fe],
    )
    release = Task(
        description="Produce changelog, migration notes, and a go/no-go on the merge.",
        expected_output="Changelog + migration + decision.",
        agent=release_manager,
        context=[plan, implement_be, implement_fe, review_bugs, review_sec, review_perf, test, docs],
    )

    return Crew(
        agents=[
            product_planner, architect, backend_dev, frontend_dev,
            bug_hunter, security_reviewer, perf_reviewer,
            qa_engineer, doc_writer, release_manager,
        ],
        tasks=[
            plan, design, implement_be, implement_fe,
            review_bugs, review_sec, review_perf, test, docs, release,
        ],
        process=Process.sequential,  # switch to hierarchical for manager-led
        memory=True,                  # uses ChromaDB if configured
        verbose=True,
    )


if __name__ == "__main__":
    ticket = sys.argv[1] if len(sys.argv) > 1 else "Add rate limiting to /api/login."
    crew = build_crew(ticket)
    print(crew.kickoff())
