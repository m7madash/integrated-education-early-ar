#!/usr/bin/env python3
"""Privacy module — health data protection (XOR demo, extensible to AES)."""

import base64

def xor_encrypt(data: str, key: str) -> str:
    """XOR encryption demo (simple — replace with AES-256 in production)."""
    if not data or not key:
        raise ValueError("Data and key required")
    # Simple XOR cyclic
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
    return base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')

def xor_decrypt(enc_b64: str, key: str) -> str:
    """Decrypt XOR-encrypted base64 string."""
    enc = base64.b64decode(enc_b64).decode('utf-8')
    decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(enc))
    return decrypted

def anonymize_name(name: str) -> str:
    """Remove PII from patient name for logs."""
    if not name:
        return "anonymous"
    # Keep first letter + asterisks
    return name[0] + "*" * (len(name) - 1)

if __name__ == "__main__":
    # Demo round-trip
    secret = "Patient: Ahmad, Symptoms: high fever, cough"
    key = "healthbot"
    enc = xor_encrypt(secret, key)
    dec = xor_decrypt(enc, key)
    print(f"Original: {secret}")
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {dec}")
    assert dec == secret, "Round-trip failed"
    print("✅ Privacy module works!")
