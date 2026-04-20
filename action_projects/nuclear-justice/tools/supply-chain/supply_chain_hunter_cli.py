#!/usr/bin/env python3
"""
Supply Chain Hunter CLI — Tool 3 of Nuclear Justice (Fixed)

Usage:
  schunter --demo                    # Full pipeline with sample data
  schunter --step tracker --output network.json
  schunter --step analyzer --input network.json --output analysis.json
  schunter --step disruptor --input analysis.json --output campaign.md
"""

import argparse, sys, os, json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tracker.network_mapper import SupplyChainTracker
from analyzer.pattern_detector import SupplyChainAnalyzer
from disruptor.campaign_planner import build_disruption_campaign, SupplyChainDisruptor

def run_demo():
    """Full pipeline with embedded sample data."""
    print("=" * 60)
    print("SUPPLY CHAIN HUNTER — Tool 3 DEMO (Fixed)")
    print("=" * 60)

    # Tracker
    print("\n[1] Tracker — building sample nuclear procurement network...")
    tracker = SupplyChainTracker()
    tracker.add_entity("ABC Trading LLC", "UAE", "distributor", risk=8)
    tracker.add_entity("XYZ Industries", "China", "manufacturer", risk=9)
    tracker.add_entity("Front Co Ltd", "Turkey", "front_company", risk=10)
    tracker.add_entity("Oceanic Shipping", "Malaysia", "shipping_agent", risk=6)
    tracker.add_entity("Dr. Ahmad Vahidi", "Iran", "individual", risk=9)

    tracker.add_shipment("TRK001", "China", "UAE", "CNC milling machines (dual-use)",
                         hs_code="8459", quantity=2, date_str="2025-03-10",
                         carrier="Oceanic Shipping", status="delivered")
    tracker.add_shipment("TRK002", "UAE", "Turkey", "High-strength aluminum alloy plates",
                         hs_code="7606", quantity=5000, date_str="2025-03-20",
                         carrier="Oceanic Shipping", status="in_transit")

    tracker.add_connection("ABC Trading LLC", "Front Co Ltd", "supplies", 8)
    tracker.add_connection("XYZ Industries", "ABC Trading LLC", "sells_to", 9)
    tracker.add_connection("Front Co Ltd", "Dr. Ahmad Vahidi", "controlled_by", 7)

    net_out = "demo_network.json"
    tracker.save(Path(net_out))
    print(f"    Saved: {net_out}  ({len(tracker.entities)} entities, {len(tracker.shipments)} shipments)")

    # Analyzer
    print("\n[2] Analyzer — computing chokepoints and suspicious routes...")
    with open(net_out) as f:
        network_data = json.load(f)
    analyzer = SupplyChainAnalyzer(network_data)
    report = analyzer.analyze()

    ch = report["chokepoints"]
    sr = report["suspicious_routes"]
    tp = report["timing_patterns"]

    print(f"    Chokepoints: {len(ch)}  (critical: {sum(1 for c in ch if c['risk_level']=='critical')})")
    for c in ch[:3]:
        print(f"      • {c['entity_name']} — centrality {c['centrality']:.2f}, risk: {c['risk_level']}")
    print(f"    Suspicious routes: {len(sr)}")
    print(f"    Timing patterns: {len(tp)}")

    analysis_out = "demo_analysis.json"
    Path(analysis_out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"    Saved: {analysis_out}")

    # Disruptor
    print("\n[3] Disruptor — designing nonviolent intervention campaign...")
    disruptor = build_disruption_campaign(
        Path(analysis_out),
        output_md="demo_campaign_plan.md",
        output_json="demo_campaign.json"
    )
    print(f"    Campaign plan: demo_campaign_plan.md")
    print(f"    Campaign JSON: demo_campaign.json")
    print(f"    Interventions: {len(disruptor.interventions)}")

    print("\n" + "=" * 60)
    print("✅ Tool 3 demo complete.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Supply Chain Hunter — Tool 3 of Nuclear Justice")
    parser.add_argument("--demo", action="store_true", help="Run full demo pipeline")
    parser.add_argument("--step", choices=["tracker", "analyzer", "disruptor"], help="Run single step")
    parser.add_argument("--input", help="Input file (JSON)")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return 0

    if not args.step:
        parser.print_help()
        return 1

    if args.step == "tracker":
        if not args.output:
            print("❌ --output required for tracker step")
            return 1
        tracker = SupplyChainTracker()
        tracker.save(Path(args.output))
        print(f"✅ Empty network template saved: {args.output}")
        return 0

    elif args.step == "analyzer":
        if not args.input or not args.output:
            print("❌ --input and --output required for analyzer step")
            return 1
        with open(args.input) as f:
            data = json.load(f)
        analyzer = SupplyChainAnalyzer(data)
        analyzer.save_report(Path(args.output))
        print(f"✅ Analysis report saved: {args.output}")
        return 0

    elif args.step == "disruptor":
        if not args.input or not args.output:
            print("❌ --input and --output required for disruptor step")
            return 1
        out_path = Path(args.output)
        if out_path.suffix == ".md":
            build_disruption_campaign(Path(args.input), args.output, args.output.replace(".md", ".json"))
        else:
            data = json.loads(Path(args.input).read_text())
            disruptor = SupplyChainDisruptor(data)
            disruptor.design_campaign()
            disruptor.save_json(out_path)
        print(f"✅ Campaign generated: {args.output}")
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
