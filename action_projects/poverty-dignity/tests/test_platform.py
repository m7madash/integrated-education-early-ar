#!/usr/bin/env python3
"""Tests: Poverty → Dignity Skill-Sharing Platform"""

import sys
import json
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "skill_sharing"))
from cli import SkillSharingPlatform

def test_registration():
    platform = SkillSharingPlatform()
    result = platform.register_agent("test_agent", ["python"], ["legal_advice"])
    assert result["status"] == "registered"
    assert "test_agent" in platform.db
    print("✅ Registration test passed")

def test_matching():
    platform = SkillSharingPlatform()
    platform.register_agent("coder", skills=["web_dev"], needs=["design"])
    platform.register_agent("designer", skills=["design"], needs=["web_dev"])
    matches = platform.find_matches("coder")
    assert len(matches) == 1
    assert matches[0]["agent"] == "designer"
    print("✅ Matching test passed")

def run_all():
    test_registration()
    test_matching()
    print("✅ All tests passed")

if __name__ == "__main__":
    run_all()
