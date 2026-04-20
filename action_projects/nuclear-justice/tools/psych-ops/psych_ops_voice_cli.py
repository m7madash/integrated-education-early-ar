#!/usr/bin/env python3
"""
Psych Ops Voice CLI — Tool 4 of Nuclear Justice

Nonviolent psychological influence campaigns against nuclear decision-makers.

Pipeline:
  1. Targeting — profile high-influence individuals from sanctions lists
  2. Messenger — generate tailored messages (legacy, family, religion, science)
  3. Channels — plan dissemination (social, email, press, open letters)

Usage:
  psychops --demo [--sanctions FILE]   # Run full demo
  psychops --targets --input sanctions.json --output targets.json
  psychops --messages --input targets.json --output messages.json
  psychops --plan --input messages.json --output plan.json
"""

import argparse, sys, os, json
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from targeting.profiler import TargetProfiler
from messenger.generator import MessageGenerator
from channels.manager import ChannelManager

def run_demo(sanctions_path: str = None):
    print("=" * 60)
    print("PSYCH OPS VOICE — Tool 4 DEMO")
    print("Nonviolent psychological influence campaign builder")
    print("=" * 60)

    # Use Tool 2 demo sanctions if none provided
    if not sanctions_path:
        sanctions_path = "/root/.openclaw/workspace/action_projects/nuclear-justice/tools/legal/demo_sanctions.json"
        if not Path(sanctions_path).exists():
            print("⚠️  Sanctions demo not found — using minimal inline data")
            return

    # Step 1: Targeting
    print("\n[1] Profiling high-influence targets from sanctions list...")
    profiler = TargetProfiler()
    profiler.load_from_sanctions(Path(sanctions_path))
    high_priority = profiler.prioritize(min_influence=7)
    print(f"    High-priority targets: {len(high_priority)}")
    for t in high_priority[:5]:
        print(f"      • {t.name} — influence {t.influence_score}/10")
    profiles_out = "demo_target_profiles.json"
    Path(profiles_out).write_text(
        json.dumps(profiler.generate_profiles(high_priority), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"    Profiles saved: {profiles_out}")

    # Step 2: Messenger
    print("\n[2] Generating tailored messages per target...")
    messenger = MessageGenerator()
    messages = []
    for target in high_priority[:3]:  # sample first 3
        for theme in ["legacy", "family", "religion", "international_community"]:
            msg = messenger.generate(target.known_values, theme=theme)
            if msg:
                customized = messenger.customize_message(msg, target.name, target.title)
                messages.append({
                    "target": target.name,
                    "theme": msg.theme,
                    "tone": msg.tone,
                    "content": customized,
                    "impact": msg.expected_impact
                })
    print(f"    Messages generated: {len(messages)}")
    msgs_out = "demo_messages.json"
    Path(msgs_out).write_text(json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"    Messages saved: {msgs_out}")

    # Step 3: Channels (dry-run delivery plan)
    print("\n[3] Planning dissemination channels (dry-run)...")
    channels_mgr = ChannelManager(dry_run=True)
    plan = []
    sample_target = high_priority[0] if high_priority else None
    if sample_target:
        for ch in ["social_media", "email", "press_release", "open_letter"]:
            record = channels_mgr.send("demo_message", sample_target, ch)
            plan.append(asdict(record))
    print(f"    Delivery plan entries: {len(plan)}")
    plan_out = "demo_delivery_plan.json"
    Path(plan_out).write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"    Plan saved: {plan_out}")

    # Full campaign log
    log_out = "demo_campaign_log.json"
    channels_mgr.save_history(Path(log_out))
    print(f"    Campaign log: {log_out}")

    print("\n" + "=" * 60)
    print("✅ Psych Ops Voice demo complete.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Psych Ops Voice — Tool 4 of Nuclear Justice")
    parser.add_argument("--demo", action="store_true", help="Run full demo pipeline")
    parser.add_argument("--sanctions", help="Path to sanctions JSON (for demo)")
    parser.add_argument("--targets", action="store_true", help="Generate target profiles")
    parser.add_argument("--messages", action="store_true", help="Generate messages")
    parser.add_argument("--plan", action="store_true", help="Plan delivery channels")
    parser.add_argument("--input", help="Input JSON file")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    if args.demo:
        run_demo(args.sanctions)
        return 0

    if args.targets:
        if not args.input or not args.output:
            print("❌ --input (sanctions.json) and --output required")
            return 1
        profiler = TargetProfiler().load_from_sanctions(Path(args.input))
        targets = profiler.prioritize()
        Path(args.output).write_text(
            json.dumps(profiler.generate_profiles(targets), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"✅ Target profiles saved: {args.output}")
        return 0

    if args.messages:
        if not args.input or not args.output:
            print("❌ --input (targets.json) and --output required")
            return 1
        # Not implemented in this stub
        print("⚠️  Message generation from targets not fully implemented yet")
        return 0

    if args.plan:
        if not args.input or not args.output:
            print("❌ --input (messages.json) and --output required")
            return 1
        # Not implemented
        print("⚠️  Channel planning stub")
        return 0

    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
