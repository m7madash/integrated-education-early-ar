"""
Threshold Loader — Fajr Observer Agent

Loads and interpolates detection thresholds based on:
  - Geographic latitude (zone)
  - Season (winter/summer/equinox)
  - Optional: weather conditions (clear/cloudy)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

class ThresholdManager:
    """Manages detection thresholds per location and season."""

    def __init__(self, config_path: str = "../../config/thresholds.json"):
        self.config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        self.global_cfg = self.config.get("global", {})
        self.zones = self.config.get("latitudinal_zones", {})
        self.seasons = self.config.get("seasonal_adjustments", {})

    def get_zone(self, latitude: float) -> str:
        """Return zone key for given latitude."""
        for zone_name, zdata in self.zones.items():
            low, high = zdata["lat_range"]
            if low <= latitude < high:
                return zone_name
        return "mid_latitude"  # fallback

    def get_season(self, month: int = None) -> str:
        """Return season key for given month (Northern Hemisphere assumption)."""
        if month is None:
            month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"  # treat as equinox for dawn detection
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"  # treat as equinox

    def get_thresholds(self, latitude: float, month: int = None) -> Dict:
        """
        Combine zone + seasonal adjustments into final thresholds.
        Returns dict with keys like:
          - horizontal_spread_threshold
          - intensity_threshold
          - consecutive_hits_required
        """
        zone_name = self.get_zone(latitude)
        season_name = self.get_season(month)

        zone_cfg = self.zones[zone_name]
        season_cfg = self.seasons.get(season_name, self.seasons["equinox"])

        # Base values from zone
        base_hspread = zone_cfg["horizontal_spread_threshold"]
        base_intensity = zone_cfg["intensity_threshold"]

        # Apply seasonal offsets
        final_hspread = base_hspread * season_cfg.get("true_dawn_delay_factor", 1.0)
        final_intensity = base_intensity + season_cfg.get("intensity_offset", 0)

        return {
            "zone": zone_name,
            "season": season_name,
            "horizontal_spread_min": final_hspread,
            "intensity_min": final_intensity,
            "vertical_streak_max": zone_cfg.get("false_dawn_characteristics", {}).get("vertical_streak_ratio_min", 2.5),
            "consecutive_hits_required": self.global_cfg.get("consecutive_hits", 3),
            "min_confidence": self.global_cfg.get("min_confidence", 0.92)
        }

    def get_roi(self, image_height: int, image_width: int) -> Tuple[int, int, int, int]:
        """
        Region of interest: bottom horizon band where dawn appears.
        Returns (x1, y1, x2, y2).
        """
        # Default: bottom 15% of image
        roi_height = int(image_height * 0.15)
        y1 = image_height - roi_height
        return (0, y1, image_width, image_height)


def classify_by_template(features: Dict, thresholds: Dict) -> Tuple[str, float]:
    """
    Wrapper around rule-based classifier using dynamic thresholds.
    (This will eventually be replaced by ML model)
    """
    # Simple heuristic using thresholds
    hs = features["horizontal_spread"]
    ar = features["avg_aspect_ratio"]
    intensity = features["mean_intensity"]

    # Night: very dark
    if intensity < 25:
        return "night", 0.95
    # False dawn: vertical, narrow
    if ar > 2.0 and hs < thresholds["horizontal_spread_min"]:
        return "false_dawn", 0.85
    # True dawn: wide horizontal spread, not too vertical
    if hs >= thresholds["horizontal_spread_min"] and ar < 1.5 and intensity > thresholds["intensity_min"]:
        return "true_dawn", 0.90
    # Default
    return "unknown", 0.5


if __name__ == "__main__":
    tm = ThresholdManager()
    print("Threshold Manager Test")
    lat = 21.5  # Gaza approximate
    print(f"Zone for lat {lat}: {tm.get_zone(lat)}")
    print(f"Season now: {tm.get_season()}")
    thr = tm.get_thresholds(lat)
    print("Thresholds:", json.dumps(thr, indent=2))
