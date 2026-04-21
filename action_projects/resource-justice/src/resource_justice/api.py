#!/usr/bin/env python3
"""
Resource Justice — Flask REST API
Endpoints for budget tracking, impact calculation, and advocacy.
"""

from flask import Flask, jsonify, request
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from resource_justice.collector import load_budgets
from resource_justice.calculator import calculate_impact

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "resource-justice"})

@app.route('/budgets')
def get_budgets():
    """Return all country budgets."""
    budgets = load_budgets()
    return jsonify(budgets)

@app.route('/budget/<country>')
def get_budget(country):
    """Return budget for specific country."""
    budgets = load_budgets()
    if country not in budgets:
        return jsonify({"error": "Country not found"}), 404
    return jsonify(budgets[country])

@app.route('/impact/<country>')
def get_impact(country):
    """
    Calculate impact for a country.
    Query params:
      percent (required): percentage to reallocate
    """
    percent = request.args.get('percent', type=float)
    if percent is None:
        return jsonify({"error": "Missing 'percent' query parameter"}), 400
    try:
        result = calculate_impact(country, percent)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/reallocate', methods=['POST'])
def reallocate():
    """
    Suggest reallocation. Returns impact metrics.
    Body: { "country": "X", "percent": 10 }
    """
    data = request.get_json()
    country = data.get('country')
    percent = data.get('percent')
    if not country or not percent:
        return jsonify({"error": "Missing country or percent"}), 400
    try:
        result = calculate_impact(country, percent)
        return jsonify({
            "message": f"Reallocating {percent}% of {country}'s military budget would yield:",
            "impact": result
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/leaderboard')
def leaderboard():
    """Rank countries by potential impact (meals saved per $1B reallocated)."""
    budgets = load_budgets()
    rankings = []
    for country, data in budgets.items():
        try:
            impact_1p = calculate_impact(country, 1.0)
            rankings.append({
                "country": country,
                "meals_per_billion": impact_1p["meals"] / (data["military_budget_usd"] / 1e9),
                "military_budget_usd": data["military_budget_usd"]
            })
        except Exception:
            continue
    rankings.sort(key=lambda x: x["meals_per_billion"], reverse=True)
    return jsonify(rankings[:10])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
