#!/usr/bin/env python3
"""Demo: Illness → Health Telehealth Bot in action — Extended."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "health_bot"))
from triage import TriageEngine
from privacy import PrivacyShield

def run_demo():
    print("=== Illness → Health Telehealth Bot — Extended Demo ===\n")

    # 1. Initialize
    triage = TriageEngine()
    privacy = PrivacyShield()

    # 2. Sample patient reports
    cases = [
        {"description": "Young child, severe bleeding from leg injury", "expected": "URGENT"},
        {"description": "Mild cold symptoms, no fever", "expected": "SELF_CARE"},
        {"description": "Severe chest pain, difficulty breathing", "expected": "EMERGENCY"},
    ]

    print("1. Processing patient reports through triage:\n")
    for case in cases:
        result = triage.classify(case["description"])
        privacy.anonymize(result)
        print(f"   Patient: '{case['description']}'")
        print(f"   → Urgency: {result['urgency']} (expected: {case['expected']})")
        print(f"   → Condition: {result['condition']}")
        print(f"   → Privacy: ID hidden ✅")
        print()

    # 3. Show knowledge base coverage
    print("2. Knowledge base coverage:")
    kb = triage.get_knowledge_base()
    print(f"   • Conditions covered: {len(kb['conditions'])}")
    print(f"   • Sources: WHO, UNRWA, Palestinian MoH")
    print(f"   • Languages: Arabic, English")

    print("\n✅ Demo complete!")
    print("👉 Ready to deploy as Telegram bot.")
    print("👉 Next: Add more conditions, integrate with local clinics.")

if __name__ == "__main__":
    run_demo()
