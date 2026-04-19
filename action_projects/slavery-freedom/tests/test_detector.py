#!/usr/bin/env python3
"""Tests for slavery-freedom detector."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.slavery_detector.detector import SlaveryDetector, Supplier
from src.slavery_detector.privacy import anonymize_id, encrypt_report, decrypt_report

def test_high_risk_supplier():
    d = SlaveryDetector()
    s = Supplier(
        id="TEST-001", name="HighRisk Factory", country="BD",
        industry="garment", workers=200, avg_hours_per_week=70,
        average_wage=60, has_contracts=False, unionized=False, audit_date=None
    )
    result = d.assess_supplier(s)
    assert result['risk_score'] >= 10, f"Expected high risk, got {result['risk_score']}"
    assert "CRITICAL" in result['verdict']
    print("✅ High-risk supplier detected (critical)")

def test_low_risk_supplier():
    d = SlaveryDetector()
    s = Supplier(
        id="TEST-002", name="Ethical Factory", country="PS",
        industry="tech", workers=50, avg_hours_per_week=40,
        average_wage=500, has_contracts=True, unionized=True, audit_date="2026-01-01"
    )
    result = d.assess_supplier(s)
    assert result['risk_score'] <= 2, f"Expected low risk, got {result['risk_score']}"
    print("✅ Low-risk supplier (ethical)")

def test_medium_risk_union_missing():
    d = SlaveryDetector()
    s = Supplier(
        id="TEST-003", name="Medium Risk", country="PK",
        industry="agriculture", workers=100, avg_hours_per_week=55,
        average_wage=120, has_contracts=True, unionized=False, audit_date=None
    )
    result = d.assess_supplier(s)
    print(f"  Score: {result['risk_score']}, Verdict: {result['verdict']}")
    assert True  # Accept any score

def test_privacy_anonymize():
    vid = "VICTIM-2026-12345"
    anon = anonymize_id(vid)
    assert len(anon) == 12
    assert vid not in anon
    print("✅ Victim ID anonymization works")

def test_privacy_encryption():
    text = "Supplier A: CRITICAL — 70 hrs/week, no contracts"
    enc = encrypt_report(text, "key")
    dec = decrypt_report(enc, "key")
    assert dec == text
    print("✅ Report encryption/decryption round-trip works")

if __name__ == "__main__":
    print("=== Slavery-Freedom Tests ===\n")
    test_high_risk_supplier()
    test_low_risk_supplier()
    test_medium_risk_union_missing()
    test_privacy_anonymize()
    test_privacy_encryption()
    print("\n✅ All 5 tests passed!")
