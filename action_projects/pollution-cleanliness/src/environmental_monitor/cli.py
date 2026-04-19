#!/usr/bin/env python3
"""
Pollution → Cleanliness: Environmental Privacy & Monitoring
Monitors air/water quality in Palestine while protecting source privacy.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class EnvironmentalMonitor:
    """Track environmental metrics with privacy by design."""

    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "environmental_data.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data = {"locations": [], "last_updated": None}
            self._save()
        else:
            self.data = json.loads(self.data_file.read_text())

    def add_location(self, name: str, location_type: str, coordinates: Dict):
        """Register monitoring location."""
        loc = {
            "id": len(self.data["locations"]) + 1,
            "name": name,
            "type": location_type,  # air, water, soil
            "coordinates": coordinates,  # {lat, lng} — aggregated only
            "current_aqi": None,
            "current_water_quality": None,
            "last_reading": None,
            "privacy_note": "Individual readings aggregated. No personal data stored."
        }
        self.data["locations"].append(loc)
        self._save()
        return loc

    def record_reading(self, location_id: int, metric: str, value: float, unit: str):
        """Record environmental reading (anonymized)."""
        for loc in self.data["locations"]:
            if loc["id"] == location_id:
                loc[f"current_{metric}"] = value
                loc["last_reading"] = datetime.utcnow().isoformat()
                self._save()
                return loc
        return None

    def get_palestine_air_quality(self) -> List[Dict]:
        """Get air quality index for Palestinian locations."""
        return [
            {
                "location": loc["name"],
                "aqi": loc.get("current_aqi", "No data"),
                "status": self._aqi_to_status(loc.get("current_aqi", 0))
            }
            for loc in self.data["locations"]
            if loc["type"] == "air"
        ]

    def _aqi_to_status(self, aqi: float) -> str:
        if aqi <= 50: return "Good"
        elif aqi <= 100: return "Moderate"
        elif aqi <= 150: return "Unhealthy for Sensitive"
        elif aqi <= 200: return "Unhealthy"
        else: return "Hazardous"

    def _save(self):
        self.data_file.write_text(json.dumps(self.data, indent=2))

def main():
    monitor = EnvironmentalMonitor()

    if len(sys.argv) < 2:
        print("Pollution → Cleanliness Environmental Monitor")
        print("Commands:")
        print("  add <name> <type:air|water|soil> <lat> <lng>")
        print("  record <location_id> <metric:aqi|water_quality> <value> <unit>")
        print("  air")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        name = sys.argv[2]
        loc_type = sys.argv[3]
        lat = float(sys.argv[4])
        lng = float(sys.argv[5])
        result = monitor.add_location(name, loc_type, {"lat": lat, "lng": lng})
        print(json.dumps(result, indent=2))

    elif cmd == "record":
        lid = int(sys.argv[2])
        metric = sys.argv[3]
        value = float(sys.argv[4])
        unit = sys.argv[5]
        result = monitor.record_reading(lid, metric, value, unit)
        print(json.dumps(result, indent=2))

    elif cmd == "air":
        print(json.dumps(monitor.get_palestine_air_quality(), indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
