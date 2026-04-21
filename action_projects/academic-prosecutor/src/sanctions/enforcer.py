#!/usr/bin/env python3
"""
Academic Prosecutor — Sanction Enforcer
Applies penalties based on violation type, severity, and offender history.
"""

import json
import urllib.request
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from .registry import OffenseRegistry, Offense

@dataclass
class SanctionRule:
    """Penalty configuration."""
    violation_type: str
    min_severity: int
    max_severity: int
    actions: List[str]  # e.g., ["retract", "report_to_institution", "block_funding"]
    notify: List[str]   # e.g., ["publisher", "university", "funding_agency"]

# Default penalty matrix (configurable via JSON later)
DEFAULT_RULES = [
    SanctionRule("plagiarism", 4, 5, ["retract", "report_to_institution", "block_funding"], ["publisher", "university", "funding_agency"]),
    SanctionRule("plagiarism", 1, 3, ["correct", "warning"], ["publisher"]),
    SanctionRule("data_fabrication", 5, 5, ["retract", "ban_from_publishing", "legal_referral"], ["publisher", "institution", "legal"]),
    SanctionRule("duplicate_submission", 3, 5, ["reject", "blacklist_journal"], ["publisher"]),
    SanctionRule("authorship_fraud", 4, 5, ["retract", "report_to_institution"], ["publisher", "university"]),
]

class SanctionEnforcer:
    """Applies sanctions automatically."""

    def __init__(self, rules_path: Optional[Path] = None):
        self.rules = self._load_rules(rules_path) if rules_path else DEFAULT_RULES
        self.registry = OffenseRegistry()

    def _load_rules(self, path: Path):
        with open(path) as f:
            data = json.load(f)
        return [SanctionRule(**r) for r in data]

    def determine_sanction(self, violation_type: str, severity: int, offender_id: str) -> List[str]:
        """Pick sanction based on rules + offender risk level."""
        risk = self.registry.get_risk_level(offender_id)
        actions = []

        for rule in self.rules:
            if rule.violation_type == violation_type and rule.min_severity <= severity <= rule.max_severity:
                actions.extend(rule.actions)

        # Escalate for repeat offenders
        if risk == "critical":
            actions = [a for a in actions if a not in ["warning", "correct"]]  # no leniency
            if "retract" not in actions:
                actions.append("blacklist")
        elif risk == "high":
            # prefer stricter actions
            actions = [a for a in actions if a not in ["warning"]]

        return list(set(actions))  # deduplicate

    def apply(self, offense: Offense) -> bool:
        """Apply sanctions to an offense."""
        actions = self.determine_sanction(offense.violation_type, offense.severity, offense.offender_id)
        if not actions:
            print(f"⚠️ No sanction rule for {offense.violation_type} severity {offense.severity}")
            return False

        summary = ", ".join(actions)
        success = self.registry.apply_sanction(offense.id, "automated_sanction", summary)
        if success:
            print(f"✅ Sanction applied to {offense.offender_name}: {summary}")
        else:
            print(f"❌ Failed to apply sanction for offense {offense.id}")

        # TODO: actually execute actions (retraction notice, email, etc.)
        self._execute_actions(offense, actions)

        return success

    def _execute_actions(self, offense: Offense, actions: List[str]):
        """Placeholder: call external APIs to enforce."""
        # Would call Crossref API, email SMTP, institutional webhooks here
        pass

# Convenience
def sanction_offense(offense: Offense) -> bool:
    enforcer = SanctionEnforcer()
    return enforcer.apply(offense)

if __name__ == "__main__":
    # Demo: load from registry
    reg = OffenseRegistry()
    if reg.offenses:
        for oid, offense in reg.offenses.items():
            if offense.status == "pending":
                print(f"🔸 Processing pending offense: {oid}")
                enforcer = SanctionEnforcer()
                enforcer.apply(offense)
    else:
        print("ℹ️ No pending offenses in registry. Add one first.")
