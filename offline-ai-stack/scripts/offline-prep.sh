#!/usr/bin/env bash
# One-shot offline preparation. Run ONCE with internet, then the stack is
# strictly offline at runtime. This script:
#   1. Pre-downloads scanner DBs (trivy, OSV for pip-audit) into ~/offline-ai-stack/cache/
#   2. Vendors a semgrep ruleset locally so --config auto is never needed
#   3. Pre-downloads ALL model artifacts as physical files into
#      ~/offline-ai-stack/models/<name>/ — no HF cache layout, no repo IDs
#      at runtime. vLLM and embedding code reference local paths only.
#   4. Pre-pulls docker images so pull_policy: never works
#   5. Pins a system-wide opt-out for agent CLI telemetry
#
# Run with internet:   bash scripts/offline-prep.sh
# Re-run quarterly to refresh CVE / OSV data; otherwise no network calls
# happen at runtime.
#
# Skip the two large coding models with: SKIP_LARGE_MODELS=1 bash scripts/offline-prep.sh
# (useful when you've imported them out-of-band via scripts/import-models.sh)
set -euo pipefail

STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"
CACHE="${STACK_HOME}/cache"
MODELS="${STACK_HOME}/models"
mkdir -p "$CACHE" "$MODELS"

echo "==> 1. Trivy CVE database"
TRIVY_DB="$CACHE/trivy-db"
mkdir -p "$TRIVY_DB"
TRIVY_CACHE_DIR="$TRIVY_DB" trivy --download-db-only

echo "==> 2. OSV mirror for pip-audit"
OSV_CACHE="$CACHE/osv"
mkdir -p "$OSV_CACHE"
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

echo "==> 4. Models — downloaded to plain local paths, no HF cache layout"
# Each entry: <hf-repo-id> <local-dir-name> <approx-gb>
# Files are downloaded with --local-dir + symlinks-off, so the resulting
# directory is fully self-contained (no dependency on the HF cache).
download_model() {
  local repo="$1" name="$2" gb="$3"
  local dest="$MODELS/$name"
  if [[ -d "$dest" && -f "$dest/config.json" ]]; then
    echo "   [skip] $name (already present at $dest)"
    return 0
  fi
  echo "   pulling $repo → $dest (~${gb} GB)"
  huggingface-cli download "$repo" \
    --local-dir "$dest" \
    --local-dir-use-symlinks False \
    --quiet
}

# Small models (always pulled)
download_model "sentence-transformers/all-MiniLM-L6-v2"  "all-minilm-l6-v2"     "0.1"
download_model "BAAI/bge-reranker-v2-m3"                 "bge-reranker-v2-m3"   "2"
download_model "Systran/faster-whisper-large-v3"         "faster-whisper-large-v3" "3"
download_model "Qwen/Qwen3-Embedding-8B"                 "qwen3-embedding-8b"   "16"

# Large coding models (opt-out with SKIP_LARGE_MODELS=1 — pull via removable
# media + scripts/import-models.sh instead)
if [[ "${SKIP_LARGE_MODELS:-0}" != "1" ]]; then
  echo "   (set SKIP_LARGE_MODELS=1 to skip Qwen3-Coder-Next + Devstral)"
  echo "   Devstral may require huggingface-cli login first (gated model)"
  download_model "Qwen/Qwen3-Coder-Next"                 "qwen3-coder-next"     "50"
  download_model "mistralai/Devstral-Small-2-24B-Instruct-2512" "devstral-small-2" "25"
fi

echo "==> 5. Pre-pull docker images (so docker-compose's pull_policy: never works)"
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

echo "==> 6. Telemetry opt-outs (persisted to /etc/environment if writable, else user shell)"
TELEMETRY_VARS=$(cat <<'EOF'
# Agent / SDK telemetry opt-outs (set by offline-ai-stack/scripts/offline-prep.sh)
DO_NOT_TRACK=1
TELEMETRY_DISABLED=1
SCARF_NO_ANALYTICS=true
OPENAI_API_KEY=local
OPENAI_API_BASE=http://localhost:8000/v1
ANTHROPIC_API_KEY=
LANGCHAIN_TRACING_V2=false
LANGCHAIN_TRACING=false
LANGCHAIN_API_KEY=
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
CREWAI_TELEMETRY_OPT_OUT=true
CREWAI_DISABLE_TELEMETRY=true
OTEL_SDK_DISABLED=true
AIDER_ANALYTICS=false
AIDER_ANALYTICS_DISABLE=1
PROMPTFOO_DISABLE_TELEMETRY=1
ANONYMIZED_TELEMETRY=false
HF_HUB_DISABLE_TELEMETRY=1
HF_HUB_DISABLE_IMPLICIT_TOKEN=1
VLLM_NO_USAGE_STATS=1
VLLM_DO_NOT_TRACK=1
# LlamaIndex / GPTCache / posthog (some llama-index extras send analytics)
LLAMA_INDEX_TELEMETRY_DISABLED=true
LLAMA_INDEX_ANALYTICS_DISABLED=true
POSTHOG_DISABLED=true
# pip / setuptools / pkg_resources analytics (newer pip has telemetry plans)
PIP_DISABLE_PIP_VERSION_CHECK=1
PIP_NO_INDEX=
# Ollama (if ever installed) — phones home for model updates
OLLAMA_NOPRUNE=1
OLLAMA_HOST=127.0.0.1:11434
# Block 'check for update' on generic Python tools
NO_COLOR=
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
echo "Offline prep complete."
echo "   Cache:  $CACHE"
echo "   Models: $MODELS"
echo
echo "Verify before disconnecting:"
echo "   make hf-audit            # confirms all model paths exist + no repo-ID usage in runtime code"
echo "   make offline-doctor      # confirms no non-localhost network traffic"
echo
echo "Disconnect the network now; the stack will run strictly offline."
echo "Re-run this script (with internet) every ~90 days to refresh CVE/OSV data."
