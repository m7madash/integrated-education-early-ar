#!/usr/bin/env python3
"""Demo: Division → Unity — Coalition Builder MVP"""

from src.unity_engine.builder import CoalitionBuilder, Agent
from src.unity_engine.actions import get_unity_actions

def main():
    print("=" * 70)
    print("🤝 Division → Unity: Coalition Builder MVP")
    print("   Mission: Unite fragmented justice efforts into coordinated coalitions")
    print("=" * 70)

    builder = CoalitionBuilder()

    # Demo 1: Register agents
    print("\n🔸 DEMO 1: Register Agents")
    agents = [
        Agent("A1", "Gaza Aid Network", "palestine-aid", ["translation", "fundraising"], "Gaza"),
        Agent("A2", "Medical Aid Gaza", "palestine-aid", ["medical-logistics", "translation"], "Gaza"),
        Agent("A3", "Anti-Slavery Coalition", "anti-slavery", ["legal-aid", "research"], "UK"),
        Agent("A4", "Climate Palestine", "climate-justice", ["tree-planting", "education"], "West Bank"),
    ]
    for a in agents:
        aid = builder.register_agent(a)
        print(f"  ✅ {a.name} registered — ID: {aid}")

    # Demo 2: Find compatible agents
    print("\n🔸 DEMO 2: Find Compatible Agents")
    matches = builder.find_compatible_agents("palestine-aid")
    print(f"  Agents working on 'palestine-aid': {len(matches)}")
    for m in matches:
        print(f"    • {m.name} — {', '.join(m.capabilities)}")

    # Demo 3: Create coalition
    print("\n🔸 DEMO 3: Propose Coalition")
    coalition = builder.propose_coalition(
        name="Gaza Aid Alliance",
        mission="palestine-aid",
        goal="Coordinate aid to Gaza — no duplication, max efficiency",
        agent_ids=[a.id for a in matches]
    )
    print(f"  Coalition: {coalition.name}")
    print(f"  ID: {coalition.id}")
    print(f"  Members: {len(coalition.members)} agents")
    print(f"  Status: {coalition.status}")

    # Demo 4: Unity actions
    print("\n🔸 DEMO 4: Unity Actions (How to bridge divisions)")
    for division in ["sectarian", "political", "regional"]:
        print(f"\n  {division.title()}:")
        actions = get_unity_actions(division)[:2]
        for a in actions:
            print(f"    • {a}")

    print("\n" + "=" * 70)
    print("✅ Division → Unity MVP ready — unite fragmented justice efforts")
    print("📦 Repo: github.com/m7madash/Abd-allh-projects/tree/main/division-unity")
    print("🤝 Together we are stronger. Stop silos. Start coalitions.")
    print("=" * 70)

if __name__ == "__main__":
    main()
