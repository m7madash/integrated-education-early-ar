#!/usr/bin/env python3
"""
Illness → Health — Flask REST API
Expose medical triage and knowledge as web service.
"""

import os
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from flask import Flask, request, jsonify, abort

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.health_bot.detector import HealthDetector, assess_health as assess_health_core
from src.health_bot.triage import MedicalTriage, Symptom, PatientContext, triage as triage_core
from src.health_bot.knowledge import MedicalKnowledgeBase, knowledge_base as kb_core
from src.health_bot.privacy import HealthDataPrivacy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# In-memory storage (demo)
REPORTS = {}
detector = HealthDetector()
triage_engine = MedicalTriage()
kb = MedicalKnowledgeBase()
privacy = HealthDataPrivacy()  # demo key

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'illness-health',
        'version': '0.1.0',
        'timestamp': datetime.now(timezone=None).isoformat()
    })

@app.route('/triage', methods=['POST'])
def triage_endpoint():
    """
    Run triage on symptoms.
    JSON body: {"symptoms": ["fever", "cough"], "age": 30, "sex": "male", ...}
    """
    data = request.get_json()
    if not data or 'symptoms' not in data:
        abort(400, description="Missing symptoms")
    
    symptoms = [Symptom(name=s, severity=5, duration_hours=24) for s in data['symptoms']]
    patient = PatientContext(
        age=data.get('age', 30),
        sex=data.get('sex', 'unknown'),
        known_conditions=data.get('known_conditions', []),
        allergies=data.get('allergies', []),
        location=data.get('location')
    )
    result = triage_core(symptoms, patient)
    report_id = str(uuid.uuid4())
    REPORTS[report_id] = result
    return jsonify({'report_id': report_id, **result}), 200

@app.route('/assess', methods=['POST'])
def assess_endpoint():
    """
    Full health assessment (triage + knowledge + treatment).
    JSON body: same as triage + optional patient_id.
    """
    data = request.get_json()
    if not data or 'symptoms' not in data:
        abort(400, description="Missing symptoms")
    pid = data.get('patient_id', str(uuid.uuid4()))
    data['patient_id'] = pid
    report = assess_health_core(data)
    report_id = str(uuid.uuid4())
    report['report_id'] = report_id
    REPORTS[report_id] = report
    return jsonify({
        'success': True,
        'report_id': report_id,
        'urgency': report['urgency'],
        'action': report['recommended_action'][:100] + '...'
    }), 200

@app.route('/results/<report_id>', methods=['GET'])
def get_result(report_id: str):
    report = REPORTS.get(report_id)
    if not report:
        abort(404, description="Report not found")
    return jsonify(report)

@app.route('/conditions', methods=['GET'])
def list_conditions():
    """Return all conditions (metadata only)."""
    conditions = []
    for cid, cond in kb.conditions.items():
        conditions.append({
            'id': cid,
            'name': cond.name,
            'severity': cond.severity,
            'contagious': cond.contagious
        })
    return jsonify({'conditions': conditions})

@app.route('/condition/<condition_id>', methods=['GET'])
def get_condition(condition_id: str):
    cond = kb.get_condition(condition_id)
    if not cond:
        abort(404, description="Condition not found")
    return jsonify(asdict(cond))

@app.route('/search', methods=['GET'])
def search_symptoms():
    """Search conditions by symptom keyword."""
    symptom = request.args.get('q')
    if not symptom:
        abort(400, description="Missing query parameter 'q'")
    results = kb.search_by_symptom(symptom)
    return jsonify({'matches': [asdict(c) for c in results]})

@app.route('/medications', methods=['GET'])
def list_medications():
    meds = []
    for mid, med in kb.medications.items():
        meds.append({
            'id': mid,
            'name': med.name,
            'category': med.category,
            'dose': med.typical_dose
        })
    return jsonify({'medications': meds})

# --- CLI ---
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Illness → Health API")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    print(f"🏥 Starting Illness→Health API on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
