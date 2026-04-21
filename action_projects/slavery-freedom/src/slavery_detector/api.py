"""
REST API — Slavery → Freedom detector.

Endpoints:
  GET  /health — service status
  POST /detect — analyze text + return risk + resources
  GET  /resources/:country — list hotlines & NGOs
  POST /report — generate encrypted safe report
"""

from flask import Flask, request, jsonify
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from slavery_detector.detector import SlaveryDetector
from slavery_detector.knowledge import get_local_resources
from slavery_detector.privacy import PrivacyShield, generate_report_html

app = Flask(__name__)
detector = SlaveryDetector()
privacy = PrivacyShield()

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "slavery-freedom", "version": "0.1.0"})

@app.route("/detect", methods=["POST"])
def detect():
    """
    Expected JSON:
    {
      "text": "the suspicious message or ad",
      "country_code": "PS" (optional, default PS),
      "city": "Gaza" (optional)
    }
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text is required"}), 400
    country = data.get("country_code", "PS")
    city = data.get("city", "unknown")

    analysis = detector.analyze(text, country_code=country, city=city)
    return jsonify(analysis), 200

@app.route("/resources/<country_code>", methods=["GET"])
def resources(country_code: str):
    """
    Return hotlines, NGOs, legal frameworks for the given country.
    """
    resources = get_local_resources(country_code.upper())
    return jsonify(resources), 200

@app.route("/report", methods=["POST"])
def create_report():
    """
    Create an encrypted safe report.
    Body: { "text": "...", "country_code": "...", "city": "...", "consent": true/false }
    Returns: { "encrypted_report": "...", "instructions": "..." }
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    country = data.get("country_code", "PS")
    city = data.get("city", "unknown")
    consent = data.get("consent", False)

    analysis = detector.analyze(text, country_code=country, city=city)
    safe_report = detector.generate_safe_report(analysis, victim_consent=consent)
    return jsonify(safe_report), 200

@app.route("/emergency", methods=["GET"])
def emergency():
    """Return all emergency contacts across all supported regions."""
    contacts = []
    for code, data in getattr(get_local_resources, "ALL", {}).items():
        for hotline in data.get("hotlines", []):
            contacts.append({**hotline, "country": code})
    return jsonify({"emergency_contacts": contacts}), 200

if __name__ == "__main__":
    app.run(port=5009, debug=True)
