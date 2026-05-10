#!/usr/bin/env bash
set -e
mkdir -p reports
bandit -r . -f json -o reports/bandit.json || true
semgrep --config auto --json -o reports/semgrep.json . || true
safety check --json > reports/safety.json || true
pip-audit -f json > reports/pip-audit.json || true
gitleaks detect --report-format json --report-path reports/gitleaks.json || true
trivy fs --format json -o reports/trivy.json . || true
echo "Scans complete: see reports/"
