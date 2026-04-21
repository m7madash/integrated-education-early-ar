#!/usr/bin/env python3
"""
Division → Unity — REST API (Flask)
Expose agent registry and coalitions over HTTP.
"""

from flask import Flask, jsonify, request, abort
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from .storage import UnityStorage, AgentRecord, CoalitionRecord

app = Flask(__name__)
storage = UnityStorage()

# --- Agent endpoints ---

@app.route('/agents', methods=['GET'])
def list_agents():
    """List all agents, optionally filtered by region/capability."""
    region = request.args.get('region')
    capability = request.args.get('capability')
    agents = storage.list_agents(region=region, capability=capability)
    return jsonify([a.__dict__ for a in agents])

@app.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    agent = storage.get_agent(agent_id)
    if not agent:
        abort(404, description="Agent not found")
    return jsonify(agent.__dict__)

@app.route('/agents', methods=['POST'])
def create_agent():
    data = request.json
    if not data or 'agent_id' not in data or 'name' not in data:
        abort(400, description="Missing required fields: agent_id, name")
    agent = AgentRecord(
        agent_id=data['agent_id'],
        name=data['name'],
        mission=data.get('mission', ''),
        capabilities=data.get('capabilities', []),
        region=data.get('region', ''),
        contact=data.get('contact')
    )
    storage.save_agent(agent)
    return jsonify({"status": "created", "agent": agent.__dict__}), 201

@app.route('/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    success = storage.delete_agent(agent_id)
    if not success:
        abort(404, description="Agent not found")
    return jsonify({"status": "deleted", "agent_id": agent_id})

# --- Coalition endpoints ---

@app.route('/coalitions', methods=['GET'])
def list_coalitions():
    status = request.args.get('status')
    coalitions = storage.list_coalitions(status=status)
    return jsonify([c.__dict__ for c in coalitions])

@app.route('/coalitions/<coalition_id>', methods=['GET'])
def get_coalition(coalition_id):
    coalition = storage.get_coalition(coalition_id)
    if not coalition:
        abort(404, description="Coalition not found")
    return jsonify(coalition.__dict__)

@app.route('/coalitions', methods=['POST'])
def create_coalition():
    data = request.json
    required = ['coalition_id', 'name', 'goal', 'members']
    if not all(k in data for k in required):
        abort(400, description=f"Missing fields: {required}")
    coalition = CoalitionRecord(
        coalition_id=data['coalition_id'],
        name=data['name'],
        goal=data['goal'],
        members=data['members'],
        status=data.get('status', 'forming'),
        created_at=datetime.utcnow().isoformat(),
        impact_metrics=data.get('impact_metrics', {
            "people_helped": 0,
            "funds_raised": 0.0,
            "projects_completed": 0
        })
    )
    storage.save_coalition(coalition)
    return jsonify({"status": "created", "coalition": coalition.__dict__}), 201

@app.route('/coalitions/<coalition_id>/impact', methods=['POST'])
def update_impact(coalition_id):
    """Increment an impact metric."""
    data = request.json
    if not data or 'metric' not in data or 'value' not in data:
        abort(400, description="Requires: metric, value")
    success = storage.update_impact(coalition_id, data['metric'], data['value'])
    if not success:
        abort(404, description="Coalition not found")
    return jsonify({"status": "updated", "coalition_id": coalition_id})

# --- Health check ---

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "division-unity-api"})

# --- CLI entrypoint ---

def main():
    """Run API server."""
    import argparse
    parser = argparse.ArgumentParser(description="Division-Unity REST API")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
