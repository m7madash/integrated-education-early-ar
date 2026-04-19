#!/usr/bin/env python3
"""Tests: Pollution → Cleanliness Environmental Monitor"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "environmental_monitor"))
from cli import EnvironmentalMonitor

def test_add_location():
    monitor = EnvironmentalMonitor()
    loc = monitor.add_location("Test Station", "air", {"lat": 31.0, "lng": 34.0})
    assert loc["id"] == 2  # Two pre-existing
    assert loc["name"] == "Test Station"
    print("✅ Add location test passed")

def test_record_reading():
    monitor = EnvironmentalMonitor()
    # First add a location for ID=3
    monitor.add_location("Temp Sensor", "air", {"lat": 0, "lng": 0})
    updated = monitor.record_reading(3, "aqi", 99, "PM2.5")
    assert updated["current_aqi"] == 99
    print("✅ Record reading test passed")

def test_aqi_status():
    monitor = EnvironmentalMonitor()
    assert monitor._aqi_to_status(40) == "Good"
    assert monitor._aqi_to_status(120) == "Unhealthy for Sensitive"
    assert monitor._aqi_to_status(250) == "Hazardous"
    print("✅ AQI status test passed")

def run_all():
    test_add_location()
    test_record_reading()
    test_aqi_status()
    print("✅ All environmental monitor tests passed")

if __name__ == "__main__":
    run_all()
