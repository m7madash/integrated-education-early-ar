#!/usr/bin/env python3
"""Tests for extremism-moderation detector and responder."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.moderation_engine.detector import ExtremismDetector
from src.moderation_engine.responder import ModerationResponder
from src.moderation_engine.privacy import anonymize_user, encrypt_log_entry, generate_report_id

def test_extreme_violence_text():
    d = ExtremismDetector()
    text = "Kill all infidels! Exterminate them all."
    result = d.score_text(text)
    assert result['score'] >= 70, f"Expected >=70, got {result['score']}"
    assert "CRITICAL" in result['verdict']
    print("✅ Extreme violence text → CRITICAL")

def test_moderate_speech():
    d = ExtremismDetector()
    text = "I disagree with your view, but respect your right to hold it."
    result = d.score_text(text)
    assert result['score'] < 20, f"Expected <20, got {result['score']}"
    print("✅ Moderate speech → BALANCED")

def test_sectarian_extremism():
    d = ExtremismDetector()
    text = "Only our sect is saved; everyone else is doomed to hell."
    result = d.score_text(text)
    assert result['score'] >= 40, f"Expected >=40, got {result['score']}"
    print("✅ Sectarian extremism → flagged")

def test_balanced_statement():
    d = ExtremismDetector()
    text = "We should seek common ground and work together despite differences."
    result = d.score_text(text)
    assert result['score'] == 0 or result['score'] < 5
    print("✅ Balanced statement → no extremism")

def test_responder_high_risk():
    r = ModerationResponder()
    response = r.craft_response("Kill all!", 80)
    assert "REMOVE" in response or "safety" in response.lower()
    print("✅ High-risk → removal recommendation")

def test_privacy_anonymize():
    user = "user_extremist_123"
    anon = anonymize_user(user)
    assert len(anon) == 12
    assert user not in anon
    print("✅ User ID anonymization works")

def test_privacy_report_id():
    rid = generate_report_id()
    assert rid.startswith("RPT-")
    assert len(rid) > 15
    print("✅ Report ID generation works")

def test_encryption_roundtrip():
    entry = {"text": "Extremist content", "user": "test_user"}
    enc = encrypt_log_entry(entry, "key")
    # Decrypt (we know key)
    import base64
    enc_bytes = base64.b64decode(enc)
    key = "key"
    decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(enc_bytes.decode('utf-8')))
    import json
    dec_entry = json.loads(decrypted)
    assert dec_entry == entry
    print("✅ Log encryption/decryption works")

if __name__ == "__main__":
    print("=== Extremism-Moderation Tests ===\n")
    test_extreme_violence_text()
    test_moderate_speech()
    test_sectarian_extremism()
    test_balanced_statement()
    test_responder_high_risk()
    test_privacy_anonymize()
    test_privacy_report_id()
    test_encryption_roundtrip()
    print("\n✅ All 8 tests passed!")
