#!/usr/bin/env bash
# Build a portable bundle on a STAGING (connected) machine for transfer to an
# AIR-GAPPED target. The bundle contains everything the target needs to run
# the offline-ai-stack without ever touching the internet:
#   - Models (under models/)
#   - Scanner DBs (under cache/)
#   - Docker images as .tar files (docker-images/)
#   - Python wheels for every dep in requirements.txt (wheels/)
#   - The offline-ai-stack repo itself (offline-ai-stack/)
#   - MANIFEST.txt with sizes + sha256 of each docker image tarball
#
# Prerequisite: `make offline-prep` has already populated models/ and cache/.
#
# Usage:
#   make stage-bundle                                    # default bundle dir
#   BUNDLE_DIR=/mnt/usb/airgap-$(date +%F) make stage-bundle
#
# The output is a DIRECTORY (not a tarball) so the user can rsync / cp / tar
# as they prefer. Wrap it yourself for transport:
#   tar -cf bundle.tar $BUNDLE_DIR
set -euo pipefail

STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"
BUNDLE_DIR="${BUNDLE_DIR:-$HOME/offline-ai-stack-bundle-$(date +%Y%m%d)}"

[[ -d "$STACK_HOME/models" ]] || {
  echo "ERROR: $STACK_HOME/models is empty. Run 'make offline-prep' first." >&2
  exit 1
}

echo "==> 0. Sanity-check staging is fully prepped"
bash "$STACK_HOME/scripts/hf-audit.sh" || {
  echo "ERROR: hf-audit failed on staging. Fix gaps before bundling." >&2
  exit 1
}

mkdir -p "$BUNDLE_DIR"

echo "==> 1. Models  →  $BUNDLE_DIR/models/"
rsync -a --info=progress2 "$STACK_HOME/models/" "$BUNDLE_DIR/models/"

echo "==> 2. Scanner DBs (trivy, OSV, semgrep rules)  →  $BUNDLE_DIR/cache/"
rsync -a --info=progress2 "$STACK_HOME/cache/" "$BUNDLE_DIR/cache/"

echo "==> 3. Docker images  →  $BUNDLE_DIR/docker-images/"
mkdir -p "$BUNDLE_DIR/docker-images"
for image in \
    chromadb/chroma:latest \
    ghcr.io/open-webui/open-webui:main \
    codeberg.org/forgejo/forgejo:9 \
    woodpeckerci/woodpecker-server:latest \
    woodpeckerci/woodpecker-agent:latest \
    nvcr.io/nvidia/k8s/dcgm-exporter:latest \
    prom/prometheus \
    grafana/grafana; do
  safe=$(echo "$image" | tr '/:' '__')
  out="$BUNDLE_DIR/docker-images/${safe}.tar"
  if [[ -s "$out" ]]; then
    echo "    [skip] $image (already exported)"
    continue
  fi
  echo "    saving $image"
  if ! docker save "$image" > "$out"; then
    echo "    WARNING: failed to save $image — it may not be pulled locally yet"
    rm -f "$out"
  fi
done

echo "==> 4. Python wheels for requirements.txt  →  $BUNDLE_DIR/wheels/"
mkdir -p "$BUNDLE_DIR/wheels"
# Build wheels for every dep (including sdists). --platform pins target arch.
# If a dep is sdist-only and won't build a wheel, we fall back to the
# unrestricted form.
if ! pip wheel -r "$STACK_HOME/requirements.txt" \
       --wheel-dir "$BUNDLE_DIR/wheels" \
       --platform manylinux2014_x86_64 \
       --python-version 3.11 \
       --only-binary :all: 2>/dev/null; then
  echo "    --only-binary failed for some packages; retrying without platform pin"
  pip wheel -r "$STACK_HOME/requirements.txt" \
            --wheel-dir "$BUNDLE_DIR/wheels"
fi

echo "==> 5. Repo files  →  $BUNDLE_DIR/offline-ai-stack/"
mkdir -p "$BUNDLE_DIR/offline-ai-stack"
# Copy the source tree but skip the huge runtime dirs (already in bundle root)
rsync -a \
  --exclude=__pycache__ --exclude=.pytest_cache \
  --exclude=models --exclude=cache --exclude=hf-cache \
  --exclude=logs --exclude=backups --exclude=memory --exclude=reports \
  --exclude=forgejo --exclude=projects \
  "$STACK_HOME/" "$BUNDLE_DIR/offline-ai-stack/"

echo "==> 6. Manifest"
{
  echo "# offline-ai-stack bundle manifest"
  echo "# Created: $(date -Iseconds)"
  echo "# Staging host: $(hostname)"
  echo
  echo "## Sizes"
  du -sh "$BUNDLE_DIR"/* 2>/dev/null
  echo
  echo "## Docker image sha256"
  (cd "$BUNDLE_DIR/docker-images" && sha256sum *.tar 2>/dev/null) || true
  echo
  echo "## Wheel count"
  ls "$BUNDLE_DIR/wheels" | wc -l | sed 's/^/    /'
  echo
  echo "## Required by target import-bundle.sh"
  echo "    bash offline-ai-stack/scripts/import-bundle.sh <this-bundle-dir>"
} > "$BUNDLE_DIR/MANIFEST.txt"

echo
echo "Bundle ready:"
echo "    $BUNDLE_DIR ($(du -sh "$BUNDLE_DIR" | cut -f1))"
echo
echo "Transfer (USB / DVD / data diode), then on the air-gapped target:"
echo "    bash offline-ai-stack/scripts/import-bundle.sh /path/to/$(basename "$BUNDLE_DIR")"
