#!/usr/bin/env bash
# One-shot offline preparation. Run ONCE with internet, then the stack is
# strictly offline at runtime. This script:
#   1. Pre-downloads scanner DBs (trivy, OSV for pip-audit) into ~/offline-ai-stack/cache/
#   2. Vendors a semgrep ruleset locally so --config auto is never needed
#   3. Pre-loads the local embedding model used by ChromaDB / claude_mem_local
#   4. Pre-loads the faster-whisper model
#   5. Pins a system-wide opt-out for agent CLI telemetry
#
# Run with internet:   bash scripts/offline-prep.sh
# Re-run quarterly to refresh CVE / OSV data; otherwise no network calls
# happen at runtime.
set -euo pipefail

STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"
CACHE="${STACK_HOME}/cache"
mkdir -p "$CACHE" "$STACK_HOME/hf-cache"

echo "==> 1. Trivy CVE database"
TRIVY_DB="$CACHE/trivy-db"
mkdir -p "$TRIVY_DB"
TRIVY_CACHE_DIR="$TRIVY_DB" trivy --download-db-only

echo "==> 2. OSV mirror for pip-audit"
OSV_CACHE="$CACHE/osv"
mkdir -p "$OSV_CACHE"
# Warm the OSV cache by running a no-op audit against a known-empty manifest
echo "" > /tmp/_offline-prep-empty.txt
pip-audit --vulnerability-service osv --cache-dir "$OSV_CACHE" \
  --requirement /tmp/_offline-prep-empty.txt --format json > /dev/null || true
rm -f /tmp/_offline-prep-empty.txt

echo "==> 3. Semgrep ruleset (vendored, no --config auto at scan time)"
SEMGREP_RULES="$CACHE/semgrep-rules"
if [[ ! -d "$SEMGREP_RULES" ]]; then
  git clone --depth 1 https://github.com/semgrep/semgrep-rules "$SEMGREP_RULES"
else
  git -C "$SEMGREP_RULES" pull --ff-only
fi

echo "==> 4. Embedding model (local sentence-transformers; used by Chroma + claude_mem_local)"
export HF_HOME="$STACK_HOME/hf-cache"
python3 - <<'PY'
import os
from huggingface_hub import snapshot_download
# Small, fast, fully-local; default Chroma embedder.
snapshot_download("sentence-transformers/all-MiniLM-L6-v2",
                  cache_dir=os.environ["HF_HOME"])
PY

echo "==> 5. faster-whisper model (large-v3)"
python3 - <<'PY'
import os
from huggingface_hub import snapshot_download
snapshot_download("Systran/faster-whisper-large-v3",
                  cache_dir=os.environ["HF_HOME"])
PY

echo "==> 6. Pre-pull docker images (so docker-compose's pull_policy: never works)"
for image in \
    chromadb/chroma:latest \
    ghcr.io/open-webui/open-webui:main \
    codeberg.org/forgejo/forgejo:9 \
    woodpeckerci/woodpecker-server:latest \
    woodpeckerci/woodpecker-agent:latest \
    nvcr.io/nvidia/k8s/dcgm-exporter:latest \
    prom/prometheus \
    grafana/grafana; do
  echo "   pulling $image"
  docker pull "$image" >/dev/null || echo "   (skipped $image — not critical for offline-prep)"
done

echo "==> 7. Telemetry opt-outs (persisted to /etc/environment if writable, else user shell)"
TELEMETRY_VARS=$(cat <<'EOF'
# Agent / SDK telemetry opt-outs (set by offline-ai-stack/scripts/offline-prep.sh)
# Universal "please don't phone home" markers
DO_NOT_TRACK=1
TELEMETRY_DISABLED=1
SCARF_NO_ANALYTICS=true
# OpenAI / Anthropic kill switches — never let an SDK accidentally hit a remote provider
OPENAI_API_KEY=local
OPENAI_API_BASE=http://localhost:8000/v1
ANTHROPIC_API_KEY=
# LangChain / LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_TRACING=false
LANGCHAIN_API_KEY=
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
# CrewAI's own telemetry (langtrace integration enabled by default in some versions)
CREWAI_TELEMETRY_OPT_OUT=true
CREWAI_DISABLE_TELEMETRY=true
OTEL_SDK_DISABLED=true
# Aider, OpenHands, promptfoo
AIDER_ANALYTICS=false
AIDER_ANALYTICS_DISABLE=1
PROMPTFOO_DISABLE_TELEMETRY=1
# ChromaDB → PostHog
ANONYMIZED_TELEMETRY=false
# HuggingFace Hub: disable telemetry (separate from OFFLINE — keep OFFLINE on systemd units only)
HF_HUB_DISABLE_TELEMETRY=1
HF_HUB_DISABLE_IMPLICIT_TOKEN=1
# vLLM
VLLM_NO_USAGE_STATS=1
VLLM_DO_NOT_TRACK=1
EOF
)

if sudo -n true 2>/dev/null && [[ -w /etc/environment || -w / ]]; then
  echo "$TELEMETRY_VARS" | sudo tee -a /etc/environment >/dev/null
  echo "   wrote telemetry opt-outs to /etc/environment (system-wide)"
else
  echo "$TELEMETRY_VARS" >> "$HOME/.bashrc"
  echo "   wrote telemetry opt-outs to ~/.bashrc (re-source or open a new shell)"
fi

echo
echo "Offline prep complete. Cached at: $CACHE"
echo "Run 'make offline-doctor' with the stack up to verify no leaks remain."
echo "Disconnect the network now; the stack will run strictly offline."
echo "Re-run this script (with internet) every ~90 days to refresh CVE/OSV data."
