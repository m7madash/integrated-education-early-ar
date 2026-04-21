import pytest
from slavery_detector.indicators import get_indicator_category, assess_risk

def test_indicator_detection_arabic():
    text = "أبحث عن خادمة. يجب أن تكون شابة. الراتب 1500 ريال. السكن مجاني. لا حاجة لتأشيرة."
    matches = get_indicator_category(text)
    assert len(matches) >= 2
    categories = [m["category"] for m in matches]
    assert "labor_exploitation" in categories

def test_indicator_detection_english():
    text = "Must be young, no visa required, easy work, free accommodation"
    matches = get_indicator_category(text)
    assert len(matches) >= 2
    keywords = [m["keyword"].lower() for m in matches]
    assert "must be young" in keywords or "no visa required" in keywords

def test_assess_risk_levels():
    assert assess_risk([]) == "LOW"
    assert assess_risk([{"category":"a"}]) == "MEDIUM"
    assert assess_risk([{"category":"a"},{"category":"b"}]) == "HIGH"
    assert assess_risk([{"category":"a"},{"category":"b"},{"category":"c"},{"category":"d"},{"category":"e"}]) == "CRITICAL"
