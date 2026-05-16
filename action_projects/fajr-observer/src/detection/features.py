"""
Dawn Feature Extraction — Fajr Observer Agent

Extracts optical features from sky images to distinguish:
  Night (ليل) → False Dawn (فجر كاذب) → True Dawn (فجر صادق)

Features:
  - Horizontal spread ratio (عرضي vs عمودي)
  - Intensity gradients (شدة الضوء)
  - Color temperature (blue vs red shift)
  - Sky coverage percentage
"""

import cv2
import numpy as np
from typing import Dict, Tuple

def extract_features(image: np.ndarray, roi: Tuple[int, int, int, int] = None) -> Dict:
    """
    Extract dawn-relevant features from an image.

    Args:
        image: BGR image (from OpenCV)
        roi: Region of interest [x1, y1, x2, y2] — typically bottom horizon band

    Returns:
        dict of features
    """
    if roi:
        x1, y1, x2, y2 = roi
        sky_band = image[y1:y2, x1:x2]
    else:
        sky_band = image

    # Convert to grayscale and HSV
    gray = cv2.cvtColor(sky_band, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(sky_band, cv2.COLOR_BGR2HSV)

    # 1. Brightness statistics
    mean_intensity = np.mean(gray)
    std_intensity = np.std(gray)

    # 2. Horizontal vs Vertical spread (aspect ratio of bright region)
    # Threshold the bright areas (above mean + 0.3*std)
    bright_thresh = mean_intensity + 0.3 * std_intensity
    _, bright_mask = cv2.threshold(gray, bright_thresh, 255, cv2.THRESH_BINARY)

    # Find contours of bright regions
    contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate aspect ratios of bright blobs
    aspect_ratios = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 0:
            aspect_ratios.append(h / w)  # height/width → >1 means vertical (false dawn)
        # Also compute area coverage
    total_bright_pixels = np.sum(bright_mask > 0)
    sky_pixels = gray.shape[0] * gray.shape[1]
    coverage_ratio = total_bright_pixels / sky_pixels if sky_pixels > 0 else 0

    # Average aspect ratio (verticality)
    avg_aspect_ratio = np.mean(aspect_ratios) if aspect_ratios else 0

    # 3. Horizontal spread: how many columns have bright pixels?
    col_sums = np.sum(bright_mask, axis=0)  # sum over rows → per column
    bright_columns = np.sum(col_sums > 0)
    total_columns = bright_mask.shape[1]
    horizontal_spread = bright_columns / total_columns if total_columns > 0 else 0

    # 4. Color: average hue & saturation (blue-ish dawn vs red/orange)
    mean_hue = np.mean(hsv[:, :, 0])
    mean_sat = np.mean(hsv[:, :, 1])
    # Dawn: hues ~20-40 (yellow/orange) for true dawn? Actually false dawn is whiter, true dawn is reddish?
    # Let's keep raw values; classifier will decide.

    # 5. Vertical position: where is the brightest spot? (higher in image = higher elevation)
    # y-coordinate of max intensity pixel
    max_pos = np.unravel_index(np.argmax(gray), gray.shape)
    brightest_row = max_pos[0]
    normalized_row = brightest_row / gray.shape[0]  # 0=top, 1=bottom

    features = {
        "mean_intensity": float(mean_intensity),
        "std_intensity": float(std_intensity),
        "coverage_ratio": float(coverage_ratio),
        "avg_aspect_ratio": float(avg_aspect_ratio),  # >1 → vertical (false dawn)
        "horizontal_spread": float(horizontal_spread),  # 0–1, higher for true dawn (wide)
        "mean_hue": float(mean_hue),
        "mean_saturation": float(mean_sat),
        "brightest_row_ratio": float(normalized_row),
        "bright_pixel_count": int(total_bright_pixels)
    }
    return features


def classify_by_rules(features: Dict, thresholds: Dict) -> Tuple[str, float]:
    """
    Rule-based classification using thresholds.

    Returns:
        (label, confidence) where label in {"night", "false_dawn", "true_dawn"}
    """
    zone = thresholds.get("zone", "mid_latitude")
    t = thresholds["latitudinal_zones"][zone]
    td = thresholds["true_dawn_characteristics"]
    fd = thresholds["false_dawn_characteristics"]

    # Score each class
    scores = {"night": 0.0, "false_dawn": 0.0, "true_dawn": 0.0}

    # Night: low intensity, low coverage
    if features["mean_intensity"] < 30:
        scores["night"] += 0.4
    if features["coverage_ratio"] < 0.05:
        scores["night"] += 0.4
    if features["horizontal_spread"] < 0.1:
        scores["night"] += 0.2

    # False dawn: vertical, narrow, moderate intensity
    if features["avg_aspect_ratio"] > fd["vertical_streak_ratio_min"]:
        scores["false_dawn"] += 0.4
    if features["horizontal_spread"] < fd["max_horizontal_spread"]:
        scores["false_dawn"] += 0.3
    if 30 < features["mean_intensity"] < 80:
        scores["false_dawn"] += 0.3

    # True dawn: horizontal spread wide, intensity moderate-high, low verticality
    if features["horizontal_spread"] >= td["horizontal_spread_min"]:
        scores["true_dawn"] += 0.4
    if features["avg_aspect_ratio"] < td["vertical_streak_ratio_max"]:
        scores["true_dawn"] += 0.3
    if features["mean_intensity"] > 50:
        scores["true_dawn"] += 0.3

    # Normalize to get confidence
    total = sum(scores.values())
    if total == 0:
        return "unknown", 0.0
    probs = {k: v / total for k, v in scores.items()}
    best = max(probs, key=probs.get)
    confidence = probs[best]
    return best, confidence


def draw_debug_overlay(image: np.ndarray, features: Dict, label: str, confidence: float) -> np.ndarray:
    """Draw features and classification on image for debugging."""
    debug = image.copy()
    # Text overlay
    text = f"{label} ({confidence:.1%})"
    cv2.putText(debug, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # Feature values
    lines = [
        f"Intensity: {features['mean_intensity']:.1f}",
        f"HSpread: {features['horizontal_spread']:.2f}",
        f"VertRatio: {features['avg_aspect_ratio']:.2f}",
        f"Coverage: {features['coverage_ratio']:.2f}"
    ]
    for i, line in enumerate(lines, 1):
        cv2.putText(debug, line, (10, 30 + 30*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    return debug


if __name__ == "__main__":
    print("Dawn Feature Extraction — Test Mode")
    print("Usage: python3 -m src.detection.features <image_path>")
    import sys, json
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        img = cv2.imread(img_path)
        if img is None:
            print("❌ Cannot read image")
            sys.exit(1)
        feats = extract_features(img)
        print("Features extracted:")
        print(json.dumps(feats, indent=2))
    else:
        print("No image provided — showing demo with synthetic data")
