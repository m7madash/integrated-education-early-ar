#!/usr/bin/env python3
"""
Privacy Shield — VPN Status Checker
Detect if VPN is active by comparing public IP with local IP.
"""

import requests
import json
from pathlib import Path
from typing import Optional, Tuple

class VPNChecker:
    """Check if a VPN connection is active."""

    PUBLIC_IP_SERVICES = [
        "https://api.ipify.org",
        "https://ident.me",
        "https://checkip.amazonaws.com",
    ]

    def __init__(self, cache_file: Path = Path("/tmp/vpn_cache.json")):
        self.cache_file = cache_file
        self.cached_ip = None
        self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    data = json.load(f)
                    self.cached_ip = data.get("ip")
            except Exception:
                pass

    def _save_cache(self, ip: str):
        with open(self.cache_file, 'w') as f:
            json.dump({"ip": ip, "timestamp": None}, f)

    def get_public_ip(self, force_refresh: bool = False) -> Optional[str]:
        """Get current public IP address."""
        if not force_refresh and self.cached_ip:
            return self.cached_ip
        for service in self.PUBLIC_IP_SERVICES:
            try:
                resp = requests.get(service, timeout=5)
                if resp.status_code == 200:
                    ip = resp.text.strip()
                    self.cached_ip = ip
                    self._save_cache(ip)
                    return ip
            except Exception:
                continue
        return None

    def is_vpn_active(self, known_non_vpn_ip: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if VPN is likely active.
        If known_non_vpn_ip (your home IP without VPN) is provided, compare.
        Otherwise, just return current public IP and let user decide.
        """
        current_ip = self.get_public_ip(force_refresh=True)
        if not current_ip:
            return False, None

        if known_non_vpn_ip:
            if current_ip != known_non_vpn_ip:
                return True, current_ip
            else:
                return False, current_ip
        else:
            # No baseline — cannot determine definitively
            return None, current_ip

    def suggest_providers(self) -> List[str]:
        """Return list of recommended VPN providers (ethically vetted)."""
        return [
            "Mullvad (no-logs, cash accepted)",
            "ProtonVPN (Swiss, audited)",
            "IVPN (audited no-logs)",
            "RiseupVPN (nonprofit, activist-oriented)"
        ]

# Convenience
def check_vpn_status() -> dict:
    checker = VPNChecker()
    active, ip = checker.is_vpn_active()
    return {
        "vpn_active": active,
        "public_ip": ip,
        "recommended_providers": checker.suggest_providers()
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check VPN status")
    parser.add_argument("--baseline", help="Your known non-VPN IP for comparison")
    args = parser.parse_args()

    checker = VPNChecker()
    active, ip = checker.is_vpn_active(known_non_vpn_ip=args.baseline)

    print(f"🌐 Public IP: {ip}")
    if active is True:
        print("✅ VPN appears to be active (IP differs from baseline)")
    elif active is False:
        print("❌ VPN appears to be OFF (IP matches baseline or no change)")
    else:
        print("⚠️  Cannot determine — no baseline IP provided")
        print("   Re-run with: --baseline <your-home-IP>")
    print("\n🔒 Recommended providers:")
    for p in checker.suggest_providers():
        print(f"   • {p}")
