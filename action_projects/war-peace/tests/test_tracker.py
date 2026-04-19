#!/usr/bin/env python3
"""Tests: War → Peace Ceasefire Tracker"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "ceasefire"))
from tracker import CeasefireTracker

def test_add_conflict():
    tracker = CeasefireTracker()
    conflict = tracker.add_conflict("Test War", "Test Location", ["SideA", "SideB"])
    assert conflict["id"] == 2  # Gaza already exists with ID 1
    assert conflict["name"] == "Test War"
    print("✅ Add conflict test passed")

def test_update_violations():
    tracker = CeasefireTracker()
    updated = tracker.update_violations(1, casualties=50, violations=5)
    assert updated["casualties_last_24h"] == 50
    print("✅ Update violations test passed")

def test_gaza_summary():
    tracker = CeasefireTracker()
    summary = tracker.get_gaza_summary()
    assert "conflict" in summary
    assert "casualties_24h" in summary
    print("✅ Gaza summary test passed")

def run_all():
    test_add_conflict()
    test_update_violations()
    test_gaza_summary()
    print("✅ All ceasefire tests passed")

if __name__ == "__main__":
    run_all()
