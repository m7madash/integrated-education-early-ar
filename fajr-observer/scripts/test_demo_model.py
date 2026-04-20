#!/usr/bin/env python3
"""Quick test of Fajr Observer demo model (no camera needed)."""

import sys
from pathlib import Path
import joblib
import numpy as np

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

MODEL_PATH = Path("models/dawn_classifier_demo.joblib")

def main():
    if not MODEL_PATH.exists():
        print(f"❌ Demo model not found: {MODEL_PATH}")
        print("   Run: bash scripts/demo_train.sh")
        sys.exit(1)

    print(f"✅ Loading demo model: {MODEL_PATH}")
    data = joblib.load(MODEL_PATH)
    model = data["model"]
    class_names = data["class_names"]
    feature_names = data["feature_names"]

    print(f"   Classes: {class_names}")
    print(f"   Features: {feature_names}")

    # Create a synthetic "true_dawn" feature vector (based on centroids from train.py)
    # Order must match feature_names sorted lexicographically
    features_dict = {
        "avg_aspect_ratio": 1.2,
        "bright_pixel_count": 50000,
        "brightest_row_ratio": 0.2,
        "coverage_ratio": 0.40,
        "horizontal_spread": 0.60,
        "mean_hue": 30,
        "mean_intensity": 120,
        "mean_saturation": 70,
        "std_intensity": 30
    }
    # Build feature vector in sorted order
    x = np.array([features_dict[k] for k in sorted(features_dict.keys())]).reshape(1, -1)

    pred = model.predict(x)[0]
    probs = model.predict_proba(x)[0]
    predicted_class = class_names[pred]

    print(f"\n🎯 Prediction: {predicted_class}")
    print(f"   Confidence: {probs[pred]:.1%}")
    print(f"   All probabilities:")
    for cls, prob in zip(class_names, probs):
        print(f"     {cls}: {prob:.1%}")

    # Sanity check: should be true_dawn with high confidence
    if predicted_class == "true_dawn" and probs[pred] > 0.5:
        print("\n✅ Demo model works correctly — recognized synthetic true dawn")
        return 0
    else:
        print("\n⚠️  Unexpected prediction — model may need retraining with real data")
        return 1

if __name__ == "__main__":
    sys.exit(main())
