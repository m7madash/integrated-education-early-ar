#!/usr/bin/env python3
"""
Climate Justice — Energy Poverty Module
Measure energy access and poverty metrics.
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RegionEnergy:
    """Energy data for a region."""
    name: str
    country: str
    avg_kwh_per_person_per_month: float
    electricity_access_rate: float  # 0-1 (percentage of population with grid)
    daily_blackout_hours: float
    primary_source: str  # "grid", "solar", "diesel", "none", "hydro", etc.

    def is_energy_poor(self, poverty_line_kwh: float = 100.0) -> bool:
        """Check if region suffers energy poverty (< 100 kWh/person/month is typical threshold)."""
        return self.avg_kwh_per_person_per_month < poverty_line_kwh

    def energy_injustice_score(self, global_avg: float = 500.0) -> float:
        """
        Calculate energy injustice score (0-100).
        Higher score = more injustice (much lower consumption than global average).
        Formula: ((global_avg - local) / global_avg) * 100, capped at 100.
        """
        if self.avg_kwh_per_person_per_month >= global_avg:
            return 0.0
        score = ((global_avg - self.avg_kwh_per_person_per_month) / global_avg) * 100
        return min(score, 100.0)

class EnergyPoverty:
    """Analyze energy poverty across regions."""

    def __init__(self):
        self.regions: List[RegionEnergy] = []
        self._load_examples()

    def _load_examples(self):
        """Load example regions (hardcoded for demo)."""
        examples = [
            RegionEnergy("Gaza Strip", "Palestine", 120.0, 0.45, 20.0, "grid"),
            RegionEnergy("West Bank", "Palestine", 250.0, 0.75, 8.0, "grid"),
            RegionEnergy("Khartoum", "Sudan", 80.0, 0.35, 12.0, "diesel"),
            RegionEnergy("Rwanda", "Rwanda", 50.0, 0.25, 16.0, "solar"),
            RegionEnergy("New York", "USA", 1200.0, 0.99, 0.5, "grid"),
            RegionEnergy("Dhaka", "Bangladesh", 90.0, 0.60, 10.0, "grid"),
        ]
        self.regions = examples

    def analyze_region(self, region: RegionEnergy) -> Dict:
        """Generate a detailed analysis for a region."""
        score = region.energy_injustice_score()
        is_poor = region.is_energy_poor()
        return {
            "region": region.name,
            "country": region.country,
            "kwh_per_person_month": region.avg_kwh_per_person_per_month,
            "energy_poverty": is_poor,
            "injustice_score_energy": round(score, 1),
            "electricity_access_rate": region.electricity_access_rate,
            "daily_blackout_hours": region.daily_blackout_hours,
            "primary_source": region.primary_source,
            "recommendations": self._recommendations(region)
        }

    def analyze_all(self) -> List[Dict]:
        """Analyze all loaded regions."""
        return [self.analyze_region(r) for r in self.regions]

    @staticmethod
    def _recommendations(region: RegionEnergy) -> List[str]:
        """Generate recommendations based on energy situation."""
        recs = []
        if region.is_energy_poor():
            recs.append("Deploy solar microgrids for essential services (hospitals, schools)")
            recs.append("Subsidize efficient cookstoves to reduce biomass/charcoal use")
            recs.append("Invest in community battery storage for resilience")
        if region.daily_blackout_hours > 6:
            recs.append("Strengthen grid infrastructure; add redundancy and decentralized sources")
        if region.electricity_access_rate < 0.5:
            recs.append("Expand grid to rural areas or provide off-grid solutions (solar home systems)")
        recs.append("Climate finance: wealthy nations must fund just transition for energy poverty")
        return recs

# Convenience
def analyze_energy(region_name: str) -> Dict:
    """Quick analysis by region name."""
    ep = EnergyPoverty()
    region = next((r for r in ep.regions if r.name.lower() == region_name.lower()), None)
    if not region:
        return {"error": f"Region '{region_name}' not found in examples"}
    return ep.analyze_region(region)

if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="Energy Poverty Analyzer")
    parser.add_argument("--region", help="Region name to analyze (e.g., 'Gaza Strip')")
    parser.add_argument("--all", action="store_true", help="Analyze all example regions")
    args = parser.parse_args()

    if args.region:
        result = analyze_energy(args.region)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.all:
        results = EnergyPoverty().analyze_all()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
