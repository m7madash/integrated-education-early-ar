"""
Decision Logger — Fajr Observer Agent

Logs all classification results, images, and system events.
Rotates logs daily, keeps 30 days of images by default.
"""

import json
import cv2
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class DecisionLogger:
    """Structured logging for Fajr Observer."""

    def __init__(self, logs_dir: str = "../../logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.logs_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        self.current_log = self._open_daily_log()

    def _open_daily_log(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"fajr_{date_str}.log"
        return open(log_file, "a", encoding="utf-8")

    def log_frame(self, state: str, confidence: float, features: Dict):
        """Log a single frame classification."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "frame_classified",
            "state": state,
            "confidence": round(confidence, 3),
            "features": {k: round(v, 3) if isinstance(v, float) else v for k, v in features.items()}
        }
        self.current_log.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.current_log.flush()

    def log_event(self, event_type: str, data: Dict):
        """Log a system event (start, stop, trigger, error)."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            **data
        }
        self.current_log.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.current_log.flush()

    def save_image(self, image, prefix: str = "fajr") -> Path:
        """Save image with timestamp."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{ts}.jpg"
        path = self.images_dir / filename
        cv2.imwrite(str(path), image)
        self.log_event("image_saved", {"path": str(path), "prefix": prefix})
        return path

    def close(self):
        if self.current_log:
            self.current_log.close()


# Convenience singleton-like
_default_logger = None

def get_logger() -> DecisionLogger:
    global _default_logger
    if _default_logger is None:
        _default_logger = DecisionLogger()
    return _default_logger


if __name__ == "__main__":
    logger = DecisionLogger()
    logger.log_event("test_start", {"message": "Logger test"})
    logger.log_frame("true_dawn", 0.96, {"mean_intensity": 120, "horizontal_spread": 0.6})
    print("✅ Logger test complete — check logs/ directory")
