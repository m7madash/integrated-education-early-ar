#!/usr/bin/env python3
"""
Resource Justice — Command Line Interface
Usage:
  resource-justice collect [--country <name>]
  resource-justice calculate --country <name> --percent <N>
  resource-justice serve [--port <N>]
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resource_justice.collector import collect_sample_data, fetch_live_budget
from resource_justice.calculator import calculate_impact

def main():
    parser = argparse.ArgumentParser(description="Resource Justice CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # collect
    collect_parser = subparsers.add_parser("collect", help="Collect budget data")
    collect_parser.add_argument("--country", type=str, help="Country name")
    collect_parser.add_argument("--live", action="store_true", help="Fetch live data (requires API keys)")

    # calculate
    calc_parser = subparsers.add_parser("calculate", help="Calculate reallocation impact")
    calc_parser.add_argument("--country", type=str, required=True, help="Country name")
    calc_parser.add_argument("--percent", type=float, required=True, help="Percent to reallocate (0-100)")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start Flask API server")
    serve_parser.add_argument("--port", type=int, default=5000, help="Port number")

    args = parser.parse_args()

    if args.command == "collect":
        if args.live:
            print("🔁 Fetching live data... (not implemented yet)")
            fetch_live_budget(args.country)
        else:
            print("✅ Using sample data...")
            collect_sample_data()
        print("✅ Data collection complete.")

    elif args.command == "calculate":
        result = calculate_impact(args.country, args.percent)
        print(f"\n📊 Impact for {args.country} (reallocating {args.percent}% of military budget):")
        print(f"   🍛 Meals provided: {result['meals']:,.0f}")
        print(f"   🏫 Schools built: {result['schools']:,.0f}")
        print(f"   💊 People covered by healthcare: {result['healthcare_people']:,.0f}")
        print(f"   ❤️  Lives saved (estimated): {result['lives_saved']:,.0f}")

    elif args.command == "serve":
        print(f"🚀 Starting Resource Justice API on port {args.port}...")
        from resource_justice.api import app
        app.run(host="0.0.0.0", port=args.port, debug=True)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
