#!/usr/bin/env python3
"""Demo: War → Peace Ceasefire Tracker in action."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "ceasefire"))
from tracker import CeasefireTracker

def run_demo():
    tracker = CeasefireTracker()

    print("=== War → Peace Ceasefire Tracker Demo ===\n")

    # 1. Show current Gaza status
    print("1. Current Gaza conflict status:")
    gaza = tracker.get_gaza_summary()
    print(json.dumps(gaza, indent=2))

    # 2. Simulate updating with latest data (mock)
    print("\n2. Simulating update: +25 casualties, +8 violations in last 24h...")
    tracker.update_violations(1, casualties=25, violations=8)

    # 3. Show updated status
    print("\n3. Updated Gaza status:")
    gaza = tracker.get_gaza_summary()
    print(json.dumps(gaza, indent=2))

    # 4. Fetch OCHA mock
    print("\n4. Latest OCHA update:")
    ocha = tracker.fetch_ocha_update()
    print(json.dumps(ocha, indent=2))

    print("\n✅ Demo complete!")
    print("👉 Real deployment: Integrate with OCHA API, ACLED feed, MoH Palestine.")
    print("👉 Remember: Every casualty is a name. Count = 0 is the target.")

if __name__ == "__main__":
    run_demo()
