#!/usr/bin/env python3
"""
nuclear_disruptor_cli — Command-line interface for Cyber Disruptor tool

Usage:
  nuclear-disruptor --action centrifuges --method cascade_imbalance
  nuclear-disruptor --action coolant --mode pump_disable
  nuclear-disruptor --action sensors --spoof enriched_level
  nuclear-disruptor --action full
  nuclear-disruptor --demo  (run full demo simulation)

All actions run in simulation mode only. No real facilities affected.
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulator import build_default_facility, simulate_operation
from disruptor import (
    disrupt_centrifuges,
    disrupt_coolant,
    disrupt_sensors,
    full_disruption
)

def run_demo():
    """Run full demonstration"""
    print("=" * 60)
    print("NUCLEAR CYBER DISRUPTOR — DEMO")
    print("=" * 60)

    print("\n[1] Building nuclear facility (100 centrifuges, 1 cascade)...")
    fac = build_default_facility("DemoFac-001", n_centrifuges=100)

    print("[2] Normal operation for 1 simulated hour...")
    simulate_operation(fac, hours=1.0)
    print(f"    Enriched uranium: {fac.enriched_uranium_kg:.3f} kg")
    running_before = sum(1 for c in fac.centrifuge_array if c.status == "running")
    print(f"    Centrifuges running: {running_before}/100")

    print("\n[3] CYBER ATTACK: Cascade imbalance + coolant disable + sensor spoof...")
    result = full_disruption(fac)
    print(f"    Status: {result['final_status']}")
    print(f"    Methods: {', '.join(result['methods_used'])}")

    print("\n[4] POST-ATTACK STATUS:")
    report = fac.status_report()
    print(f"    Centrifuges running: {report['centrifuges_running']}/{report['total_centrifuges']}")
    print(f"    Enriched uranium: {report['enriched_uranium_kg']:.3f} kg (production halted)")
    print(f"    Coolant temp: {report['coolant_temp']} °C")
    print(f"    Sensors compromised: {report['sensor_compromised']}")

    print("\n" + "=" * 60)
    print("RESULT: Facility disabled without physical destruction.")
    print("No civilian harm. Zero lethal force. Pure disruption.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="Nuclear Cyber Disruptor — Nonviolent Disruption Toolkit (SIMULATION ONLY)"
    )
    parser.add_argument("--action", choices=["centrifuges", "coolant", "sensors", "full"],
                        help="Type of disruption to execute")
    parser.add_argument("--method", default="cascade_imbalance",
                        help="Method for centrifuges action (default: cascade_imbalance)")
    parser.add_argument("--mode", default="pump_disable",
                        help="Mode for coolant action (default: pump_disable)")
    parser.add_argument("--spoof", default="enriched_level",
                        help="Spoof type for sensors (default: enriched_level)")
    parser.add_argument("--demo", action="store_true",
                        help="Run full demo simulation and exit")

    args = parser.parse_args()

    if args.demo:
        run_demo()
        return 0

    # Build facility
    print("[*] Building nuclear facility simulation (100 centrifuges)...")
    fac = build_default_facility("OpFac-001", n_centrifuges=100)

    # Run 1 hour normal first
    simulate_operation(fac, hours=1.0)
    running_before = sum(1 for c in fac.centrifuge_array if c.status == "running")
    enriched_before = fac.enriched_uranium_kg
    print(f"    [Before] Running: {running_before}/100, Enriched: {enriched_before:.3f} kg")

    # Execute requested action
    if args.action == "centrifuges":
        print(f"[*] Disrupting centrifuges: {args.method}...")
        result = disrupt_centrifuges(fac, method=args.method)
    elif args.action == "coolant":
        print(f"[*] Disrupting coolant: {args.mode}...")
        result = disrupt_coolant(fac, mode=args.mode)
    elif args.action == "sensors":
        print(f"[*] Spoofing sensors: {args.spoof}...")
        result = disrupt_sensors(fac, spoof_type=args.spoof)
    elif args.action == "full":
        print("[*] Executing full disruption sequence...")
        result = full_disruption(fac)
    else:
        parser.print_help()
        return 1

    # Report
    print(f"    [After] {result['message']}")
    running_after = sum(1 for c in fac.centrifuge_array if c.status == "running")
    enriched_after = fac.enriched_uranium_kg
    print(f"    Status: centrifuges running={running_after}/100, enriched={enriched_after:.3f} kg")

    print("\n✅ Simulation complete. Real-world use requires UN authorization.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
