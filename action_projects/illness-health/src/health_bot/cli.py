#!/usr/bin/env python3
"""
Illness → Health — CLI Entry Point
Unified command-line interface for triage, knowledge queries, and assessment.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.health_bot.triage import MedicalTriage, Symptom, PatientContext, triage
from src.health_bot.knowledge import MedicalKnowledgeBase, knowledge_base
from src.health_bot.detector import HealthDetector, assess_health

def main():
    parser = argparse.ArgumentParser(
        description="Illness → Health: Medical Triage & Guidance System",
        epilog="Examples:\n"
               "  python -m src.health_bot.cli triage --symptoms fever cough --age 30 --sex male\n"
               "  python -m src.health_bot.cli condition --id common_cold\n"
               "  python -m src.health_bot.cli assess --symptoms chest-pain --age 65 --sex male\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # --- Triage command ---
    triage_parser = subparsers.add_parser('triage', help='Run medical triage assessment')
    triage_parser.add_argument('--symptoms', nargs='+', required=True, help='List of symptoms')
    triage_parser.add_argument('--age', type=int, required=True)
    triage_parser.add_argument('--sex', choices=['male', 'female', 'other'], required=True)
    triage_parser.add_argument('--conditions', nargs='*', default=[], help='Known chronic conditions')
    triage_parser.add_argument('--location', help='City/region for aid matching')
    triage_parser.add_argument('--json', action='store_true', help='Output JSON only')

    # --- Condition lookup ---
    cond_parser = subparsers.add_parser('condition', help='Look up medical condition')
    cond_parser.add_argument('--id', required=True, help='Condition ID (e.g., common_cold)')
    cond_parser.add_argument('--json', action='store_true')

    # --- Search by symptom ---
    search_parser = subparsers.add_parser('search', help='Search conditions by symptom')
    search_parser.add_argument('--symptom', required=True, help='Symptom keyword')
    search_parser.add_argument('--json', action='store_true')

    # --- Full assessment ---
    assess_parser = subparsers.add_parser('assess', help='Full health assessment (triage + knowledge + guidance)')
    assess_parser.add_argument('--symptoms', nargs='+', required=True)
    assess_parser.add_argument('--age', type=int, required=True)
    assess_parser.add_argument('--sex', choices=['male', 'female', 'other'], required=True)
    assess_parser.add_argument('--conditions', nargs='*', default=[])
    assess_parser.add_argument('--location')
    assess_parser.add_argument('--json', action='store_true')

    # --- Medication lookup ---
    med_parser = subparsers.add_parser('medication', help='Look up medication info')
    med_parser.add_argument('--id', required=True, help='Medication ID (e.g., paracetamol)')
    med_parser.add_argument('--json', action='store_true')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Dispatch
    if args.command == 'triage':
        symptoms = [Symptom(name=s, severity=5, duration_hours=24) for s in args.symptoms]
        patient = PatientContext(
            age=args.age,
            sex=args.sex,
            known_conditions=args.conditions,
            allergies=[],
            location=args.location
        )
        result = triage(symptoms, patient)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n🚑 Triage Result")
            print(f"Urgency Level : {result['urgency_level']}")
            print(f"Recommended   : {result['recommended_action']}")
            if result['time_to_care_hours'] is not None:
                print(f"Time to care  : {result['time_to_care_hours']} hours")
            print(f"Reasoning     : {'; '.join(result['reasoning'])}")
            print(f"Follow-up     : {result['follow_up_needed']}")

    elif args.command == 'condition':
        kb = knowledge_base()
        cond = kb.get_condition(args.id)
        if args.json:
            print(json.dumps(asdict(cond) if cond else {}, indent=2, ensure_ascii=False))
        else:
            if cond:
                print(f"📋 Condition: {cond.name} ({cond.name_ar})")
                print(f"Severity     : {cond.severity}")
                print(f"Symptoms     : {', '.join(cond.symptoms)}")
                print(f"Contagious?  : {cond.contagious}")
                print(f"Duration     : {cond.typical_duration_days} days typical")
                print(f"Treatment    : {', '.join(cond.treatment_guidelines)}")
                print(f"Meds         : {', '.join(cond.recommended_medications)}")
                print(f"See doctor if: {', '.join(cond.when_to_see_doctor)}")
                print(f"Source       : {cond.source}")
            else:
                print("Condition not found. Use `search` to find by symptom.")

    elif args.command == 'search':
        kb = knowledge_base()
        matches = kb.search_by_symptom(args.symptom)
        if args.json:
            print(json.dumps([asdict(c) for c in matches], indent=2, ensure_ascii=False))
        else:
            print(f"🔍 Conditions matching '{args.symptom}':")
            for c in matches:
                print(f" • {c.name} ({c.id}) — {c.severity}")

    elif args.command == 'medication':
        kb = knowledge_base()
        med = kb.get_medication(args.id)
        if args.json:
            print(json.dumps(asdict(med) if med else {}, indent=2))
        else:
            if med:
                print(f"💊 {med.name}")
                print(f"Dose               : {med.typical_dose}")
                print(f"Contra-indications : {', '.join(med.contraindications)}")
                print(f"Affordable altern. : {', '.join(med.affordable_alternatives)}")
                print(f"Source             : {med.source}")
            else:
                print("Medication not found")

    elif args.command == 'assess':
        patient_data = {
            'patient_id': 'cli-user',
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
            print(f"\n🩺 Full Health Assessment")
            print(f"Urgency           : {report['urgency']}")
            print(f"Action            : {report['recommended_action']}")
            print(f"Possible conditions: {[c['name'] for c in report['possible_conditions']]}")
            if report['treatment_plan']:
                print(f"Treatment plan    : {report['treatment_plan'].get('general', [])}")
            print(f"Follow-up needed  : {report['follow_up_needed']}")
            print(f"\n⚠️  {report['disclaimer']}")

if __name__ == "__main__":
    main()
