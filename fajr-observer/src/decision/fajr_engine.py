"""
Fajr Engine — Decision Engine for Fajr Observer Agent

Central orchestrator:
  - Controls camera capture schedule
  - Runs classification pipeline
  - Decides when to trigger Adhan
  - Logs all decisions with images
  - Implements safety validators
"""

import cv2
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
from .dawn_classifier import DawnClassifier
from ..camera.capture import CameraCapture
from ..notification.azan_trigger import AdhanTrigger
from ..utils.logger import DecisionLogger

class FajrEngine:
    """Main decision loop for Fajr detection."""

    def __init__(self,
                 latitude: float,
                 longitude: float,
                 timezone: str,
                 config_dir: str = "../../config",
                 logs_dir: str = "../../logs",
                 dry_run: bool = True):
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.dry_run = dry_run

        # Components
        self.classifier = DawnClassifier(config_dir)
        self.trigger = AdhanTrigger(dry_run=dry_run)
        self.logger = DecisionLogger(logs_dir)

        # State
        self.state = "night"
        self.start_time = datetime.now()
        self.running = False

    def run_observation_window(self, start_hour: int = 3, end_hour: int = 6,
                                interval_seconds: int = 15):
        """
        Observe the eastern sky during the pre-Fajr window.
        Stops when true dawn is confirmed or window ends.
        """
        self.running = True
        self.logger.log_event("observation_start", {
            "start_hour": start_hour,
            "end_hour": end_hour,
            "interval": interval_seconds
        })

        with CameraCapture() as cam:
            while self.running and self._within_window(start_hour, end_hour):
                try:
                    frame = cam.capture(save=False)  # we'll save manually on key events
                    state, conf, features = self.classifier.classify(
                        frame, self.latitude, datetime.now().month
                    )

                    # Log every frame (lightweight)
                    self.logger.log_frame(state, conf, features)

                    # Check for trigger
                    if self.classifier.should_trigger_adhan(state, conf,
                        self.classifier.thresh_mgr.get_thresholds(self.latitude)):
                        self._handle_true_dawn(frame)
                        break

                    # Print status every iteration
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] {state.upper()} | conf={conf:.2f} | hits={self.classifier.consecutive_hits}", end="")

                    time.sleep(interval_seconds)

        self.running = False
        self.logger.log_event("observation_end", {})
        print("\n✅ Observation window ended.")

    def _within_window(self, start_hour: int, end_hour: int) -> bool:
        now = datetime.now()
        return start_hour <= now.hour < end_hour

    def _handle_true_dawn(self, frame):
        """Actions when true dawn confirmed."""
        self.state = "true_dawn"
        print(f"\n✅ TRUE DAWN DETECTED at {datetime.now().strftime('%H:%M:%S')}")

        # Save image with timestamp
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = Path(f"logs/fajr_true_dawn_{ts}.jpg")
        cv2.imwrite(str(img_path), frame)
        print(f"   Image saved: {img_path}")

        # Trigger Adhan
        self.trigger.trigger()
        self.logger.log_event("adhan_triggered", {"image": str(img_path)})

        # Stop observation (Fajr time entered)
        self.running = False

    def stop(self):
        self.running = False


def run_fajr_engine(latitude: float, longitude: float, timezone: str = "Asia/Gaza",
                    dry_run: bool = True):
    """Convenience entrypoint."""
    print("=" * 60)
    print("FAJR OBSERVER — Engine Starting")
    print(f"Location: {latitude}, {longitude} | TZ: {timezone}")
    print(f"Mode: {'DRY-RUN (no Adhan)' if dry_run else 'LIVE'}")
    print("=" * 60)

    engine = FajrEngine(latitude, longitude, timezone, dry_run=dry_run)
    try:
        engine.run_observation_window()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        engine.stop()


if __name__ == "__main__":
    # Quick test with synthetic data
    print("Fajr Engine Module — for integration testing")
    print("Use: from decision.fajr_engine import FajrEngine")
