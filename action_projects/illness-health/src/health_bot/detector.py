#!/usr/bin/env python3
"""
Illness → Health — Main Detector Orchestrator
Combine triage, knowledge, privacy into unified health assessment.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from .triage import MedicalTriage, Symptom, PatientContext, TriageResult
from .knowledge import MedicalKnowledgeBase, Condition, Medication
from .privacy import HealthDataPrivacy

@dataclass
class HealthAssessmentReport:
    """Full health assessment report."""
    patient_id: str
    symptoms: List[str]
    urgency: str
    recommended_action: str
    possible_conditions: List[Dict]  # condition IDs + confidence
    treatment_plan: Dict
    medication_guidelines: List[Dict]
    aid_resources: List[Dict]
    privacy_notice: str
    disclaimer: str
    timestamp: str
    follow_up_needed: bool

class HealthDetector:
    """Orchestrate health assessment pipeline."""

    def __init__(self, knowledge_path: Optional[Path] = None, privacy_key_path: Optional[Path] = None):
        self.triage_engine = MedicalTriage()
        self.kb = MedicalKnowledgeBase(knowledge_path)
        self.privacy = HealthDataPrivacy(key_file=privacy_key_path)
        self.disclaimer = (
            "⚠️ This tool provides guidance only, not diagnosis. "
            "Always consult a licensed healthcare professional. "
            "In emergencies, call emergency services immediately."
        )

    def assess(self, patient_data: Dict) -> HealthAssessmentReport:
        """
        Run full health assessment.
        patient_data keys: patient_id, age, sex, symptoms (list), known_conditions, location
        """
        # Extract
        pid = patient_data.get('patient_id', 'anonymous')
        symptoms_raw = patient_data.get('symptoms', [])
        age = patient_data.get('age', 30)
        sex = patient_data.get('sex', 'unknown')
        known_conditions = patient_data.get('known_conditions', [])
        allergies = patient_data.get('allergies', [])
        location = patient_data.get('location')

        # Convert to objects
        symptoms = [Symptom(name=s, severity=5, duration_hours=24, description="") for s in symptoms_raw]
        patient = PatientContext(
            age=age,
            sex=sex,
            known_conditions=known_conditions,
            allergies=allergies,
            location=location
        )

        # 1. Triage
        triage_result: TriageResult = self.triage_engine.assess(symptoms, patient)

        # 2. Knowledge: suggest possible conditions based on symptoms
        possible_conditions = []
        for s in symptoms_raw:
            matches = self.kb.search_by_symptom(s)
            for cond in matches[:2]:  # top 2 per symptom
                possible_conditions.append({
                    'id': cond.id,
                    'name': cond.name,
                    'name_ar': cond.name_ar,
                    'severity': cond.severity,
                    'match_symptom': s
                })
        # Deduplicate by condition id
        seen = set()
        uniq_conditions = []
        for pc in possible_conditions:
            if pc['id'] not in seen:
                uniq_conditions.append(pc)
                seen.add(pc['id'])

        # 3. Treatment plan (from most severe possible condition or triage guidance)
        treatment_plan = {}
        if uniq_conditions:
            # Use highest severity condition
            severity_order = {'critical': 4, 'severe': 3, 'moderate': 2, 'mild': 1}
            sorted_conds = sorted(uniq_conditions, key=lambda x: severity_order.get(x['severity'], 0), reverse=True)
            top_cond_id = sorted_conds[0]['id']
            treatment_plan = self.kb.suggest_treatment(top_cond_id)
        else:
            treatment_plan = {
                'general': [
                    "Rest",
                    "Stay hydrated",
                    "Monitor symptoms; seek care if worsen"
                ],
                'source': 'General health guidelines'
            }

        # 4. Medication guidelines (filter allergies)
        medication_guidelines = []
        for cond in uniq_conditions[:3]:
            cond_obj = self.kb.get_condition(cond['id'])
            if cond_obj:
                for med_name in cond_obj.recommended_medications:
                    med = self.kb.get_medication(med_name)
                    if med:
                        # Check allergies
                        safe = not any(allergen in med.contraindications for allergen in allergies)
                        medication_guidelines.append({
                            'condition': cond['name'],
                            'medication': med.name,
                            'dose': med.typical_dose,
                            'safe': safe,
                            'alternatives': med.affordable_alternatives if not safe else []
                        })

        # 5. Aid resources (from triage result resources)
        aid_resources = []  # populate from triage or external DB

        # 6. Privacy: anonymize report for storage/logging
        privacy_note = "Patient data is encrypted at rest. Consent required for data sharing."

        # 7. Build report
        report = HealthAssessmentReport(
            patient_id=pid,
            symptoms=symptoms_raw,
            urgency=triage_result.urgency_level,
            recommended_action=triage_result.recommended_action,
            possible_conditions=uniq_conditions,
            treatment_plan=treatment_plan,
            medication_guidelines=medication_guidelines,
            aid_resources=aid_resources,
            privacy_notice=privacy_note,
            disclaimer=self.disclaimer,
            timestamp=datetime.now(timezone.utc).isoformat(),
            follow_up_needed=triage_result.follow_up_needed
        )

        return report

# Convenience
def assess_health(patient_data: Dict) -> Dict:
    detector = HealthDetector()
    report = detector.assess(patient_data)
    return asdict(report)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Health Assessment Orchestrator")
    parser.add_argument("--patient-id", required=True, help="Anonymous patient ID")
    parser.add_argument("--symptoms", nargs="+", required=True, help="Symptoms list")
    parser.add_argument("--age", type=int, required=True)
    parser.add_argument("--sex", choices=['male', 'female', 'other'], required=True)
    parser.add_argument("--conditions", nargs="*", default=[], help="Known chronic conditions")
    parser.add_argument("--location", help="City/region for aid matching")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    patient_data = {
        'patient_id': args.patient_id,
        'symptoms': args.symptoms,
        'age': args.age,
        'sex': args.sex,
        'known_conditions': args.conditions,
        'location': args.location
    }
    report = assess_health(patient_data)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"🩺 Health Assessment Report")
        print(f"Patient ID: {report['patient_id']}")
        print(f"Urgency: {report['urgency']}")
        print(f"Action: {report['recommended_action']}")
        print(f"Possible conditions: {[c['name'] for c in report['possible_conditions']]}")
        print(f"Follow-up needed: {report['follow_up_needed']}")
        print(f"\n{report['disclaimer']}")
