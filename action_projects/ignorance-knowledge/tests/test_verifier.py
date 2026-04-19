#!/usr/bin/env python3
"""Tests: Ignorance → Knowledge Fact-Checker"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "factcheck"))
from verifier import FactChecker, TRUSTED_SOURCES

def test_verified_check():
    checker = FactChecker()
    result = checker.check("test claim", source="who")
    assert result["verified"] == True
    assert result["confidence"] == 0.9
    print("✅ Verified source test passed")

def test_unverified_check():
    checker = FactChecker()
    result = checker.check("test claim", source="not_a_source")
    assert result["verified"] == False
    print("✅ Unverified source rejection test passed")

def run_all():
    test_verified_check()
    test_unverified_check()
    print("✅ All fact-checker tests passed")

if __name__ == "__main__":
    run_all()
