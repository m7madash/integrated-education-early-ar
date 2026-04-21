#!/usr/bin/env python3
"""
Media Integrity — Flask REST API
Expose media integrity analysis as web service.
"""

import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from flask import Flask, request, jsonify, abort
from werkzeug.utils import secure_filename

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.media_integrity.detector import MediaDetector, analyze as analyze_media
from src.media_integrity.image import analyze_image as analyze_image_core
from src.media_integrity.text import analyze_text as analyze_text_core
from src.media_integrity.source import analyze_source as analyze_source_core
from src.media_integrity.video import analyze_video as analyze_video_core
from src.media_integrity.social import analyze_bot as analyze_bot_core, analyze_network as analyze_network_core

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/media_integrity_uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['JSON_AS_ASCII'] = False

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage (for demo). In production, use Redis/DB.
REPORTS = {}

detector = MediaDetector()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'media-integrity',
        'version': '0.1.0',
        'timestamp': datetime.now(timezone=None).isoformat()
    })

@app.route('/components', methods=['GET'])
def components():
    return jsonify({
        'components': [
            {'name': 'image_forensics', 'description': 'Error Level Analysis, metadata, noise consistency'},
            {'name': 'fake_news_detector', 'description': 'Pattern matching, emotional language, source credibility'},
            {'name': 'source_reputation', 'description': 'Domain age, SSL, contact, corrections, citations'},
            {'name': 'video_deepfake', 'description': 'Frame artifacts, blink inconsistencies, lip-sync'},
            {'name': 'bot_detector', 'description': 'Account behavior, content repetition, timing patterns'}
        ]
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze media item.
    Expects:
      - file upload (image/video) OR
      - JSON body with 'item' and optional 'type', 'context'
    """
    report_id = str(uuid.uuid4())
    item_type = request.form.get('type') or request.args.get('type')
    context = {}

    # Check for file upload
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            abort(400, description="No file selected")
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        item = filepath
        # Auto-detect type from MIME
        if not item_type:
            mime, _ = mimetypes.guess_type(filepath)
            if mime:
                if mime.startswith('image/'):
                    item_type = 'image'
                elif mime.startswith('video/'):
                    item_type = 'video'
                else:
                    item_type = 'text'  # treat unknown as text
        # context: source_url if provided
        if request.form.get('source_url'):
            context['source_url'] = request.form['source_url']

    elif request.is_json:
        data = request.get_json()
        item = data.get('item')
        if not item:
            abort(400, description="Missing 'item' in request body")
        item_type = item_type or data.get('type')
        context = data.get('context', {})
    else:
        # form data without file? maybe text in 'item'
        item = request.form.get('item')
        if not item:
            abort(400, description="No item provided")

    if not item_type:
        # fallback auto-detection
        item_type = detector._detect_type(item)

    # Run analysis
    try:
        report = detector.analyze(item, item_type=item_type, context=context if context else None)
        report_dict = asdict(report)
        report_dict['report_id'] = report_id
        REPORTS[report_id] = report_dict
        return jsonify({
            'success': True,
            'report_id': report_id,
            'verdict': report.verdict,
            'score': report.overall_integrity_score,
            'timestamp': report.timestamp
        }), 200
    except Exception as e:
        app.logger.error(f"Analysis error: {e}", exc_info=True)
        abort(500, description=str(e))

@app.route('/results/<report_id>', methods=['GET'])
def get_result(report_id):
    report = REPORTS.get(report_id)
    if not report:
        abort(404, description="Report not found")
    return jsonify(report)

@app.route('/batch', methods=['POST'])
def batch_analyze():
    """
    Accept multiple items in one call.
    JSON array: [{'item': ..., 'type': ...}, ...]
    """
    if not request.is_json:
        abort(400, description="Expected JSON")
    items = request.get_json()
    if not isinstance(items, list):
        abort(400, description="Expected a list of items")

    results = []
    for item_data in items:
        item = item_data.get('item')
        item_type = item_data.get('type')
        context = item_data.get('context', {})
        try:
            report = detector.analyze(item, item_type=item_type, context=context)
            results.append({
                'item': str(item)[:50],
                'success': True,
                'verdict': report.verdict,
                'score': report.overall_integrity_score
            })
        except Exception as e:
            results.append({
                'item': str(item)[:50],
                'success': False,
                'error': str(e)
            })
    return jsonify({'batch_results': results}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Expose basic usage statistics."""
    total_analyses = len(REPORTS)
    verdict_counts = {'PASS': 0, 'SUSPICIOUS': 0, 'FAIL': 0}
    for r in REPORTS.values():
        v = r.get('verdict')
        if v in verdict_counts:
            verdict_counts[v] += 1
    return jsonify({
        'total_analyses': total_analyses,
        'verdicts': verdict_counts,
        'uptime_seconds': 3600  # placeholder (would need real uptime)
    })

# --- CLI runner ---
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Media Integrity API")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    print(f"🚀 Starting Media Integrity API on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
