#!/usr/bin/env python3
"""Demo: Ignorance → Knowledge Fact-Checker in action."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "factcheck"))
from verifier import FactChecker

def run_demo():
    checker = FactChecker()

    print("=== Ignorance → Knowledge Fact-Checker Demo ===\n")

    # Demo 1: Verified claim
    print("1. Checking verified claim (UN source)...")
    result = checker.check("Gaza population is approximately 2 million", source="un")
    print(f"   Verified: {result['verified']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Note: {result['note']}\n")

    # Demo 2: Unverified source
    print("2. Checking claim with unknown source...")
    result = checker.check("Some random opinion", source="random_twitter")
    print(f"   Verified: {result['verified']}")
    print(f"   Note: {result['note']}\n")

    # Demo 3: List sources
    print("3. All verified sources:")
    from factcheck.verifier import TRUSTED_SOURCES
    for name, info in TRUSTED_SOURCES.items():
        print(f"   • {name} ({info['type']}) — confidence {info['confidence']}")

    print("\n✅ Demo complete!")
    print("👉 Next: Add your verified sources, reject unverified claims.")

if __name__ == "__main__":
    run_demo()
