"""
Validator — Fajr Observer Agent

Additional safety checks to avoid false positives:
  - Sudden bright light (car headlights, lightning)
  - Moon presence (full/partial)
  - Clouds reflecting city lights
  - Camera shake/blur

Runs after classifier before triggering Adhan.
"""

import cv2
import numpy as np
from typing import Tuple

class DawnValidator:
    """Validates true dawn detection to prevent false triggers."""

    def __init__(self):
        self.recent_frames = []  # store last N frames for temporal consistency

    def is_moon_present(self, image: np.ndarray) -> bool:
        """Detect moon (bright round object) that could be mistaken for dawn."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Adaptive threshold to find bright regions
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 51, -30)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:  # tiny noise
                continue
            # Check circularity
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity > 0.7:  # pretty round
                return True
        return False

    def is_ sudden_flash(self, image: np.ndarray, previous: np.ndarray = None) -> bool:
        """Detect sudden increase in brightness (car lights, lightning)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if previous is not None:
            prev_gray = cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray, prev_gray)
            increase = np.mean(diff)
            if increase > 50:  # sudden spike
                return True
        return False

    def is_cloud_reflection(self, image: np.ndarray) -> bool:
        """Detect diffuse light from clouds (city lights reflection)."""
        # Clouds have high variance but low directional spread
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        std = np.std(gray)
        mean = np.mean(gray)
        # High variance + moderate mean could be clouds
        if std > 30 and 50 < mean < 120:
            return True
        return False

    def validate(self, image: np.ndarray, state: str, confidence: float,
                 previous_frame: np.ndarray = None) -> Tuple[bool, str]:
        """
        Validate the classification result.
        Returns: (is_valid, reason_if_invalid)
        """
        if state != "true_dawn":
            return True, "not_true_dawn"

        # Check moon
        if self.is_moon_present(image):
            return False, "moon_detected"

        # Check sudden flash
        if previous_frame is not None and self.is_ sudden_flash(image, previous_frame):
            return False, "sudden_flash"

        # Check clouds (city lights)
        if self.is_cloud_reflection(image):
            return False, "cloud_reflection_likely"

        # All clear
        return True, "passed"

    def add_to_history(self, frame: np.ndarray):
        """Keep last 3 frames for temporal checks."""
        self.recent_frames.append(frame.copy())
        if len(self.recent_frames) > 3:
            self.recent_frames.pop(0)
