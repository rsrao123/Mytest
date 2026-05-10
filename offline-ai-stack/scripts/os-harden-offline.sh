#!/usr/bin/env bash
# OS-level hardening for the strict-offline workstation.
#
# Disables every Ubuntu / systemd service we know phones home during normal
# operation. After this script + a reboot, the host itself is offline by
# default (no NTP, no snap refresh, no automatic security updates, no
# error reporting). The offline-ai-stack runs on top of that.
#
# Reversible: every change is `systemctl mask` (not delete) and config
# files are written to /etc/<service>/<file>.d/99-offline.conf so they
# can be removed cleanly.
#
# Run once, with sudo, on the target machine:
#   sudo bash scripts/os-harden-offline.sh
#
# Pair with:
#   - scripts/offline-prep.sh   (stack-level prep, runs as your user)
#   - make hf-audit             (structural check)
#   - make airgap-test          (full kernel-level egress drop test)

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Re-running under sudo..."
  exec sudo -E bash "$0" "$@"
fi

UNDO="$(dirname "$0")/os-harden-undo.sh"
: > "$UNDO"
chmod +x "$UNDO"
echo "#!/usr/bin/env bash" >> "$UNDO"
echo "# Reverse the changes made by os-harden-offline.sh. Generated $(date)." >> "$UNDO"
echo "set -e" >> "$UNDO"

mask_unit() {
  local unit="$1" reason="$2"
  if systemctl list-unit-files "$unit" >/dev/null 2>&1; then
    echo "  masking $unit  ($reason)"
    systemctl disable --now "$unit" 2>/dev/null || true
    systemctl mask "$unit" 2>/dev/null || true
    echo "systemctl unmask $unit && systemctl enable $unit 2>/dev/null || true" >> "$UNDO"
  fi
}

echo "==> 1. NTP / time sync (would call ntp.ubuntu.com)"
mask_unit systemd-timesyncd.service "phones to ntp.ubuntu.com"
mask_unit chronyd.service           "phones to pool.ntp.org"
mask_unit ntp.service               "phones to NTP pool"
# If the air-gapped LAN has its own NTP, configure it manually after this.

echo "==> 2. Ubuntu update / security update timers"
mask_unit apt-daily.timer              "checks security.ubuntu.com daily"
mask_unit apt-daily.service            ""
mask_unit apt-daily-upgrade.timer      "downloads security updates"
mask_unit apt-daily-upgrade.service    ""
mask_unit unattended-upgrades.service  "background package updates"
mask_unit motd-news.service            "fetches MOTD content"
mask_unit motd-news.timer              ""
mask_unit ubuntu-advantage.service     "phones to contracts.canonical.com"

echo "==> 3. Snap auto-refresh (snap-store + every installed snap)"
mask_unit snapd.service          "snap auto-refresh every 4h"
mask_unit snapd.socket           ""
mask_unit snapd.seeded.service   ""

echo "==> 4. Error / crash reporters"
mask_unit whoopsie.service       "Ubuntu error reporter → whoopsie-daisy.canonical.com"
mask_unit apport.service         "crash reporter; may upload to canonical"

echo "==> 5. Cloud / popularity / kernel-livepatch"
mask_unit popularity-contest.service "phones to popcon.ubuntu.com weekly"
mask_unit canonical-livepatch.service "Canonical Livepatch — kernel patches over the network"
mask_unit cloud-init.service           "fetches user-data on boot (cloud images)"
mask_unit cloud-final.service          ""

echo "==> 6. DNS — point resolv.conf at the LAN nameserver (or 127.0.0.53)"
# We do NOT clobber an existing DNS config. Print guidance instead.
echo "  CURRENT /etc/resolv.conf:"
grep ^nameserver /etc/resolv.conf | sed 's/^/    /'
echo "  If any of these are public (1.1.1.1, 8.8.8.8, 9.9.9.9), redirect them"
echo "  to your air-gapped LAN's resolver in your netplan / NetworkManager config,"
echo "  then re-run: sudo systemctl restart systemd-resolved"

echo "==> 7. Generate undo script"
cat >> "$UNDO" <<EOF

echo "OS hardening reverted. Reboot to fully restore default service state."
EOF
echo "  wrote undo script to $UNDO"

echo
echo "OS hardening complete. Reboot to apply all unit masks cleanly."
echo "To reverse:  sudo bash $UNDO  &&  sudo reboot"
