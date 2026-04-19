#!/usr/bin/env python3
"""Tests for illness-health triage bot."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.health_bot import TriageBot

def test_heavy_bleeding():
    bot = TriageBot()
    result = bot.assess("نزيف غزير لا يتوقف")
    assert result['urgency'] == bot.URGENT, f"Expected urgent, got {result['urgency']}"
    print("✅ Heavy bleeding → URGENT")

def test_chest_pain():
    bot = TriageBot()
    result = bot.assess("ألم في الصدر وضيق تنفس")
    assert result['urgency'] == bot.URGENT
    print("✅ Chest pain → URGENT")

def test_severe_infection():
    bot = TriageBot()
    result = bot.assess("حرارة 40، قشعريرة")
    assert result['urgency'] == bot.URGENT_SOON
    print("✅ Severe infection → URGENT_SOON")

def test_dehydration():
    bot = TriageBot()
    result = bot.assess("عطش شديد، دوار، التبول قليل")
    assert result['urgency'] == bot.URGENT_SOON
    print("✅ Dehydration → URGENT_SOON")

def test_minor_wound():
    bot = TriageBot()
    result = bot.assess("جرح طفيف، ينزف قليلاً")
    assert result['urgency'] == bot.ROUTINE
    print("✅ Minor wound → ROUTINE")

def test_common_cold():
    bot = TriageBot()
    result = bot.assess("سعال خفيف، سيلان الأنف")
    assert result['urgency'] == bot.SELF_CARE
    print("✅ Common cold → SELF_CARE")

def test_unknown_symptoms():
    bot = TriageBot()
    result = bot.assess("صداع نصفي")
    assert result['urgency'] == bot.ROUTINE
    print("✅ Unknown symptoms → ROUTINE (safe default)")

if __name__ == "__main__":
    print("=== Illness-Health Tests ===\n")
    test_heavy_bleeding()
    test_chest_pain()
    test_severe_infection()
    test_dehydration()
    test_minor_wound()
    test_common_cold()
    test_unknown_symptoms()
    print("\n✅ All 7 tests passed!")
