#!/usr/bin/env python3
"""
Illness → Health — Medical Triage System
Classify symptoms by urgency and recommend action.
"""

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

@dataclass
class Symptom:
    """A reported symptom."""
    name: str
    severity: int  # 1-10 (patient-reported)
    duration_hours: int
    description: str = ""

@dataclass
class PatientContext:
    """Patient demographics and history."""
    age: int
    sex: str  # 'male', 'female', 'other'
    known_conditions: List[str]  # chronic illnesses
    allergies: List[str]
    pregnancy_status: Optional[str] = None  # 'not_pregnant', 'pregnant', 'unknown'
    location: Optional[str] = None  # region for aid matching

@dataclass
class TriageResult:
    """Triage assessment outcome."""
    urgency_level: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'SELF_CARE'
    reasoning: List[str]
    recommended_action: str
    time_to_care_hours: Optional[int]
    follow_up_needed: bool
    resources: List[str]  # links to aid, clinics, hotlines

class MedicalTriage:
    """Rule-based medical triage engine."""

    # Critical symptoms (require immediate attention)
    CRITICAL_SYMPTOMS = {
        'chest pain', 'shortness of breath', 'unconscious', 'unresponsive',
        'severe bleeding', 'stroke', 'heart attack', 'seizure', 'anaphylaxis',
        'نزيف حاد', 'آلام في الصدر', 'ضيق تنفس حاد', 'غيبوبة'
    }

    # High-priority symptoms
    HIGH_SYMPTOMS = {
        'high fever', 'vomiting blood', 'severe abdominal pain', 'head injury',
        'broken bone', 'difficulty breathing', 'confusion', 'persistent vomiting',
        'حمى شديدة', 'ألم حاد في البطن', 'كسر', 'نزيف في الدماغ'
    }

    # Medium-priority symptoms
    MEDIUM_SYMPTOMS = {
        'fever', 'cough', 'sore throat', 'ear pain', 'rash', 'diarrhea',
        'headache', 'back pain', 'joint pain', 'حرارة', 'سعال', 'صداع', 'إسهال'
    }

    # Low-priority / self-care
    LOW_SYMPTOMS = {
        'common cold', 'mild allergy', 'minor cut', 'bruise', 'sore muscles',
        'زكام', 'حساسية خفيفة', 'خدش بسيط'
    }

    def __init__(self, aid_org_path: Optional[Path] = None):
        self.aid_orgs = self._load_aid_orgs(aid_org_path)

    def _load_aid_orgs(self, path: Optional[Path]) -> List[Dict]:
        """Load aid organizations (clinics, hospitals, hotlines)."""
        # Demo data — replace with real database
        return [
            {"name": "Red Crescent Clinic", "type": "clinic", "location": "Gaza", "services": ["general", "emergency"], "phone": "123"},
            {"name": "MSF Hospital", "type": "hospital", "location": "various", "services": ["emergency", "surgery"], "phone": "emergency hotline"},
            {"name": "WHO Helpline", "type": "hotline", "location": "global", "services": ["advice"], "phone": "locale-specific"}
        ]

    def assess(self, symptoms: List[Symptom], patient: PatientContext) -> TriageResult:
        """
        Run triage assessment.
        Returns: urgency level + recommended action.
        """
        reasoning = []
        risk_factors = []
        urgency = "LOW"
        time_to_care = None
        resources = []

        # 1. Check critical symptoms
        critical_found = []
        for s in symptoms:
            if any(crit in s.name.lower() for crit in self.CRITICAL_SYMPTOMS):
                critical_found.append(s.name)
        if critical_found:
            urgency = "CRITICAL"
            reasoning.append(f"Critical symptoms detected: {', '.join(critical_found)}")
            time_to_care = 0  # immediate

        # 2. Check high-priority symptoms
        high_found = []
        if urgency != "CRITICAL":
            for s in symptoms:
                if any(high in s.name.lower() for high in self.HIGH_SYMPTOMS):
                    high_found.append(s.name)
            if high_found:
                urgency = "HIGH"
                reasoning.append(f"High-priority symptoms: {', '.join(high_found)}")
                time_to_care = 2  # within 2 hours

        # 3. Medium priority
        medium_found = []
        if urgency not in ["CRITICAL", "HIGH"]:
            for s in symptoms:
                if any(med in s.name.lower() for med in self.MEDIUM_SYMPTOMS):
                    medium_found.append(s.name)
            if medium_found:
                urgency = "MEDIUM"
                reasoning.append(f"Moderate symptoms: {', '.join(medium_found)}")
                time_to_care = 24  # within 24 hours

        # 4. Low priority
        low_found = []
        if urgency == "LOW":
            for s in symptoms:
                if any(low in s.name.lower() for low in self.LOW_SYMPTOMS):
                    low_found.append(s.name)
            if len(low_found) == len(symptoms):
                urgency = "SELF_CARE"
                reasoning.append("Symptoms align with self-care conditions")
                time_to_care = 72  # 3 days

        # 5. Risk factors: age, chronic conditions, pregnancy
        if patient.age < 5 or patient.age > 65:
            risk_factors.append("Age vulnerability (under 5 or over 65)")
        if patient.known_conditions:
            risk_factors.append(f"Chronic conditions: {', '.join(patient.known_conditions)}")
        if patient.pregnancy_status == 'pregnant':
            risk_factors.append("Pregnancy — higher risk")
        if risk_factors:
            reasoning.append(f"Risk factors: {'; '.join(risk_factors)}")
            # Upgrade urgency by one level if risk present (but not beyond CRITICAL)
            if urgency == "LOW":
                urgency = "MEDIUM"
                time_to_care = 24
            elif urgency == "MEDIUM":
                urgency = "HIGH"
                time_to_care = 2

        # 6. Determine recommended action text
        action_text, resources = self._recommend_action(urgency, patient)

        follow_up = urgency in ["MEDIUM", "LOW", "SELF_CARE"]

        return TriageResult(
            urgency_level=urgency,
            reasoning=reasoning,
            recommended_action=action_text,
            time_to_care_hours=time_to_care,
            follow_up_needed=follow_up,
            resources=resources
        )

    def _recommend_action(self, urgency: str, patient: PatientContext) -> Tuple[str, List[str]]:
        """Generate recommended action string and resource links."""
        resources = self._match_aid(patient.location, urgency)

        if urgency == "CRITICAL":
            action = "🔴 EMERGENCY: Go to nearest ER or call emergency services immediately. Do not wait."
            resources.insert(0, " emergency hotline available")
        elif urgency == "HIGH":
            action = "🟠 Seek medical care TODAY — urgent evaluation needed to prevent complications."
        elif urgency == "MEDIUM":
            action = "🟡 See a doctor/doctor within 24–48 hours for proper diagnosis."
        elif urgency == "LOW":
            action = "🟢 Monitor symptoms; if worsen or persist >48h, consult a doctor."
        else:  # SELF_CARE
            action = "🟢 Home care sufficient: rest, hydration, OTC meds as directed. Seek care if symptoms worsen."

        # Append resource links (phone numbers, clinics)
        if resources:
            action += f"\n\nResources nearby: {', '.join(resources[:3])}"  # show top 3

        return action, resources

    def _match_aid(self, location: Optional[str], urgency: str) -> List[str]:
        """Simple aid matching by location and urgency."""
        if not location:
            return ["General: contact local health authorities"]
        matches = []
        for org in self.aid_orgs:
            if org['location'].lower() in location.lower() or org['location'] == 'global':
                if urgency in ['CRITICAL', 'HIGH'] and 'emergency' in org['services']:
                    matches.append(f"{org['name']} — {org['phone']}")
                elif urgency in ['MEDIUM', 'LOW'] and 'general' in org['services']:
                    matches.append(f"{org['name']} — {org['phone']}")
        return matches if matches else ["No specific orgs found — call national emergency number"]

