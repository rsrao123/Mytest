"""
Local Claude-MEM equivalent.
- Records tool calls & observations during a session
- AI-compresses sessions into summaries at end
- Extracts atomic observations as separately-retrievable memory units
- Auto-injects relevant past context on demand
- Backend: ChromaDB (local), no cloud
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime

import chromadb
from langchain_openai import ChatOpenAI

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8002"))
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

SESSIONS = client.get_or_create_collection("mem_sessions")
OBSERVATIONS = client.get_or_create_collection("mem_observations")

LLM = ChatOpenAI(
    base_url="http://localhost:8000/v1", api_key="local",
    model="Qwen/Qwen3-Coder-Next", temperature=0.0,
)


class SessionRecorder:
    def __init__(self, project: str):
        self.project = project
        self.session_id = f"{project}-{datetime.now().isoformat(timespec='seconds')}"
        self.calls = []
        self.notes = []

    def tool_call(self, tool: str, args: dict, result: str):
        self.calls.append({
            "ts": time.time(), "tool": tool,
            "args": str(args)[:1000], "result": str(result)[:2000],
        })

    def note(self, text: str):
        self.notes.append(text)

    def end(self):
        if not (self.calls or self.notes):
            return
        payload = json.dumps({"calls": self.calls, "notes": self.notes}, indent=2, default=str)
        summary = LLM.invoke(
            "Summarize this coding session in 5–10 bullets capturing: "
            "decisions made, patterns discovered, conventions confirmed, "
            "things worth remembering next time. Be concrete.\n\n" + payload[:8000]
        ).content
        SESSIONS.add(
            documents=[summary],
            ids=[self.session_id],
            metadatas=[{"project": self.project, "ts": self.session_id, "n_calls": len(self.calls)}],
        )
        atoms_raw = LLM.invoke(
            "Extract atomic, single-fact observations from this summary "
            "as a JSON array of strings. Each must stand alone and be useful "
            "in a future session. Return ONLY the JSON array.\n\n" + summary
        ).content
        try:
            start = atoms_raw.find("[")
            end = atoms_raw.rfind("]") + 1
            atoms = json.loads(atoms_raw[start:end])
            for atom in atoms:
                aid = hashlib.sha256(f"{self.project}:{atom}".encode()).hexdigest()[:24]
                OBSERVATIONS.upsert(
                    documents=[atom], ids=[aid],
                    metadatas=[{"project": self.project, "session": self.session_id}],
                )
        except Exception as e:
            print(f"Atom extraction failed: {e}", file=sys.stderr)
        return summary


def get_context(project: str, query: str, k: int = 8) -> str:
    """Call this at the start of any new session/agent run."""
    obs = OBSERVATIONS.query(query_texts=[query], n_results=k, where={"project": project})
    sess = SESSIONS.query(query_texts=[query], n_results=3, where={"project": project})
    lines = ["## Recalled context from previous sessions"]
    for doc in (obs.get("documents") or [[]])[0]:
        lines.append(f"- {doc}")
    if (sess.get("documents") or [[]])[0]:
        lines.append("\n## Recent relevant session summaries")
        for s in sess["documents"][0]:
            lines.append(s)
    return "\n".join(lines)


# CLI: python claude_mem_local.py recall <project> <query>
if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "recall":
        print(get_context(sys.argv[2], " ".join(sys.argv[3:])))
    else:
        print("Usage: claude_mem_local.py recall <project> <query>")
