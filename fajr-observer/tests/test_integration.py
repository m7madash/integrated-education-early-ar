"""
Integration Tests — Fajr Observer Agent
Run: python3 -m pytest tests/  (or python3 tests/test_integration.py)
"""

import cv2
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from detection.features import extract_features
from detection.dawn_classifier import DawnClassifier
from detection.thresholds import ThresholdManager

def create_synthetic_image(state: str = "night", size=(640, 480)) -> np.ndarray:
    """Generate a fake sky image for testing."""
    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    if state == "night":
        # pure black
        pass
    elif state == "false_dawn":
        # vertical bright streak in the middle-bottom
        cv2.rectangle(img, (280, 300), (360, 480), (200, 200, 200), -1)
    elif state == "true_dawn":
        # horizontal band across bottom
        cv2.rectangle(img, (0, 350), (640, 420), (220, 220, 220), -1)
    return img

def test_feature_extraction():
    print("Testing feature extraction...")
    night = create_synthetic_image("night")
    feats = extract_features(night)
    assert feats["mean_intensity"] < 10, "Night should be dark"
    print("  ✓ Night features correct")

    false_dawn = create_synthetic_image("false_dawn")
    feats = extract_features(false_dawn)
    assert feats["avg_aspect_ratio"] > 1.0, "False dawn should be vertical"
    print("  ✓ False dawn features correct")

    true_dawn = create_synthetic_image("true_dawn")
    feats = extract_features(true_dawn)
    assert feats["horizontal_spread"] > 0.3, "True dawn should be wide"
    print("  ✓ True dawn features correct")
    return True

def test_classifier():
    print("Testing classifier rules...")
    cls = DawnClassifier()
    night = create_synthetic_image("night")
    state, conf, _ = cls.classify(night, latitude=21.5)
    assert state == "night", f"Expected night, got {state}"
    print(f"  ✓ Night → {state} ({conf:.1%})")

    false_dawn = create_synthetic_image("false_dawn")
    state, conf, _ = cls.classify(false_dawn, latitude=21.5)
    assert state == "false_dawn", f"Expected false_dawn, got {state}"
    print(f"  ✓ False dawn → {state} ({conf:.1%})")

    true_dawn = create_synthetic_image("true_dawn")
    state, conf, _ = cls.classify(true_dawn, latitude=21.5)
    assert state == "true_dawn", f"Expected true_dawn, got {state}"
    print(f"  ✓ True dawn → {state} ({conf:.1%})")
    return True

def test_thresholds():
    print("Testing threshold zones...")
    tm = ThresholdManager()
    z1 = tm.get_zone(21.5)  # Gaza ~21.5°N
    z2 = tm.get_zone(45.0)  # mid-latitude
    assert z1 == "subtropical", f"Expected subtropical, got {z1}"
    assert z2 == "mid_latitude", f"Expected mid_latitude, got {z2}"
    print(f"  ✓ Zone detection: 21.5° → {z1}, 45° → {z2}")
    return True

def run_all():
    print("=" * 50)
    print("FAJR OBSERVER — Integration Tests")
    print("=" * 50)
    print()
    try:
        test_feature_extraction()
        print()
        test_classifier()
        print()
        test_thresholds()
        print()
        print("=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_all())
