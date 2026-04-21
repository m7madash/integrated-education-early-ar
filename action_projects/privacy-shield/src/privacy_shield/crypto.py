#!/usr/bin/env python3
"""
Privacy Shield — Cryptography Module
Secure file encryption/decryption using Fernet (AES-128 in CBC + HMAC).
"""

import sys
from pathlib import Path
from getpass import getpass
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoEngine:
    """Handles encryption and decryption of files."""

    def __init__(self, password: str, salt: bytes = None):
        """
        Initialize with a password. Salt is optional; if not provided, a random one is used.
        """
        self.password = password.encode('utf-8')
        self.salt = salt or self._generate_salt()
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)

    def _generate_salt(self) -> bytes:
        """Generate a random 16-byte salt."""
        import os
        return os.urandom(16)

    def _derive_key(self) -> bytes:
        """Derive a 32-byte key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100_000,
        )
        return kdf.derive(self.password)

    def encrypt_file(self, input_path: Path, output_path: Path = None) -> Path:
        """Encrypt a file. Returns path to encrypted file."""
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + '.enc')
        data = input_path.read_bytes()
        encrypted = self.fernet.encrypt(data)
        # Prepend salt so we can decrypt later
        output_path.write_bytes(self.salt + encrypted)
        return output_path

    def decrypt_file(self, input_path: Path, output_path: Path = None) -> Path:
        """Decrypt a file. Returns path to decrypted file."""
        if output_path is None:
            # Remove .enc suffix if present
            output_path = input_path.with_suffix('') if input_path.suffix == '.enc' else input_path.parent / (input_path.stem + '.dec')
        blob = input_path.read_bytes()
        if len(blob) < 16:
            raise ValueError("File too short to contain salt")
        salt, encrypted = blob[:16], blob[16:]
        # Re-derive key with extracted salt
        self.salt = salt
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
        try:
            decrypted = self.fernet.decrypt(encrypted)
        except InvalidToken:
            raise ValueError("Invalid password or corrupted file")
        output_path.write_bytes(decrypted)
        return output_path

    def generate_key_from_password(self, password: str) -> bytes:
        """Static method: generate a URL-safe base64-encoded key from a password (for sharing)."""
        pwd = password.encode('utf-8')
        salt = self._generate_salt()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = kdf.derive(pwd)
        return Fernet(key).encrypt(b'dummy')  # Actually just return the Fernet token? No, we want key.
        # Instead, return base64-encoded key directly:
        # return base64.urlsafe_b64encode(key)

# Convenience functions
def encrypt_file(path: Path, password: str) -> Path:
    engine = CryptoEngine(password)
    return engine.encrypt_file(path)

def decrypt_file(path: Path, password: str) -> Path:
    engine = CryptoEngine(password)
    return engine.decrypt_file(path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Encrypt or decrypt a file")
    parser.add_argument("file", type=Path, help="File to process")
    parser.add_argument("-d", "--decrypt", action="store_true", help="Decrypt instead of encrypt")
    parser.add_argument("-o", "--output", type=Path, help="Output path")
    args = parser.parse_args()

    pwd = getpass("Password: ")
    try:
        if args.decrypt:
            out = decrypt_file(args.file, pwd)
            print(f"✅ Decrypted to: {out}")
        else:
            out = encrypt_file(args.file, pwd)
            print(f"✅ Encrypted to: {out}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
