#!/usr/bin/env python3
"""Slavery Detector CLI — Investigate supply chain red flags."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from slavery_detector.detector import SlaveryDetector, Supplier
from slavery_detector.knowledge import SLAVERY_TYPES, get_type_info
from slavery_detector.privacy import anonymize_id, encrypt_report, redact_pii

def main():
    detector = SlaveryDetector()

    print("\n" + "="*70)
    print("⚖️ Slavery → Freedom: Modern Slavery Detector")
    print("   Mission: End forced labor, human trafficking, debt bondage")
    print("="*70 + "\n")

    while True:
        print("خيارات التحقيق:")
        print("  1. تقييم مورد (supplier assessment)")
        print("  2. عرض أنواع العبودية الحديثة")
        print("  3. تحقق من علم (privacy demo)")
        print("  4. خروج")

        choice = input("\nاختر (1-4): ").strip()

        if choice == "1":
            print("\n--- أدخل بيانات المورد ---")
            name = input("اسم المورد/المصنع: ").strip()
            country = input("رمز البلد (مثال: BD, PK, PS): ").strip().upper()
            industry = input("الصناعة (garment, agriculture, mining): ").strip()
            workers = int(input("عدد العمال: ").strip() or 100)
            hours = float(input("متوسط ساعات العمل/أسبوع: ").strip() or "40")
            wage = float(input("متوسط الأجر/شهر (USD): ").strip() or "100")
            contracts = input("هل هناك عقود مكتوبة؟ (y/n): ").strip().lower() == 'y'
            union = input("هل العمال منظمون في نقابة؟ (y/n): ").strip().lower() == 'y'

            supplier = Supplier(
                id=f"SUP-{hash(name)%10000}",
                name=name,
                country=country,
                industry=industry,
                workers=workers,
                avg_hours_per_week=hours,
                average_wage=wage,
                has_contracts=contracts,
                unionized=union,
                audit_date=None
            )

            result = detector.assess_supplier(supplier)
            print(f"\n🔍 النتيجة: {result['verdict']}")
            print(f"📊 Risk Score: {result['risk_score']}/20")
            print(f"📝 Recommendation: {result['recommendation']}")

            if result['flags']:
                print("\n⚠️  Red Flags Detected:")
                for flag in result['flags']:
                    print(f"  • {flag['flag']}: {flag['description']}")
                    print(f"    Detail: {flag['detail']}")

            # Privacy wrap
            anon_id = anonymize_id(supplier.id)
            print(f"\n🔒 Report ID (encrypted): {anon_id}")

        elif choice == "2":
            print("\n⌨️ أنواع العبودية الحديثة:")
            for key, info in SLAVERY_TYPES.items():
                print(f"\n  {info['name']} ({key}):")
                print(f"    {info['description']}")
                print(f"    Globally: {info['global_estimate']}")

        elif choice == "3":
            print("\n🔐 Privacy Demo:")
            report = "Supplier: Factory X, 70 hrs/week, no contracts, wages withheld — CRITICAL"
            enc = encrypt_report(report, "investigator-key")
            redacted = redact_pii(report)
            print(f"  Original: {report}")
            print(f"  Encrypted: {enc[:60]}...")
            print(f"  Redacted: {redacted}")
            print("  ✅ Privacy tools working")

        elif choice == "4":
            print("\nمع السلامة. القتال ضد العبودية يستمر. 🕊️")
            break

        else:
            print("اختر 1-4")

if __name__ == "__main__":
    main()
