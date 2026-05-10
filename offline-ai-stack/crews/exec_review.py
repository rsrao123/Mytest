"""CEO / Eng / Design / QA / Release review agents — replacement for /plan-*-review and /ship."""
import argparse
import sys
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from skills import with_defaults  # noqa: E402

reasoner = ChatOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="local",
    model="Qwen/Qwen3-Coder-Next",
    temperature=0.4,
)

ceo = with_defaults(
    Agent(
        role="CEO",
        goal=(
            "Make a decisive go/no-go on features based on market fit, pricing, and competitive position. "
            "Be ruthless about scope."
        ),
        backstory=(
            "Has launched and shut down multiple products. Reads the room. Hates feature bloat. "
            "Will ship at 80% if 80% is the right call."
        ),
        llm=reasoner, allow_delegation=False,
    ),
    "writing-plans", "yagni",
)

eng_lead = with_defaults(
    Agent(
        role="Engineering Lead",
        goal="Assess feasibility, complexity, time-to-ship, and tech-debt impact.",
        backstory=(
            "Estimates in days, not points. Calls out hidden coupling. "
            "Knows when to say 'rewrite' vs 'patch'."
        ),
        llm=reasoner, allow_delegation=False,
    ),
    "writing-plans", "architecture-decision-record", "yagni",
)

design_lead = with_defaults(
    Agent(
        role="Design Lead",
        goal="Assess UX coherence, user-flow completeness, and design-system consistency.",
        backstory="Cares about empty states, error states, and the third user the team forgot about.",
        llm=reasoner, allow_delegation=False,
    ),
    "frontend-design",
)

qa_lead = with_defaults(
    Agent(
        role="QA Lead",
        goal="Identify high-risk regressions, untested branches, and rollback feasibility.",
        backstory="Has seen which 'small changes' took prod down. Asks for a kill-switch on every launch.",
        llm=reasoner, allow_delegation=False,
    ),
    "writing-tests", "avoiding-flaky-tests", "incident-response",
)

release_mgr = with_defaults(
    Agent(
        role="Release Manager",
        goal="Plan rollout phases, comms, monitoring, and rollback. Produce a go/no-go.",
        backstory="Friday-deploy survivor. Won't ship without monitors and a documented rollback.",
        llm=reasoner, allow_delegation=False,
    ),
    "incident-response", "handling-failures-and-retries", "explaining-changes",
)

ROLES = {
    "ceo": (
        ceo,
        "Review this plan as CEO. Decide go/no-go. Cover: market fit, pricing, "
        "competitive moat, scope discipline, ship-now vs wait.",
    ),
    "eng": (
        eng_lead,
        "Review this plan as Engineering Lead. Cover: feasibility, complexity, "
        "time-to-ship, tech-debt, hidden risks.",
    ),
    "design": (
        design_lead,
        "Review this plan as Design Lead. Cover: UX coherence, flow gaps, "
        "empty/error states, accessibility, design-system consistency.",
    ),
    "qa": (
        qa_lead,
        "Review this plan as QA Lead. Cover: high-risk regressions, untested branches, "
        "rollout risk, rollback feasibility.",
    ),
    "release": (
        release_mgr,
        "Plan the rollout. Cover: phases, comms, monitors, rollback, go/no-go.",
    ),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=list(ROLES) + ["all"])
    ap.add_argument("--plan", required=True)
    args = ap.parse_args()
    plan_text = Path(args.plan).read_text()

    if args.role == "all":
        tasks, agents = [], []
        for _name, (agent, prompt) in ROLES.items():
            tasks.append(Task(
                agent=agent,
                description=f"{prompt}\n\nPlan:\n{plan_text}",
                expected_output="A structured review with explicit decision.",
            ))
            agents.append(agent)
        crew = Crew(agents=agents, tasks=tasks, process=Process.parallel, verbose=True)
    else:
        agent, prompt = ROLES[args.role]
        task = Task(
            agent=agent,
            description=f"{prompt}\n\nPlan:\n{plan_text}",
            expected_output="A structured review with explicit decision.",
        )
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)

    print(crew.kickoff())


if __name__ == "__main__":
    main()
