#!/usr/bin/env python3
"""Extremism Moderation CLI — Detect, respond, teach middle-path."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from moderation_engine.detector import ExtremismDetector, TextSample
from moderation_engine.responder import ModerationResponder
from moderation_engine.knowledge import EXTREMISM_TYPES, get_extremism_info
from moderation_engine.principles import MIDDLE_PATH_PRINCIPLES, get_principle

def main():
    detector = ExtremismDetector()
    responder = ModerationResponder()

    print("\n" + "="*70)
    print("🛡️ Extremism → Moderation: Counter-Radicalization Tool")
    print("   Mission: Promote wasatiyyah, reject ghuluww (extremism)")
    print("="*70 + "\n")

    while True:
        print("خيارات:")
        print("  1. فحص نص (detect extremism level)")
        print("  2. اقتراح رد (moderate response to extreme text)")
        print("  3. عرض مبادئ الوسطية (Quran/Hadith)")
        print("  4. أنواع التطرف (knowledge base)")
        print("  5. خروج")

        choice = input("\nاختر (1-5): ").strip()

        if choice == "1":
            print("\nأدخل النص للفحص:")
            text = input("> ").strip()
            if not text:
                continue
            result = detector.score_text(text)
            print(f"\n🔍 النتيجة:")
            print(f"   Score: {result['score']}/100")
            print(f"   Verdict: {result['verdict']}")
            print(f"   Matched terms: {result['term_count']}")
            if result['matched_terms']:
                print("   Terms:")
                for mt in result['matched_terms'][:5]:
                    print(f"     • {mt['term']} (weight: {mt['weight']})")

        elif choice == "2":
            print("\nأدخل النص المتطرف:")
            text = input("> ").strip()
            if not text:
                continue
            result = detector.score_text(text)
            response = responder.craft_response(text, result['score'])
            action = responder.suggest_platform_action(result['score'])
            print(f"\n💡 الرد المقترح:")
            print(f"   {response}")
            print(f"\n🔧 إجراء المنصة: {action}")

        elif choice == "3":
            print("\nمبادئ الوسطية (Wasatiyyah) من القرآن والسنة:")
            for key, p in MIDDLE_PATH_PRINCIPLES.items():
                print(f"\n  {p['title']} ({key}):")
                print(f"   {p['arabic_text']}")
                print(f"   {p['source_type']} {p['reference']}: {p['principle']}")

        elif choice == "4":
            print("\nأنواع التطرف:")
            for key, info in EXTREMISM_TYPES.items():
                print(f"\n  {info['name']} ({key}):")
                print(f"    {info['description']}")
                print(f"    Indicators: {', '.join(info['indicators'][:3])}...")

        elif choice == "5":
            print("\nمع السلامة. تذكّر: الوسطية ديانة.")
            break

        else:
            print("اختر 1-5")

if __name__ == "__main__":
    main()
