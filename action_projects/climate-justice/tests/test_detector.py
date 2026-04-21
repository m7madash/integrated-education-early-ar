#!/usr/bin/env python3
"""Tests for Climate Justice modules."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from climate_justice.water import WaterJustice, RegionWater
from climate_justice.energy import EnergyPoverty, RegionEnergy
from climate_justice.refugees import ClimateRefugees, DisplacementEvent
from climate_justice.detector import ClimateDetector

def test_water_scarcity():
    wj = Water Justice()
    gaza = next(r for r in wj.regions if r.name == "Gaza Strip")
    assert gaza.is_scarce()
    assert gaza.injustice_score() > 50
    print("✅ Water scarcity detection works")

def test_energy_poverty():
    ep = EnergyPoverty()
    rwanda = next(r for r in ep.regions if r.name == "Rwanda")
    assert rwanda.is_energy_poor()
    assert rwanda.energy_injustice_score() > 50
    print("✅ Energy poverty detection works")

def test_refugees_tracking():
    cr = ClimateRefugees()
    gaza_events = cr.get_events_by_region("Gaza Strip")
    assert len(gaza_events) >= 1
    total = cr.total_displaced("Gaza Strip")
    assert total > 0
    assessment = cr.needs_assessment("Gaza Strip")
    assert "total_displaced" in assessment
    print(f"✅ Climate refugees tracking works (Gaza: {total:,} displaced)")

def test_full_detector():
    detector = ClimateDetector()
    result = detector.assess_region("Gaza Strip")
    assert "overall_injustice_score" in result
    assert result["severity_level"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    assert "recommendations" in result
    print(f"✅ Full detector: Gaza score = {result['overall_injustice_score']}/100 — {result['severity_level']}")

if __name__ == "__main__":
    print("=== Climate Justice Tests ===\n")
    test_water_scarcity()
    test_energy_poverty()
    test_refugees_tracking()
    test_full_detector()
    print("\n🎉 All Climate Justice tests passed!")
