"""
Privacy & safe reporting module.
Ensures victim data is encrypted and reporting is anonymous (unless victim consents to identify).

NOTE: Requires `cryptography` for Fernet encryption. Falls back to base64 if not available.
Production deployment should: pip install -r requirements.txt
"""

import base64
import json
import os

# Try cryptography; fall back to obfuscation-only if missing
try:
    from cryptography.fernet import Fernet
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False


class PrivacyShield:
    """
    Encrypts sensitive victim data. Key can be derived from environment variable.
    If cryptography library is missing, uses base64 encoding (NOT secure for production).
    """
    def __init__(self, key_env: str = "SLAVERY_FREEDOM_KEY"):
        self.key_str = os.getenv(key_env, "dev-key-please-set-SLAVERY_FREEDOM_KEY")
        if _HAS_CRYPTO:
            # Derive a 32-byte key (Fernet requires 32 urlsafe base64 bytes)
            import hashlib
            key_bytes = hashlib.sha256(self.key_str.encode()).digest()
            self.key = base64.urlsafe_b64encode(key_bytes)
            self.cipher = Fernet(self.key)
        else:
            self.cipher = None
            print("⚠️  cryptography not installed — encryption disabled (base64 only). Install requirements.txt for production.")

    def encrypt(self, data: str) -> bytes:
        """Encrypt string data. Returns base64-encoded payload."""
        if _HAS_CRYPTO:
            return self.cipher.encrypt(data.encode('utf-8'))
        else:
            # Fallback: simple base64 (obfuscation only, NOT secure)
            return base64.b64encode(data.encode('utf-8'))

    def decrypt(self, token: bytes) -> str:
        """Decrypt bytes to string."""
        if _HAS_CRYPTO:
            return self.cipher.decrypt(token).decode('utf-8')
        else:
            return base64.b64decode(token).decode('utf-8')

    def anonymize_report(self, report: dict) -> dict:
        """
        Remove personally identifying fields unless consent given.
        Fields kept: indicators, location (city level), outcome needed.
        Fields removed/dropped: full name, exact address, ID numbers.
        """
        anonymized = {
            "indicators": report.get("indicators", []),
            "risk_level": report.get("risk_level", "UNKNOWN"),
            "sector": report.get("sector", "unknown"),
            "city": report.get("city", "unknown"),
            "needs": report.get("needs", []),
            "contact_consent": report.get("contact_consent", False)
        }
        return anonymized


REPORT_TEMPLATE = """
# Slavery Freedom — Incident Report

## ⚠️ Risk Level: {risk_level}

## 🔍 Indicators Found
{indicators_list}

## 📍 Location
{country} — {city}

## 🏭 Sector
{sector}

## 🆘 Immediate Needs
{needs_list}

## 🔐 Privacy
This report was submitted anonymously. To follow up, consent required.
"""


def generate_report_html(report: dict) -> str:
    """Generate a human-readable HTML report for authorities."""
    indicators_list = "\n".join([f"- {i}" for i in report["indicators"]])
    needs_list = "\n".join([f"- {n}" for n in report["needs"]])
    return REPORT_TEMPLATE.format(
        risk_level=report["risk_level"],
        indicators_list=indicators_list,
        country=report.get("country", "unknown"),
        city=report.get("city", "unknown"),
        sector=report.get("sector", "unknown"),
        needs_list=needs_list
    )
