#!/usr/bin/env python3
"""
Privacy Shield — Breach Checker
Check if email/username appears in known data breaches using HaveIBeenPwned API.
"""

import requests
import json
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass

@dataclass
class BreachRecord:
    """Single breach record."""
    name: str
    title: str
    name: str
    domain: str
    breach_date: str
    added_date: str
    modified_date: str
    pwn_count: int
    description: str
    logo_path: str
    primary_domain: str

class BreachChecker:
    """Check emails/phones against HIBP database."""

    API_BASE = "https://haveibeenpwned.com/api/v3"

    def __init__(self, api_key: Optional[str] = None, cache_dir: Path = Path("/tmp/hibp_cache")):
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def check_email(self, email: str, use_cache: bool = True) -> List[BreachRecord]:
        """
        Check an email address against HIBP.
        Returns list of breaches. Empty list if none found.
        """
        cache_file = self.cache_dir / f"{hashlib.sha256(email.encode()).hexdigest()[:16]}.json"
        if use_cache and cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                return [BreachRecord(**b) for b in data]

        headers = {
            "hibp-api-key": self.api_key,
            "User-Agent": "Privacy-Shield/0.1 (https://github.com/m7madash/m7mad-ai-work)"
        } if self.api_key else {"hibp-api-key": "none"}

        # v3 endpoint: /breachedaccount/{account}
        url = f"{self.API_BASE}/breachedaccount/{email}?truncateResponse=false"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 404:
                # No breaches
                breaches = []
            elif resp.status_code == 200:
                breaches_data = resp.json()
                breaches = [BreachRecord(**b) for b in breaches_data]
            else:
                # Rate limit or error
                print(f"⚠️ HIBP returned {resp.status_code}: {resp.text}")
                breaches = []
        except Exception as e:
            print(f"⚠️ HIBP request failed: {e}")
            breaches = []

        # Cache result
        with open(cache_file, 'w') as f:
            json.dump([b.__dict__ for b in breaches], f, indent=2)
        return breaches

    def check_phone(self, phone: str, use_cache: bool = True) -> List[BreachRecord]:
        """Check phone number (requires API key)."""
        if not self.api_key:
            print("❌ Phone lookup requires HIBP API key")
            return []
        cache_file = self.cache_dir / f"phone_{hashlib.sha256(phone.encode()).hexdigest()[:16]}.json"
        if use_cache and cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                return [BreachRecord(**b) for b in data]

        headers = {
            "hibp-api-key": self.api_key,
            "User-Agent": "Privacy-Shield/0.1"
        }
        url = f"{self.API_BASE}/breachedphone/{phone}?truncateResponse=false"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code in (200, 404):
                breaches = [BreachRecord(**b) for b in resp.json()] if resp.status_code == 200 else []
            else:
                print(f"⚠️ HIBP phone error: {resp.status_code}")
                breaches = []
        except Exception as e:
            print(f"⚠️ HIBP phone request failed: {e}")
            breaches = []

        with open(cache_file, 'w') as f:
            json.dump([b.__dict__ for b in breaches], f, indent=2)
        return breaches

# Convenience
def quick_check(email: str, api_key: Optional[str] = None) -> List[BreachRecord]:
    checker = BreachChecker(api_key)
    return checker.check_email(email)

if __name__ == "__main__":
    import argparse, hashlib
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="Email to check")
    parser.add_argument("--api-key", help="HIBP API key (optional, but rate-limited without)")
    args = parser.parse_args()

    checker = BreachChecker(api_key=args.api_key)
    breaches = checker.check_email(args.email)
    if breaches:
        print(f"⚠️ {args.email} found in {len(breaches)} breach(es):")
        for b in breaches:
            print(f"   • {b.name} ({b.breach_date}) — {b.pwn_count:,} accounts")
    else:
        print(f"✅ {args.email} not found in known breaches (or API limit reached)")
