# Offline AI Engineering Stack — Complete Build

A fully-offline, open-source replacement for Claude Code + Claude MEM + a multi-agent dev team. Targets a single-workstation deployment.

## Strict-offline guarantee

After a one-time prep with internet (model downloads, scanner DB caches, image
pulls), the stack runs **with the network unplugged**. The guarantee covers:

- All inference (vLLM + Qwen3-Coder-Next + Devstral) — local
- All embeddings (Chroma's local sentence-transformers default) — local
- All security scans (bandit / semgrep / gitleaks / pip-audit / trivy) — local rules + cached DBs
- All agent frameworks (CrewAI, LangGraph) — only call localhost vLLM
- All storage (Chroma, Forgejo, Woodpecker, Langfuse, Open WebUI) — self-hosted
- Memory layer (`scripts/claude_mem_local.py`) — Chroma + local LLM
- Telemetry — disabled everywhere via system-wide env vars (see below)

### What's removed
- **SearXNG** — metasearch proxy that queries Google / Bing / DDG
- **browser-use / Playwright** — drives a real browser at real URLs
- **`safety`** scanner — offline DB is commercial; `pip-audit` covers same ground via OSV

### Telemetry opt-outs (system-wide)
Written to `/etc/environment` by `make offline-prep`:

| Tool | Variable(s) |
|---|---|
| ChromaDB → PostHog | `ANONYMIZED_TELEMETRY=false` |
| HuggingFace Hub | `HF_HUB_DISABLE_TELEMETRY=1`, `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` |
| CrewAI | `CREWAI_TELEMETRY_OPT_OUT=true`, `CREWAI_DISABLE_TELEMETRY=true`, `OTEL_SDK_DISABLED=true` |
| LangChain / LangSmith | `LANGCHAIN_TRACING_V2=false`, `LANGSMITH_TRACING=false`, `LANGSMITH_API_KEY=` |
| Aider | `AIDER_ANALYTICS=false`, `AIDER_ANALYTICS_DISABLE=1` |
| promptfoo | `PROMPTFOO_DISABLE_TELEMETRY=1` |
| vLLM | `VLLM_NO_USAGE_STATS=1`, `VLLM_DO_NOT_TRACK=1` |
| Universal | `DO_NOT_TRACK=1`, `TELEMETRY_DISABLED=1`, `SCARF_NO_ANALYTICS=true` |
| Provider kill-switches | `OPENAI_API_KEY=local`, `OPENAI_API_BASE=http://localhost:8000/v1`, `ANTHROPIC_API_KEY=` |

### Per-service opt-outs (in `docker-compose.yml`)

| Service | Variable(s) |
|---|---|
| chroma | `ANONYMIZED_TELEMETRY=false`, `ALLOW_RESET=false` |
| open-webui | `SCARF_NO_ANALYTICS=true`, `DO_NOT_TRACK=1`, `ANONYMIZED_TELEMETRY=false` |
| forgejo | `FORGEJO__server__OFFLINE_MODE=true` |
| grafana | `GF_ANALYTICS_REPORTING_ENABLED=false`, `GF_ANALYTICS_CHECK_FOR_UPDATES=false`, `GF_ANALYTICS_CHECK_FOR_PLUGIN_UPDATES=false`, `GF_ANALYTICS_FEEDBACK_LINKS_ENABLED=false` |

Every service in `docker-compose.yml` also has `pull_policy: never`, so
`docker compose up` never reaches dockerhub / ghcr / etc.

### vLLM systemd units
`configs/vllm-primary.service` and `configs/vllm-devstral.service` set:
- `HF_HUB_OFFLINE=1` (no model-metadata checks)
- `TRANSFORMERS_OFFLINE=1`
- `HF_HUB_DISABLE_TELEMETRY=1`
- `VLLM_NO_USAGE_STATS=1`, `VLLM_DO_NOT_TRACK=1`

These are NOT in `/etc/environment` because they'd break a future
`huggingface-cli download`. They live on the systemd unit so vLLM never
phones home at boot.

### HuggingFace lockdown

Models are stored as plain local directories under
`~/offline-ai-stack/models/<name>/`, not in the HF cache. vLLM serves the
local path with `--served-model-name <repo-id>` so client code can still
reference the familiar repo-ID alias without any HF Hub lookup happening.
Embedding code (`scripts/ingest.py`) loads from a local path. No runtime
Python file imports `huggingface_hub`.

The `transformers` library is still a hard dependency of vLLM (used
internally for tokenizer + model loading). When given a local path with
`HF_HUB_OFFLINE=1` set, it never reaches for the Hub. To remove
`transformers` entirely you would have to swap vLLM for llama.cpp / GGUF
or an equivalent non-HF engine.

`scripts/hf-audit.sh` (also `make hf-audit`) verifies:
- every model directory listed in `offline-prep.sh` exists locally with a `config.json`
- no runtime Python code references HF repo IDs *except* as vLLM service-name aliases
- no runtime Python file imports `huggingface_hub`

### Two-machine air-gapped flow (target never sees the internet)

The target machine has **no internet at all** — files arrive via removable
media. We use a staging machine (any Linux workstation with internet) to
build a portable bundle, then import it on the target.

```
┌─────────────────────────┐                   ┌─────────────────────────┐
│ STAGING (has internet)  │                   │ TARGET (air-gapped)     │
│                         │                   │                         │
│ sudo apt install ...    │                   │ sudo apt install ...    │
│ pip install -r req.txt  │                   │ (from local apt mirror, │
│ make offline-prep       │                   │  or pre-installed)      │
│ make stage-bundle       │  USB / DVD /      │                         │
│   ↓                     │  removable drive  │ make import-bundle      │
│ offline-ai-stack-       │ ─────────────────►│   BUNDLE=/mnt/usb/...   │
│ bundle-YYYYMMDD/        │                   │   ↓                     │
│ (~110 GB)               │                   │ sudo make os-harden     │
│                         │                   │ sudo reboot             │
│                         │                   │ make bring-up           │
│                         │                   │ sudo make airgap-test   │
└─────────────────────────┘                   └─────────────────────────┘
```

#### On STAGING (one-time, with internet)

```bash
sudo apt install -y curl wget git python3.11 python3.11-venv \
                    docker.io docker-compose-v2 iptables \
                    bandit semgrep gitleaks rsync
python3.11 -m venv ~/ai-stack && source ~/ai-stack/bin/activate
pip install -r offline-ai-stack/requirements.txt

# Authenticate for gated models (Devstral, Llama, etc.)
huggingface-cli login

# Downloads models + scanner DBs + docker images, sets telemetry-off
make offline-prep

# Bundles everything for transfer (~110 GB without large coding models,
# ~200 GB with them all). Output is a DIRECTORY at $HOME/offline-ai-stack-
# bundle-YYYYMMDD/. Tar it yourself if you want a single file for transport.
make stage-bundle
```

What `stage-bundle` packages:
- `models/`         — every model directory, plain local-dir layout
- `cache/`          — trivy CVE DB, OSV mirror, semgrep rules
- `docker-images/`  — every required image as a `.tar` (`docker save`)
- `wheels/`         — every Python dep from `requirements.txt`, built for `manylinux2014_x86_64` + Python 3.11
- `offline-ai-stack/` — the repo itself (without runtime data dirs)
- `MANIFEST.txt`    — sizes + sha256 of image tarballs

#### Transfer the bundle to the target

`rsync`, `cp -r`, `tar -cf bundle.tar` + USB, data diode — whatever fits
your air-gap rules.

#### On the air-gapped TARGET

```bash
# Prerequisites that must exist already (from your air-gapped OS image or
# a local apt mirror): docker, python3.11, iptables, rsync.
# The bundle does NOT carry apt packages.

# Import the bundle. No internet needed at any step.
make import-bundle BUNDLE=/mnt/usb/offline-ai-stack-bundle-YYYYMMDD

# OS-level lockdown (masks Ubuntu's NTP / snap / unattended-upgrades /
# whoopsie / apport / popularity-contest / canonical-livepatch / cloud-init)
sudo make os-harden
sudo reboot

# After reboot, activate the venv that import-bundle created (or your own)
source ~/ai-stack/bin/activate
make bring-up

# Four-tier verification, weakest first:
make hf-audit                   # STRUCTURAL: every model present, no repo-ID surprises in code
make offline-doctor             # OBSERVED:   passive 30s probe; reports non-loopback ESTAB sockets
sudo make offline-doctor-strict # ADVERSARIAL: 30s with iptables blocking egress
sudo make airgap-test           # HARDEST:    full 90s smoke under kernel-level OUTPUT drop
```

If `airgap-test` returns PASS, the box is provably surviving without network.

#### Refreshing the bundle (~90 days)

CVE / OSV data ages. To refresh: re-run `make offline-prep && make stage-bundle`
on staging, transfer the new bundle, `make import-bundle BUNDLE=...` on
target. Existing models / docker images that haven't changed are skipped
via `rsync` delta transfer.

### What each verification catches

| Check | Scope | Catches |
|---|---|---|
| `hf-audit` | Static repo scan + filesystem | Code paths that could leak to HF Hub; missing model files |
| `offline-doctor` (passive) | Live `ss -tunap` sampling | Anything actively connecting to non-loopback during the window |
| `offline-doctor-strict` | iptables OUTPUT drop, 30s | Anything that *tries* to connect — fails loudly under the rule |
| `airgap-test` | iptables OUTPUT drop + full smoke, 90s | End-to-end: every probe (pytest, scanners, claude_mem, vLLM, Chroma, crews) must complete |
| `os-harden-offline.sh` | systemd unit masking | OS-level services (NTP, snap, apt-daily, whoopsie, apport, canonical-livepatch) that phone home outside the stack |

`airgap-test` is the only one that proves the *full system* survives a real network outage. If it passes, you can physically disconnect.

### Irreducible dependencies

After everything above, these remain:
1. **One-time setup with internet** — model downloads, image pulls, apt/pip installs.
2. **The `transformers` Python library** (a `vllm` dep). Stays importable, never reaches HF Hub at runtime. Removing it requires swapping vLLM for llama.cpp/GGUF or equivalent.
3. **The host OS itself** — kernel, glibc, NVIDIA driver. Updates need internet by definition; `os-harden-offline.sh` disables the automatic timers but doesn't replace the underlying packages.

Everything else is offline.

### The remaining online dependency

The first-time model pull (~400 GB from HuggingFace) plus `apt`/`pip`/`docker
pull` for the base system. Re-run `make offline-prep` every ~90 days to
refresh CVE / OSV data.

## 0. Target machine

| Item | Spec |
|---|---|
| OS | Ubuntu 24.04 LTS |
| GPU | NVIDIA RTX Pro 6000 Blackwell, 96 GB VRAM (sm_120) |
| Driver | NVIDIA ≥ 570 |
| CUDA | 12.8+ |
| Python | 3.11 |
| Node | 20 LTS |
| Docker | 27+ with Compose v2 |
| RAM | 64 GB+ recommended |
| Disk | 2 TB NVMe (models alone need ~400 GB) |

---

## 1. Base system

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  git curl wget build-essential cmake pkg-config \
  python3.11 python3.11-venv python3-pip \
  nodejs npm docker.io docker-compose-v2 \
  ripgrep fd-find jq htop nvtop unzip restic caddy

sudo usermod -aG docker $USER
newgrp docker
```

Install NVIDIA Container Toolkit so containers can see the GPU:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify Blackwell:

```bash
nvidia-smi
python3.11 -c "import torch; print(torch.cuda.get_device_capability())"
# Expect (12, 0)
```

---

## 2. Folder layout

```bash
mkdir -p ~/offline-ai-stack/{projects,memory,reports,configs,scripts,logs,backups,crews}
export HF_HOME=~/offline-ai-stack/hf-cache
echo 'export HF_HOME=~/offline-ai-stack/hf-cache' >> ~/.bashrc
```

```
~/offline-ai-stack
├── projects     # codebases agents work on
├── memory       # ChromaDB volumes
├── reports      # security/eval outputs
├── configs      # systemd unit copies, Caddyfile, etc.
├── scripts      # bring-up/teardown
├── logs         # vLLM, agents
├── backups      # restic snapshots
├── crews        # CrewAI/LangGraph definitions
└── hf-cache     # HF model cache (HF_HOME)
```

---

## 3. Inference layer (vLLM, dual-model)

Python venv:

```bash
python3.11 -m venv ~/ai-stack
source ~/ai-stack/bin/activate
pip install -U pip
pip install -U vllm "mistral_common>=1.8.6"
```

Authenticate with HuggingFace (Llama is gated):

```bash
huggingface-cli login
```

### Primary coding model — Qwen3-Coder-Next (80B / 3B-active MoE)

```bash
vllm serve Qwen/Qwen3-Coder-Next \
  --host 0.0.0.0 --port 8000 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.55 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

### Specialist — Devstral Small 2 (24B, FP8, agentic SWE)

```bash
vllm serve mistralai/Devstral-Small-2-24B-Instruct-2512 \
  --host 0.0.0.0 --port 8001 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.28 \
  --enable-auto-tool-choice \
  --tool-call-parser mistral
```

Devstral **requires** `--tool-call-parser mistral` and `mistral_common >= 1.8.6` or tool calls fail silently.

### Embeddings + reranker (CPU/GPU lightweight, run alongside)

Use `text-embeddings-inference` (TEI) or just call sentence-transformers from LlamaIndex. Models:

- `Qwen/Qwen3-Embedding-8B` — vectors
- `BAAI/bge-reranker-v2-m3` — top-k re-scoring

VRAM budget on 96 GB:

| Component | VRAM |
|---|---|
| Qwen3-Coder-Next (BF16) | ~50 GB |
| Devstral Small 2 (FP8) | ~25 GB |
| Embedding + reranker | ~8 GB |
| KV cache headroom | ~13 GB |

---

## 4. Coding agents (clients of vLLM)

### Aider

```bash
pip install aider-chat
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=local
aider --model openai/Qwen/Qwen3-Coder-Next --architect
```

### Qwen Code (Alibaba's Claude-Code-style CLI)

```bash
npm install -g @qwen-code/qwen-code
cd ~/offline-ai-stack/projects/your-project
qwen   # prompts for endpoint on first run
```

Endpoint: `http://localhost:8000/v1`, key: `local`, model: `Qwen/Qwen3-Coder-Next`.

### OpenHands (autonomous, sandboxed)

```bash
docker run -d --pull=always \
  --name openhands \
  -e LLM_BASE_URL=http://host.docker.internal:8000/v1 \
  -e LLM_API_KEY=local \
  -e LLM_MODEL=openai/Qwen/Qwen3-Coder-Next \
  --add-host=host.docker.internal:host-gateway \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 127.0.0.1:3000:3000 \
  docker.all-hands.dev/all-hands-ai/openhands:latest
```

Bind to `127.0.0.1` only — the docker-socket mount makes this container effectively root on host.

---

## 5. Superpowers — multi-agent orchestration

This is what turns the stack from "an LLM with tools" into "a team."

```bash
pip install crewai crewai-tools langgraph langchain langchain-openai \
  langchain-community chromadb llama-index \
  llama-index-vector-stores-chroma \
  llama-index-embeddings-huggingface
```

### 5.1 CrewAI — role-based crew

`~/offline-ai-stack/crews/dev_team.py`:

```python
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, DirectoryReadTool, CodeDocsSearchTool
from langchain_openai import ChatOpenAI

# Two endpoints, different temperatures per role
primary = ChatOpenAI(
    model="Qwen/Qwen3-Coder-Next",
    base_url="http://localhost:8000/v1",
    api_key="local", temperature=0.2,
)
specialist = ChatOpenAI(
    model="mistralai/Devstral-Small-2-24B-Instruct-2512",
    base_url="http://localhost:8001/v1",
    api_key="local", temperature=0.1,
)
reasoner = ChatOpenAI(
    model="Qwen/Qwen3-Coder-Next",
    base_url="http://localhost:8000/v1",
    api_key="local", temperature=0.4,  # higher for ideation
)

PROJECT = os.environ["PROJECT_DIR"]
file_tool = FileReadTool()
dir_tool = DirectoryReadTool(directory=PROJECT)

# --- Roles -----------------------------------------------------------

product_planner = Agent(
    role="Product Planner",
    goal="Convert vague user requests into precise, testable specs.",
    backstory="Senior PM who refuses to let work start without acceptance criteria.",
    llm=reasoner, tools=[dir_tool], allow_delegation=False, verbose=True,
)

architect = Agent(
    role="System Architect",
    goal="Design modular, maintainable architecture; flag risk early.",
    backstory="Has rebuilt three legacy monoliths and learned to prefer boring choices.",
    llm=reasoner, tools=[dir_tool, file_tool], allow_delegation=True,
)

backend_dev = Agent(
    role="Backend Developer",
    goal="Implement backend changes with tests, idiomatic to the existing codebase.",
    backstory="Reads the surrounding code before writing new code.",
    llm=primary, tools=[dir_tool, file_tool], allow_delegation=False,
)

frontend_dev = Agent(
    role="Frontend Developer",
    goal="Ship accessible, fast UI using the project's existing component system.",
    backstory="Hates re-inventing components; reaches for shadcn/Tailwind first.",
    llm=primary, tools=[dir_tool, file_tool], allow_delegation=False,
)

bug_hunter = Agent(
    role="Bug Hunter",
    goal="Find regressions, edge cases, and silent failures in proposed diffs.",
    backstory="Obsessed with off-by-one errors and unhandled error paths.",
    llm=specialist, tools=[file_tool], allow_delegation=False,
)

security_reviewer = Agent(
    role="Security Reviewer",
    goal="Find injections, auth holes, secrets, unsafe deserialization, OWASP top-10.",
    backstory="Treats every input as hostile until proven otherwise.",
    llm=specialist, tools=[file_tool], allow_delegation=False,
)

perf_reviewer = Agent(
    role="Performance Reviewer",
    goal="Spot N+1 queries, hot-path allocations, and unnecessary network round-trips.",
    backstory="Has a profiler open at all times.",
    llm=specialist, tools=[file_tool], allow_delegation=False,
)

qa_engineer = Agent(
    role="QA Engineer",
    goal="Write unit + integration tests; identify untested branches.",
    backstory="Coverage report is their love language.",
    llm=primary, tools=[dir_tool, file_tool], allow_delegation=False,
)

release_manager = Agent(
    role="Release Manager",
    goal="Produce changelog, migration notes, deploy plan; gate the merge.",
    backstory="Has rolled back enough Friday deploys to be cautious.",
    llm=reasoner, tools=[file_tool], allow_delegation=False,
)

doc_writer = Agent(
    role="Documentation Writer",
    goal="Update README/docs/ADRs to match the actual change.",
    backstory="Believes undocumented code is a half-finished change.",
    llm=primary, tools=[dir_tool, file_tool], allow_delegation=False,
)

# --- Tasks (a representative pipeline; customize per ticket) ---------

def build_crew(ticket: str) -> Crew:
    plan = Task(
        description=f"Turn this request into a spec with acceptance criteria:\n\n{ticket}",
        expected_output="A markdown spec: goals, constraints, acceptance tests, out-of-scope.",
        agent=product_planner,
    )
    design = Task(
        description="Propose architecture for the spec; list modules touched, new interfaces, migration risks.",
        expected_output="An architecture note + risk list.",
        agent=architect, context=[plan],
    )
    implement_be = Task(
        description="Implement backend changes per the architecture.",
        expected_output="A unified diff plus brief rationale.",
        agent=backend_dev, context=[plan, design],
    )
    implement_fe = Task(
        description="Implement frontend changes if applicable; otherwise return 'no UI changes'.",
        expected_output="A unified diff or 'no UI changes'.",
        agent=frontend_dev, context=[plan, design],
    )
    review_bugs = Task(
        description="Review the diffs above for bugs, edge cases, silent failures.",
        expected_output="A list of issues by severity, with file:line refs.",
        agent=bug_hunter, context=[implement_be, implement_fe],
    )
    review_sec = Task(
        description="Review the diffs for security issues (OWASP, secrets, injection, auth).",
        expected_output="A security finding list with severity and remediation.",
        agent=security_reviewer, context=[implement_be, implement_fe],
    )
    review_perf = Task(
        description="Review the diffs for performance regressions.",
        expected_output="A perf-issue list with measured/estimated impact.",
        agent=perf_reviewer, context=[implement_be, implement_fe],
    )
    test = Task(
        description="Write unit + integration tests covering the new code paths and one failure mode each.",
        expected_output="A test diff and a coverage rationale.",
        agent=qa_engineer, context=[implement_be, implement_fe, review_bugs],
    )
    docs = Task(
        description="Update docs and ADR for this change.",
        expected_output="A docs diff.",
        agent=doc_writer, context=[plan, design, implement_be, implement_fe],
    )
    release = Task(
        description="Produce changelog, migration notes, and a go/no-go on the merge.",
        expected_output="Changelog + migration + decision.",
        agent=release_manager,
        context=[plan, implement_be, implement_fe, review_bugs, review_sec, review_perf, test, docs],
    )

    return Crew(
        agents=[product_planner, architect, backend_dev, frontend_dev,
                bug_hunter, security_reviewer, perf_reviewer,
                qa_engineer, doc_writer, release_manager],
        tasks=[plan, design, implement_be, implement_fe,
               review_bugs, review_sec, review_perf, test, docs, release],
        process=Process.sequential,   # switch to hierarchical for manager-led
        memory=True,                  # uses ChromaDB if configured
        verbose=True,
    )

if __name__ == "__main__":
    import sys
    ticket = sys.argv[1] if len(sys.argv) > 1 else "Add rate limiting to /api/login."
    crew = build_crew(ticket)
    print(crew.kickoff())
```

Run:

```bash
PROJECT_DIR=~/offline-ai-stack/projects/myapp \
python ~/offline-ai-stack/crews/dev_team.py "Add SSO via OIDC to the admin panel."
```

### 5.2 LangGraph — deterministic CI workflow

CrewAI agents talk to each other; LangGraph enforces order. Use it as the merge-gate state machine.

`~/offline-ai-stack/crews/merge_gate.py`:

```python
from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

class State(TypedDict):
    diff: str
    findings: Annotated[List[str], operator.add]
    blockers: Annotated[List[str], operator.add]
    decision: str

llm = ChatOpenAI(base_url="http://localhost:8001/v1", api_key="local",
                 model="mistralai/Devstral-Small-2-24B-Instruct-2512", temperature=0.0)

def review(prompt: str):
    def _node(s: State) -> State:
        out = llm.invoke(f"{prompt}\n\nDiff:\n{s['diff']}").content
        finding = f"[{prompt[:30]}] {out}"
        block = ["BLOCKER" in out.upper()]
        return {"findings": [finding], "blockers": ["x"] if any(block) else []}
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
# graph.invoke({"diff": open("change.diff").read(), "findings": [], "blockers": []})
```

Wire this into Woodpecker (§13) so every PR runs through it before merge.

---

## 6. Memory + RAG (Claude MEM equivalent)

Run Chroma:

```bash
docker run -d --name chroma \
  -p 8002:8000 \
  -v ~/offline-ai-stack/memory:/chroma/chroma \
  chromadb/chroma:latest
```

Project memory ingestion (`scripts/ingest.py`):

```python
import sys, chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

client = chromadb.HttpClient(host="localhost", port=8002)
collection = client.get_or_create_collection("project-memory")
vstore = ChromaVectorStore(chroma_collection=collection)
storage = StorageContext.from_defaults(vector_store=vstore)
embed = HuggingFaceEmbedding(model_name="Qwen/Qwen3-Embedding-8B")

docs = SimpleDirectoryReader(sys.argv[1], recursive=True,
    required_exts=[".md", ".py", ".ts", ".tsx", ".rs", ".go", ".java"]).load_data()
VectorStoreIndex.from_documents(docs, storage_context=storage, embed_model=embed)
```

Stores: project decisions, ADRs, past bugs, security findings, test history, meeting notes. CrewAI agents (`memory=True` above) read and write here automatically.

---

## 7. Chat UI — Open WebUI

```bash
docker run -d -p 3001:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=local \
  -e ENABLE_RAG_LOCAL_WEB_FETCH=true \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

The `--add-host` flag is required on Linux; without it `host.docker.internal` won't resolve.

---

## 8. Voice — faster-whisper

```bash
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
segments, _ = model.transcribe("input.wav", vad_filter=True)
print(" ".join(s.text for s in segments))
```

Wire to Open WebUI's audio input or a custom hotkey daemon.

---

## 9. Security suite (CI-callable, strictly offline)

```bash
pip install bandit semgrep pip-audit
sudo apt install -y gitleaks
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
```

Run `make offline-prep` once (with internet) to pre-cache the rule databases.
After that, `scripts/security_scan.sh` runs every scanner against a *local*
cache and never reaches for the network. It fails loud (exit 2) rather than
silently going online if a cache is missing:

- `bandit` — fully offline (rules baked into the package).
- `semgrep` — vendored ruleset under `~/offline-ai-stack/cache/semgrep-rules/`;
  refuses `--config auto`.
- `pip-audit` — OSV-mirror cache under `~/offline-ai-stack/cache/osv/`.
- `gitleaks` — fully offline (rules baked into the binary).
- `trivy` — pre-downloaded CVE DB under `~/offline-ai-stack/cache/trivy-db/`;
  invoked with `--offline-scan --skip-db-update`.

**`safety` removed** — its offline DB requires a commercial license; `pip-audit`
covers the same ground via OSV.

---

## 10. Browser & research

**Removed for strict-offline operation.** SearXNG is a metasearch *proxy* that
queries Google / Bing / DDG, and browser-use drives a real browser against real
URLs — both make external HTTP calls every time they're invoked. Re-add them
deliberately only if you accept that they violate the offline guarantee.

---

## 11. Image / UI generation — ComfyUI

```bash
git clone https://github.com/comfyanonymous/ComfyUI ~/offline-ai-stack/ComfyUI
cd ~/offline-ai-stack/ComfyUI
python3.11 -m venv venv && source venv/bin/activate
# Blackwell needs cu128 PyTorch
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
pip install -r requirements.txt
python main.py --listen 0.0.0.0 --port 8188
```

---

## 12. Git — Forgejo

```bash
docker run -d --name forgejo \
  -p 3002:3000 -p 222:22 \
  -v ~/offline-ai-stack/forgejo:/data \
  codeberg.org/forgejo/forgejo:9
```

Open `http://localhost:3002`, create admin, then create an OAuth2 application for Woodpecker (Settings → Applications → Create OAuth2 App, redirect URI `http://localhost:8003/authorize`).

---

## 13. CI/CD — Woodpecker

A Woodpecker server is useless without an agent and Forgejo OAuth. Full setup:

```bash
SECRET=$(openssl rand -hex 32)

docker run -d --name woodpecker-server \
  -p 8003:8000 -p 9000:9000 \
  --add-host=host.docker.internal:host-gateway \
  -e WOODPECKER_OPEN=true \
  -e WOODPECKER_HOST=http://localhost:8003 \
  -e WOODPECKER_GITEA=true \
  -e WOODPECKER_GITEA_URL=http://host.docker.internal:3002 \
  -e WOODPECKER_GITEA_CLIENT=<oauth_client_id_from_forgejo> \
  -e WOODPECKER_GITEA_SECRET=<oauth_client_secret_from_forgejo> \
  -e WOODPECKER_AGENT_SECRET=$SECRET \
  -v woodpecker-server-data:/var/lib/woodpecker \
  woodpeckerci/woodpecker-server:latest

docker run -d --name woodpecker-agent \
  --link woodpecker-server \
  -e WOODPECKER_SERVER=woodpecker-server:9000 \
  -e WOODPECKER_AGENT_SECRET=$SECRET \
  -v /var/run/docker.sock:/var/run/docker.sock \
  woodpeckerci/woodpecker-agent:latest
```

Pipeline (`.woodpecker.yml` in repos):

```yaml
steps:
  test:
    image: python:3.11
    commands: [pip install -r requirements.txt, pytest]
  security:
    image: python:3.11
    commands: [bash scripts/security_scan.sh]
  ai_review:
    image: python:3.11
    commands:
      - pip install langgraph langchain-openai
      - python crews/merge_gate.py change.diff
  eval:
    image: node:20
    commands: [npm i -g promptfoo, promptfoo eval]
```

---

## 14. Eval — promptfoo

```bash
npm install -g promptfoo
```

`promptfooconfig.yaml`:

```yaml
providers:
  - id: openai:chat:Qwen/Qwen3-Coder-Next
    config: { apiBaseUrl: http://localhost:8000/v1, apiKey: local }
  - id: openai:chat:mistralai/Devstral-Small-2-24B-Instruct-2512
    config: { apiBaseUrl: http://localhost:8001/v1, apiKey: local }

tests:
  - vars: { task: "Fix race condition in worker pool (Python)." }
    assert:
      - type: llm-rubric
        value: "Patch is correct, minimal, includes a regression test."
  - vars: { task: "Refactor duplicate auth checks across 3 routes into middleware." }
    assert:
      - type: llm-rubric
        value: "Single middleware applied; behavior preserved; tests updated."
```

Stand up 20-30 of these mirroring real tasks before any model swap. Without a real test set, eval is decorative.

---

## 15. Observability — Langfuse

```bash
git clone https://github.com/langfuse/langfuse ~/offline-ai-stack/langfuse
cd ~/offline-ai-stack/langfuse
docker compose up -d
```

Instrument CrewAI/LangGraph by setting env vars:

```bash
export LANGFUSE_PUBLIC_KEY=...
export LANGFUSE_SECRET_KEY=...
export LANGFUSE_HOST=http://localhost:3000
```

Captures every agent call, tool invocation, and token-equivalent cost.

---

## 16. systemd units (the part most stacks skip)

Create `/etc/systemd/system/vllm-primary.service`:

```ini
[Unit]
Description=vLLM Qwen3-Coder-Next
After=network.target nvidia-persistenced.service

[Service]
Type=simple
User=cemilac
Environment=HF_HOME=/home/cemilac/offline-ai-stack/hf-cache
ExecStart=/home/cemilac/ai-stack/bin/vllm serve Qwen/Qwen3-Coder-Next \
  --host 0.0.0.0 --port 8000 --max-model-len 262144 \
  --gpu-memory-utilization 0.55 --enable-auto-tool-choice \
  --tool-call-parser hermes
Restart=always
RestartSec=10
StandardOutput=append:/home/cemilac/offline-ai-stack/logs/vllm-primary.log
StandardError=append:/home/cemilac/offline-ai-stack/logs/vllm-primary.err

[Install]
WantedBy=multi-user.target
```

Same pattern for `vllm-devstral.service` (port 8001, Devstral, mistral parser).

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now vllm-primary vllm-devstral
```

For dockerized services (Chroma, Forgejo, Woodpecker, Open WebUI, Langfuse, SearXNG), use `--restart unless-stopped` on every `docker run`, or convert to a single `docker-compose.yml` and put one systemd unit on `docker compose up`.

---

## 17. Reverse proxy + auth — Caddy

`/etc/caddy/Caddyfile`:

```
{
  auto_https off
}

ai.local:80 {
  basicauth { you $2a$14$<bcrypt_hash> }
  reverse_proxy localhost:3001
}
git.local:80    { reverse_proxy localhost:3002 }
ci.local:80     { reverse_proxy localhost:8003 }
trace.local:80  { reverse_proxy localhost:3000 }
search.local:80 { reverse_proxy localhost:8888 }
```

Generate the bcrypt hash with `caddy hash-password`. Add the `*.local` names to `/etc/hosts`. For real LAN access add `tls internal` and Caddy issues a self-signed cert.

---

## 18. Backups — restic

The irreplaceable state is: ChromaDB (memory), Forgejo (git history), Langfuse Postgres (traces), Open WebUI volume (chats), eval results.

`scripts/backup.sh`:

```bash
#!/usr/bin/env bash
set -e
export RESTIC_REPOSITORY=/mnt/nas/restic-ai-stack
export RESTIC_PASSWORD_FILE=~/.restic-password

restic backup \
  ~/offline-ai-stack/memory \
  ~/offline-ai-stack/forgejo \
  ~/offline-ai-stack/projects \
  ~/offline-ai-stack/reports \
  ~/offline-ai-stack/crews \
  /var/lib/docker/volumes/open-webui \
  --tag daily

restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
```

Cron it nightly (`crontab -e`):

```
30 3 * * * /home/cemilac/offline-ai-stack/scripts/backup.sh >> /home/cemilac/offline-ai-stack/logs/backup.log 2>&1
```

---

## 19. GPU/system monitoring

```bash
# Quick install dcgm-exporter + Prometheus + Grafana
docker run -d --gpus all --rm -p 9400:9400 nvcr.io/nvidia/k8s/dcgm-exporter:latest
docker run -d -p 9090:9090 -v ./prom.yml:/etc/prometheus/prometheus.yml prom/prometheus
docker run -d -p 3003:3000 grafana/grafana
```

Import the NVIDIA DCGM dashboard (id 12239). VRAM creep, thermal throttling, and KV-cache spikes are the failure modes you'll actually hit at sustained multi-agent load.

---

## 20. Final architecture

```
                  [User / Voice → faster-whisper]   (no network)
                              │
                       [Caddy reverse proxy]
                              │
            ┌─────────────────┼──────────────────┐
            ▼                 ▼                  ▼
       Open WebUI        Forgejo           Langfuse
        :3001             :3002              :3000
            │                                  ▲
            │                                  │ traces
   ┌────────┴─────────┐                        │
   ▼        ▼         ▼                        │
  Aider  QwenCode  OpenHands ──────────────────┤
            │                                  │
            ▼                                  │
   CrewAI dev_team.py / LangGraph merge_gate.py│
            │                                  │
   ┌────────┴────────┐                         │
   ▼                 ▼                         │
vLLM :8000      vLLM :8001                     │
Qwen3-Coder    Devstral Small 2 ───────────────┘
            │
            ▼
ChromaDB :8002 ─── LlamaIndex + bge-reranker
            │
            ▼
Woodpecker :8003 ── security scans ── promptfoo evals
            │
            ▼
            restic → NAS
```

---

## 21. Bring-up order (one-time)

1. NVIDIA driver 570+ → CUDA 12.8 → `nvidia-smi` clean
2. Docker + NVIDIA container toolkit → GPU visible in containers
3. Python 3.11 venv + vLLM + `mistral_common`
4. `huggingface-cli login`
5. Pull models: `huggingface-cli download Qwen/Qwen3-Coder-Next` (and Devstral, embeddings, reranker, whisper)
6. Bring up vLLM (manually first; turn into systemd units once stable)
7. Chroma container + first ingestion run on a project
8. Open WebUI; verify chat works
9. Aider + Qwen Code + OpenHands; verify each connects
10. CrewAI: `dev_team.py` end-to-end on a tiny ticket
11. LangGraph: merge_gate.py on a real diff
12. Security suite + promptfoo (build the eval set)
13. Forgejo → register OAuth app → Woodpecker server + agent
14. Langfuse + instrument CrewAI
15. SearXNG + browser-use + faster-whisper
16. ComfyUI (last, optional)
17. Caddy + auth
18. systemd units + restic cron
19. dcgm-exporter + Prometheus + Grafana

---

## 22. Daily-use minimum

If you skip anything, keep this core: vLLM + Qwen3-Coder-Next, Aider, Open WebUI, Chroma + LlamaIndex, CrewAI dev_team, Bandit/Semgrep/Gitleaks, Forgejo, Langfuse. That's the cleanest viable Claude-Code + Superpowers + MEM replacement, fully offline.


---

## 23. Plugin-by-plugin offline equivalents

Concrete, one-to-one mappings for the six Claude Code plugins/skills shown in the source video. Each section gives the local replacement, the actual files to create, and the slash-command-style entry point.

### 23.1 Superpowers (`obra/superpowers`) → local skill framework

The Superpowers plugin ships ~21 skills (brainstorming, writing-plans, executing-plans, test-driven-development, systematic-debugging, subagent-driven-development, dispatching-parallel-agents, and more). Each is a structured prompt that gets loaded into the agent's context on demand.

**Offline equivalent:** a folder of markdown skill files plus a loader that injects them into CrewAI agent backstories or Aider system prompts.

```bash
mkdir -p ~/offline-ai-stack/skills
```

Create these skill files:

`~/offline-ai-stack/skills/brainstorming.md`:
```markdown
# Skill: Brainstorming
1. Generate at least 5 distinct directions before evaluating any.
2. Force variety: include the obvious, the contrarian, the simplest viable, and the most ambitious.
3. Score each on (a) effort, (b) impact, (c) reversibility.
4. Surface the strongest two with explicit tradeoffs; do not collapse to a single recommendation prematurely.
```

`~/offline-ai-stack/skills/writing-plans.md`:
```markdown
# Skill: Writing Plans
A plan must contain:
- Goal (one sentence, outcome-shaped)
- Acceptance criteria (testable)
- Out-of-scope (explicit)
- Steps (ordered, each with a verify step)
- Rollback for each step
- Time estimate per step
Reject any plan missing rollback or acceptance criteria.
```

`~/offline-ai-stack/skills/executing-plans.md`:
```markdown
# Skill: Executing Plans
1. Read the entire plan before touching anything.
2. Execute one step at a time; verify before proceeding.
3. If a step fails, do NOT improvise — report the failure with state and ask.
4. Update the plan in place when reality diverges; never silently deviate.
```

`~/offline-ai-stack/skills/test-driven-development.md`:
```markdown
# Skill: TDD
1. Write the failing test first; do not write implementation code yet.
2. Run the test and confirm it fails for the expected reason (not import error).
3. Write the minimum code to make it pass.
4. Run the full suite to catch regressions.
5. Refactor with the test as a safety net.
6. Commit at green.
```

`~/offline-ai-stack/skills/systematic-debugging.md`:
```markdown
# Skill: Systematic Debugging
1. State the expected behavior precisely.
2. State the observed behavior precisely.
3. Form a hypothesis. Predict what would prove it wrong.
4. Run the cheapest experiment that would falsify the hypothesis.
5. If falsified, revise. Do not speculate without testing.
6. Bisect when the search space is large (git bisect, binary-search inputs).
7. Fix the cause, not the symptom. Add a regression test.
```

`~/offline-ai-stack/skills/subagent-driven-development.md`:
```markdown
# Skill: Subagent-Driven Development
For tasks larger than ~50 LOC of changes:
1. Decompose into independent subtasks.
2. Spawn a focused subagent per subtask with a tightly scoped prompt and only the files it needs.
3. Each subagent returns a diff + rationale + self-review.
4. Parent agent integrates and runs cross-cutting tests.
```

`~/offline-ai-stack/skills/dispatching-parallel-agents.md`:
```markdown
# Skill: Dispatching Parallel Agents
When subtasks are independent (no shared file writes):
- Dispatch them concurrently via CrewAI Process.parallel or asyncio.gather.
- Set explicit non-overlapping file scopes per agent.
- Merge results; if conflicts, escalate to the architect agent.
```

Add the rest as needed:
- `code-search.md` — grep/ripgrep patterns and ranking
- `refactoring.md` — Tidy First; behavior-preserving changes only
- `pr-review.md` — review checklist (bugs, perf, security, style, tests)
- `incident-response.md` — stabilize → diagnose → fix → postmortem
- `prompt-engineering.md` — examples, negative examples, output schema
- `architecture-decision-record.md` — context/decision/consequences template
- `commit-discipline.md` — atomic commits, conventional format
- `dependency-hygiene.md` — pin, audit, update on schedule

**Loader:**

`~/offline-ai-stack/skills/loader.py`:
```python
from pathlib import Path
SKILLS_DIR = Path("~/offline-ai-stack/skills").expanduser()

def load(*names: str) -> str:
    return "\n\n".join((SKILLS_DIR / f"{n}.md").read_text() for n in names)

def inject(agent, *names: str):
    """Append skill prompts to a CrewAI agent's backstory."""
    agent.backstory = f"{agent.backstory}\n\n{load(*names)}"
    return agent
```

Use in `crews/dev_team.py`:
```python
from skills.loader import inject
backend_dev = inject(backend_dev, "test-driven-development", "systematic-debugging", "commit-discipline")
architect = inject(architect, "writing-plans", "architecture-decision-record")
```

### 23.2 Frontend Design (`anthropic/frontend-design`) → design skill prompt

The Anthropic plugin steers the model away from generic AI aesthetics (purple gradients, glassmorphism, three-color rainbows). The local equivalent is a strong skill prompt that hard-codes those constraints plus aesthetic profiles.

`~/offline-ai-stack/skills/frontend-design.md`:
```markdown
# Skill: Frontend Design

## Anti-patterns (never produce these by default)
- Purple/blue gradient hero sections
- Glassmorphism (backdrop-blur on every card)
- Emoji used as functional icons
- Border-radius > 16px without explicit reason
- Three+ accent colors competing
- Generic "AI assistant" iconography (sparkles, magic wand)
- Drop shadows with opacity > 0.15
- Centered marketing copy by default

## Aesthetic profiles — pick exactly one and commit

LUXURY
- Headlines: serif (Playfair Display, EB Garamond)
- Body: sans (Inter, Söhne)
- Palette: monochrome + 1 jewel accent (deep emerald, oxblood, sapphire)
- Whitespace: 1.5x typical; tighten kerning on display sizes
- Imagery: editorial photography, no illustrations

REFINED (default for SaaS)
- Headlines: Inter Tight or Geist Sans, 600 weight
- Body: Inter, 400, 1.6 line-height
- 8pt grid; no arbitrary spacing
- Palette: neutral 50-900 + 1 functional accent
- Shadows: max 0.08 opacity, 4px blur

BRUTALIST
- Mono headlines (JetBrains Mono, IBM Plex Mono)
- Hard 4px shadows, offset only
- Primary RGB colors, no tints
- border-radius: 0
- Visible grid lines

EDITORIAL
- Serif body text (Source Serif, Lora)
- Multi-column layout above lg breakpoint
- Drop caps, footnote markers
- Pull quotes with rule-line treatment

## Stack defaults
- Components: shadcn/ui — do not reinvent
- Styling: Tailwind tokens only; no arbitrary `[#hex]` values
- Icons: lucide-react, single weight, single size scale
- Motion: framer-motion, easing `[0.16, 1, 0.3, 1]`, duration ≤ 300ms
- Forms: react-hook-form + zod

## Process
1. State which aesthetic profile applies.
2. List the 3-4 components from shadcn that compose the layout.
3. Build mobile-first; verify at 375 / 768 / 1280.
4. Run through the anti-pattern list as a self-check before returning.
```

Use it: pass to Aider with `--read ~/offline-ai-stack/skills/frontend-design.md` or attach via the CrewAI loader to a dedicated `frontend_dev` agent.

### 23.3 Code Review (`/code-review` parallel agents) → code_review crew

The video shows four parallel review agents: CLAUDE.md compliance, redundant-rule check, bug detection, git-history context.

`~/offline-ai-stack/crews/code_review.py`:
```python
import subprocess, sys
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
from skills.loader import inject

llm = ChatOpenAI(base_url="http://localhost:8001/v1", api_key="local",
                 model="mistralai/Devstral-Small-2-24B-Instruct-2512", temperature=0.0)

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

claude_md_compliance = inject(Agent(
    role="Project Conventions Compliance Checker",
    goal="Verify the diff follows CONVENTIONS.md / CLAUDE.md / project rules.",
    backstory="Reads the project's rule files first, then audits the diff for violations. "
              "Reports each violation as (rule, file:line, evidence).",
    llm=llm, tools=[file_tool], allow_delegation=False,
), "pr-review")

redundancy_checker = inject(Agent(
    role="Redundancy Detector",
    goal="Find duplicated logic, redundant rules, and dead code in the diff.",
    backstory="Loves DRY but understands when it harms clarity. "
              "Reports duplications with concrete refactor suggestions.",
    llm=llm, tools=[file_tool], allow_delegation=False,
), "refactoring")

bug_detector = inject(Agent(
    role="Bug Detector",
    goal="Find logic bugs, off-by-ones, race conditions, and unhandled errors.",
    backstory="Adversarial reader. Treats every branch as guilty until proven correct.",
    llm=llm, tools=[file_tool], allow_delegation=False,
), "systematic-debugging")

git_history_reviewer = inject(Agent(
    role="Git History Context Reviewer",
    goal="Use git log/blame to find why touched code was last changed and surface relevant prior context.",
    backstory="Always asks 'why was this written this way?' before suggesting changes. "
              "Uses git blame and log to recover institutional memory.",
    llm=llm, tools=[file_tool, git_tool], allow_delegation=False,
), "code-search")

def build(diff_path: str):
    diff = Path(diff_path).read_text()
    common = f"\n\nDiff under review:\n```diff\n{diff[:8000]}\n```"
    tasks = [
        Task(agent=claude_md_compliance,
             description="Audit the diff against project conventions." + common,
             expected_output="A list of violations (rule, file:line, evidence) or 'no violations'."),
        Task(agent=redundancy_checker,
             description="Find redundancy and dead code in the diff." + common,
             expected_output="A redundancy list with refactor suggestions."),
        Task(agent=bug_detector,
             description="Find bugs in the diff." + common,
             expected_output="A bug list (severity, file:line, scenario, fix)."),
        Task(agent=git_history_reviewer,
             description="Use git log/blame on the touched files; surface relevant historical context." + common,
             expected_output="Per-file historical context that affects the review."),
    ]
    return Crew(
        agents=[claude_md_compliance, redundancy_checker, bug_detector, git_history_reviewer],
        tasks=tasks,
        process=Process.parallel,   # all four run concurrently
        verbose=True,
    )

if __name__ == "__main__":
    crew = build(sys.argv[1])
    print(crew.kickoff())
```

Run it like the video's `/code-review`:
```bash
git diff main > change.diff
python ~/offline-ai-stack/crews/code_review.py change.diff
```

### 23.4 Security Review (`anthropic/security-guidance`) → security skill + scanner combo

Two layers: the static scanner suite from Section 9 catches the deterministic stuff, and an LLM agent with this skill prompt catches the contextual cases the scanners miss.

`~/offline-ai-stack/skills/security-review.md`:
```markdown
# Skill: Security Review

Audit the code for these specific vulnerability classes. For each finding, report:
SEVERITY (CRITICAL / HIGH / MEDIUM / LOW), FILE:LINE, EXPLOIT, FIX.

1. **Command injection**
   - subprocess.run(..., shell=True) with unsanitized input
   - os.system(), os.popen() with user input
   - eval/exec of shell-formatted strings

2. **Code execution sinks**
   - eval(), exec(), Function constructor, new Function()
   - JSON parsers that allow function references
   - Template engines with code execution (Jinja2 sandbox bypass)

3. **XSS vectors**
   - dangerouslySetInnerHTML in React with user input
   - element.innerHTML = user_input
   - v-html in Vue, {@html} in Svelte
   - Markdown rendering without sanitization

4. **Unsafe deserialization**
   - pickle.loads, pickle.load (Python)
   - yaml.load (use yaml.safe_load)
   - Marshal, ObjectInputStream
   - JSON parsers configured to instantiate classes

5. **Path traversal**
   - open(user_input), Path(user_input)
   - Concatenation of user input into file paths without resolve()/normalize()
   - Zip/tar extraction without member-name validation (zip-slip)

6. **SQL injection**
   - String-formatted queries (f"SELECT ... {var}")
   - .format() into queries
   - Missing parameterization in ORM raw() calls

7. **Hardcoded secrets**
   - API keys, tokens, passwords, private keys in source
   - Default credentials in config defaults
   - Secrets in test fixtures committed to git

8. **AuthN/AuthZ bypasses**
   - Routes missing auth middleware
   - IDOR (object access by ID without ownership check)
   - JWT verification with `algorithms=['none']` or no `verify_signature`
   - Privilege checks that compare strings without canonicalization

9. **SSRF**
   - HTTP clients fetching user-supplied URLs without allowlist
   - Cloud metadata endpoint reachability (169.254.169.254)

10. **Open redirect**
    - Redirects to user-supplied URLs without origin check

End with a triage recommendation: which findings block merge, which can ship with follow-up tickets.
```

Wire into a security agent in `crews/code_review.py` or run on demand:
```bash
python ~/offline-ai-stack/crews/security_review.py change.diff
bash ~/offline-ai-stack/scripts/security_scan.sh    # static scanners
```

### 23.5 Claude MEM (Alex Newman) → claude_mem_local

Claude MEM records tool calls, AI-compresses session summaries, auto-injects relevant past context on session start, and persists locally. Full local implementation:

`~/offline-ai-stack/scripts/claude_mem_local.py`:
```python
"""
Local Claude-MEM equivalent.
- Records tool calls & observations during a session
- AI-compresses sessions into summaries at end
- Extracts atomic observations as separately-retrievable memory units
- Auto-injects relevant past context on demand
- Backend: ChromaDB (local), no cloud
"""
import os, json, time, hashlib, sys
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
```

**Aider integration** — wrap Aider so memory is auto-injected:

`~/offline-ai-stack/scripts/aider-mem`:
```bash
#!/usr/bin/env bash
PROJECT="$(basename "$(pwd)")"
QUERY="${1:-current task}"
CTX=$(python ~/offline-ai-stack/scripts/claude_mem_local.py recall "$PROJECT" "$QUERY")
echo "$CTX" > /tmp/aider-context.md
aider --read /tmp/aider-context.md --model openai/Qwen/Qwen3-Coder-Next "$@"
```

```bash
chmod +x ~/offline-ai-stack/scripts/aider-mem
```

**End-of-session hook** — call from a wrapper or a CrewAI callback:
```python
from claude_mem_local import SessionRecorder
rec = SessionRecorder("myapp")
# ... agents run, calling rec.tool_call(...) and rec.note(...) ...
rec.end()
```

### 23.6 Stack (Gary Tan / `garytan/stack`) → exec review crew + Makefile commands

The Stack plugin adds CEO/Eng/Design review agents and slash commands `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/review`, `/qa`, `/ship`. Local equivalent:

`~/offline-ai-stack/crews/exec_review.py`:
```python
import sys, argparse
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from skills.loader import inject

reasoner = ChatOpenAI(base_url="http://localhost:8000/v1", api_key="local",
                      model="Qwen/Qwen3-Coder-Next", temperature=0.4)

ceo = inject(Agent(
    role="CEO",
    goal="Make a decisive go/no-go on features based on market fit, pricing, and competitive position. "
         "Be ruthless about scope.",
    backstory="Has launched and shut down multiple products. Reads the room. Hates feature bloat. "
              "Will ship at 80% if 80% is the right call.",
    llm=reasoner, allow_delegation=False,
), "writing-plans"),

eng_lead = inject(Agent(
    role="Engineering Lead",
    goal="Assess feasibility, complexity, time-to-ship, and tech-debt impact.",
    backstory="Estimates in days, not points. Calls out hidden coupling. Knows when to say 'rewrite' vs 'patch'.",
    llm=reasoner, allow_delegation=False,
), "writing-plans", "architecture-decision-record")

design_lead = inject(Agent(
    role="Design Lead",
    goal="Assess UX coherence, user-flow completeness, and design-system consistency.",
    backstory="Cares about empty states, error states, and the third user the team forgot about.",
    llm=reasoner, allow_delegation=False,
), "frontend-design")

qa_lead = Agent(
    role="QA Lead",
    goal="Identify high-risk regressions, untested branches, and rollback feasibility.",
    backstory="Has seen which 'small changes' took prod down. Asks for a kill-switch on every launch.",
    llm=reasoner, allow_delegation=False,
)

release_mgr = Agent(
    role="Release Manager",
    goal="Plan rollout phases, comms, monitoring, and rollback. Produce a go/no-go.",
    backstory="Friday-deploy survivor. Won't ship without monitors and a documented rollback.",
    llm=reasoner, allow_delegation=False,
)

ROLES = {
    "ceo": (ceo, "Review this plan as CEO. Decide go/no-go. Cover: market fit, pricing, "
                 "competitive moat, scope discipline, ship-now vs wait."),
    "eng": (eng_lead, "Review this plan as Engineering Lead. Cover: feasibility, complexity, "
                      "time-to-ship, tech-debt, hidden risks."),
    "design": (design_lead, "Review this plan as Design Lead. Cover: UX coherence, flow gaps, "
                            "empty/error states, accessibility, design-system consistency."),
    "qa": (qa_lead, "Review this plan as QA Lead. Cover: high-risk regressions, untested branches, "
                    "rollout risk, rollback feasibility."),
    "release": (release_mgr, "Plan the rollout. Cover: phases, comms, monitors, rollback, go/no-go."),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=list(ROLES) + ["all"])
    ap.add_argument("--plan", required=True)
    args = ap.parse_args()
    plan_text = Path(args.plan).read_text()

    if args.role == "all":
        tasks, agents = [], []
        for name, (agent, prompt) in ROLES.items():
            tasks.append(Task(agent=agent,
                description=f"{prompt}\n\nPlan:\n{plan_text}",
                expected_output="A structured review with explicit decision."))
            agents.append(agent)
        crew = Crew(agents=agents, tasks=tasks, process=Process.parallel, verbose=True)
    else:
        agent, prompt = ROLES[args.role]
        task = Task(agent=agent,
            description=f"{prompt}\n\nPlan:\n{plan_text}",
            expected_output="A structured review with explicit decision.")
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)

    print(crew.kickoff())

