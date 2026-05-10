#!/usr/bin/env bash
# Stop the offline AI stack. Volumes are preserved by default.
set -euo pipefail

STACK="${HOME}/offline-ai-stack"
cd "$STACK"

echo "==> Stopping docker services"
docker compose down

echo "==> Stopping vLLM (systemd)"
sudo systemctl stop vllm-primary vllm-devstral || true

echo "Stack stopped. Volumes preserved. Run with --purge to drop them."

if [[ "${1:-}" == "--purge" ]]; then
  echo "==> Purging volumes (irreversible)"
  docker compose down -v
fi
