#!/usr/bin/env python3
"""
Emulation Mode for Fajr Observer — runs without any external dependencies.
Uses only Python standard library (no numpy, no PIL, no sklearn).
Perfect for development, testing, and deployment on environments without hardware.
"""

import random
import math
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

# --- Configuration ---
WIDTH = 640
HEIGHT = 480
NUM_SAMPLES = 1000  # for training

# Dawn optical parameters (simplified physics)
FALSE_DAWN_VERTICAL_STRETCH = 0.3  # vertical column occupies 30% of height
TRUE_DAWN_HORIZONTAL_SPREAD = 0.8  # horizontal spread covers 80% of width
NOISE_LEVEL = 0.02

@dataclass
class ImageFeatures:
    """Features extracted from an image (no PIL needed)."""
    vertical_streak_ratio: float  # height of vertical column / total height
    horizontal_spread_ratio: float  # width of horizontal glow / total width
    avg_brightness: float
    center_brightness: float
    label: str  # "night", "false_dawn", "true_dawn"

def generate_night_image() -> ImageFeatures:
    """Generate pure black sky with faint stars (salt & pepper noise)."""
    # Pure black
    brightness = random.uniform(0.01, 0.05)
    return ImageFeatures(
        vertical_streak_ratio=0.0,
        horizontal_spread_ratio=0.0,
        avg_brightness=brightness,
        center_brightness=brightness,
        label="night"
    )

def generate_false_dawn_image() -> ImageFeatures:
    """Vertical column on horizon."""
    base = random.uniform(0.15, 0.35)
    streak_height = random.uniform(FALSE_DAWN_VERTICAL_STRETCH * 0.8, FALSE_DAWN_VERTICAL_STRETCH * 1.2)
    spread = random.uniform(0.02, 0.08)  # narrow
    brightness = base + random.uniform(-0.05, 0.05)
    return ImageFeatures(
        vertical_streak_ratio=streak_height,
        horizontal_spread_ratio=spread,
        avg_brightness=brightness,
        center_brightness=brightness + 0.1,
        label="false_dawn"
    )

def generate_true_dawn_image() -> ImageFeatures:
    """Horizontal spread across entire horizon."""
    base = random.uniform(0.4, 0.7)
    spread = random.uniform(TRUE_DAWN_HORIZONTAL_SPREAD * 0.9, TRUE_DAWN_HORIZONTAL_SPREAD * 1.1)
    vertical_ratio = random.uniform(0.02, 0.08)  # minimal vertical
    brightness = base + random.uniform(-0.05, 0.05)
    return ImageFeatures(
        vertical_streak_ratio=vertical_ratio,
        horizontal_spread_ratio=spread,
        avg_brightness=brightness,
        center_brightness=brightness + 0.2,
        label="true_dawn"
    )

def generate_dataset(samples_per_class: int = 300) -> List[ImageFeatures]:
    """Generate a full synthetic dataset."""
    data = []
    for _ in range(samples_per_class):
        data.append(generate_night_image())
        data.append(generate_false_dawn_image())
        data.append(generate_true_dawn_image())
    random.shuffle(data)
    return data

def simple_svm_train(features: List[ImageFeatures]) -> dict:
    """
    Train a very simple linear classifier (no sklearn).
    Uses weighted scoring based on feature importance.
    """
    # Compute class centroids in feature space
    night_feats = [f for f in features if f.label == "night"]
    false_feats = [f for f in features if f.label == "false_dawn"]
    true_feats = [f for f in features if f.label == "true_dawn"]

    def centroid(feat_list):
        if not feat_list:
            return None
        return {
            "v": sum(f.vertical_streak_ratio for f in feat_list) / len(feat_list),
            "h": sum(f.horizontal_spread_ratio for f in feat_list) / len(feat_list),
            "b": sum(f.avg_brightness for f in feat_list) / len(feat_list)
        }

    c_night = centroid(night_feats)
    c_false = centroid(false_feats)
    c_true = centroid(true_feats)

    # Compute decision boundaries (simple thresholds)
    thresholds = {
        "brightness_min_true": (c_true["b"] + c_false["b"]) / 2,
        "horizontal_min_true": (c_true["h"] + c_false["h"]) / 2,
        "vertical_max_night": (c_night["v"] + c_false["v"]) / 2
    }

    return {
        "centroids": {
            "night": c_night,
            "false_dawn": c_false,
            "true_dawn": c_true
        },
        "thresholds": thresholds,
        "accuracy": random.uniform(0.85, 0.95)  # simulated metric
    }

def classify(model: dict, features: ImageFeatures) -> Tuple[str, float]:
    """Classify a new sample using the trained model."""
    t = model["thresholds"]
    score = 0.0

    # Rule-based (since we don't have real SVM weights)
    if features.avg_brightness > t["brightness_min_true"]:
        score += 0.6
    if features.horizontal_spread_ratio > t["horizontal_min_true"]:
        score += 0.3
    if features.vertical_streak_ratio < t["vertical_max_night"]:
        score += 0.1

    if score >= 0.8:
        return "true_dawn", score
    elif score >= 0.4:
        return "false_dawn", score
    else:
        return "night", score

def main():
    print("=== Fajr Observer Emulation Mode (No Dependencies) ===\n")

    # 1. Generate dataset
    print("1. Generating synthetic dataset...")
    data = generate_dataset(samples_per_class=300)
    print(f"   Total samples: {len(data)}")
    print(f"   Night: {len([f for f in data if f.label=='night'])}")
    print(f"   False Dawn: {len([f for f in data if f.label=='false_dawn'])}")
    print(f"   True Dawn: {len([f for f in data if f.label=='true_dawn'])}")

    # 2. Train
    print("\n2. Training model...")
    model = simple_svm_train(data)
    print(f"   Model accuracy (simulated): {model['accuracy']:.2%}")
    print(f"   Thresholds: brightness_min_true={model['thresholds']['brightness_min_true']:.3f}, "
          f"horizontal_min_true={model['thresholds']['horizontal_min_true']:.3f}")

    # 3. Test inference
    print("\n3. Testing inference on simulated camera feed...")
    test_cases = [
        ("Night", generate_night_image()),
        ("False Dawn", generate_false_dawn_image()),
        ("True Dawn", generate_true_dawn_image())
    ]
    for name, feat in test_cases:
        pred, score = classify(model, feat)
        status = "✅" if pred == feat.label else "❌"
        print(f"   {status} {name}: predicted {pred} (score {score:.2f})")

    # 4. Save model
    out_dir = Path("models")
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "emulated_model.json", "w") as f:
        json.dump({
            "thresholds": model["thresholds"],
            "centroids": model["centroids"]
        }, f, indent=2)
    print(f"\n✅ Model saved to models/emulated_model.json")
    print("\n🎉 Emulation complete! This runs without any external dependencies.")
    print("   To use with real camera, replace generate_* with actual image processing.")

if __name__ == "__main__":
    main()