if __name__ == "__main__":
    main()
```

**Makefile in each project repo** for the slash-command UX:

`Makefile`:
```makefile
PLAN ?= PLAN.md
CREWS := $(HOME)/offline-ai-stack/crews
SCRIPTS := $(HOME)/offline-ai-stack/scripts

plan-ceo-review:
	python $(CREWS)/exec_review.py --role ceo --plan $(PLAN)

plan-eng-review:
	python $(CREWS)/exec_review.py --role eng --plan $(PLAN)

plan-design-review:
	python $(CREWS)/exec_review.py --role design --plan $(PLAN)

plan-all-reviews:
	python $(CREWS)/exec_review.py --role all --plan $(PLAN)

review:
	git diff main > /tmp/change.diff
	python $(CREWS)/code_review.py /tmp/change.diff

qa:
	bash $(SCRIPTS)/security_scan.sh
	pytest -q

ship:
	python $(CREWS)/exec_review.py --role release --plan $(PLAN)
	@echo "Run 'git push' if release manager approved."

mem-recall:
	python $(SCRIPTS)/claude_mem_local.py recall $$(basename $$(pwd)) "$(Q)"
```

Now your in-repo workflow mirrors the video:
```bash
make plan-ceo-review PLAN=PLAN.md     # /plan-ceo-review
make plan-eng-review PLAN=PLAN.md     # /plan-eng-review
make plan-design-review PLAN=PLAN.md  # /plan-design-review
make review                            # /code-review (4 parallel agents)
make qa                                # /qa (security scans + tests)
make ship                              # /ship (release plan + go/no-go)
make mem-recall Q="how does auth work" # Claude-MEM recall
```

### 23.7 Mapping at a glance

| Claude Code plugin | Local equivalent | Entry point |
|---|---|---|
| `obra/superpowers` | `~/offline-ai-stack/skills/*.md` + `loader.py` | `from skills.loader import inject` |
| `anthropic/frontend-design` | `skills/frontend-design.md` | Loaded into frontend agent backstory |
| `/code-review` | `crews/code_review.py` (4 parallel agents) | `make review` |
| `anthropic/security-guidance` | `skills/security-review.md` + scanner suite | `make qa` |
| `claude-mem` (Alex Newman) | `scripts/claude_mem_local.py` + ChromaDB | `make mem-recall Q="..."` |
| `garytan/stack` | `crews/exec_review.py` + Makefile | `make plan-{ceo,eng,design}-review`, `make ship` |

That's the full Claude Code plugin surface, reproduced offline against your local vLLM stack with no cloud calls.