# Convenience
def triage(symptoms: List[Symptom], patient: PatientContext) -> Dict:
    engine = MedicalTriage()
    result = engine.assess(symptoms, patient)
    return asdict(result)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Medical Triage System")
    parser.add_argument("--symptoms", nargs="+", help="List of symptoms (e.g., 'fever' 'cough')")
    parser.add_argument("--age", type=int, required=True, help="Patient age")
    parser.add_argument("--sex", choices=['male', 'female', 'other'], required=True)
    parser.add_argument("--conditions", nargs="*", default=[], help="Known chronic conditions")
    parser.add_argument("--location", help="City/region for aid matching")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.symptoms:
        print("Example usage: python triage.py --symptoms fever cough --age 30 --sex male")
        exit(0)

    symptom_objs = [Symptom(name=s, severity=5, duration_hours=24) for s in args.symptoms]
    patient = PatientContext(
        age=args.age,
        sex=args.sex,
        known_conditions=args.conditions,
        allergies=[],
        location=args.location
    )
    result = triage(symptom_objs, patient)
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(f"🚑 Medical Triage Assessment")
        print(f"Urgency: {result['urgency_level']}")
        print(f"Action: {result['recommended_action']}")
        if result['time_to_care_hours'] is not None:
            print(f"Time to care: {result['time_to_care_hours']} hours")
        print(f"Reasoning: {'; '.join(result['reasoning'])}")
        print(f"Follow-up needed: {result['follow_up_needed']}")
