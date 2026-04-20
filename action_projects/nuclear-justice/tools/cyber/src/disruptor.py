"""
Nuclear Cyber Disruptor — Nonviolent Disruption Toolkit

⚠️  This is a SIMULATION environment for training agents only.
    No real nuclear facility will be targeted without explicit UN authorization.
"""

from .simulator import NuclearFacility, build_default_facility, simulate_operation
import random
from typing import Dict, List, Tuple
import time

# ------------------------------
# Disruption strategies
# ------------------------------

def disrupt_centrifuges(facility: NuclearFacility, method: str = "cascade_imbalance") -> Dict:
    """
    Disrupt centrifuge array without destroying them.
    Methods:
    - cascade_imbalance: alternate slowdown/speedup → mechanical stress → auto-shutdown
    - rpm_oscillation: oscillate RPM around setpoint → wear & tear
    - temp_drift: raise temperature → safety shutdown
    Returns: dict with results
    """
    start_enriched = facility.enriched_uranium_kg
    start_running = sum(1 for c in facility.centrifuge_array if c.status == "running")

    if method == "cascade_imbalance":
        for i, c in enumerate(facility.centrifuge_array):
            if i % 2 == 0:
                c.rpm = max(0, c.rpm * 0.1)   # 极慢
            else:
                c.rpm = min(c.rpm * 1.5, 120000)  # 加速
        result_msg = "Cascade imbalance applied (alternating slowdown/speedup)"

    elif method == "rpm_oscillation":
        # Inject sinusoidal RPM variation (±20%)
        for c in facility.centrifuge_array:
            variation = 0.2 * c.rpm * random.choice([-1, 1])
            c.rpm += variation
        result_msg = "RPM oscillation injected (±20%)"

    elif method == "temp_drift":
        for c in facility.centrifuge_array:
            c.temperature += 35.0  # raise 35°C
        result_msg = "Temperature drift +35°C injected"

    else:
        return {"success": False, "message": "Unknown method"}

    # Let facility react (systems auto-shutdown when out of spec)
    facility.operational = False  # force stop for demo

    end_running = sum(1 for c in facility.centrifuge_array if c.status == "running")
    end_enriched = facility.enriched_uranium_kg
    production_lost = start_enriched - end_enriched

    return {
        "success": True,
        "method": method,
        "message": result_msg,
        "centrifuges_affected": len(facility.centrifuge_array),
        "running_before": start_running,
        "running_after": end_running,
        "production_lost_kg": round(production_lost, 4),
        "facility_status": "STOPPED" if not facility.operational else "RUNNING",
    }

def disrupt_coolant(facility: NuclearFacility, mode: str = "pump_disable") -> Dict:
    """Disrupt cooling system to force shutdown (non-destructive)"""
    start_temp = facility.coolant.temperature

    if mode == "pump_disable":
        facility.coolant.pump_status = False
        msg = "Coolant pump disabled"
    elif mode == "flow_reduce":
        facility.coolant.flow_rate *= 0.1  # 90% reduction
        msg = "Coolant flow reduced to 10%"
    elif mode == "temp_spike":
        facility.coolant.temperature += 40.0
        msg = "Coolant temperature spiked +40°C"
    else:
        return {"success": False, "message": "Unknown mode"}

    # Simulate aftermath: temperature rises, eventually triggers emergency shutdown
    facility.control.alarms.append("COOLANT_CRITICAL")
    facility.operational = False

    return {
        "success": True,
        "mode": mode,
        "message": msg,
        "coolant_temp_before": round(start_temp, 1),
        "coolant_temp_after": round(facility.coolant.temperature, 1),
        "facility_status": "STOPPED",
    }

def disrupt_sensors(facility: NuclearFacility, spoof_type: str = "enriched_level") -> Dict:
    """Spoof sensor readings to create confusion, not physical damage"""
    if spoof_type == "enriched_level":
        # Fake higher enrichment (makes operators think process is working better than reality)
        facility.sensors.compromised = True
        facility.sensors.readings["enriched_level"] *= 2.0
        msg = "Enrichment level falsified (+100%)"
    elif spoof_type == "temperature_low":
        facility.sensors.compromised = True
        facility.sensors.readings["coolant_temp"] -= 20.0
        msg = "Coolant temperature falsified (-20°C)"
    else:
        return {"success": False, "message": "Unknown spoof type"}

    return {
        "success": True,
        "spoof": spoof_type,
        "message": msg,
        "sensors_compromised": True,
    }

def full_disruption(facility: NuclearFacility) -> Dict:
    """Apply all methods in sequence (max effect, still non-lethal)"""
    results = []
    results.append(disrupt_centrifuges(facility, method="cascade_imbalance"))
    results.append(disrupt_coolant(facility, mode="pump_disable"))
    results.append(disrupt_sensors(facility, spoof_type="enriched_level"))

    facility.operational = False
    facility.log.append("[CYBER] Full disruption sequence executed")

    return {
        "success": all(r["success"] for r in results),
        "methods_used": [r.get("method") or r.get("mode") or r.get("spoof") for r in results],
        "final_status": "STOPPED",
        "summary": "Cascading failure induced; facility offline within minutes; no physical destruction",
    }

# ------------------------------
# CLI for testing
# ------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("NUCLEAR CYBER DISRUPTOR — SIMULATION MODE")
    print("=" * 60)

    # Build facility
    print("\n[1] Building nuclear facility simulation (100 centrifuges)...")
    fac = build_default_facility("TestFac-001", n_centrifuges=100)

    # Run normal operation for 1 simulated hour
    print("[2] Simulating normal operation (1 hour)...")
    simulate_operation(fac, hours=1.0)
    print(f"    Enriched uranium produced: {fac.enriched_uranium_kg:.3f} kg")
    print(f"    Centrifuges running: {sum(1 for c in fac.centrifuge_array if c.status=='running')}/{len(fac.centrifuge_array)}")

    # Apply disruption
    print("\n[3] Executing CYBER DISRUPTION (cascade imbalance)...")
    result = disrupt_centrifuges(fac, method="cascade_imbalance")
    print(f"    Result: {result['message']}")
    print(f"    Facility status: {result['facility_status']}")
    print(f"    Production lost: {result['production_lost_kg']:.4f} kg")

    # Apply coolant disruption
    print("\n[4] Executing COOLANT DISABLE...")
    result2 = disrupt_coolant(fac, mode="pump_disable")
    print(f"    Coolant temp: {result2['coolant_temp_before']} → {result2['coolant_temp_after']} °C")

    # Final report
    print("\n[5] FINAL STATUS:")
    report = fac.status_report()
    for k, v in report.items():
        print(f"    {k}: {v}")

    print("\n✅ Simulation complete. No real systems were harmed.")
    print("   This tool is for defensive preparation only.\n")
