#!/usr/bin/env python3
"""Privacy Shield Demo — without external deps (pure stdlib)"""

import sys
from pathlib import Path

# Simple XOR encryption for demo (NOT for production!)
def simple_encrypt(data: bytes, password: str) -> bytes:
    """Simple XOR cipher — for demo only"""
    salt = b'PrivacyShield2026!'
    key = (password + salt.decode()).encode()
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def simple_decrypt(data: bytes, password: str) -> bytes:
    """Decrypt XOR (same as encrypt)"""
    return simple_encrypt(data, password)  # XOR symmetric

def demo_encrypt_decrypt():
    print("🔐 Privacy Shield Demo — File Encryption")
    print("="*50)
    
    # Create demo file
    demo_text = "هذا نص سري يجب تشفيره. History: 2026-04-19."
    demo_file = Path('/tmp/secret_message.txt')
    demo_file.write_text(demo_text, encoding='utf-8')
    print(f"📄 Created: {demo_file}")
    print(f"   Content: {demo_text}")
    
    # Encrypt
    password = "MyStrongPassword123!"
    encrypted = simple_encrypt(demo_text.encode('utf-8'), password)
    enc_file = Path('/tmp/secret_message.txt.enc')
    enc_file.write_bytes(encrypted)
    print(f"\n🔒 Encrypted: {enc_file}")
    print(f"   Size: {len(encrypted)} bytes")
    
    # Decrypt
    decrypted = simple_decrypt(encrypted, password)
    dec_text = decrypted.decode('utf-8')
    dec_file = Path('/tmp/secret_message_decrypted.txt')
    dec_file.write_text(dec_text, encoding='utf-8')
    print(f"\n🔓 Decrypted: {dec_file}")
    print(f"   Content: {dec_text}")
    
    # Verify
    if dec_text == demo_text:
        print("\n✅ Encryption/Decryption works!")
    else:
        print("\n❌ Failed")
    
    print("\n⚠️  Note: This is XOR demo only. Real implementation uses AES-256.")
    print("   Next: Add `cryptography` library for Fernet/AES.")

def demo_breach_check():
    print("\n\n🔍 Privacy Shield — Breach Check Demo")
    print("="*50)
    print("Email: test@example.com")
    print("Status: ✅ Not found in public breaches (demo)")
    print("\n⚠️  Real implementation uses HaveIBeenPwned API v3")

def demo_browser_harden():
    print("\n\n🛡️  Privacy Shield — Browser Hardening Demo")
    print("="*50)
    print("Firefox settings to enable:")
    print("   • privacy.resistFingerprinting = True")
    print("   • privacy.firstparty.isolate = True")
    print("   • network.trr.mode = 2 (DNS-over-HTTPS)")
    print("   • dom.security.https_only_mode = True")
    print("\n✅ Would apply via Firefox profile config")

if __name__ == '__main__':
    demo_encrypt_decrypt()
    demo_breach_check()
    demo_browser_harden()
    print("\n" + "="*50)
    print("Privacy Shield MVP Demo Complete!")
    print("Action Before Speech: Tools built, now ready for education.")
    print("="*50)
