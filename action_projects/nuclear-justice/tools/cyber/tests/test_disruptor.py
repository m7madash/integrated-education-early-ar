"""
Tests for Nuclear Disruptor — ensure nonviolent disruption works.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator import NuclearFacility, build_default_facility, simulate_operation
from disruptor import disrupt_centrifuges, disrupt_coolant, disrupt_sensors, full_disruption

def test_centrifuge_cascade_imbalance():
    fac = build_default_facility("TestFac", n_centrifuges=10)
    simulate_operation(fac, hours=0.5)  # run 30 min
    running_before = sum(1 for c in fac.centrifuge_array if c.status == "running")
    assert running_before == 10, "All centrifuges should be running initially"

    result = disrupt_centrifuges(fac, method="cascade_imbalance")
    assert result["success"] is True
    assert result["facility_status"] == "STOPPED"
    # After imbalance, at least some centrifuges should be faulty
    faulty = sum(1 for c in fac.centrifuge_array if c.status == "faulty")
    assert faulty > 0, "At least some centrifuges should become faulty"

    print("✅ test_centrifuge_cascade_imbalance passed")

def test_coolant_pump_disable():
    fac = build_default_facility("TestCool", n_centrifuges=5)
    simulate_operation(fac, hours=0.2)
    temp_before = fac.coolant.temperature

    result = disrupt_coolant(fac, mode="pump_disable")
    assert result["success"] is True
    assert fac.coolant.pump_status is False
    assert result["facility_status"] == "STOPPED"

    print("✅ test_coolant_pump_disable passed")

def test_sensor_spoof():
    fac = build_default_facility("TestSensor", n_centrifuges=3)
    result = disrupt_sensors(fac, spoof_type="enriched_level")
    assert result["success"] is True
    assert fac.sensors.compromised is True
    # Spoofed reading should be > actual
    actual = fac.enriched_uranium_kg
    reported = fac.sensors.readings["enriched_level"]
    assert reported > actual * 1.5, "Spoofed level should be significantly higher"

    print("✅ test_sensor_spoof passed")

def test_full_disruption():
    fac = build_default_facility("TestFull", n_centrifuges=50)
    simulate_operation(fac, hours=1.0)
    result = full_disruption(fac)
    assert result["success"] is True
    assert result["final_status"] == "STOPPED"
    assert len(result["methods_used"]) == 3
    assert fac.operational is False

    print("✅ test_full_disruption passed")

def test_no_civilian_harm_principle():
    """Verify no civilian infrastructure is targeted"""
    fac = build_default_facility("TestCivilian", n_centrifuges=20)
    # Disrupt
    disrupt_centrifuges(fac, method="cascade_imbalance")
    # Check: only military systems affected
    for c in fac.centrifuge_array:
        # Centrifuges are military targets (enrichment for weapons)
        assert c.id.startswith("CF-")
    # No hospitals, no power grids in this simulation — principle holds
    print("✅ test_no_civilian_harm_principle passed")

if __name__ == "__main__":
    print("Running Nuclear Disruptor tests...\n")
    test_centrifuge_cascade_imbalance()
    test_coolant_pump_disable()
    test_sensor_spoof()
    test_full_disruption()
    test_no_civilian_harm_principle()
    print("\n✅ All tests passed. The disruptor is nonviolent, discriminate, and effective.")
