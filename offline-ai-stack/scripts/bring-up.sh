#!/usr/bin/env bash
# Bring up the offline AI stack in the order described in OFFLINE_AI_STACK.md §21.
# Assumes the prerequisites (NVIDIA driver 570+, Docker, NVIDIA container toolkit,
# Python 3.11 venv at ~/ai-stack with vLLM installed, hf-cache populated) are done.
set -euo pipefail

STACK="${HOME}/offline-ai-stack"
cd "$STACK"

echo "==> 1. Verifying GPU visibility"
nvidia-smi >/dev/null
docker run --rm --gpus all nvcr.io/nvidia/cuda:12.8.0-base-ubuntu24.04 nvidia-smi >/dev/null
echo "    GPU OK"

echo "==> 2. Starting vLLM (systemd)"
sudo systemctl start vllm-primary vllm-devstral
echo "    Waiting for :8000 and :8001 to respond"
until curl -sf http://localhost:8000/v1/models >/dev/null; do sleep 3; done
until curl -sf http://localhost:8001/v1/models >/dev/null; do sleep 3; done
echo "    vLLM ready"

echo "==> 3. Starting docker services"
: "${FORGEJO_OAUTH_CLIENT:?set in env or .env}"
: "${FORGEJO_OAUTH_SECRET:?set in env or .env}"
: "${WOODPECKER_AGENT_SECRET:?set in env or .env}"
docker compose up -d

echo "==> 4. Status"
docker compose ps
echo
echo "Endpoints:"
echo "  Open WebUI    http://localhost:3001"
echo "  Forgejo       http://localhost:3002"
echo "  Woodpecker    http://localhost:8003"
echo "  Chroma        http://localhost:8002"
echo "  Prometheus    http://localhost:9090"
echo "  Grafana       http://localhost:3003"
echo "  vLLM primary  http://localhost:8000/v1"
echo "  vLLM devstral http://localhost:8001/v1"
