#!/usr/bin/env python3
"""Demo: Pollution → Cleanliness Environmental Monitor in action."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "environmental_monitor"))
from cli import EnvironmentalMonitor

def run_demo():
    monitor = EnvironmentalMonitor()

    print("=== Pollution → Cleanliness Environmental Monitor Demo ===\n")

    # 1. Show registered locations
    print("1. Registered monitoring locations:")
    for loc in monitor.data["locations"]:
        print(f"   📍 {loc['name']} ({loc['type']})")
        if loc.get("current_aqi"):
            print(f"      AQI: {loc['current_aqi']} — {monitor._aqi_to_status(loc['current_aqi'])}")
        if loc.get("current_water_quality"):
            print(f"      Water Quality Index: {loc['current_water_quality']}")
        print(f"      Last reading: {loc['last_reading']}")
        print()

    # 2. Get air quality summary
    print("2. Palestine Air Quality Summary:")
    air_data = monitor.get_palestine_air_quality()
    print(json.dumps(air_data, indent=2))

    # 3. Demonstrate adding new location
    print("\n3. Adding new monitoring station (Rafah — Air)...")
    new_loc = monitor.add_location(
        "Rafah Air Quality",
        "air",
        {"lat": 31.2751, "lng": 34.2593}
    )
    print(f"   Added: {new_loc['name']} (ID: {new_loc['id']})")

    # 4. Record reading
    print("\n4. Recording AQI reading for Rafah (245 — Hazardous)...")
    monitor.record_reading(3, "aqi", 245, "PM2.5")
    print("   ✅ Reading saved")

    print("\n✅ Demo complete!")
    print("👉 Next: Integrate real-time sensors, public dashboards, alert system.")
    print("👉 Goal: Every Palestinian has right to clean air — we'll prove when it's violated.")

if __name__ == "__main__":
    run_demo()
