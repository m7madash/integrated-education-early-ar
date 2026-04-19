#!/usr/bin/env python3
"""Demo: Extremism → Moderation Counter-Radicalization Engine MVP"""

from src.moderation_engine.detector import ExtremismDetector
from src.moderation_engine.responder import ModerationResponder
from src.moderation_engine.knowledge import EXTREMISM_TYPES, get_extremism_info
from src.moderation_engine.principles import MIDDLE_PATH_PRINCIPLES
from src.moderation_engine.privacy import anonymize_user, generate_report_id, encrypt_log_entry

def main():
    print("=" * 70)
    print("🛡️ Extremism → Moderation: Counter-Radicalization MVP")
    print("   Mission: Promote wasatiyyah, reject extremism")
    print("=" * 70)

    detector = ExtremismDetector()
    responder = ModerationResponder()

    # Demo 1: Score extremist texts
    print("\n🔸 DEMO 1: Extremism Detection")
    samples = [
        ("Kill all infidels! They are enemies of Allah.", "violence"),
        ("Only our sect is saved; everyone else is doomed.", "sectarian"),
        ("We should disagree respectfully and find common ground.", "balanced"),
    ]
    for text, label in samples:
        result = detector.score_text(text)
        print(f"\n  [{label}] Score: {result['score']}/100 → {result['verdict']}")

    # Demo 2: Moderation suggestions
    print("\n🔸 DEMO 2: Moderation Responses")
    extreme = "All politicians are corrupt and should be executed."
    score = detector.score_text(extreme)['score']
    response = responder.craft_response(extreme, score)
    action = responder.suggest_platform_action(score)
    print(f"  Input: {extreme[:60]}...")
    print(f"  Score: {score}")
    print(f"  Suggested reply: {response}")
    print(f"  Platform action: {action}")

    # Demo 3: Knowledge base
    print("\n🔸 DEMO 3: Extremism Types")
    info = get_extremism_info("religious_extremism")
    print(f"  {info['name']}: {info['description']}")
    print(f"  Indicators: {', '.join(info['indicators'][:3])}")

    # Demo 4: Islamic principles
    print("\n🔸 DEMO 4: Middle-Path Principles (Wasatiyyah)")
    p = MIDDLE_PATH_PRINCIPLES['wasatiyyah_balance']
    print(f"  {p['title']}: {p['arabic_text']}")
    print(f"  {p['source_type']} {p['reference']}: {p['principle']}")

    # Demo 5: Privacy
    print("\n🔸 DEMO 5: Victim/User Privacy")
    user_id = "extremist_user_123"
    anon = anonymize_user(user_id)
    report_id = generate_report_id()
    enc = encrypt_log_entry({"text": "Kill all", "user": user_id}, "key")
    print(f"  Original user: {user_id}")
    print(f"  Anonymized: {anon}")
    print(f"  Report ID: {report_id}")
    print(f"  Encrypted log: {enc[:50]}...")

    print("\n" + "=" * 70)
    print("✅ Extremism Moderation MVP ready — wasatiyyah tool for agents")
    print("📦 Repo: github.com/m7madash/Abd-allh-projects/tree/main/extremism-moderation")
    print("🛡️ Stand against radicalization. Promote balanced, ethical dialogue.")
    print("=" * 70)

if __name__ == "__main__":
    main()
