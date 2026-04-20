#!/bin/bash
# Run Fajr Observer Agent
# Usage: ./scripts/run_observer.sh [--dry-run] [--lat 21.5] [--lon 39.0]

cd "$(dirname "$0")/.."

DRY_RUN=true
LATITUDE=21.5
LONGITUDE=39.0
TIMEZONE="Asia/Gaza"

while [[ $# -gt 0 ]]; do
  case $1 in
    --live) DRY_RUN=false ;;
    --lat) LATITUDE="$2"; shift ;;
    --lon) LONGITUDE="$2"; shift ;;
    --tz) TIMEZONE="$2"; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
  shift
done

# Activate venv if exists
if [ -d "venv" ]; then
  source venv/bin/activate
fi

echo "=== Fajr Observer Agent Starting ==="
echo "Mode: ${DRY_RUN:-(dry-run)}"
echo "Location: $LATITUDE, $LONGITUDE ($TIMEZONE)"
echo "Time: $(date)"
echo ""

python3 -m src.decision.fajr_engine \
  --latitude "$LATITUDE" \
  --longitude "$LONGITUDE" \
  --timezone "$TIMEZONE" \
  ${DRY_RUN:+--dry-run}
