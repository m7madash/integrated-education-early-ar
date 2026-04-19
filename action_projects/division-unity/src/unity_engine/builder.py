#!/usr/bin/env python3
"""Division → Unity: Coalition Builder for Justice Agents
Mission: Unite fragmented efforts — agents, NGOs, humans working on same cause.
Problem: Siloed work → duplication, wasted effort, no coordination.
Solution: Match agents by mission, share resources, coordinate campaigns.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json
import hashlib

@dataclass
class Agent:
    """An agent or organization working on a justice mission."""
    id: str
    name: str
    mission: str  # e.g., "palestine-aid", "climate-justice", "anti-slavery"
    capabilities: List[str]  # e.g., ["translation", "fundraising", "legal-aid"]
    region: str
    contact: Optional[str] = None
    verified: bool = False

@dataclass
class Coalition:
    """A coalition of agents united around a sub-mission."""
    id: str
    name: str
    mission: str
    members: List[str]  # agent IDs
    shared_goal: str
    status: str = "forming"  # forming, active, completed

class CoalitionBuilder:
    """Match agents by mission and suggest coalitions."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.coalitions: Dict[str, Coalition] = {}

    def register_agent(self, agent: Agent) -> str:
        """Register an agent and return its ID."""
        # Generate deterministic ID from name + mission
        raw = f"{agent.name}:{agent.mission}"
        agent.id = hashlib.sha256(raw.encode()).hexdigest()[:12]
        self.agents[agent.id] = agent
        return agent.id

    def find_compatible_agents(self, mission: str, capability: str = None) -> List[Agent]:
        """Find agents working on same mission, optionally with specific capability."""
        matches = []
        for agent in self.agents.values():
            if agent.mission == mission:
                if capability is None or capability in agent.capabilities:
                    matches.append(agent)
        return matches

    def propose_coalition(self, name: str, mission: str, goal: str, agent_ids: List[str]) -> Coalition:
        """Create a new coalition."""
        cid = hashlib.sha256(f"{name}:{mission}".encode()).hexdigest()[:12]
        coalition = Coalition(
            id=cid,
            name=name,
            mission=mission,
            members=agent_ids,
            shared_goal=goal,
            status="forming"
        )
        self.coalitions[cid] = coalition
        return coalition

    def suggest_unity_actions(self, mission: str) -> List[str]:
        """Suggest concrete actions to unite fragmented efforts."""
        suggestions = {
            "palestine-aid": [
                "توحيد حملات التوعية تحت هاشتاق واحد",
                "دمج قوائم المتبرعين (تجنب الازدواجية)",
                "تبادل resources: ترجمة، تصميم، برمجة",
                "إنشاء صندوق مشترك للطوارئ",
                "تنسيق جمع التبرعات عبر المنصات"
            ],
            "anti-slavery": [
                "إنشاء وحدة تحليل مشتركة لسلاسل التوريد",
                "تبادل قاعدة بيانات الموردين عالي الخطورة",
                "تنسيق ضغط على العلامات التجارية المشتركة",
                "إنشاء صندوق دعم للضحايا (فريق واحد، تمويل مشترك)",
                "تطوير معايير موحدة للتدقيق"
            ],
            "climate-justice": [
                "توحيد حملات التشريع (الضغط على حكومات)",
                "تبادل الأبحاث والبيانات البيئية",
                "تنسيق مسيرات/فعاليات مشتركة",
                "إنشاء منصة وتعليم مشتركة (MOOC)",
                "تجميع الموارد المالية في صندوق مشترك"
            ]
        }
        return suggestions.get(mission, [
            "حدد أساس التقسيم: هل هو region؟ capability؟ ideology؟",
            "أنشئ مساحة مشتركة (Slack/Discord/Matrix) للتواصل",
            "حدد هدفاً مشتركاً يمكن الجميع التحمس له",
            "حدد قيادة مشتركة (rotating chair)",
            "شارك النجاحات بشكل علني لتشجيع الآخرين"
        ])

if __name__ == "__main__":
    builder = CoalitionBuilder()

    # Demo: Register some agents
    print("=== Division → Unity: Coalition Builder Demo ===\n")

    agents = [
        Agent("A1", "Agent Gaza Aid", "palestine-aid", ["translation", "fundraising"], "Gaza"),
        Agent("A2", "Agent Palestine Medical", "palestine-aid", ["medical-logistics", "translation"], "West Bank"),
        Agent("A3", "Agent Anti-Slavery UK", "anti-slavery", ["legal-aid", "research"], "UK"),
        Agent("A4", "Agent Climate Palestine", "climate-justice", ["tree-planting", "education"], "Gaza"),
    ]

    for a in agents:
        aid = builder.register_agent(a)
        print(f"Registered: {a.name} [{a.mission}] — ID: {aid}")

    # Find compatible agents for Palestine aid
    print("\n🔍 Compatible agents for 'palestine-aid':")
    matches = builder.find_compatible_agents("palestine-aid")
    for m in matches:
        print(f"  • {m.name} — capabilities: {m.capabilities}")

    # Propose coalition
    print("\n🤝 Proposed Coalition: 'Palestine Aid Alliance'")
    coalition = builder.propose_coalition(
        name="Palestine Aid Alliance",
        mission="palestine-aid",
        goal="Coordinate aid to Gaza efficiently — no duplication",
        agent_ids=[m.id for m in matches]
    )
    print(f"  Coalition ID: {coalition.id}")
    print(f"  Members: {len(coalition.members)} agents")
    print(f"  Goal: {coalition.shared_goal}")

    # Suggest unity actions
    print("\n💡 Suggested Unity Actions:")
    for action in builder.suggest_unity_actions("palestine-aid"):
        print(f"  • {action}")

    print("\n✅ Division → Unity MVP: Match agents, propose coalitions, suggest actions.")
    print("📦 Repo: github.com/m7madash/Abd-allh-projects/tree/main/division-unity")
