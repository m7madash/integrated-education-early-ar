#!/usr/bin/env python3
"""
Climate Justice — Climate Displacement Tracking
Track populations displaced by climate impacts (floods, drought, sea-level rise).
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DisplacementEvent:
    """Represents a climate-induced displacement event."""
    region: str
    country: str
    displaced_count: int  # number of people displaced
    cause: str  # "flood", "drought", "sea_level_rise", "wildfire", "storm", "slow_onset"
    year: int
    status: str  # "ongoing", "resettled", "returned", "protracted"

    def severity_score(self) -> int:
        """
        Severity level 1-5 based on scale of displacement.
        UNHCR thresholds: >1M = 5 (massive), 500k-1M = 4, 100k-500k = 3, 10k-100k = 2, <10k = 1.
        """
        if self.displaced_count >= 1_000_000:
            return 5
        elif self.displaced_count >= 500_000:
            return 4
        elif self.displaced_count >= 100_000:
            return 3
        elif self.displaced_count >= 10_000:
            return 2
        else:
            return 1

class ClimateRefugees:
    """Tracker for climate-displaced populations."""

    def __init__(self):
        self.events: List[DisplacementEvent] = []
        self._load_events()

    def _load_events(self):
        """Load example displacement events (hardcoded for demo)."""
        self.events = [
            # Ongoing major displacements
            DisplacementEvent("Gaza Strip", "Palestine", 500_000, "war + blockade", 2023, "ongoing"),
            DisplacementEvent("Khartoum", "Sudan", 300_000, "flood", 2023, "ongoing"),
            DisplacementEvent("Mekong Delta", "Vietnam", 1_200_000, "sea_level_rise", 2022, "ongoing"),
            DisplacementEvent("Sahel Region", "Mali", 400_000, "drought", 2021, "ongoing"),
            DisplacementEvent("Tangier", "Morocco", 50_000, "wildfire", 2022, "resettled"),
            DisplacementEvent("Karachi", "Pakistan", 800_000, "flood", 2022, "protracted"),
            DisplacementEvent("Sindh", "Pakistan", 1_000_000, "flood", 2022, "protracted"),
            DisplacementEvent("Barbados", "Caribbean", 30_000, "hurricane", 2021, "resettled"),
            DisplacementEvent("Lamu", "Kenya", 15_000, "sea_level_rise", 2023, "ongoing"),
            DisplacementEvent("Fire Islands", "USA", 5_000, "sea_level_rise", 2022, "resettled"),
        ]

    def get_events_by_region(self, region_name: str) -> List[DisplacementEvent]:
        """Get all displacement events for a given region."""
        return [e for e in self.events if e.region.lower() == region_name.lower()]

    def total_displaced(self, region_name: str = None) -> int:
        """Total displaced count; if region specified, sum that region's events."""
        if region_name:
            return sum(e.displaced_count for e in self.get_events_by_region(region_name))
        return sum(e.displaced_count for e in self.events)

    def needs_assessment(self, region_name: str) -> Dict:
        """
        Generate a needs assessment for displaced population in a region.
        Returns: dictionary with totals, severity, causes, immediate needs, recommended actions.
        """
        events = self.get_events_by_region(region_name)
        if not events:
            return {"error": f"No displacement data for region '{region_name}'"}
        total = sum(e.displaced_count for e in events)
        avg_severity = sum(e.severity_score() for e in events) / len(events)
        # Primary cause: most frequent
        cause_counts = {}
        for e in events:
            cause_counts[e.cause] = cause_counts.get(e.cause, 0) + 1
        primary_cause = max(cause_counts, key=cause_counts.get)
        overall_status = "critical" if avg_severity >= 4 else "high" if avg_severity >= 3 else "medium" if avg_severity >= 2 else "low"
        return {
            "region": region_name,
            "total_displaced": total,
            "primary_cause": primary_cause,
            "events_count": len(events),
            "average_severity": round(avg_severity, 1),
            "status_level": overall_status,
            "immediate_needs": [
                "Shelter (tents, temporary housing)",
                "Clean water and sanitation",
                "Food and nutritional support",
                "Medical aid and disease prevention",
                "Psychosocial support",
                "Legal aid (documentation, asylum claims)"
            ],
            "recommended_actions": [
                "Coordinate with UNHCR, IOM, and local NGOs",
                "Establish safe corridors for aid delivery",
                "Protect displaced from exploitation and trafficking",
                "Long-term: support return or resettlement with dignity",
                "Advocate for climate finance to support hosting communities"
            ]
        }

def analyze_refugees(region_name: str) -> Dict:
    """Convenience function: get needs assessment for region."""
    tracker = ClimateRefugees()
    return tracker.needs_assessment(region_name)

if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="Climate Displacement Tracker")
    parser.add_argument("--region", help="Region name (e.g., 'Gaza Strip')")
    parser.add_argument("--global", action="store_true", help="Show global displaced total (tracked)")
    args = parser.parse_args()

    if args.region:
        result = analyze_refugees(args.region)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.global:
        total = ClimateRefugees().total_displaced()
        print(f"Total climate-displaced tracked: {total:,} (subset of actual)")
    else:
        parser.print_help()
