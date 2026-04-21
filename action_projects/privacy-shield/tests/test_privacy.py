#!/usr/bin/env python3
"""
Privacy Shield — Tests
"""

import sys
from pathlib import Path
import tempfile
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from privacy_shield.crypto import CryptoEngine, encrypt_file, decrypt_file
from privacy_shield.browser import FirefoxHardener, ChromeHardener
from privacy_shield.vpn import VPNChecker

def test_crypto_roundtrip():
    """Encrypt and decrypt a file."""
    test_data = b"Secret message: Hello, world! 123"
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(test_data)
        input_path = Path(tf.name)
    output_path = input_path.with_suffix('.enc')
    decrypted_path = output_path.with_suffix('.dec')

    # Encrypt
    pwd = "test_password_123"
    enc = encrypt_file(input_path, pwd)
    assert enc.exists(), "Encrypted file not created"
    assert enc.suffix == '.enc'

    # Decrypt
    dec = decrypt_file(enc, pwd)
    assert dec.exists(), "Decrypted file not created"
    assert dec.read_bytes() == test_data, "Content mismatch"

    # Cleanup
    input_path.unlink(missing_ok=True)
    output_path.unlink(missing_ok=True)
    dec.unlink(missing_ok=True)
    print("✅ Crypto: encryption/decryption round-trip works")

def test_firefox_prefs():
    """Generate Firefox prefs.js and validate content."""
    with tempfile.TemporaryDirectory() as td:
        out = FirefoxHardener.generate_prefs_file(Path(td) / "prefs.js")
        content = out.read_text()
        assert "user_pref" in content
        assert 'media.peerconnection.enabled' in content
        assert 'false' in content or 'true' in content
        print("✅ FirefoxHardener: prefs.js generated successfully")

def test_chrome_policies():
    """Generate Chrome policies.json."""
    with tempfile.TemporaryDirectory() as td:
        out = ChromeHardener.generate_policy_json(Path(td) / "policies.json")
        data = json.loads(out.read_text())
        assert "policies" in data
        assert "IncognitoModeAvailability" in data["policies"]
        print("✅ ChromeHardener: policies.json generated successfully")

def test_vpn_checker():
    """VPNChecker can fetch public IP."""
    checker = VPNChecker()
    ip = checker.get_public_ip(force_refresh=True)
    if ip:
        assert isinstance(ip, str) and '.' in ip
        print(f"✅ VPNChecker: public IP fetched — {ip}")
    else:
        print("⚠️ VPNChecker: could not fetch public IP (network issue)")

if __name__ == "__main__":
    import json
    test_crypto_roundtrip()
    test_firefox_prefs()
    test_chrome_policies()
    test_vpn_checker()
    print("\n🎉 Privacy Shield core tests passed!")
