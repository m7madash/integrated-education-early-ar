#!/usr/bin/env python3
"""
Climate Justice — Water Justice Module
Calculate water scarcity and injustice metrics.
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RegionWater:
    """Water data for a region."""
    name: str
    country: str
    daily_consumption_liters: float  # per person
    population: int
    water_quality_score: float = 1.0  # 0-1 (1 = clean, 0 = undrinkable)
    source: str = "estimated"

    def is_scarce(self, threshold_liters: float = 50.0) -> bool:
        """Check if region suffers water scarcity (< 50L/person/day)."""
        return self.daily_consumption_liters < threshold_liters

    def injustice_score(self, global_avg: float = 100.0) -> float:
        """
        Calculate water injustice score (0-100).
        Higher score = more injustice (lower consumption relative to global average).
        Formula: ((global_avg - local) / global_avg) * 100
        """
        if self.daily_consumption_liters >= global_avg:
            return 0.0
        return ((global_avg - self.daily_consumption_liters) / global_avg) * 100

class WaterJustice:
    """Analyze water justice across regions."""

    def __init__(self, data_source: str = None):
        self.data_source = data_source or "built-in examples"
        self.regions: List[RegionWater] = []
        self._load_examples()

    def _load_examples(self):
        """Load example regions (hardcoded for demo)."""
        examples = [
            RegionWater("Gaza Strip", "Palestine", 35.0, 2_000_000, water_quality_score=0.3),
            RegionWater("West Bank", "Palestine", 70.0, 3_000_000, water_quality_score=0.6),
            RegionWater("Khartoum", "Sudan", 40.0, 6_000_000, water_quality_score=0.5),
            RegionWater("Dhaka", "Bangladesh", 50.0, 22_000_000, water_quality_score=0.4),
            RegionWater("Amsterdam", "Netherlands", 150.0, 800_000, water_quality_score=0.95),
        ]
        self.regions = examples

    def analyze_region(self, region: RegionWater) -> Dict:
        """Generate a detailed analysis for a region."""
        score = region.injustice_score()
        return {
            "region": region.name,
            "country": region.country,
            "daily_consumption_liters": region.daily_consumption_liters,
            "is_scarce": region.is_scarce(),
            "injustice_score_water": round(score, 1),
            "water_quality": region.water_quality_score,
            "population_affected": region.population if region.is_scarce() else 0,
            "recommendations": self._recommendations(region)
        }

    def analyze_all(self) -> List[Dict]:
        """Analyze all loaded regions."""
        return [self.analyze_region(r) for r in self.regions]

    @staticmethod
    def _recommendations(region: RegionWater) -> List[str]:
        """Generate recommendations based on water situation."""
        recs = []
        if region.is_scarce():
            recs.append("Implement rainwater harvesting systems")
            recs.append("Repair and expand water distribution networks to reduce loss")
            recs.append("Invest in desalination (solar-powered if possible)")
        if region.water_quality_score < 0.5:
            recs.append("Purify water sources — remove pollutants (e.g., seawater intrusion, sewage)")
            recs.append("Monitor water quality continuously — public alert system")
        recs.append("Water justice advocacy: wealthy nations must fund infrastructure")
        return recs

# Convenience
def analyze_water(region_name: str) -> Dict:
    wj = WaterJustice()
    region = next((r for r in wj.regions if r.name.lower() == region_name.lower()), None)
    if not region:
        return {"error": f"Region '{region_name}' not found"}
    return wj.analyze_region(region)

if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="Water Justice Analyzer")
    parser.add_argument("--region", help="Region name to analyze (e.g., 'Gaza Strip')")
    parser.add_argument("--all", action="store_true", help="Analyze all example regions")
    args = parser.parse_args()

    wj = WaterJustice()
    if args.region:
        result = analyze_water(args.region)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.all:
        results = wj.analyze_all()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("Specify --region or --all")
