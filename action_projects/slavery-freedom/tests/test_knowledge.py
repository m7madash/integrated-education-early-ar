import pytest
from slavery_detector.knowledge import get_local_resources, format_emergency_contacts

def test_get_local_resources_ps():
    res = get_local_resources("PS")
    assert "hotlines" in res
    assert len(res["hotlines"]) > 0
    assert any("Palestinian" in h["name"] for h in res["hotlines"])

def test_get_local_resources_default():
    res = get_local_resources("XX")
    assert "note" in res
    assert "hotlines" in res
    assert len(res["hotlines"]) > 0

def test_format_emergency_contacts():
    text = format_emergency_contacts()
    assert "PS" in text or "Palestinian" in text
