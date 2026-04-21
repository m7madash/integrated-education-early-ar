#!/usr/bin/env python3
"""
CLI for Slavery → Freedom detector.

Usage:
    slavery-detector scan "text here" --country SA
    slavery-detector resources --country PS
    slavery-detector report --risk HIGH --city Gaza
    slavery-detector demo
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from slavery_detector.detector import SlaveryDetector
from slavery_detector.knowledge import get_local_resources, format_emergency_contacts
from slavery_detector.privacy import PrivacyShield, generate_report_html

def cmd_scan(args):
    detector = SlaveryDetector()
    result = detector.analyze(args.text, country_code=args.country, city=args.city)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_resources(args):
    resources = get_local_resources(args.country)
    print(f"# Resources for {args.country}\n")
    print("## Hotlines")
    for h in resources.get("hotlines", []):
        print(f"- **{h['name']}**: {h.get('phone','N/A')} | {h.get('website','')}")
    print("\n## NGOs")
    for ngo in resources.get("ngos", []):
        print(f"- **{ngo['name']}**: {ngo.get('phone','N/A')} — {ngo.get('location','')}")
    print("\n## Legal Frameworks")
    for law in resources.get("legal_framework", []):
        print(f"- {law}")

def cmd_report(args):
    detector = SlaveryDetector()
    analysis = detector.analyze(args.text, country_code=args.country, city=args.city)
    report = detector.generate_safe_report(analysis, victim_consent=args.consent)
    if args.html:
        html = generate_report_html(analysis)
        print(html)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

def cmd_demo(args):
    detector = SlaveryDetector()
    samples = [
        ("Job ad — domestic worker, SA", "تبحث عن خادمة منزلية. يجب أن تكون شابة، بدون أطفال. الراتب 1500 ريال، السكن مجاني. لا حاجة لتأشيرة.", "SA", "Riyadh"),
        ("Forced fishing labor", "العمال يعملون 18 ساعة، الأجور لا تدفع، جوازاتterdam محفوظة.", "ID", "Jakarta"),
        ("Suspicious online job", "اربح 5000 دولار أسبوعياً من المنزل — لا خبرة مطلوبة. أصدر 300 تحويل يومياً.", "MY", "Kuala Lumpur"),
        ("Normal job ad (control)", "نبحث عن مسؤول تسويق. خبرة سنتين. راتب تنافسي. أوفيس في دبي.", "AE", "Dubai")
    ]
    print("🎯 Slavery Freedom Detector — Demo\n")
    for title, text, country, city in samples:
        print(f"\n{'='*60}")
        print(f"📌 {title}")
        print(f"   Text: {text[:80]}...")
        result = detector.analyze(text, country_code=country, city=city)
        print(f"   Risk: {result['risk_level']} | Indicators: {result['indicators_count']}")
        if result['action_recommended']:
            print("   ⚠️  ACTION NEEDED")
        else:
            print("   ℹ️  Monitor only")

def main():
    parser = argparse.ArgumentParser(description="Slavery → Freedom detector CLI")
    sub = parser.add_subcommands

    # The argparse SubParsers workaround for Python 3.8+
    # We'll do it manually to avoid mypy/style issues

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    command = sys.argv[1]

    if command == "scan":
        p = argparse.ArgumentParser()
        p.add_argument("text", help="Text to scan for indicators")
        p.add_argument("--country", default="PS", help="ISO country code (default: PS)")
        p.add_argument("--city", default="unknown", help="City name")
        args = p.parse_args(sys.argv[2:])
        cmd_scan(args)

    elif command == "resources":
        p = argparse.ArgumentParser()
        p.add_argument("--country", default="PS", help="ISO country code")
        args = p.parse_args(sys.argv[2:])
        cmd_resources(args)

    elif command == "report":
        p = argparse.ArgumentParser()
        p.add_argument("text", help="Text to analyze then encrypt as report")
        p.add_argument("--country", default="PS")
        p.add_argument("--city", default="unknown")
        p.add_argument("--consent", action="store_true", help="Victim consents to identification")
        p.add_argument("--html", action="store_true", help="Output human-readable HTML report")
        args = p.parse_args(sys.argv[2:])
        cmd_report(args)

    elif command == "demo":
        cmd_demo(None)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
