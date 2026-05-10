#!/usr/bin/env bash
set -e
export RESTIC_REPOSITORY="${RESTIC_REPOSITORY:-/mnt/nas/restic-ai-stack}"
export RESTIC_PASSWORD_FILE="${RESTIC_PASSWORD_FILE:-$HOME/.restic-password}"

restic backup \
  "$HOME/offline-ai-stack/memory" \
  "$HOME/offline-ai-stack/forgejo" \
  "$HOME/offline-ai-stack/projects" \
  "$HOME/offline-ai-stack/reports" \
  "$HOME/offline-ai-stack/crews" \
  /var/lib/docker/volumes/open-webui \
  --tag daily

restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
