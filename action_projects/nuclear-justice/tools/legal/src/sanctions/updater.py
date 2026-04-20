"""
Sanctions List Updater — Tool 2 of Nuclear Justice

Generates targeted sanctions recommendations (asset freeze, travel ban)
against individuals and entities supporting nuclear weapons programs.

Based on UN Sanctions Committee patterns (e.g., DPRK, Iran).
"""

import csv
import json
from dataclasses import dataclass, asdict
from typing import List, Dict
from pathlib import Path
from datetime import date

@dataclass
class PersonEntity:
    name: str
    title: str
    organization: str
    country: str
    risk_score: int  # 1-10
    sanction_type: str  # "asset_freeze", "travel_ban", "both"

@dataclass
class Organization:
    name: str
    org_type: str  # type of organization (state_enterprise, bank, shipping)
    country: str
    risk_score: int
    justification: str

class SanctionsGenerator:
    """Generates sanctions recommendations in JSON format for UN/ national lists."""

    def __init__(self):
        self.people: List[PersonEntity] = []
        self.orgs: List[Organization] = []
        self.evidence_summary: str = ""

    def add_person(self, name: str, title: str, organization: str, country: str, risk: int, stype: str = "both"):
        self.people.append(PersonEntity(name, title, organization, country, risk, stype))

    def add_organization(self, name: str, org_type: str = None, otype: str = None, country: str = None, risk: int = 5, justification: str = ""):
        final_type = org_type or otype or "unknown"
        self.orgs.append(Organization(name, final_type, country, risk, justification))

    def set_evidence_summary(self, text: str):
        self.evidence_summary = text

    def generate_json(self) -> dict:
        data = {
            "generated_date": date.today().isoformat(),
            "program": "Nuclear Justice — Sanctions Recommendations",
            "total_entities": len(self.people) + len(self.orgs),
            "persons": [asdict(p) for p in self.people],
            "organizations": [asdict(o) for o in self.orgs],
            "evidence_summary": self.evidence_summary,
            "recommended_actions": [
                "Asset freeze on all listed persons and entities",
                "Travel ban on listed individuals",
                "Notify all UN member states for implementation"
            ]
        }
        return data

    def save_json(self, output_path: Path):
        data = self.generate_json()
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path

    def save_csv_persons(self, output_path: Path):
        fields = ["name", "title", "organization", "country", "risk_score", "sanction_type"]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for p in self.people:
                writer.writerow(asdict(p))
        return output_path

    def save_csv_orgs(self, output_path: Path):
        fields = ["name", "type", "country", "risk_score", "justification"]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for o in self.orgs:
                row = asdict(o)
                row["type"] = row.pop("org_type")  # rename key for CSV compatibility
                writer.writerow(row)
        return output_path

# Convenience function
def generate_sanctions_list(person_data: List[dict], org_data: List[dict], evidence: str, output_prefix: str):
    gen = SanctionsGenerator()
    for p in person_data:
        # Map CSV column names to parameter names
        org_val = p.get("organization") or p.get("org")
        risk_val = p.get("risk") or p.get("risk_score") or 5
        stype_val = p.get("stype") or p.get("sanction_type") or "both"
        gen.add_person(
            name=p["name"],
            title=p["title"],
            organization=org_val,
            country=p["country"],
            risk=risk_val,
            stype=stype_val
        )
    for o in org_data:
        gen.add_organization(
            name=o["name"],
            org_type=o.get("type") or o.get("otype"),
            country=o["country"],
            risk=o.get("risk") or o.get("risk_score") or 5,
            justification=o["justification"]
        )
    gen.set_evidence_summary(evidence)
    gen.save_json(Path(f"{output_prefix}.json"))
    gen.save_csv_persons(Path(f"{output_prefix}_persons.csv"))
    gen.save_csv_orgs(Path(f"{output_prefix}_orgs.csv"))
    return gen

if __name__ == "__main__":
    # Demo data: typical nuclear program officials
    sample_persons = [
        {
            "name": "Dr. Ahmad Vahidi",
            "title": "Minister of Defense",
            "org": "Ministry of Defense, State X",
            "country": "State X",
            "risk": 9,
            "stype": "both"
        },
        {
            "name": "General Y",
            "title": "Head of Nuclear Command",
            "org": "Strategic Forces Command",
            "country": "State X",
            "risk": 10,
            "stype": "both"
        },
        {
            "name": "Dr. Z",
            "title": "Chief Scientist",
            "org": "Nuclear Research Center",
            "country": "State X",
            "risk": 7,
            "stype": "asset_freeze"
        }
    ]

    sample_orgs = [
        {
            "name": "Atomic Energy Organization of State X",
            "otype": "state_enterprise",
            "country": "State X",
            "risk": 8,
            "justification": "Controls all nuclear material and enrichment activities"
        },
        {
            "name": "Bank X",
            "otype": "bank",
            "country": "State X",
            "risk": 6,
            "justification": "Facilitates financial transactions for prohibited program"
        }
    ]

    evidence = "Satellite imagery of enrichment sites; procurement records for centrifuge components; official budgets allocated to nuclear program."

    gen = generate_sanctions_list(sample_persons, sample_orgs, evidence, "demo_sanctions")
    print("✅ Sample sanctions lists generated:")
    print("   - demo_sanctions.json")
    print("   - demo_sanctions_persons.csv")
    print("   - demo_sanctions_orgs.csv")
