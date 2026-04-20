"""
Psych Ops Voice — Tool 4 of Nuclear Justice

Nonviolent psychological influence operations against nuclear weapons
decision-makers. Creates moral dissonance, encourages reflection, promotes
disarmament through ethical messaging.

All operations:
- Lawful (no threats, no deception)
- Nonviolent (no coercion)
- Reversible (no permanent damage)
- Discriminate (targets only decision-makers, not civilians)
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
from pathlib import Path

@dataclass
class Target:
    name: str
    title: str
    country: str
    influence_score: int  # 1-10
    known_values: List[str]
    psychological_levers: List[str]
    contact_points: List[str]

class TargetProfiler:
    """Identifies and profiles high-value influence targets."""

    def __init__(self):
        self.targets: List[Target] = []

    def add_target(self, name: str, title: str, country: str,
                   influence: int, values: List[str], levers: List[str],
                   contacts: List[str] = None):
        self.targets.append(Target(name, title, country, influence, values, levers, contacts or []))

    def load_from_sanctions(self, sanctions_json: Path):
        """Seed targets from Tool 2 sanctions list (high-risk individuals)."""
        data = json.loads(sanctions_json.read_text(encoding="utf-8"))
        for p in data.get("persons", []):
            self.add_target(
                name=p["name"],
                title=p.get("title", "Government Official"),
                country=p["country"],
                influence=min(10, int(p.get("risk_score", 5))),
                values=["patriotism", "family", "legacy"],
                levers=["moral_responsibility", "historical_legacy", "fear_of_condemnation"],
                contacts=[]  # to be enriched from OSINT
            )
        return self

    def prioritize(self, min_influence: int = 7) -> List[Target]:
        return [t for t in self.targets if t.influence_score >= min_influence]

    def generate_profiles(self, targets: List[Target]) -> List[dict]:
        return [self._to_dict(t) for t in targets]

    def _to_dict(self, t: Target) -> dict:
        return {
            "name": t.name,
            "title": t.title,
            "country": t.country,
            "influence": t.influence_score,
            "values": t.known_values,
            "levers": t.psychological_levers,
            "contacts": t.contact_points,
            "recommended_channels": self._suggest_channels(t),
            "message_themes": self._suggest_themes(t)
        }

    def _suggest_channels(self, t: Target) -> List[str]:
        channels = ["press_releases", "open_letters"]
        if any("twitter" in c.lower() or "x.com" in c.lower() for c in t.contact_points):
            channels.append("social_media")
        if any("email" in c.lower() for c in t.contact_points):
            channels.append("email")
        return channels

    def _suggest_themes(self, t: Target) -> List[str]:
        themes = ["international_community"]
        if "family" in t.known_values:
            themes.append("family_legacy")
        if "religion" in t.known_values or "faith" in t.known_values:
            themes.append("faith_morality")
        themes.append("historical_legacy")
        return themes

if __name__ == "__main__":
    print("Psych Ops Target Profiler — Tool 4 Component")
    print("Use: from targeting.profiler import TargetProfiler")
