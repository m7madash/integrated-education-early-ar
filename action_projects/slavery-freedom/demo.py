"""
Slavery → Freedom — Interactive demo

Shows detection workflow on sample cases.
Run: python3 demo.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from slavery_detector.detector import SlaveryDetector
from slavery_detector.knowledge import get_local_resources, format_emergency_contacts

def main():
    detector = SlaveryDetector()

    print("=" * 70)
    print("🔍 SLAVERY → FREEDOM DETECTOR — DEMO")
    print("=" * 70)

    samples = [
        {
            "title": "Domestic worker ad (Saudi Arabia)",
            "text": "أبحث عن خادمة منزلية. يجب أن تكون شابة (22-28 سنة)، بدون أطفال. الراتب 1500 ريال، السكن مجاني. لا حاجة لتأشيرة. دوام من 6 صباحاً حتى 11 مساءً، إجازة واحدة في الشهر.",
            "country": "SA",
            "city": "Riyadh"
        },
        {
            "title": "Forced fishing labor (Indonesia)",
            "text": "العمال يعملون 18 ساعة يومياً. الأجور لا تدفع. جوازات السفر عند الكابتن. لا يوجد هاتف. الديون تتراكم.",
            "country": "ID",
            "city": "Jakarta"
        },
        {
            "title": "Scam farm (Myanmar)",
            "text": "يجب تنفيذ 200 عملية احتيال يومياً. إذا فشلت، ضرب. الزملاء الذين يفشلون يختفون. لا يمكنك مغادرة المبنى.",
            "country": "MM",
            "city": "Myawaddy"
        },
        {
            "title": "Normal job ad (control)",
            "text": "نبحث عن مسؤول تسويق ذو خبرة. راتب 15000 درهم + عمولات. أوفيس في دبي. ترحيب بجميع الجنسيات.",
            "country": "AE",
            "city": "Dubai"
        }
    ]

    for i, sample in enumerate(samples, 1):
        print(f"\n{'='*70}")
        print(f"📌 Test {i}: {sample['title']}")
        print(f"   Location: {sample['city']}, {sample['country']}")
        print(f"   Text: {sample['text'][:120]}...\n")

        result = detector.analyze(sample['text'], country_code=sample['country'], city=sample['city'])

        print(f"⚖️  Risk Level: {result['risk_level']}")
        print(f"📊 Indicators found: {result['indicators_count']}")
        if result['indicators']:
            print("🔍 Matched indicators:")
            for ind in result['indicators']:
                print(f"   • {ind}")
        if result['action_recommended']:
            print("⚠️   → ACTION NEEDED")
        else:
            print("ℹ️   → Monitor only")
        print(f"📞 Emergency contacts: {', '.join(result['emergency_contacts'][:2])}")
        print()

    print("=" * 70)
    print("📋 Emergency Contacts Reference (all regions):")
    print(format_emergency_contacts())

    print("\n✅ Demo complete. Run CLI: python3 src/slavery_detector/cli.py scan 'text' --country SA")

if __name__ == "__main__":
    main()
