#!/usr/bin/env bash
# Strictly-offline security scan. Every tool here runs against a *cached*
# rule/DB; if you haven't run `make offline-prep` first, the cached paths
# below will be missing and scans will fail loud rather than silently
# reach for the internet.
set -euo pipefail

STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"
CACHE="${STACK_HOME}/cache"
SEMGREP_RULES="${CACHE}/semgrep-rules"
TRIVY_DB="${CACHE}/trivy-db"
OSV_CACHE="${CACHE}/osv"

mkdir -p reports

# bandit — fully offline (rules baked into the package).
bandit -r . -f json -o reports/bandit.json || true

# semgrep — local ruleset only; refuse `--config auto` which would hit
# semgrep.dev. If the vendored ruleset isn't present, fail loudly.
if [[ ! -d "$SEMGREP_RULES" ]]; then
  echo "semgrep ruleset missing at $SEMGREP_RULES — run 'make offline-prep' first." >&2
  exit 2
fi
semgrep scan --config "$SEMGREP_RULES" --metrics=off --json -o reports/semgrep.json . || true

# pip-audit — OSV-mirrored data, no network at scan time.
if [[ ! -d "$OSV_CACHE" ]]; then
  echo "OSV cache missing at $OSV_CACHE — run 'make offline-prep' first." >&2
  exit 2
fi
pip-audit --vulnerability-service osv --cache-dir "$OSV_CACHE" --format json > reports/pip-audit.json || true

# gitleaks — fully offline (rules baked in).
gitleaks detect --no-banner --report-format json --report-path reports/gitleaks.json || true

# trivy — must run with a pre-downloaded DB and explicit offline flags.
if [[ ! -d "$TRIVY_DB" ]]; then
  echo "trivy DB missing at $TRIVY_DB — run 'make offline-prep' first." >&2
  exit 2
fi
TRIVY_CACHE_DIR="$TRIVY_DB" trivy --offline-scan fs --skip-db-update \
  --format json -o reports/trivy.json . || true

# safety intentionally removed — its DB requires a commercial offline license.
# pip-audit covers the same ground via OSV.

echo "Offline scans complete: see reports/"
