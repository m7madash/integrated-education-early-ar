#!/usr/bin/env python3
"""Division → Unity: Coalition Builder CLI"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unity_engine.builder import CoalitionBuilder, Agent
from unity_engine.actions import get_unity_actions

def main():
    builder = CoalitionBuilder()

    print("\n" + "="*70)
    print("🤝 Division → Unity: Coalition Builder")
    print("   Mission: Unite fragmented justice efforts into coordinated coalitions")
    print("="*70 + "\n")

    while True:
        print("خيارات:")
        print("  1. تسجيل وكيل (agent) جديد")
        print("  2. البحث عن وكلاء متوافقين")
        print("  3. إنشاء تحالف (coalition)")
        print("  4. عرض خطوات الوحدة لمشكلة")
        print("  5. خروج")

        choice = input("\nاختر (1-5): ").strip()

        if choice == "1":
            print("\n--- تسجيل وكيل جديد ---")
            name = input("اسم الوكيل/المنظمة: ").strip()
            mission = input("المهمة (palestine-aid, anti-slavery, climate-justice, إلخ): ").strip()
            caps = input("القدرات (مفصولة بفاصلة: translation,fundraising,legal-aid): ").strip()
            region = input("المنطقة (Gaza, West Bank, UK, إلخ): ").strip()
            agent = Agent(
                id="",
                name=name,
                mission=mission,
                capabilities=[c.strip() for c in caps.split(",") if c.strip()],
                region=region,
                verified=False
            )
            aid = builder.register_agent(agent)
            print(f"✅ تم التسجيل! ID: {aid}")

        elif choice == "2":
            mission = input("\nالمهمة للبحث: ").strip()
            capability = input("القدرة المطلوبة (Enter for all): ").strip() or None
            matches = builder.find_compatible_agents(mission, capability)
            print(f"\n🔍 الوكلاء المتوافقون مع '{mission}':")
            for m in matches:
                print(f"  • {m.name} [{m.region}] — {', '.join(m.capabilities)}")
            print(f"  المجموع: {len(matches)}")

        elif choice == "3":
            name = input("\nاسم التحالف: ").strip()
            mission = input("المهمة: ").strip()
            goal = input("الهدف المشترك: ").strip()
            # Get agent IDs from compatible agents
            matches = builder.find_compatible_agents(mission)
            if not matches:
                print("  ❌ لا يوجد وكلاء متوافقين — سجل وكلاء أولاً")
                continue
            print("  الوكلاء المتوفرون:")
            for i, m in enumerate(matches):
                print(f"    {i+1}. {m.name}")
            selected = input("  أدخل أرقاء الوكلاء (مفصولة بفاصلة): ").strip()
            try:
                indices = [int(x)-1 for x in selected.split(",")]
                Agent_ids = [matches[i].id for i in indices]
            except:
                print("  ❌ خطأ في الاختيار")
                continue
            coalition = builder.propose_coalition(name, mission, goal, agent_ids)
            print(f"✅ تم إنشاء التحالف! ID: {coalition.id}")
            print(f"   الأعضاء: {len(coalition.members)}")
            print(f"   الهدف: {coalition.shared_goal}")

        elif choice == "4":
            print("\nأنواع الانقسامات:")
            print("  1. طائفي (sectarian)")
            print("  2. سياسي (political)")
            print("  3. إقليمي (regional)")
            dtype = input("\nاختر النوع (1-3): ").strip()
            mapping = {"1": "sectarian", "2": "political", "3": "regional"}
            division = mapping.get(dtype, "sectarian")
            actions = get_unity_actions(division)
            print(f"\n💡 خطوات الوحدة ({division}):")
            for a in actions:
                print(f"  • {a}")

        elif choice == "5":
            print("\nمع السلامة. الوحدة تبدأ بخطوة صغيرة. 🤝")
            break

        else:
            print("اختر 1-5")

if __name__ == "__main__":
    main()
