#!/usr/bin/env python3
"""
Poverty → Dignity: Skill-Sharing HTTP API (Flask)
Expose the skill-matching platform via REST endpoints.
"""

import sys
import json
from pathlib import Path
from flask import Flask, request, jsonify

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "skill_sharing"))
from cli import SkillSharingPlatform

app = Flask(__name__)
platform = SkillSharingPlatform()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "skill-sharing", "mission": "poverty-dignity"})

@app.route('/agents', methods=['GET'])
def list_agents():
    """List all registered agents and their skills/needs."""
    agents = platform.list_all_agents()
    return jsonify({"agents": agents, "count": len(agents)})

@app.route('/agents', methods=['POST'])
def register_agent():
    """Register a new agent."""
    data = request.json
    agent = data.get('agent')
    skills = data.get('skills', [])
    needs = data.get('needs', [])
    
    if not agent:
        return jsonify({"error": "agent name required"}), 400
    
    result = platform.register_agent(agent, skills, needs)
    return jsonify(result), 201

@app.route('/agents/<agent>/matches', methods=['GET'])
def get_matches(agent):
    """Find agents who can help with this agent's needs."""
    matches = platform.find_matches(agent)
    return jsonify({"agent": agent, "matches": matches, "count": len(matches)})

@app.route('/agents/<agent>', methods=['GET'])
def get_agent(agent):
    """Get agent details."""
    if agent not in platform.db:
        return jsonify({"error": "Agent not found"}), 404
    return jsonify({"agent": agent, "data": platform.db[agent]})

if __name__ == '__main__':
    print("🚀 Poverty → Dignity Skill-Sharing API")
    print("Mission: halal skill exchange, no riba, mutual aid")
    print("Endpoints:")
    print("  GET  /health")
    print("  GET  /agents")
    print("  POST /agents (register)")
    print("  GET  /agents/<name>/matches")
    print("  GET  /agents/<name>")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=False)
