#!/usr/bin/env python3
"""
War → Peace: Ceasefire Tracker
Monitors active conflicts, ceasefire violations, and civilian casualties.
Data sources: UN OCHA, ACLED, Palestinian Ministry of Health
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.error

class CeasefireTracker:
    """Track ceasefire status and violations in real-time."""

    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "conflicts.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data = {"conflicts": [], "last_updated": None}
            self._save()
        else:
            self.data = json.loads(self.data_file.read_text())

    def add_conflict(self, name: str, location: str, parties: List[str]):
        """Register an active conflict zone."""
        conflict = {
            "id": len(self.data["conflicts"]) + 1,
            "name": name,
            "location": location,
            "parties": parties,
            "ceasefire_status": "active",
            " casualties_last_24h": 0,
            "violations_last_24h": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        self.data["conflicts"].append(conflict)
        self._save()
        return conflict

    def update_violations(self, conflict_id: int, casualties: int, violations: int):
        """Update ceasefire violation metrics."""
        for c in self.data["conflicts"]:
            if c["id"] == conflict_id:
                c["casualties_last_24h"] = casualties
                c["violations_last_24h"] = violations
                c["last_updated"] = datetime.utcnow().isoformat()
                self._save()
                return c
        return None

    def get_gaza_summary(self) -> Dict:
        """Get current Gaza conflict status (primary focus)."""
        gaza = next((c for c in self.data["conflicts"] if "Gaza" in c["name"]), None)
        if not gaza:
            return {"error": "Gaza conflict not registered. Add it first."}
        return {
            "conflict": gaza["name"],
            "location": gaza["location"],
            "ceasefire_active": gaza["ceasefire_status"] == "active",
            "casualties_24h": gaza["casualties_last_24h"],
            "violations_24h": gaza["violations_last_24h"],
            "status_note": "Every casualty is a name. Count = 0 is the only acceptable target."
        }

    def fetch_ocha_update(self):
        """Fetch latest from UN OCHA (simulated — implement real API later)."""
        # Placeholder — real implementation would call OCHA API
        return {
            "source": "UN OCHA oPt",
            "update_time": datetime.utcnow().isoformat(),
            "note": "Integration pending: real-time API fetch from ochaonline.org"
        }

    def _save(self):
        self.data_file.write_text(json.dumps(self.data, indent=2))

def main():
    import os
    os.chdir(Path(__file__).parent.parent)
    tracker = CeasefireTracker()

    if len(sys.argv) < 2:
        print("War → Peace Ceasefire Tracker")
        print("Commands:")
        print("  add <name> <location> <parties_comma_separated>")
        print("  update <conflict_id> <casualties> <violations>")
        print("  gaza")
        print("  ocha")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        name = sys.argv[2]
        location = sys.argv[3]
        parties = sys.argv[4].split(',')
        result = tracker.add_conflict(name, location, parties)
        print(json.dumps(result, indent=2))

    elif cmd == "update":
        cid = int(sys.argv[2])
        casualties = int(sys.argv[3])
        violations = int(sys.argv[4])
        result = tracker.update_violations(cid, casualties, violations)
        print(json.dumps(result, indent=2))

    elif cmd == "gaza":
        print(json.dumps(tracker.get_gaza_summary(), indent=2))

    elif cmd == "ocha":
        print(json.dumps(tracker.fetch_ocha_update(), indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
