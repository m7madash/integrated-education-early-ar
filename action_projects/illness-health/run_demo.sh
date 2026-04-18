#!/bin/bash
# Telehealth Bot Demo — Illness → Health

echo "🏥 Telehealth Bot — Illness → Health"
echo "======================================"

# Check dependencies
python3 -c "import yaml" 2>/dev/null || echo "Note: PyYAML not installed (optional)"

# Run triage test cases
echo -e "\n🧪 Testing priority engine..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/illness-health/src')
from health_bot.triage import HealthTriage

triage = HealthTriage()

test_cases = [
    ("I'm having a heart attack", "user1"),
    ("High fever, my child is burning up", "user2"),
    ("What's a good diet for diabetes?", "user3"),
    ("I have a mild headache", "user4"),
    ("Can't breathe, help!", "user5"),
]

for text, uid in test_cases:
    result = triage.process_request(text, uid)
    print(f"\n📝 Request: '{text}'")
    print(f"   Priority: {result['priority']} (level {result['priority_level']})")
    print(f"   Action: {result['action_plan']['action']}")
    print(f"   Response time: {result['response_time']}")
    if result['requires_human']:
        print(f"   ⚠️  ESCALATE TO HUMAN")
PYEOF

echo -e "\n✅ Demo complete!"
echo ""
echo "📂 Project: /root/.openclaw/workspace/action_projects/illness-health"
echo "🌐 Push to GitHub and test with real cases"
