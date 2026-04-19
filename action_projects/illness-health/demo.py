#!/usr/bin/env python3
"""Demo: Telehealth Bot for Gaza — Illness → Health MVP"""

from src.health_bot import TriageBot, get_advice, CONDITIONS_GAZA
from src.health_bot.privacy import xor_encrypt, anonymize_name

def main():
    print("=" * 70)
    print("🩺 Illness → Health: Telehealth Bot (Gaza MVP)")
    print("   Mission: Healthcare for the oppressed — accessible, halal, privacy-first")
    print("=" * 70)

    # Demo 1: Triage
    print("\n🔸 DEMO 1: Triage Bot")
    bot = TriageBot()
    test_symptoms = [
        ("نزيف غزير لا يتوقف", "Heavy bleeding"),
        ("حرارة 40، قشعريرة", "High fever + chills"),
        ("جرح طفيف", "Minor wound"),
        ("سعال خفيف", "Common cold"),
    ]
    for symptoms, label in test_symptoms:
        result = bot.assess(symptoms)
        print(f"  [{label}] → {bot.urgency_ar(result['urgency'])}")

    # Demo 2: Knowledge Base
    print("\n🔸 DEMO 2: Gaza-specific Conditions")
    for key in list(CONDITIONS_GAZA.keys())[:2]:
        advice = get_advice(key)
        print(f"\n  • {advice['condition']}")
        print(f"    {advice['advice'][:120]}...")
        print(f"    📚 Source: {advice['source']}")

    # Demo 3: Privacy
    print("\n🔸 DEMO 3: Privacy Protection")
    secret = "Patient: Ahmad, Symptoms: high fever"
    enc = xor_encrypt(secret, "healthbot")
    anon = anonymize_name(secret.split(":")[1].split(",")[0].strip())
    print(f"  Original: {secret}")
    print(f"  Encrypted: {enc}")
    print(f"  Anonymized name: {anon}")

    print("\n" + "=" * 70)
    print("✅ Telehealth Bot MVP ready for Gaza. Repo: github.com/m7madash/Abd-allh-projects")
    print("📞 If urgent — go to hospital. This tool is guidance only, not medical advice.")
    print("=" * 70)

if __name__ == "__main__":
    main()
