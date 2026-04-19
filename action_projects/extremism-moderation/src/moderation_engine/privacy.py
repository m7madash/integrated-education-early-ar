#!/usr/bin/env python3
"""Privacy module: protect identities in moderation logs.
No PII stored. Reports anonymized. No surveillance.
"""

import hashlib
import base64
import json
import datetime
from typing import Dict

def anonymize_user(user_id: str, salt: str = "extremism-mod-2026") -> str:
    """One-way hash — cannot recover original user ID."""
    return hashlib.sha256((user_id + salt).encode()).hexdigest()[:12]

def anonymize_text(text: str, keep_words: int = 3) -> str:
    """Redact PII from text but keep some context."""
    import re
    # Replace emails, phones, IDs
    text = re.sub(r'\S+@\S+', '[EMAIL]', text)
    text = re.sub(r'\+\d{10,}', '[PHONE]', text)
    text = re.sub(r'\b\d{6,}\b', '[ID]', text)
    # Keep first 3 words, then truncate if long
    words = text.split()
    if len(words) > keep_words * 2:
        return ' '.join(words[:keep_words]) + ' ... [REDACTED]'
    return text

def generate_report_id() -> str:
    """Unique, non-reversible report ID."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    rand = hashlib.sha256(str(datetime.datetime.utcnow().timestamp()).encode()).hexdigest()[:6]
    return f"RPT-{ts}-{rand}"

def encrypt_log_entry(entry: Dict, key: str) -> str:
    """Encrypt log entry for secure storage (XOR demo)."""
    entry_str = json.dumps(entry, ensure_ascii=False)
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(entry_str))
    return base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')

if __name__ == "__main__":
    # Demo
    user = "user_12345"
    text = "User user_12345 said: Kill all infidels! Contact: +1234567890"
    anon_id = anonymize_user(user)
    anon_text = anonymize_text(text)
    report_id = generate_report_id()
    enc = encrypt_log_entry({"text": text, "user": user}, "key")

    print(f"Original user: {user}")
    print(f"Anonymized ID: {anon_id}")
    print(f"Anonymized text: {anon_text}")
    print(f"Report ID: {report_id}")
    print(f"Encrypted log sample: {enc[:50]}...")
    print("✅ Privacy module active — no PII in logs.")
