#!/usr/bin/env python3
"""Test priority engine"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/illness-health/src')
from health_bot.priority import PriorityEngine, HealthRequest

engine = PriorityEngine()

test_cases = [
    ("I'm having a heart attack", "CRITICAL"),
    ("My child has high fever", "URGENT"),
    ("What's good for headache?", "ROUTINE"),
    ("Tell me about healthy diet", "INFORMATIONAL"),
    ("Random question", "UNKNOWN"),
]

print("🧪 Testing Priority Engine:\n")
passed = 0
for text, expected in test_cases:
    request = HealthRequest(text=text, user_id="test")
    result = engine.assess(request)
    status = "✅" if result.name == expected else "❌"
    print(f"{status} '{text[:40]}...' → {result.name} (expected {expected})")
    if result.name == expected:
        passed += 1

print(f"\n📊 Score: {passed}/{len(test_cases)} passed")
