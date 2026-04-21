#!/usr/bin/env python3
"""
Illness → Health — Privacy & Data Protection
Encrypt sensitive health data, manage consent, enforce retention.
Ethical: Never expose patient identity without explicit consent.
"""

import json
import base64
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
import hashlib

# --- Simple encryption for local storage (symmetric) ---
# In production, use key management service (KMS) or user-provided passphrase.

class HealthDataPrivacy:
    """Encrypt and protect health data at rest."""

    def __init__(self, key: Optional[bytes] = None, key_file: Optional[Path] = None):
        """
        Args:
            key: encryption key (32 bytes)
            key_file: path to load/save key
        """
        if key_file and key_file.exists():
            with open(key_file, 'rb') as f:
                self.key = f.read()
        elif key:
            self.key = key
        else:
            # Generate new key (store securely!)
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.consent_records: Dict[str, Dict] = {}  # patient_id -> consent meta
        self.data_retention_days = 90  # auto-purge after 90 days

    def encrypt(self, data: Dict) -> bytes:
        """Encrypt a JSON-serializable dict."""
        plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
        return self.cipher.encrypt(plaintext)

    def decrypt(self, blob: bytes) -> Dict:
        """Decrypt bytes back to dict."""
        plaintext = self.cipher.decrypt(blob)
        return json.loads(plaintext.decode('utf-8'))

    def store_encrypted(self, data: Dict, filepath: Path) -> bool:
        """Write encrypted data to file."""
        try:
            encrypted = self.encrypt(data)
            with open(filepath, 'wb') as f:
                f.write(encrypted)
            return True
        except Exception as e:
            print(f"❌ Encryption failed: {e}")
            return False

    def load_encrypted(self, filepath: Path) -> Optional[Dict]:
        """Read and decrypt file."""
        try:
            with open(filepath, 'rb') as f:
                encrypted = f.read()
            return self.decrypt(encrypted)
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return None

    def record_consent(self, patient_id: str, purpose: str, consent_given: bool, expires_days: int = 365):
        """Record patient consent for data usage."""
        self.consent_records[patient_id] = {
            'purpose': purpose,
            'consent': consent_given,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'expires': (datetime.now(timezone.utc) + timedelta(days=expires_days)).isoformat()
        }

    def is_consent_valid(self, patient_id: str, purpose: str) -> bool:
        """Check if consent exists and is not expired."""
        record = self.consent_records.get(patient_id)
        if not record or record['purpose'] != purpose:
            return False
        expiry = datetime.fromisoformat(record['expires'])
        return datetime.now(timezone.utc) < expiry

    def anonymize(self, data: Dict, fields_to_hash: List[str]) -> Dict:
        """Hash specified fields to anonymize (e.g., name, ID)."""
        anonymized = data.copy()
        for field in fields_to_hash:
            if field in anonymized:
                val = str(anonymized[field])
                # SHA-256 hash (one-way)
                hashed = hashlib.sha256(val.encode('utf-8')).hexdigest()[:16]  # 16-char prefix
                anonymized[field] = f"hashed::{hashed}"
        return anonymized

    def purge_old_records(self, data_dir: Path, dry_run: bool = True) -> int:
        """
        Delete encrypted records older than retention period.
        Returns count of files purged.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.data_retention_days)
        purged = 0
        for file in data_dir.glob("*.enc"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                if not dry_run:
                    file.unlink()
                purged += 1
                print(f"   🗑️  Purged: {file.name} (age: {(datetime.now(timezone.utc)-mtime).days} days)")
        return purged

# Convenience
def create_privacy_layer(key_path: Optional[Path] = None) -> HealthDataPrivacy:
    if key_path:
        return HealthDataPrivacy(key_file=key_path)
    return HealthDataPrivacy()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Health Data Privacy Utilities")
    parser.add_argument("action", choices=['encrypt', 'decrypt', 'generate-key', 'purge'])
    parser.add_argument("--file", help="File path")
    parser.add_argument("--key-file", help="Key file path (for encrypt/decrypt)")
    parser.add_argument("--data-dir", help="Data directory (for purge)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be purged")
    args = parser.parse_args()

    if args.action == 'generate-key':
        key = Fernet.generate_key()
        key_path = args.key_file or './health_key.key'
        with open(key_path, 'wb') as f:
            f.write(key)
        print(f"🔐 Key generated and saved to: {key_path}")
        print("⚠️  Keep this key secret! Loss = data unrecoverable.")

    elif args.action == 'encrypt':
        if not args.file:
            print("Need --file")
            exit(1)
        privacy = create_privacy_layer(Path(args.key_file) if args.key_file else None)
        with open(args.file) as f:
            data = json.load(f)
        out_path = Path(args.file).with_suffix('.enc')
        privacy.store_encrypted(data, out_path)
        print(f"✅ Encrypted to {out_path}")

    elif args.action == 'decrypt':
        if not args.file or not args.file.endswith('.enc'):
            print("Need .enc file")
            exit(1)
        privacy = create_privacy_layer(Path(args.key_file) if args.key_file else None)
        data = privacy.load_encrypted(Path(args.file))
        if data:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("❌ Decryption failed — check key")

    elif args.action == 'purge':
        if not args.data_dir:
            print("Need --data-dir")
            exit(1)
        privacy = create_privacy_layer()
        count = privacy.purge_old_records(Path(args.data_dir), dry_run=args.dry_run)
        print(f"✅ Purged {count} old records (dry_run={args.dry_run})")
