"""LLM-driven browser research via browser-use, pointed at the local vLLM.

Usage:
    python browser_research.py "Compare vLLM and TGI for FP8 inference."
"""
import asyncio
import sys

from browser_use import Agent
from langchain_openai import ChatOpenAI


async def run(task: str) -> str:
    llm = ChatOpenAI(
        base_url="http://localhost:8000/v1",
        api_key="local",
        model="Qwen/Qwen3-Coder-Next",
        temperature=0.2,
    )
    agent = Agent(task=task, llm=llm)
    result = await agent.run()
    return str(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: browser_research.py <task>", file=sys.stderr)
        sys.exit(2)
    print(asyncio.run(run(" ".join(sys.argv[1:]))))
