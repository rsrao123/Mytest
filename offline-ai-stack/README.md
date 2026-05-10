# offline-ai-stack

Materialized scaffolding for the offline AI engineering stack described in
[`../OFFLINE_AI_STACK.md`](../OFFLINE_AI_STACK.md). Drop this directory at
`~/offline-ai-stack/` on the target workstation; paths in the scripts and
`Makefile` assume that location.

## Layout

```
offline-ai-stack/
├── projects/    # codebases agents work on (runtime; .gitkeep'd)
├── memory/      # ChromaDB volumes (runtime)
├── reports/     # security/eval outputs (runtime)
├── configs/     # Caddyfile, systemd unit files
├── scripts/     # ingest, security_scan, backup, claude_mem_local, aider-mem
├── logs/        # vLLM, agents (runtime)
├── backups/     # restic snapshots (runtime)
├── crews/       # CrewAI / LangGraph definitions
├── skills/      # markdown skill prompts + loader.py
└── hf-cache/    # HF model cache (runtime; HF_HOME)
```

## Bootstrap on the workstation

```bash
# 1. Place this tree at ~/offline-ai-stack
cp -r offline-ai-stack ~/

# 2. Python venv
python3.11 -m venv ~/ai-stack
source ~/ai-stack/bin/activate
pip install -U pip
pip install -r ~/offline-ai-stack/requirements.txt
pip install -U vllm "mistral_common>=1.8.6"

# 3. systemd units
sudo cp ~/offline-ai-stack/configs/vllm-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vllm-primary vllm-devstral

# 4. Caddy
sudo cp ~/offline-ai-stack/configs/Caddyfile /etc/caddy/Caddyfile
# Replace REPLACE_WITH_BCRYPT_HASH with the output of: caddy hash-password
sudo systemctl reload caddy
```

See `OFFLINE_AI_STACK.md` for the full bring-up order, model pulls, container
runs, and per-plugin replacements (Section 23).

## Per-project usage

In any project repo, drop a copy of `offline-ai-stack/Makefile` (or symlink it)
to get the slash-command-equivalent commands:

```bash
make plan-ceo-review PLAN=PLAN.md
make plan-eng-review PLAN=PLAN.md
make plan-design-review PLAN=PLAN.md
make review                            # 4-agent parallel code review
make qa                                # security scans + pytest
make ship                              # release plan + go/no-go
make mem-recall Q="how does auth work" # Claude-MEM recall
```
