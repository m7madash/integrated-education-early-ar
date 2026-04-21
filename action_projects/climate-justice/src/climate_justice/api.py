#!/usr/bin/env python3
"""
Climate Justice — Flask REST API
Expose climate justice modules as web endpoints.
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

from src.climate_justice.water import WaterJustice, analyze_water as analyze_water_core
from src.climate_justice.energy import EnergyPoverty, analyze_energy as analyze_energy_core
from src.climate_justice.refugees import ClimateRefugees, analyze_refugees as analyze_refugees_core
from src.climate_justice.detector import ClimateDetector, analyze as analyze_detector_core
from src.climate_justice.accountability import CarbonAccountability, analyze_polluter as analyze_accountability_core, rank_polluters as rank_polluters_core

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# In-memory storage for reports
REPORTS = {}

# Available modules
MODULES = {
    'water': {'class': WaterJustice, 'analyze': analyze_water_core, 'desc': 'Water justice analysis'},
    'energy': {'class': EnergyPoverty, 'analyze': analyze_energy_core, 'desc': 'Energy poverty assessment'},
    'refugees': {'class': ClimateRefugees, 'analyze': analyze_refugees_core, 'desc': 'Climate displacement forecasting'},
    'detector': {'class': ClimateDetector, 'analyze': analyze_detector_core, 'desc': 'General climate hazard detection'},
    'accountability': {'class': CarbonAccountability, 'analyze': analyze_accountability_core, 'desc': 'Carbon polluter accountability'}
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'climate-justice',
        'version': '0.1.0',
        'modules': list(MODULES.keys()),
        'timestamp': datetime.now(timezone=None).isoformat()
    })

@app.route('/modules', methods=['GET'])
def modules():
    return jsonify({
        'modules': [
            {'name': k, 'description': v['desc']} for k, v in MODULES.items()
        ]
    })

@app.route('/analyze/<module_name>', methods=['POST'])
def analyze_module(module_name: str):
    """
    Analyze climate justice data for a specific module.
    Expects JSON body with module-specific parameters.
    """
    if module_name not in MODULES:
        abort(404, description=f"Module {module_name} not found")

    report_id = str(uuid.uuid4())
    data = request.get_json(silent=True) or {}

    try:
        analyzer_class = MODULES[module_name]['class']
        analyzer = analyzer_class()
        result = analyzer.analyze(**data) if hasattr(analyzer, 'analyze') else MODULES[module_name]['analyze'](**data)
        # Convert dataclass to dict if needed
        if hasattr(result, '__dict__'):
            result_dict = asdict(result)
        else:
            result_dict = result
        result_dict['report_id'] = report_id
        REPORTS[report_id] = result_dict
        return jsonify({
            'success': True,
            'report_id': report_id,
            'summary': {k: v for k, v in result_dict.items() if k not in ['component_results', 'raw_bands']}
        }), 200
    except Exception as e:
        app.logger.error(f"Analysis error: {e}", exc_info=True)
        abort(500, description=str(e))

@app.route('/results/<report_id>', methods=['GET'])
def get_result(report_id: str):
    report = REPORTS.get(report_id)
    if not report:
        abort(404, description="Report not found")
    return jsonify(report)

@app.route('/accountability/<polluter_id>', methods=['GET'])
def get_accountability(polluter_id: str):
    """Shortcut to get polluter accountability report."""
    try:
        result = analyze_accountability_core(polluter_id)
        return jsonify(result)
    except Exception as e:
        abort(500, description=str(e))

@app.route('/accountability/rank', methods=['GET'])
def get_rankings():
    """Return ranked list of top polluters."""
    try:
        top_n = request.args.get('top_n', default=10, type=int)
        results = rank_polluters_core(top_n=top_n)
        return jsonify({'rankings': results})
    except Exception as e:
        abort(500, description=str(e))

# --- CLI ---
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Climate Justice API")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    print(f"🌍 Starting Climate Justice API on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
