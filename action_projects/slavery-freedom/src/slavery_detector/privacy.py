#!/usr/bin/env python3
"""Privacy module — protect victim identities in slavery reports."""

import hashlib
import base64

def anonymize_id(real_id: str, salt: str = "slavery-free-2026") -> str:
    """One-way hash for victim/supplier IDs (non-reversible)."""
    return hashlib.sha256((real_id + salt).encode()).hexdigest()[:12]

def encrypt_report(report_text: str, key: str) -> str:
    """XOR encrypt report for confidential storage."""
    if not report_text or not key:
        raise ValueError("Text and key required")
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(report_text))
    return base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')

def decrypt_report(enc_b64: str, key: str) -> str:
    """Decrypt report (only for authorized investigators)."""
    enc = base64.b64decode(enc_b64).decode('utf-8')
    decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(enc))
    return decrypted

def redact_pii(text: str) -> str:
    """Replace PII with [REDACTED]."""
    import re
    # Patterns: emails, phones, IDs, full names (basic)
    patterns = [
        (r'\S+@\S+', '[EMAIL]'),
        (r'\+\d{10,}', '[PHONE]'),
        (r'\b\d{6,}\b', '[ID]'),
        (r'([A-Z][a-z]+ [A-Z][a-z]+)', '[NAME]')  # simple full name
    ]
    for pattern, repl in patterns:
        text = re.sub(pattern, repl, text)
    return text

if __name__ == "__main__":
    # Test victim ID anonymization
    victim = "VIC-2026-04-19-001"
    anon = anonymize_id(victim)
    print(f"Original ID: {victim}")
    print(f"Anonymized: {anon}")

    # Test encrypt/decrypt
    secret = "Supplier A: 60+ hrs/week, no contracts, wages withheld"
    enc = encrypt_report(secret, "detective-key")
    dec = decrypt_report(enc, "detective-key")
    print(f"\nOriginal: {secret}")
    print(f"Enc: {enc[:50]}...")
    print(f"Dec: {dec}")
    assert dec == secret
    print("✅ Privacy module works!")
