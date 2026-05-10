#!/usr/bin/env bash
# Consume a bundle produced by stage-bundle.sh on an AIR-GAPPED target.
# No internet is required (or attempted) at any step.
#
# Usage:
#   bash offline-ai-stack/scripts/import-bundle.sh /mnt/usb/offline-ai-stack-bundle-YYYYMMDD/
#
# Steps:
#   1. Verify the bundle layout
#   2. rsync models/ and cache/ into $STACK_HOME
#   3. rsync repo files into $STACK_HOME
#   4. docker load every image tarball
#   5. pip install --no-index --find-links wheels/ -r requirements.txt
#   6. Write telemetry opt-outs to /etc/environment (if sudo) or ~/.bashrc
#   7. Run hf-audit to confirm everything is in place
#
# After this, the target needs zero internet for the rest of its life with
# this stack.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash import-bundle.sh /path/to/bundle-dir"
  exit 2
fi

BUNDLE="$1"
STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"

[[ -d "$BUNDLE" ]] || { echo "ERROR: bundle directory not found: $BUNDLE"; exit 1; }
for required in models cache docker-images wheels offline-ai-stack; do
  [[ -d "$BUNDLE/$required" ]] || {
    echo "ERROR: bundle is missing $required/ — was stage-bundle.sh run successfully?"
    exit 1
  }
done

echo "==> 1. Verifying bundle"
if [[ -f "$BUNDLE/MANIFEST.txt" ]]; then
  echo "    manifest present; total size $(du -sh "$BUNDLE" | cut -f1)"
else
  echo "    no MANIFEST.txt — proceeding without integrity check"
fi

echo "==> 2. Models  ←  $BUNDLE/models/"
mkdir -p "$STACK_HOME"
rsync -a --info=progress2 "$BUNDLE/models/" "$STACK_HOME/models/"

echo "==> 3. Scanner DBs  ←  $BUNDLE/cache/"
rsync -a --info=progress2 "$BUNDLE/cache/" "$STACK_HOME/cache/"

echo "==> 4. Repo files  ←  $BUNDLE/offline-ai-stack/"
rsync -a --info=progress2 \
  --exclude=__pycache__ --exclude=.pytest_cache \
  "$BUNDLE/offline-ai-stack/" "$STACK_HOME/"

echo "==> 5. Loading docker images"
for tar in "$BUNDLE/docker-images"/*.tar; do
  [[ -f "$tar" ]] || continue
  echo "    loading $(basename "$tar")"
  docker load < "$tar" >/dev/null
done

echo "==> 6. Installing Python wheels (no internet, no-index)"
# Find a Python venv to install into; default to $HOME/ai-stack (matches the
# layout in OFFLINE_AI_STACK.md). User can override with PIP_VENV.
PIP_VENV="${PIP_VENV:-$HOME/ai-stack}"
if [[ ! -x "$PIP_VENV/bin/pip" ]]; then
  echo "    creating venv at $PIP_VENV"
  python3.11 -m venv "$PIP_VENV"
fi
"$PIP_VENV/bin/pip" install --quiet --upgrade pip --no-index --find-links "$BUNDLE/wheels"
"$PIP_VENV/bin/pip" install --no-index --find-links "$BUNDLE/wheels" \
  -r "$STACK_HOME/requirements.txt"

echo "==> 7. Telemetry opt-outs"
TELEMETRY=$(cat <<'EOF'

# Offline-ai-stack telemetry opt-outs (written by import-bundle.sh)
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
LLAMA_INDEX_TELEMETRY_DISABLED=true
LLAMA_INDEX_ANALYTICS_DISABLED=true
POSTHOG_DISABLED=true
PIP_DISABLE_PIP_VERSION_CHECK=1
EOF
)
if sudo -n true 2>/dev/null; then
  echo "$TELEMETRY" | sudo tee -a /etc/environment >/dev/null
  echo "    wrote to /etc/environment"
else
  echo "$TELEMETRY" >> "$HOME/.bashrc"
  echo "    wrote to ~/.bashrc (sudo not available; re-source the shell)"
fi

echo "==> 8. Structural verification"
bash "$STACK_HOME/scripts/hf-audit.sh"

echo
echo "Bundle imported. The target is now fully self-contained."
echo "Next steps:"
echo "  sudo make os-harden    # mask Ubuntu phone-home services"
echo "  sudo reboot"
echo "  source $PIP_VENV/bin/activate"
echo "  make bring-up          # start vLLM + docker stack"
echo "  sudo make airgap-test  # confirm full operation under egress drop"
