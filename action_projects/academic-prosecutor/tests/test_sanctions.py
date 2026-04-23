#!/usr/bin/env python3
"""
Academic Prosecutor — Tests for Sanctions Module
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sanctions.registry import OffenseRegistry, Offense, OffenderProfile
from sanctions.enforcer import SanctionEnforcer, SanctionRule
from datetime import datetime, timezone

# CLEAR TEST DATA BEFORE RUNNING
def _clear_test_data():
    test_data = Path("tests/test_data")
    for f in test_data.glob("registry_*.json"):
        f.unlink(missing_ok=True)
    test_data.mkdir(parents=True, exist_ok=True)

def test_registry_add_offense():
    _clear_test_data()
    reg = OffenseRegistry(Path("tests/test_data/registry_test.json"))
    offense = Offense(
        id="test-001",
        offender_id="test_user_1",
        offender_name="Dr. Test",
        paper_id="10.1234/test.2025",
        violation_type="plagiarism",
        severity=4,
        evidence="Test evidence",
        discovered_at=datetime.now(timezone.utc).isoformat(),
        sanction_applied="",
        status="pending"
    )
    oid = reg.add_offense(offense)
    assert oid == "test-001"
    assert "test_user_1" in reg.offenders
    profile = reg.offenders["test_user_1"]
    # Debug: print details
    print(f"DEBUG: score={profile.total_severity_score}, risk={profile.risk_level}, offenses_count={len(profile.offenses)}")
    assert profile.total_severity_score == 4
    assert profile.risk_level == "low"  # single offense score<5 = low
    print("✅ Registry: add_offense works, risk level correct (low for score<5)")

def test_risk_escalation():
    _clear_test_data()
    reg = OffenseRegistry(Path("tests/test_data/registry_escalation.json"))
    # Add three medium offenses (severity 4 each = 12 total -> high)
    for i in range(3):
        off = Offense(
            id=f"escalate-{i}",
            offender_id="repeat_offender",
            offender_name="Dr. Repeat",
            paper_id=f"10.1234/dup{i}",
            violation_type="plagiarism",
            severity=4,
            evidence="duplicate",
            discovered_at=datetime.now(timezone.utc).isoformat(),
            sanction_applied="",
            status="pending"
        )
        reg.add_offense(off)
    profile = reg.offenders["repeat_offender"]
    assert profile.total_severity_score == 12
    assert profile.risk_level == "high"
    print("✅ Risk escalation: 3×severity4 → high (12 pts)")

def test_sanction_enforcer():
    _clear_test_data()
    enforcer = SanctionEnforcer()
    # Create a pending offense
    offense = Offense(
        id="enforce-test",
        offender_id="enforcer_user",
        offender_name="Dr. Enforce",
        paper_id="10.1234/enforce.2025",
        violation_type="plagiarism",
        severity=4,
        evidence="Test sanction",
        discovered_at=datetime.now(timezone.utc).isoformat(),
        sanction_applied="",
        status="pending"
    )
    # Add to registry first
    enforcer.registry.add_offense(offense)
    # Apply
    result = enforcer.apply(offense)
    assert result == True
    # Check sanction recorded
    updated = enforcer.registry.offenses["enforce-test"]
    assert updated.status == "applied"
    assert "retract" in updated.sanction_applied or "report" in updated.sanction_applied
    print("✅ SanctionEnforcer: applies penalty and updates registry")

def test_rule_selection():
    _clear_test_data()
    enforcer = SanctionEnforcer()
    # Low severity plagiarism -> should get warning/correct
    actions_low = enforcer.determine_sanction("plagiarism", 2, "some_id")
    assert "warning" in actions_low or "correct" in actions_low
    # High severity -> retract + report
    actions_high = enforcer.determine_sanction("plagiarism", 5, "some_id")
    assert "retract" in actions_high and "report_to_institution" in actions_high
    # Data fabrication critical -> ban
    actions_fab = enforcer.determine_sanction("data_fabrication", 5, "some_id")
    assert "ban_from_publishing" in actions_fab
    print("✅ Rule selection: severity-based actions correct")

if __name__ == "__main__":
    # Ensure test data dir exists
    Path("tests/test_data").mkdir(parents=True, exist_ok=True)
    test_registry_add_offense()
    test_risk_escalation()
    test_sanction_enforcer()
    test_rule_selection()
    print("\n🎉 All sanctions tests passed!")
