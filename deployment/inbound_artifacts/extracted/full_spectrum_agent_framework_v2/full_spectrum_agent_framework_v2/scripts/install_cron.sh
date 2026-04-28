#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_FILE="$ROOT/cron/evez.crontab"

if ! command -v crontab >/dev/null 2>&1; then
  echo "crontab not found on this system"
  exit 1
fi

TMP_FILE="$(mktemp)"
if crontab -l >/dev/null 2>&1; then
  crontab -l > "$TMP_FILE"
fi

grep -v "full_spectrum_agent_framework_v2" "$TMP_FILE" > "${TMP_FILE}.clean" || true

{
  cat "${TMP_FILE}.clean"
  echo ""
  echo "# full_spectrum_agent_framework_v2"
  sed "s|__ROOT__|$ROOT|g" "$CRON_FILE"
} | crontab -

rm -f "$TMP_FILE" "${TMP_FILE}.clean"
echo "Installed cron jobs from $CRON_FILE"
crontab -l
