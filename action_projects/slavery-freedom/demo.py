#!/usr/bin/env python3
"""Demo: Slavery → Freedom — Modern Slavery Detector MVP"""

from src.slavery_detector.detector import SlaveryDetector, Supplier
from src.slavery_detector.knowledge import SLAVERY_TYPES, get_type_info
from src.slavery_detector.privacy import anonymize_id, encrypt_report

def main():
    print("=" * 70)
    print("⚖️ Slavery → Freedom: Modern Slavery Detector MVP")
    print("   Mission: End forced labor, human trafficking, debt bondage")
    print("=" * 70)

    # Demo 1: High-risk supplier
    print("\n🔸 DEMO 1: High-Risk Supplier Assessment")
    detector = SlaveryDetector()
    risky = Supplier(
        id="SUP-BD-001", name="Dangerous Garment Factory", country="BD",
        industry="garment", workers=500, avg_hours_per_week=72,
        average_wage=65, has_contracts=False, unionized=False, audit_date=None
    )
    res = detector.assess_supplier(risky)
    print(f"Supplier: {risky.name} ({risky.country})")
    print(f"Verdict: {res['verdict']}")
    print(f"Score: {res['risk_score']}/20")
    for flag in res['flags'][:3]:
        print(f"  ⚠️  {flag['flag']}: {flag['detail']}")

    # Demo 2: Low-risk supplier
    print("\n🔸 DEMO 2: Ethical Supplier")
    ethical = Supplier(
        id="SUP-PS-001", name="Fair Trade Workshop", country="PS",
        industry="craft", workers=25, avg_hours_per_week=40,
        average_wage=450, has_contracts=True, unionized=True, audit_date="2026-03-01"
    )
    res2 = detector.assess_supplier(ethical)
    print(f"Supplier: {ethical.name} ({ethical.country})")
    print(f"Verdict: {res2['verdict']}")
    print(f"Score: {res2['risk_score']}/20 — 🟢 Safe")

    # Demo 3: Knowledge base
    print("\n🔸 DEMO 3: Modern Slavery Types (Global)")
    for key in ["forced_labor", "debt_bondage", "human_trafficking"][:2]:
        info = get_type_info(key)
        print(f"\n  {info['name']}: {info['description']}")
        print(f"  Estimate: {info['global_estimate']}")

    # Demo 4: Privacy
    print("\n🔸 DEMO 4: Victim Privacy Protection")
    victim_id = "VIC-2026-0420-001"
    anon = anonymize_id(victim_id)
    report = f"Victim {victim_id}: 70 hrs/week, no contracts (Factory BD-001)"
    enc = encrypt_report(report, "investigator-key-2026")
    print(f"  Original ID: {victim_id}")
    print(f"  Anonymized: {anon}")
    print(f"  Encrypted report: {enc[:50]}...")
    print("  Identity and evidence protected. 🔒")

    print("\n" + "=" * 70)
    print("✅ Slavery Detector MVP ready — supply chain transparency tool")
    print("📦 Repo: github.com/m7madash/Abd-allh-projects/tree/main/slavery-freedom")
    print("⚖️ Stand with the oppressed. Expose the hidden chains.")
    print("=" * 70)

if __name__ == "__main__":
    main()
