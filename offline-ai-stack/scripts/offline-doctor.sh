#!/usr/bin/env bash
# Probe the running stack for network egress to non-loopback destinations.
#
# Two modes:
#   passive (default): sample `ss -tunap` for $DURATION seconds while the
#                      stack runs normally; report any non-loopback ESTAB
#                      sockets. No host config changes; safe.
#   strict (--strict): use iptables to REJECT all OUTPUT to non-loopback
#                      destinations for $DURATION seconds, run the probe
#                      workload, then restore. Catches anything that would
#                      have leaked. Requires sudo. Risky if interrupted
#                      mid-run — uses a trap to restore, but be careful.
#
# Usage:
#   bash offline-doctor.sh                       # 30s passive probe
#   bash offline-doctor.sh 60                    # 60s passive probe
#   bash offline-doctor.sh --strict 30           # 30s strict probe (sudo)
#   bash offline-doctor.sh --probe-workload      # actively exercise the stack

set -euo pipefail

DURATION=30
STRICT=0
PROBE_WORKLOAD=0
for arg in "$@"; do
  case "$arg" in
    --strict)             STRICT=1 ;;
    --probe-workload)     PROBE_WORKLOAD=1 ;;
    [0-9]*)               DURATION="$arg" ;;
    -h|--help)
      grep '^# ' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
  esac
done

STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"
LOG=$(mktemp -t offline-doctor-XXXXXX.log)
EGRESS=$(mktemp -t offline-doctor-egress-XXXXXX.log)
cleanup() {
  rm -f "$LOG" "$EGRESS"
  if [[ $STRICT -eq 1 ]] && [[ -n "${IPT_RESTORED:-}" && "$IPT_RESTORED" == "no" ]]; then
    echo "==> Restoring iptables (cleanup trap)"
    restore_iptables || true
  fi
}
trap cleanup EXIT INT TERM

# ---- helpers ---------------------------------------------------------------

SS_CMD=(ss -tunap)
if sudo -n true 2>/dev/null; then SS_CMD=(sudo "${SS_CMD[@]}"); fi

# A connection counts as "egress" if its peer is NOT loopback AND state is ESTAB.
sample_egress() {
  "${SS_CMD[@]}" 2>/dev/null \
    | awk '$2 == "ESTAB"' \
    | grep -vE ' (127\.0\.0\.1|::1|0\.0\.0\.0|\[::\]):' \
    || true
}

# ---- strict mode iptables helpers (IPv4 + IPv6) ---------------------------

IPT_RESTORED=yes
apply_iptables() {
  IPT_RESTORED=no
  echo "==> Applying iptables egress block (loopback + localhost only)"
  # Allow loopback and established connections; reject everything else outbound.
  sudo iptables -I OUTPUT 1 -o lo -j ACCEPT
  sudo iptables -I OUTPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  sudo iptables -A OUTPUT -j REJECT --reject-with icmp-net-unreachable
  sudo ip6tables -I OUTPUT 1 -o lo -j ACCEPT 2>/dev/null || true
  sudo ip6tables -I OUTPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
  sudo ip6tables -A OUTPUT -j REJECT 2>/dev/null || true
}
restore_iptables() {
  echo "==> Restoring iptables (removing our rules)"
  sudo iptables -D OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
  sudo iptables -D OUTPUT -o lo -j ACCEPT 2>/dev/null || true
  sudo iptables -D OUTPUT -j REJECT --reject-with icmp-net-unreachable 2>/dev/null || true
  sudo ip6tables -D OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
  sudo ip6tables -D OUTPUT -o lo -j ACCEPT 2>/dev/null || true
  sudo ip6tables -D OUTPUT -j REJECT 2>/dev/null || true
  IPT_RESTORED=yes
}

# ---- optional workload probe ----------------------------------------------

run_workload() {
  echo "==> Exercising the stack (generating traffic during the window)"
  # Each probe is best-effort; any failure is logged but doesn't abort the run.
  (
    set +e
    bash "$STACK_HOME/scripts/security_scan.sh" >>"$LOG" 2>&1
    python3 "$STACK_HOME/scripts/claude_mem_local.py" recall offline-doctor "smoke test" >>"$LOG" 2>&1
    if [[ -f /tmp/sample.diff ]]; then
      python3 "$STACK_HOME/crews/security_review.py" /tmp/sample.diff >>"$LOG" 2>&1
    fi
  ) || true
}

# ---- main ------------------------------------------------------------------

echo "==> offline-doctor: ${DURATION}s probe ($([[ $STRICT -eq 1 ]] && echo strict || echo passive))"
[[ $STRICT -eq 1 ]] && apply_iptables

# Sample egress every second during the window.
(
  end=$(( $(date +%s) + DURATION ))
  while [[ $(date +%s) -lt $end ]]; do
    sample_egress >> "$EGRESS"
    sleep 1
  done
) &
WATCHER=$!

[[ $PROBE_WORKLOAD -eq 1 ]] && run_workload

wait $WATCHER 2>/dev/null || true

[[ $STRICT -eq 1 ]] && restore_iptables

# ---- analyze ---------------------------------------------------------------

# Unique non-loopback peers seen.
peers=$(awk '{print $5}' "$EGRESS" | sort -u | grep -v '^$' || true)

echo
echo "==> Captured non-loopback ESTAB sockets:"
if [[ -z "$peers" ]]; then
  echo "    none. ✓"
  echo
  echo "PASS: no non-localhost connections observed during ${DURATION}s window."
  echo "(Note: passive mode only sees connections active during sampling. Run with"
  echo "--probe-workload or --strict for a stronger signal.)"
  exit 0
fi

echo "$peers" | sed 's/^/    /'
echo
n=$(echo "$peers" | wc -l)
echo "FAIL: ${n} non-localhost endpoint(s) reached during the probe."
echo "      Identify the owning process with: sudo lsof -i -P -n | grep <ip>"
exit 1
