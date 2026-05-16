"""
Dawn Classifier — Fajr Observer Agent

Main classifier: determines if current sky image shows Night, False Dawn, or True Dawn.
Uses rule-based system now; will be replaced by ML model later.
"""

import cv2
import numpy as np
from pathlib import Path
import json
from typing import Tuple, Optional
from .features import extract_features, draw_debug_overlay
from .thresholds import ThresholdManager

class DawnClassifier:
    """Classify sky images into dawn states."""

    STATES = ["night", "false_dawn", "true_dawn", "unknown"]

    def __init__(self, config_dir: str = "../../config"):
        self.thresh_mgr = ThresholdManager(f"{config_dir}/thresholds.json")
        self.consecutive_hits = 0
        self.last_state = "night"
        self.confidence_history = []

    def classify(self, image: np.ndarray, latitude: float = None, month: int = None) -> Tuple[str, float, Dict]:
        """
        Classify one image.

        Returns:
            (state, confidence, features_dict)
        """
        # Get thresholds for location/season
        thresholds_dict = self.thresh_mgr.get_thresholds(latitude or 0.0, month)
        features = extract_features(image)

        # Rule-based classification
        state, confidence = self._classify_rules(features, thresholds_dict)

        # Temporal smoothing: require consecutive hits
        if state == self.last_state:
            self.consecutive_hits += 1
        else:
            self.consecutive_hits = 1
            self.last_state = state

        # If we have enough consecutive confirmations, boost confidence
        required = thresholds_dict["consecutive_hits_required"]
        if self.consecutive_hits >= required:
            confidence = min(1.0, confidence + 0.1)  # boost slightly

        return state, confidence, features

    def _classify_rules(self, feats: Dict, thr: Dict) -> Tuple[str, float]:
        """Heuristic classification."""
        hs = feats["horizontal_spread"]
        ar = feats["avg_aspect_ratio"]
        intensity = feats["mean_intensity"]

        # Night
        if intensity < 25 and hs < 0.1:
            return "night", 0.95
        # False dawn: vertical streak, low horizontal spread
        if ar > thr["vertical_streak_max"] and hs < thr["horizontal_spread_min"]:
            return "false_dawn", 0.85
        # True dawn: wide horizontal, moderate vertical
        if hs >= thr["horizontal_spread_min"] and ar < 1.5 and intensity >= thr["intensity_min"]:
            return "true_dawn", 0.90
        # Unknown/transition
        return "unknown", 0.5

    def should_trigger_adhan(self, state: str, confidence: float, thresholds: Dict) -> bool:
        """Decide if we should trigger Adhan based on state + confidence."""
        if state != "true_dawn":
            return False
        if confidence < thresholds["min_confidence"]:
            return False
        # Must have at least 3 consecutive true_dawn classifications
        return self.consecutive_hits >= thresholds["consecutive_hits_required"]

    def reset(self):
        """Clear temporal state (for new day)."""
        self.consecutive_hits = 0
        self.last_state = "night"
        self.confidence_history = []


def classify_image_file(image_path: str, latitude: float = 21.5, month: int = None) -> dict:
    """Convenience: classify a saved image file."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read: {image_path}")
    cls = DawnClassifier()
    state, conf, feats = cls.classify(img, latitude, month)
    return {
        "image": image_path,
        "state": state,
        "confidence": conf,
        "features": feats
    }


if __name__ == "__main__":
    import sys
    print("Dawn Classifier — Test Mode")
    if len(sys.argv) > 1:
        result = classify_image_file(sys.argv[1], latitude=21.5)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python3 -m src.detection.dawn_classifier <image.jpg>")
