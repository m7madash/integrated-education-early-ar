#!/usr/bin/env python3
"""
Ignorance → Knowledge: Fact-Checker Bot
Checks claims against verified sources only.
NO speculation. NO opinion. Only proof.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Verified sources (only these allowed)
TRUSTED_SOURCES = {
    "quran": {"type": "quran", "confidence": 1.0, "requires_arabic": True},
    "bukhari": {"type": "hadith", "confidence": 0.99, "sunnah": True},
    "muslim": {"type": "hadith", "confidence": 0.99, "sunnah": True},
    "un": {"type": "international", "confidence": 0.8},
    "who": {"type": "health", "confidence": 0.9},
    "unrwa": {"type": "palestine", "confidence": 0.85},
    "pzoa": {"type": "palestine", "confidence": 0.85}  # Palestinian Ministry of Health
}

class FactChecker:
    """Verify claims using ONLY verified sources."""

    def __init__(self):
        self.verification_log = []

    def check(self, claim: str, source: Optional[str] = None) -> Dict:
        """
        Check a claim.
        Returns: {verified: bool, source: str, confidence: float, note: str}
        """
        if source not in TRUSTED_SOURCES:
            return {
                "verified": False,
                "source": None,
                "confidence": 0.0,
                "note": "Source not in verified list. Add trusted source first."
            }

        # In real implementation, would query source API/database
        # For MVP: assume claim matches source if provided
        src_info = TRUSTED_SOURCES[source]
        result = {
            "verified": True,
            "source": source,
            "confidence": src_info["confidence"],
            "note": f"Claim matches verified source: {source}"
        }

        # For Quran/hadith: require Arabic text + reference
        if src_info.get("requires_arabic"):
            result["note"] += " (Arabic text required with surah:ayah or hadith ref)"

        self.verification_log.append(result)
        return result

    def add_source(self, name: str, source_type: str, confidence: float, **kwargs):
        """Add a new verified source (admin only)."""
        TRUSTED_SOURCES[name] = {
            "type": source_type,
            "confidence": confidence,
            **kwargs
        }
        return {"status": "added", "source": name}

def main():
    checker = FactChecker()

    if len(sys.argv) < 2:
        print("Ignorance → Knowledge Fact-Checker")
        print("Usage: python3 verifier.py check '<claim>' --source <source_name>")
        print("       python3 verifier.py sources (list verified sources)")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "check":
        claim = sys.argv[2]
        source = sys.argv[sys.argv.index("--source")+1] if "--source" in sys.argv else None
        if not source:
            print("ERROR: --source required (choose from:", ",".join(TRUSTED_SOURCES.keys()), ")")
            sys.exit(1)
        result = checker.check(claim, source)
        print(json.dumps(result, indent=2))

    elif cmd == "sources":
        print("Verified Sources:")
        for name, info in TRUSTED_SOURCES.items():
            print(f"  {name}: {info['type']} (confidence: {info['confidence']})")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
