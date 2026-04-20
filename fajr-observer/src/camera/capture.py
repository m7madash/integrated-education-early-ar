"""
Camera Capture Module — Fajr Observer Agent

Captures images from the eastern sky at configurable intervals.
Designed for Raspberry Pi + Pi Camera or USB webcam.
"""

import cv2
import time
import yaml
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraCapture:
    """Manages camera capture for dawn detection."""

    def __init__(self, config_path: str = "../config/camera_settings.yaml"):
        self.config = self._load_config(config_path)
        self.camera = None
        self.capture_dir = Path(self.config.get("storage_dir", "logs/captures"))
        self.capture_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, path: str) -> dict:
        """Load YAML config or use defaults."""
        try:
            import yaml
            with open(path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Config not found, using defaults: {e}")
            return {
                "device_id": 0,
                "width": 1920,
                "height": 1080,
                "exposure": -1,  # auto
                "iso": 400,
                "interval_seconds": 15,
                "storage_dir": "logs/captures"
            }

    def open(self):
        """Initialize camera."""
        self.camera = cv2.VideoCapture(self.config["device_id"])
        if not self.camera.isOpened():
            raise RuntimeError("Cannot open camera")
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["width"])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["height"])
        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # manual mode
        self.camera.set(cv2.CAP_PROP_EXPOSURE, self.config["exposure"])
        logger.info(f"Camera opened: {self.config['width']}x{self.config['height']}")

    def capture(self, save: bool = True) -> "np.ndarray":
        """Grab a single frame."""
        if self.camera is None:
            self.open()
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError("Failed to capture frame")
        if save:
            self._save(frame)
        return frame

    def _save(self, frame):
        """Save frame with timestamp."""
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path = self.capture_dir / f"fajr_{ts}.jpg"
        cv2.imwrite(str(path), frame)
        logger.debug(f"Saved: {path}")

    def close(self):
        if self.camera:
            self.camera.release()
            self.camera = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


defcontinuous_capture(interval: int = 15, duration_minutes: int = 180):
    """Capture continuously for duration (default 3 hours before Fajr)."""
    import numpy as np
    start = time.time()
    end = start + (duration_minutes * 60)
    frames = []

    with CameraCapture() as cam:
        logger.info(f"Starting continuous capture: {duration_minutes} minutes, interval {interval}s")
        while time.time() < end:
            frame = cam.capture()
            frames.append(frame)
            time.sleep(interval)

    logger.info(f"Capture complete: {len(frames)} frames")
    return frames


if __name__ == "__main__":
    # Quick test
    print("Camera Capture Module — Fajr Observer")
    print("Usage: python3 -m src.camera.capture [--test]")
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        cam = CameraCapture()
        cam.open()
        frame = cam.capture()
        print(f"Frame shape: {frame.shape}")
        cam.close()
        print("✅ Camera test passed")
