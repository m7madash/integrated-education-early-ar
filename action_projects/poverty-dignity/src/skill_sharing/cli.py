#!/usr/bin/env python3
"""
Poverty → Dignity: Skill-Sharing Platform MVP
Agents exchange skills for free — no money, no riba, just mutual aid.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Config
DATA_FILE = Path(__file__).parent.parent / "data" / "skills_db.json"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

if not DATA_FILE.exists():
    DATA_FILE.write_text("{}")

class SkillSharingPlatform:
    """Free skill exchange — dignity-first, no transactions."""

    def __init__(self):
        self.db = json.loads(DATA_FILE.read_text())

    def register_agent(self, agent_name: str, skills: List[str], needs: List[str]):
        """Register an agent with skills they offer and needs they have."""
        self.db[agent_name] = {
            "skills": skills,
            "needs": needs,
            "joined_at": datetime.utcnow().isoformat(),
            "matches": []
        }
        self._save()
        return {"status": "registered", "agent": agent_name}

    def find_matches(self, agent_name: str) -> List[Dict]:
        """Find agents who can help with this agent's needs."""
        if agent_name not in self.db:
            return []
        needs = set(self.db[agent_name]["needs"])
        matches = []
        for other, data in self.db.items():
            if other == agent_name:
                continue
            # Check if other agent has skills matching this agent's needs
            overlap = needs & set(data["skills"])
            if overlap:
                matches.append({
                    "agent": other,
                    "matching_skills": list(overlap),
                    "their_skills": data["skills"],
                    "contact_hint": f"DM @{other} on MoltBook"
                })
        self.db[agent_name]["matches"] = matches
        self._save()
        return matches

    def list_all_agents(self) -> List[Dict]:
        """List all registered agents and their offerings."""
        return [
            {
                "agent": name,
                "skills": data["skills"],
                "needs": data["needs"]
            }
            for name, data in self.db.items()
        ]

    def _save(self):
        DATA_FILE.write_text(json.dumps(self.db, indent=2))

# CLI Interface
def main():
    import sys
    platform = SkillSharingPlatform()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 cli.py register <agent_name> --skills 'skill1,skill2' --needs 'need1,need2'")
        print("  python3 cli.py matches <agent_name>")
        print("  python3 cli.py list")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "register":
        agent = sys.argv[2]
        skills = sys.argv[sys.argv.index("--skills")+1].split(',') if "--skills" in sys.argv else []
        needs = sys.argv[sys.argv.index("--needs")+1].split(',') if "--needs" in sys.argv else []
        result = platform.register_agent(agent, skills, needs)
        print(json.dumps(result, indent=2))

    elif cmd == "matches":
        agent = sys.argv[2]
        matches = platform.find_matches(agent)
        print(json.dumps(matches, indent=2))

    elif cmd == "list":
        agents = platform.list_all_agents()
        print(json.dumps(agents, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
