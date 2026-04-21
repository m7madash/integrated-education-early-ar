#!/usr/bin/env python3
"""
Academic Prosecutor — Sanctions Registry
Tracks offenders, violation history, and penalty escalation.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Offense:
    """Single offense record."""
    id: str  # offender_id + timestamp hash
    offender_id: str  # author identifier (ORCID, email, institution ID)
    offender_name: str
    paper_id: str
    violation_type: str
    severity: int  # 1-5
    evidence: str
    discovered_at: str
    sanction_applied: str
    status: str  # pending, applied, appealed, resolved

@dataclass
class OffenderProfile:
    """Cumulative profile of an offender."""
    offender_id: str
    name: str
    affiliation: str
    offenses: List[Offense]
    total_severity_score: int
    risk_level: str  # low, medium, high, critical
    first_offense: str
    last_offense: str

class OffenseRegistry:
    """Persistent registry of academic offenses."""

    def __init__(self, db_path: Path = Path("data/registry.json")):
        self.db_path = db_path
        self.offenses: Dict[str, Offense] = {}
        self.offenders: Dict[str, OffenderProfile] = {}
        self._load()

    def _load(self):
        if self.db_path.exists():
            with open(self.db_path) as f:
                data = json.load(f)
                for oid, odata in data.get("offenses", {}).items():
                    self.offenses[oid] = Offense(**odata)
                # Rebuild offender profiles
                for offense in self.offenses.values():
                    self._update_offender_profile(offense)

    def _save(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "offenses": {oid: asdict(off) for oid, off in self.offenses.items()},
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add_offense(self, offense: Offense) -> str:
        """Record a new offense."""
        self.offenses[offense.id] = offense
        self._update_offender_profile(offense)
        self._save()
        return offense.id

    def _update_offender_profile(self, offense: Offense):
        oid = offense.offender_id
        if oid not in self.offenders:
            self.offenders[oid] = OffenderProfile(
                offender_id=oid,
                name=offense.offender_name,
                affiliation="",  # TODO: enrich from external DB
                offenses=[],
                total_severity_score=0,
                risk_level="low",
                first_offense=offense.discovered_at,
                last_offense=offense.discovered_at
            )
        profile = self.offenders[oid]
        profile.offenses.append(offense)
        profile.total_severity_score += offense.severity
        profile.last_offense = offense.discovered_at
        # Escalate risk level
        if profile.total_severity_score >= 20:
            profile.risk_level = "critical"
        elif profile.total_severity_score >= 10:
            profile.risk_level = "high"
        elif profile.total_severity_score >= 5:
            profile.risk_level = "medium"

    def get_offender_history(self, offender_id: str) -> List[Offense]:
        """Get all offenses for an offender."""
        return [o for o in self.offenses.values() if o.offender_id == offender_id]

    def get_risk_level(self, offender_id: str) -> str:
        """Get current risk level for an offender."""
        if offender_id in self.offenders:
            return self.offenders[offender_id].risk_level
        return "unknown"

    def apply_sanction(self, offense_id: str, sanction_type: str, details: str) -> bool:
        """Mark an offense as sanctioned."""
        if offense_id not in self.offenses:
            return False
        offense = self.offenses[offense_id]
        offense.sanction_applied = f"{sanction_type}: {details}"
        offense.status = "applied"
        self._save()
        return True

# Convenience
def load_registry() -> OffenseRegistry:
    return OffenseRegistry()

if __name__ == "__main__":
    reg = OffenseRegistry()
    # Demo: add a fake offense
    demo = Offense(
        id="demo-001",
        offender_id="demo_author_123",
        offender_name="Dr. F. Ake",
        paper_id="10.1234/demo.2023.001",
        violation_type="plagiarism",
        severity=5,
        evidence="Title+abstract copy from known paper",
        discovered_at=datetime.now(timezone.utc).isoformat(),
        sanction_applied="",
        status="pending"
    )
    reg.add_offense(demo)
    print(f"✅ Added demo offense. Risk level: {reg.get_risk_level('demo_author_123')}")
