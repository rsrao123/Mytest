"""Deterministic merge-gate state machine.

CrewAI agents talk to each other; LangGraph enforces order. Use this as the
merge-gate state machine wired into Woodpecker so every PR runs through it
before merge.
"""
import operator
import sys
from pathlib import Path
from typing import Annotated, List, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph


class State(TypedDict):
    diff: str
    findings: Annotated[List[str], operator.add]
    blockers: Annotated[List[str], operator.add]
    decision: str


llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",
    api_key="local",
    model="mistralai/Devstral-Small-2-24B-Instruct-2512",
    temperature=0.0,
)


def review(prompt: str):
    def _node(s: State) -> State:
        out = llm.invoke(f"{prompt}\n\nDiff:\n{s['diff']}").content
        finding = f"[{prompt[:30]}] {out}"
        block = "BLOCKER" in out.upper()
        return {"findings": [finding], "blockers": ["x"] if block else []}
    return _node


def decide(s: State) -> State:
    return {"decision": "block" if s["blockers"] else "approve"}


g = StateGraph(State)
g.add_node("security", review("Find security issues. Mark fatal ones with the word BLOCKER."))
g.add_node("perf",     review("Find performance regressions. Mark fatal ones with the word BLOCKER."))
g.add_node("bugs",     review("Find bugs and edge cases. Mark fatal ones with the word BLOCKER."))
g.add_node("decide",   decide)

g.set_entry_point("security")
g.add_edge("security", "perf")
g.add_edge("perf", "bugs")
g.add_edge("bugs", "decide")
g.add_edge("decide", END)

graph = g.compile()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: merge_gate.py <change.diff>", file=sys.stderr)
        sys.exit(2)
    diff_text = Path(sys.argv[1]).read_text()
    result = graph.invoke({"diff": diff_text, "findings": [], "blockers": []})
    print("=== Findings ===")
    for f in result["findings"]:
        print(f)
    print(f"\n=== Decision: {result['decision']} ===")
    sys.exit(0 if result["decision"] == "approve" else 1)
