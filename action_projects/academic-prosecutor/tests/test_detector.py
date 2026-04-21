#!/usr/bin/env python3
"""
Academic Prosecutor — Tests for Investigator
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from investigator.detector import Investigator, Paper, Violation

def test_jaccard_similarity():
    inv = Investigator()
    assert inv._jaccard_similarity("hello world", "hello there") > 0.0
    assert inv._jaccard_similarity("abc", "def") == 0.0
    print("✅ Jaccard similarity works")

def test_plagiarism_detection():
    """Should detect exact title match with different authors."""
    inv = Investigator()
    # Create a fake corpus entry
    corpus_dir = Path("tests/test_data")
    corpus_dir.mkdir(parents=True, exist_ok=True)
    (corpus_dir / "known_paper.json").write_text(json.dumps({
        "title": "A Novel Approach to Deep Learning",
        "authors": ["Smith, J.", "Doe, J."],
        "id": "10.1234/test.2023"
    }))

    paper = Paper(
        id="10.5678/plagiarism.2024",
        title="A Novel Approach to Deep Learning",
        authors=["Someone, Else"],
        abstract="This is a test abstract.",
        text="",
        source="test"
    )
    violations = inv._check_plagiarism(paper)
    assert len(violations) >= 1
    assert violations[0].type == "plagiarism"
    print("✅ Plagiarism detection: exact title match found")

def test_duplicate_submission():
    inv = Investigator()
    paper = Paper(
        id="10.1234/existing",
        title="Another Paper",
        authors=["Author, A."],
        abstract="test",
        text="",
        source="test"
    )
    violations = inv._check_duplicate_submission(paper)
    assert len(violations) >= 1
    assert violations[0].type == "duplicate_submission"
    print("✅ Duplicate submission detection works")

if __name__ == "__main__":
    import json
    test_jaccard_similarity()
    test_plagiarism_detection()
    test_duplicate_submission()
    print("\n🎉 All basic detector tests passed!")
