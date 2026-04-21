#!/usr/bin/env python3
"""
Media Integrity — Test Suite
"""

import json
import tempfile
from pathlib import Path
from PIL import Image
import numpy as np

# Test data directory
TEST_DIR = Path(__file__).parent.parent / "tests"
TEST_DATA_DIR = TEST_DIR / "test_data"
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

def create_test_image(color=(255, 0, 0), size=(100, 100)) -> Path:
    """Create a simple test image."""
    img = Image.new('RGB', size, color)
    path = TEST_DATA_DIR / "test_image.jpg"
    img.save(path, quality=95)
    return path

def test_image_forensics():
    """Test image forensics on a clean image."""
    from src.media_integrity.image import analyze_image, ImageForensics
    test_img = create_test_image()
    result = analyze_image(str(test_img))
    assert 'manipulation_score' in result
    assert 0 <= result['manipulation_score'] <= 1
    # All-red image should be consistent (no ELA anomalies typically)
    print(f"✅ Image forensics test passed — score: {result['manipulation_score']}")

def test_fake_news_detector():
    """Test fake news detection with obvious fake."""
    from src.media_integrity.text import analyze_text
    fake_text = "Shocking! 5G causes coronavirus! Secret exposure!"
    result = analyze_text(fake_text)
    assert result['is_likely_fake'] is True or result['manipulation_score'] > 0.3
    print(f"✅ Fake news test passed — score: {result['manipulation_score']}")

def test_source_reputation():
    """Test source reputation evaluator."""
    from src.media_integrity.source import analyze_source
    # Test reliable domain
    result_reliable = analyze_source("https://reuters.com/article")
    assert result_reliable['reputation_score'] > 0.6
    # Test unknown domain
    result_unknown = analyze_source("https://unknown-blog.blogspot.com/article")
    assert result_unknown['reputation_score'] < 0.5
    print(f"✅ Source reputation test passed (reuter: {result_reliable['reputation_score']}, blog: {result_unknown['reputation_score']})")

def test_bot_detector():
    """Test bot detection on clear bot account."""
    from src.media_integrity.social import analyze_bot
    bot_account = {
        "id": "test_bot_1",
        "username": "user328415",
        "join_date": "2026-04-10T00:00:00Z",
        "followers": 5,
        "following": 500,
        "posts": 300,
        "content_samples": [
            "Check out this link! http://example.com",
            "Check out this link! http://example.com",
            "Amazing news! http://example.com"
        ]
    }
    result = analyze_bot(bot_account)
    assert result['is_likely_bot'] is True or result['bot_score'] > 0.5
    print(f"✅ Bot detection test passed — score: {result['bot_score']}")

def test_network_analysis():
    """Test coordinated network detection."""
    from src.media_integrity.social import analyze_network
    posts = [
        {"account_id": "a1", "timestamp": "2026-04-21T10:00:00Z", "content": "Same message 1"},
        {"account_id": "a2", "timestamp": "2026-04-21T10:00:10Z", "content": "Same message 1"},
        {"account_id": "a3", "timestamp": "2026-04-21T10:00:20Z", "content": "Same message 1"},
    ]
    result = analyze_network(posts)
    assert result['coordination_score'] > 0.0
    print(f"✅ Network analysis test passed — coordination: {result['coordination_score']}")

def test_orchestrator():
    """Test full orchestrator with text."""
    from src.media_integrity.detector import analyze
    result = analyze("Breaking: Artificial intelligence will take all jobs tomorrow!", item_type='text')
    assert result['item_type'] == 'text'
    assert 'overall_integrity_score' in result
    print(f"✅ Orchestrator test passed — verdict: {result['verdict']}, score: {result['overall_integrity_score']}")

if __name__ == "__main__":
    print("\n🧪 Media Integrity — Running Tests\n")
    tests = [
        ("Image Forensics", test_image_forensics),
        ("Fake News Detector", test_fake_news_detector),
        ("Source Reputation", test_source_reputation),
        ("Bot Detector", test_bot_detector),
        ("Network Analysis", test_network_analysis),
        ("Orchestrator", test_orchestrator),
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            print(f"Running: {name}...", end=" ")
            fn()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
    print(f"\n📊 Results: {passed} passed, {failed} failed\n")
