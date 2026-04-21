#!/usr/bin/env python3
"""
Climate Justice — Main Detector
Combine water, energy, and displacement metrics into an overall injustice score.
"""

from typing import Dict
from .water import WaterJustice, RegionWater as WaterRegion
from .energy import EnergyPoverty, RegionEnergy
from .refugees import ClimateRefugees

class ClimateDetector:
    """Main detector: assess climate injustice for a region."""

    def __init__(self):
        self.water = WaterJustice()
        self.energy = EnergyPoverty()
        self.refugees = ClimateRefugees()

    def assess_region(self, region_name: str) -> Dict:
        """
        Comprehensive climate injustice assessment.
        Returns combined scores and recommendations.
        """
        # Find matching region in water and energy datasets
        water_region = next((r for r in self.water.regions if r.name.lower() == region_name.lower()), None)
        energy_region = next((r for r in self.energy.regions if r.name.lower() == region_name.lower()), None)

        if not water_region or not energy_region:
            return {"error": f"Region '{region_name}' not found in water or energy datasets"}

        water_data = self.water.analyze_region(water_region)
        energy_data = self.energy.analyze_region(energy_region)
        refugee_data = self.refugees.needs_assessment(region_name)

        # Extract scores
        water_score = water_data.get("injustice_score_water", 0)
        energy_score = energy_data.get("injustice_score_energy", 0)
        # Displacement impact: ratio of displaced to population, scaled
        if "error" not in refugee_data:
            displaced = refugee_data.get("total_displaced", 0)
            # Use water region population as proxy for total pop
            pop = water_region.population
            displacement_ratio = displaced / pop if pop > 0 else 0
            displacement_score = min(displacement_ratio * 100, 100)  # scale to 0-100
        else:
            displacement_score = 0

        # Overall score: average of three components
        overall = (water_score + energy_score + displacement_score) / 3

        # Determine severity label
        severity = self._severity_label(overall)

        return {
            "region": region_name,
            "country": water_region.country,
            "scores": {
                "water_injustice": round(water_score, 1),
                "energy_injustice": round(energy_score, 1),
                "displacement_impact": round(displacement_score, 1)
            },
            "overall_injustice_score": round(overall, 1),
            "severity_level": severity,
            "details": {
                "water_consumption_liters_per_day": water_region.daily_consumption_liters,
                "energy_kwh_per_person_month": energy_region.avg_kwh_per_person_per_month,
                "climate_displaced": refugee_data.get("total_displaced", 0) if "error" not in refugee_data else 0
            },
            "recommendations": self._combine_recommendations(water_data, energy_data, refugee_data)
        }

    @staticmethod
    def _severity_label(score: float) -> str:
        if score >= 75:
            return "CRITICAL — immediate international intervention required"
        elif score >= 50:
            return "HIGH — urgent action needed"
        elif score >= 25:
            return "MEDIUM — significant injustice, address within 2 years"
        else:
            return "LOW — monitor, but not critical"

    @staticmethod
    def _combine_recommendations(water_data: Dict, energy_data: Dict, refugee_data: Dict) -> List[str]:
        """Merge recommendations from all modules, deduplicate."""
        recs = set()
        recs.update(water_data.get("recommendations", []))
        recs.update(energy_data.get("recommendations", []))
        if "recommended_actions" in refugee_data:
            recs.update(refugee_data["recommended_actions"])
        # Add cross-cutting
        recs.add("Climate finance: wealthy nations must fund adaptation and loss & damage")
        recs.add("Hold polluters accountable via carbon accountability framework")
        recs.add("Support community-led solutions; listen to frontline voices")
        return sorted(list(recs))

# Convenience
def assess_region(region_name: str) -> Dict:
    detector = ClimateDetector()
    return detector.assess_region(region_name)

if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="Climate Justice Detector — Combined Analysis")
    parser.add_argument("--region", required=True, help="Region name (e.g., 'Gaza Strip')")
    parser.add_argument("--json", action="store_true", help="Output JSON only (no extra text)")
    args = parser.parse_args()

    result = assess_region(args.region)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"=== Climate Injustice Assessment: {result['region']} ({result.get('country')}) ===\n")
        print(f"Overall Score: {result['overall_injustice_score']}/100 — {result['severity_level']}\n")
        print("Component Scores:")
        print(f"  Water: {result['scores']['water_injustice']}")
        print(f"  Energy: {result['scores']['energy_injustice']}")
        print(f"  Displacement: {result['scores']['displacement_impact']}\n")
        print("Key Stats:")
        for k, v in result["details"].items():
            print(f"  {k}: {v}")
        print("\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
