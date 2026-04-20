#!/usr/bin/env python3
"""
Fajr Observer Agent — Main Entry Point

Command-line interface for the Fajr Observer system.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from decision.fajr_engine import FajrEngine

def main():
    parser = argparse.ArgumentParser(
        description="Fajr Observer — detect true dawn via camera + AI"
    )
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--tz", default="Asia/Gaza", help="Timezone (e.g. Asia/Gaza)")
    parser.add_argument("--dry-run", action="store_true", help="No Adhan sound/notifications")
    parser.add_argument("--test", action="store_true", help="Run unit tests and exit")
    args = parser.parse_args()

    if args.test:
        import subprocess
        print("Running integration tests...")
        result = subprocess.run([sys.executable, "tests/test_integration.py"])
        sys.exit(result.returncode)

    # Run the observer engine
    engine = FajrEngine(
        latitude=args.lat,
        longitude=args.lon,
        timezone=args.tz,
        dry_run=args.dry_run
    )
    try:
        engine.run_observation_window()
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
        engine.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
