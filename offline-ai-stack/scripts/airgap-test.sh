#!/usr/bin/env bash
# Harshest possible offline check: drop ALL non-loopback OUTPUT at the
# kernel for the duration of a full smoke test, then restore.
#
# What it proves: with the network blackholed, the agent loop / scanners /
# memory / docker stack still complete their representative workloads.
# If anything tries to phone home, it fails with "Network is unreachable"
# and the test reports the offending stage.
#
# Run only when the stack is already up and stable.
# Requires sudo (iptables manipulation).
#
# Usage:
#   sudo make airgap-test           # default: 90s window, full smoke
#   sudo bash scripts/airgap-test.sh --dry-run    # show what would be tested
#
# Safety: the iptables rules are removed by an EXIT trap; if the script is
# killed -9 the rules linger and you lose internet until you run:
#   sudo iptables -F OUTPUT && sudo ip6tables -F OUTPUT

set -euo pipefail

DRYRUN=0
DURATION=${DURATION:-90}
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRYRUN=1 ;;
    [0-9]*)    DURATION="$arg" ;;
    -h|--help)
      grep '^# ' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
  esac
done

if [[ $DRYRUN -eq 0 && $EUID -ne 0 ]]; then
  echo "Re-running under sudo..."
  exec sudo -E bash "$0" "$@"
fi

STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"
LOG=$(mktemp -t airgap-test-XXXXXX.log)
RESTORED=yes

cleanup() {
  if [[ "$RESTORED" == "no" ]]; then
    echo
    echo "==> EXIT trap: restoring iptables"
    restore_rules
  fi
  rm -f "$LOG"
}
trap cleanup EXIT INT TERM

apply_rules() {
  RESTORED=no
  echo "==> Applying kernel-level OUTPUT drop (loopback + established only)"
  iptables -I OUTPUT 1 -o lo -j ACCEPT
  iptables -I OUTPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  iptables -A OUTPUT -j REJECT --reject-with icmp-net-unreachable
  ip6tables -I OUTPUT 1 -o lo -j ACCEPT 2>/dev/null || true
  ip6tables -I OUTPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
  ip6tables -A OUTPUT -j REJECT 2>/dev/null || true
}

restore_rules() {
  iptables -D OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
  iptables -D OUTPUT -o lo -j ACCEPT 2>/dev/null || true
  iptables -D OUTPUT -j REJECT --reject-with icmp-net-unreachable 2>/dev/null || true
  ip6tables -D OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
  ip6tables -D OUTPUT -o lo -j ACCEPT 2>/dev/null || true
  ip6tables -D OUTPUT -j REJECT 2>/dev/null || true
  RESTORED=yes
}

# Each probe records pass/fail. None abort the script — we want to see
# every stage's behavior under the blackhole.
probe() {
  local name="$1"; shift
  local start=$(date +%s)
  echo -n "    $name ... "
  if "$@" >>"$LOG" 2>&1; then
    echo "PASS ($(($(date +%s) - start))s)"
    return 0
  else
    echo "FAIL ($(($(date +%s) - start))s)"
    return 1
  fi
}

probes_pass=0
probes_fail=0
run_probe() {
  if probe "$@"; then
    probes_pass=$((probes_pass + 1))
  else
    probes_fail=$((probes_fail + 1))
  fi
}

run_smoke() {
  echo "==> Running smoke probes under blackhole ($DURATION s budget)"
  cd "$STACK_HOME"

  # Probe 1: pytest (purely static, must work offline)
  run_probe "pytest tests/" \
    python3 -m pytest tests/ -q --timeout=30

  # Probe 2: structural HF audit
  run_probe "hf-audit (structural)" \
    bash "$STACK_HOME/scripts/hf-audit.sh"

  # Probe 3: security scan (uses cached scanner DBs)
  run_probe "security_scan (uses cached DBs)" \
    bash "$STACK_HOME/scripts/security_scan.sh"

  # Probe 4: claude_mem_local recall (chroma localhost)
  run_probe "claude_mem_local recall" \
    python3 "$STACK_HOME/scripts/claude_mem_local.py" recall airgap-test "smoke"

  # Probe 5: vLLM endpoints (must be up; tests they answer over loopback)
  run_probe "vLLM primary /v1/models" \
    curl -fsS --max-time 10 http://localhost:8000/v1/models
  run_probe "vLLM specialist /v1/models" \
    curl -fsS --max-time 10 http://localhost:8001/v1/models

  # Probe 6: Chroma over loopback
  run_probe "Chroma /api/v1/heartbeat" \
    curl -fsS --max-time 10 http://localhost:8002/api/v1/heartbeat

  # Probe 7: tiny crew run (1 agent, 1 review) — exercises the LLM call path
  if [[ -f /tmp/sample.diff ]]; then
    run_probe "security_review crew on /tmp/sample.diff" \
      python3 "$STACK_HOME/crews/security_review.py" /tmp/sample.diff
  else
    echo "    security_review crew     SKIP (no /tmp/sample.diff)"
  fi
}

if [[ $DRYRUN -eq 1 ]]; then
  echo "==> DRY-RUN: probes that would run under the blackhole:"
  echo "    pytest tests/"
  echo "    hf-audit"
  echo "    security_scan.sh"
  echo "    claude_mem_local.py recall"
  echo "    curl localhost:8000/v1/models"
  echo "    curl localhost:8001/v1/models"
  echo "    curl localhost:8002/api/v1/heartbeat"
  echo "    crews/security_review.py /tmp/sample.diff (if present)"
  echo
  echo "    rules that would apply:"
  echo "      iptables -I OUTPUT 1 -o lo -j ACCEPT"
  echo "      iptables -I OUTPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"
  echo "      iptables -A OUTPUT -j REJECT --reject-with icmp-net-unreachable"
  exit 0
fi

apply_rules
run_smoke
restore_rules

echo
echo "==> Summary"
echo "    PASS: $probes_pass"
echo "    FAIL: $probes_fail"
if [[ $probes_fail -gt 0 ]]; then
  echo
  echo "Last 40 lines of probe log:"
  tail -n 40 "$LOG"
  echo
  echo "RESULT: stack is NOT fully airgap-safe — $probes_fail probe(s) failed under blackhole."
  exit 1
fi
echo
echo "RESULT: stack survived a full kernel-level egress blackhole. Airgap-ready."
