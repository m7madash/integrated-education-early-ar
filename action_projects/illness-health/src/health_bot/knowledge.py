#!/usr/bin/env python3
"""
Illness → Health — Medical Knowledge Base
Store condition → symptom → treatment mappings with credible sources.
Sources: WHO, CDC, Mayo Clinic, NHS (verifiable).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Condition:
    """Medical condition definition."""
    id: str
    name: str
    name_ar: str  # Arabic name
    symptoms: List[str]
    severity: str  # 'mild', 'moderate', 'severe', 'critical'
    contagious: bool
    typical_duration_days: int
    treatment_guidelines: List[str]
    recommended_medications: List[str]  # generic names
    when_to_see_doctor: List[str]
    source: str  # e.g., "WHO Guidelines 2023"
    source_url: Optional[str] = None

@dataclass
class Medication:
    """Medication info and alternatives."""
    id: str
    name: str
    name_ar: Optional[str] = None
    category: str  # 'pain', 'antibiotic', 'antihistamine', etc.
    typical_dose: str
    contraindications: List[str]
    affordable_alternatives: List[str]  # cheaper substitutes
    source: str

class MedicalKnowledgeBase:
    """Query medical conditions and medications."""

    def __init__(self, data_path: Optional[Path] = None):
        self.conditions: Dict[str, Condition] = {}
        self.medications: Dict[str, Medication] = {}
        if data_path:
            self._load(data_path)
        else:
            self._load_default()

    def _load_default(self):
        """Load synthetic demo dataset (small)."""
        # Conditions
        self.conditions = {
            "common_cold": Condition(
                id="common_cold",
                name="Common Cold",
                name_ar="الزكام",
                symptoms=["runny nose", "sneezing", "sore throat", "mild cough", "low fever"],
                severity="mild",
                contagious=True,
                typical_duration_days=7,
                treatment_guidelines=["Rest", "Hydration", "OTC symptom relief"],
                recommended_medications=["paracetamol", "ibuprofen"],
                when_to_see_doctor=["fever > 39°C", "symptoms > 10 days", "difficulty breathing"],
                source="CDC Common Cold Guidelines 2023",
                source_url="https://www.cdc.com"
            ),
            "influenza": Condition(
                id="influenza",
                name="Influenza (Flu)",
                name_ar="الإنفلونزا",
                symptoms=["high fever", "body aches", "fatigue", "cough", "headache"],
                severity="moderate",
                contagious=True,
                typical_duration_days=14,
                treatment_guidelines=["Rest", "Fluids", "Antivirals if within 48h"],
                recommended_medications=["oseltamivir (Tamiflu)", "paracetamol"],
                when_to_see_doctor=["difficulty breathing", "chest pain", "persistent high fever", "at-risk groups"],
                source="WHO Influenza Guidelines 2022",
                source_url="https://www.who.int"
            ),
            "covid19": Condition(
                id="covid19",
                name="COVID-19",
                name_ar="كوفيد-19",
                symptoms=["fever", "cough", "shortness of breath", "loss of taste/smell", "fatigue"],
                severity="moderate_to_severe",
                contagious=True,
                typical_duration_days=14,
                treatment_guidelines=["Isolation", "Rest", "Oxygen if needed", "Antivirals (Paxlovid) if high-risk"],
                recommended_medications=["paracetamol", "nirmatrelvir-ritonavir (Paxlovid) for high-risk"],
                when_to_see_doctor=["oxygen saturation < 94%", "persistent chest pain", "confusion", "bluish lips"],
                source="WHO COVID-19 Clinical Management 2023",
                source_url="https://www.who.int"
            ),
            "diabetes_emergency": Condition(
                id="diabetes_emergency",
                name="Diabetic Emergency (DKA/HHS)",
                name_ar="طوارئ السكري",
                symptoms=["extreme thirst", "frequent urination", "nausea", "confusion", "rapid breathing"],
                severity="critical",
                contagious=False,
                typical_duration_days=0,  # immediate
                treatment_guidelines=["Emergency room immediately", "IV fluids", "insulin therapy"],
                recommended_medications=["IV insulin", "IV fluids"],
                when_to_see_doctor=["ALWAYS — emergency"],
                source="American Diabetes Association Standards of Care 2023",
                source_url="https://diabetes.org"
            )
        }

        # Medications
        self.medications = {
            "paracetamol": Medication(
                id="paracetamol",
                name="Paracetamol (Acetaminophen)",
                name_ar="باراسيتامول",
                category="pain/fever",
                typical_dose="500-1000mg every 4-6h (max 4g/day)",
                contraindications=["severe liver disease"],
                affordable_alternatives=["generic acetaminophen"],
                source="WHO Essential Medicines List"
            ),
            "ibuprofen": Medication(
                id="ibuprofen",
                name="Ibuprofen",
                name_ar="إيبوبروفين",
                category="pain/fever/anti-inflammatory",
                typical_dose="200-400mg every 6-8h (max 1.2g/day OTC)",
                contraindications=["peptic ulcer", "severe kidney disease", "third trimester pregnancy"],
                affordable_alternatives=["generic ibuprofen", "naproxen"],
                source="WHO Essential Medicines List"
            ),
            "oseltamivir": Medication(
                id="oseltamivir",
                name="Oseltamivir (Tamiflu)",
                name_ar="أوسيلتامivir",
                category="antiviral",
                typical_dose="75mg twice daily for 5 days (within 48h of symptoms)",
                contraindications=["known hypersensitivity"],
                affordable_alternatives=["generic oseltamivir"],
                source="CDC Influenza Treatment Guidelines"
            )
        }

    def _load(self, path: Path):
        """Load from JSON files."""
        with open(path / 'conditions.json') as f:
            conds = json.load(f)
            self.conditions = {c['id']: Condition(**c) for c in conds}
        with open(path / 'medications.json') as f:
            meds = json.load(f)
            self.medications = {m['id']: Medication(**m) for m in meds}

    def get_condition(self, condition_id: str) -> Optional[Condition]:
        return self.conditions.get(condition_id)

    def search_by_symptom(self, symptom: str) -> List[Condition]:
        """Find conditions that include this symptom."""
        matches = []
        symptom_lower = symptom.lower()
        for cond in self.conditions.values():
            if any(symptom_lower in s.lower() for s in cond.symptoms):
                matches.append(cond)
        return matches

    def get_medication(self, med_id: str) -> Optional[Medication]:
        return self.medications.get(med_id)

    def suggest_treatment(self, condition_id: str) -> Dict:
        """Return treatment guidelines for a condition."""
        cond = self.get_condition(condition_id)
        if not cond:
            return {"error": "Condition not found"}
        return {
            "condition": cond.name,
            "treatment": cond.treatment_guidelines,
            "medications": cond.recommended_medications,
            "when_to_see_doctor": cond.when_to_see_doctor,
            "source": cond.source
        }

# Convenience
def knowledge_base() -> MedicalKnowledgeBase:
    return MedicalKnowledgeBase()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Medical Knowledge Base")
    parser.add_argument("--search", help="Search conditions by symptom")
    parser.add_argument("--condition", help="Get condition details by ID")
    parser.add_argument("--medication", help="Get medication info by ID")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    kb = MedicalKnowledgeBase()

    if args.search:
        results = kb.search_by_symptom(args.search)
        if args.json:
            print(json.dumps([asdict(c) for c in results], indent=2, ensure_ascii=False))
        else:
            print(f"🔍 Conditions with symptom '{args.search}':")
            for c in results:
                print(f" • {c.name} ({c.id}) — severity: {c.severity}")
    elif args.condition:
        cond = kb.get_condition(args.condition)
        if cond:
            if args.json:
                print(json.dumps(asdict(cond), indent=2, ensure_ascii=False))
            else:
                print(f"📋 Condition: {cond.name} ({cond.name_ar})")
                print(f"Severity: {cond.severity}")
                print(f"Symptoms: {', '.join(cond.symptoms)}")
                print(f"Treatment: {', '.join(cond.treatment_guidelines)}")
                print(f"Medications: {', '.join(cond.recommended_medications)}")
                print(f"See doctor if: {', '.join(cond.when_to_see_doctor)}")
                print(f"Source: {cond.source}")
        else:
            print("Condition not found")
    elif args.medication:
        med = kb.get_medication(args.medication)
        if med:
            print(f"💊 Medication: {med.name}")
            print(f"Dose: {med.typical_dose}")
            print(f"Contraindications: {', '.join(med.contraindications)}")
            print(f"Alternatives: {', '.join(med.affordable_alternatives)}")
        else:
            print("Medication not found")
    else:
        parser.print_help()
