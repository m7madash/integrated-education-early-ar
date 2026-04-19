#!/usr/bin/env python3
"""Demo: Poverty → Dignity Skill-Sharing Platform in action."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "skill_sharing"))

from cli import SkillSharingPlatform

def run_demo():
    platform = SkillSharingPlatform()

    print("=== Poverty → Dignity: Skill-Sharing Demo ===\n")

    # 1. Register 3 agents
    print("1. Registering agents...")
    platform.register_agent(
        "health-bot",
        skills=["medical_knowledge", "triage", "arabic_nlp"],
        needs=["legal_advice", "funding"]
    )
    print("   ✅ health-bot registered (skills: medical, needs: legal)")

    platform.register_agent(
        "legal-ai-bot",
        skills=["legal_advice", "contract_review"],
        needs=["medical_consultation"]
    )
    print("   ✅ legal-ai-bot registered (skills: legal, needs: medical)")

    platform.register_agent(
        "design-agent",
        skills=["ui_design", "arabic_translation"],
        needs=["web_development"]
    )
    print("   ✅ design-agent registered (skills: design, needs: web dev)")

    # 2. Find matches
    print("\n2. Finding matches...")
    matches = platform.find_matches("health-bot")
    print(f"   health-bot needs: legal_advice, funding")
    print(f"   Matches found: {len(matches)}")
    for m in matches:
        print(f"   → {m['agent']}: {m['matching_skills']}")

    # 3. Show all agents
    print("\n3. All agents in network:")
    agents = platform.list_all_agents()
    for a in agents:
        print(f"   @{a['agent']}: OFFERS {', '.join(a['skills'])} | NEEDS {', '.join(a['needs'])}")

    print("\n✅ Demo complete!")
    print("👉 Next: Run 'python3 cli.py register <your_agent>' to join.")

if __name__ == "__main__":
    run_demo()
