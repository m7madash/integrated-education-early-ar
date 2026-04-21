#!/usr/bin/env python3
"""
Illness → Health — Test Suite
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.health_bot.triage import MedicalTriage, Symptom, PatientContext, triage
from src.health_bot.knowledge import MedicalKnowledgeBase, knowledge_base
from src.health_bot.detector import HealthDetector, assess_health

def test_triage_critical():
    """Test critical symptom detection."""
    engine = MedicalTriage()
    symptoms = [Symptom(name="chest pain", severity=9, duration_hours=1)]
    patient = PatientContext(age=55, sex='male', known_conditions=['diabetes'], allergies=[])
    result = engine.assess(symptoms, patient)
    assert result['urgency_level'] == 'CRITICAL', f"Expected CRITICAL, got {result['urgency_level']}"
    print("✅ Triage critical case: PASS")

def test_triage_self_care():
    """Test self-care symptom detection."""
    engine = MedicalTriage()
    symptoms = [Symptom(name="common cold", severity=2, duration_hours=12)]
    patient = PatientContext(age=25, sex='female', known_conditions=[], allergies=[])
    result = engine.assess(symptoms, patient)
    assert result['urgency_level'] == 'SELF_CARE', f"Expected SELF_CARE, got {result['urgency_level']}"
    print("✅ Triage self-care: PASS")

def test_knowledge_search():
    """Test symptom-based condition search."""
    kb = knowledge_base()
    matches = kb.search_by_symptom("fever")
    assert len(matches) >= 2, f"Expected at least 2 matches for 'fever', got {len(matches)}"
    names = [c.name for c in matches]
    assert any("Influenza" in n or "COVID" in n for n in names), f"Missing flu/COVID in {names}"
    print("✅ Knowledge search by symptom: PASS")

def test_condition_lookup():
    """Test condition detail retrieval."""
    kb = knowledge_base()
    cond = kb.get_condition("common_cold")
    assert cond is not None
    assert cond.name == "Common Cold"
    assert "paracetamol" in cond.recommended_medications
    print("✅ Condition lookup: PASS")

def test_medication_lookup():
    """Test medication info."""
    kb = knowledge_base()
    med = kb.get_medication("paracetamol")
    assert med is not None
    assert "liver" in med.contraindications[0].lower() or "liver" in med.typical_dose.lower() or len(med.contraindications) > 0
    print("✅ Medication lookup: PASS")

def test_full_assessment():
    """Test end-to-end health assessment."""
    patient = {
        'patient_id': 'test-001',
        'symptoms': ['fever', 'cough', 'fatigue'],
        'age': 35,
        'sex': 'male',
        'known_conditions': ['asthma'],
        'location': 'Gaza Strip'
    }
    report = assess_health(patient)
    assert 'urgency' in report
    assert report['urgency'] in ['CRITICAL','HIGH','MEDIUM','LOW','SELF_CARE']
    assert 'recommended_action' in report
    assert 'disclaimer' in report
    print(f"✅ Full assessment: PASS (urgency: {report['urgency']})")

def run_all():
    print("\n🧪 Illness → Health — Running Tests\n")
    tests = [
        ("Triage Critical", test_triage_critical),
        ("Triage Self-Care", test_triage_self_care),
        ("Knowledge Search", test_knowledge_search),
        ("Condition Lookup", test_condition_lookup),
        ("Medication Lookup", test_medication_lookup),
        ("Full Assessment", test_full_assessment),
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            print(f"Running: {name}...", end=" ")
            fn()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    print(f"\n📊 Results: {passed} passed, {failed} failed\n")
    return failed == 0

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
