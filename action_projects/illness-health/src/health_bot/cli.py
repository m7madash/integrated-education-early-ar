#!/usr/bin/env python3
"""Health Bot CLI — Triage + Guidance + Privacy (Halal healthcare only)"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from health_bot.triage import TriageBot
from health_bot.knowledge import get_advice, CONDITIONS_GAZA

def main():
    bot = TriageBot()

    print("\n" + "="*60)
    print("🩺 Telehealth Bot — Gaza Focus")
    print("⚠️  تنويه: هذه الأداة إرشادية فقط — لا تغني عن الطبيب")
    print("="*60 + "\n")

    while True:
        print("خيارات:")
        print("  1. تقييم الأعراض (تصنيف)")
        print("  2. البحث عن حالة مرضية")
        print("  3. قائمة الأمراض الشائعة في غزة")
        print("  4. خروج")
        choice = input("\nاختر (1-4): ").strip()

        if choice == "1":
            symptoms = input("\nصف الأعراض (عربي/English): ").strip()
            if not symptoms:
                continue
            result = bot.assess(symptoms)
            print(f"\n🔸 الدرجة: {bot.urgency_ar(result['urgency'])}")
            print(f"🔸 النصيحة: {result['advice']}")
            if result['matched_conditions']:
                print(f"🔸 الأمراض المحتملة: {', '.join(result['matched_conditions'])}")

        elif choice == "2":
            print("\nالأمراض المتاحة:")
            for key in CONDITIONS_GAZA:
                print(f"  • {key}")
            cond = input("\nاكتب اسم الحالة: ").strip().lower()
            if cond in CONDITIONS_GAZA:
                advice = get_advice(cond)
                print(f"\n📋 {advice['condition']}")
                print(f"   {advice['advice']}")
                print(f"   📚 المصدر: {advice['source']}")
            else:
                print("  الحالة غير موجودة. استخدم 'قائمة الأمراض الشائعة'.")

        elif choice == "3":
            print("\nالأمراض الشائعة في غزة:")
            for key, cond in CONDITIONS_GAZA.items():
                print(f"  • {cond['name']} ({key})")

        elif choice == "4":
            print("\nمع السلامة! اعتن بصحتك 🩺")
            break
        else:
            print("اختر 1-4")

if __name__ == "__main__":
    main()
