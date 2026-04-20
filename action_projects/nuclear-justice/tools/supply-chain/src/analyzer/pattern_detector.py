"""
Supply Chain Analyzer — Tool 3 of Nuclear Justice

Analyzes tracked networks to identify:
- Critical chokepoints (single points of failure)
- Suspicious routing (transshipment through third countries)
- High-risk supplier clusters
- Timing patterns (rapid sequential shipments)

Generates disruption recommendations for nonviolent intervention.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime, timedelta

@dataclass
class Chokepoint:
    entity_name: str
    centrality: float  # 0-1, how central in network
    risk_level: str  # "critical", "high", "medium"
    reason: str

@dataclass
class SuspiciousRoute:
    origin: str
    destination: str
    waypoints: List[str]
    risk_score: int
    indicators: List[str]

@dataclass
class TimePattern:
    pattern_type: str  # "burst", "regular", "seasonal"
    description: str
    affected_shipments: List[str]

class SupplyChainAnalyzer:
    """Analyzes supply chain networks for vulnerabilities and suspicious patterns."""

    def __init__(self, network_data: dict):
        self.network = network_data
        self.entities = {e["name"]: e for e in network_data.get("entities", [])}
        self.shipments = network_data.get("shipments", [])
        self.connections = network_data.get("connections", [])

    def find_chokepoints(self) -> List[Chokepoint]:
        """Identify entities that are critical to network flow."""
        # Build adjacency
        from_count = {}
        to_count = {}

        for con in self.connections:
            from_count[con["from_entity"]] = from_count.get(con["from_entity"], 0) + 1
            to_count[con["to_entity"]] = to_count.get(con["to_entity"], 0) + 1

        # Centrality = outgoing + incoming connections
        centrality = {}
        for name in set(list(from_count.keys()) + list(to_count.keys())):
            centrality[name] = from_count.get(name, 0) + to_count.get(name, 0)

        max_centrality = max(centrality.values()) if centrality else 1

        chokepoints = []
        for name, score in centrality.items():
            norm = score / max_centrality
            risk = "critical" if norm >= 0.7 else "high" if norm >= 0.4 else "medium"
            chokepoints.append(Chokepoint(
                entity_name=name,
                centrality=norm,
                risk_level=risk,
                reason=f"Connected to {score} other entities in network"
            ))

        return sorted(chokepoints, key=lambda x: x.centrality, reverse=True)

    def detect_suspicious_routes(self) -> List[SuspiciousRoute]:
        """Find shipments with unusual routing (excessive waypoints, sanctions evasions)."""
        suspicious = []

        # Group shipments by origin-destination pair
        routes = {}
        for s in self.shipments:
            key = (s["origin"], s["destination"])
            routes.setdefault(key, []).append(s)

        for (origin, dest), shiplist in routes.items():
            if len(shiplist) > 3:
                # Multiple shipments on same route could be bulk transfer
                suspicious.append(SuspiciousRoute(
                    origin=origin,
                    destination=dest,
                    waypoints=[],
                    risk_score=7,
                    indicators=[f"{len(shiplist)} shipments on same route — possible bulk transfer"]
                ))

        # Check for transshipment through high-risk jurisdictions
        high_risk_countries = ["State X", "Country Y"]  # TODO: load from config
        for s in self.shipments:
            # If origin or destination is high-risk
            if s["origin"] in high_risk_countries or s["destination"] in high_risk_countries:
                suspicious.append(SuspiciousRoute(
                    origin=s["origin"],
                    destination=s["destination"],
                    waypoints=[],
                    risk_score=8,
                    indicators=["Involves high-risk jurisdiction known for nuclear proliferation"]
                ))

        return suspicious

    def find_timing_patterns(self) -> List[TimePattern]:
        """Detect burst shipments or regular intervals (covert replenishment)."""
        # Group by date
        from collections import defaultdict
        daily_counts = defaultdict(int)
        for s in self.shipments:
            d = s.get("date", "")
            if d:
                daily_counts[d] += 1

        patterns = []
        dates_sorted = sorted(daily_counts.keys())
        if len(dates_sorted) >= 5:
            # Check for bursts: any day with > 2x average
            avg = sum(daily_counts.values()) / len(dates_sorted)
            burst_days = [d for d, cnt in daily_counts.items() if cnt > avg * 2]
            if burst_days:
                patterns.append(TimePattern(
                    pattern_type="burst",
                    description=f"Burst shipments detected on: {', '.join(burst_days)}",
                    affected_shipments=[]
                ))

        return patterns

    def generate_disruption_recommendations(self, chokepoints: List[Chokepoint],
                                            routes: List[SuspiciousRoute]) -> List[dict]:
        """Produce nonviolent disruption actions (legal, technical, informational)."""
        recommendations = []

        for cp in chokepoints:
            if cp.risk_level in ["critical", "high"]:
                recommendations.append({
                    "target": cp.entity_name,
                    "action_type": "legal_block",
                    "description": f"File legal petition to restrict {cp.entity_name} from international contracts",
                    "confidence": cp.centrality,
                    "principle": "Justice through due process"
                })
                recommendations.append({
                    "target": cp.entity_name,
                    "action_type": "financial_block",
                    "description": f"Add {cp.entity_name} to sanctions watchlist (freeze assets)",
                    "confidence": cp.centrality,
                    "principle": "Nonviolent economic pressure"
                })

        for route in routes:
            recommendations.append({
                "target": f"{route.origin}→{route.destination}",
                "action_type": "inspection_alert",
                "description": "Alert customs authorities to inspect all shipments on this route",
                "risk_score": route.risk_score,
                "principle": "Lawful enforcement"
            })

        return recommendations

    def analyze(self) -> dict:
        """Run full analysis pipeline."""
        chokepoints = self.find_chokepoints()
        suspicious_routes = self.detect_suspicious_routes()
        timing_patterns = self.find_timing_patterns()
        recommendations = self.generate_disruption_recommendations(chokepoints, suspicious_routes)

        return {
            "analysis_date": datetime.now().isoformat(),
            "network_summary": {
                "total_entities": len(self.entities),
                "total_shipments": len(self.shipments),
                "total_connections": len(self.connections)
            },
            "chokepoints": [asdict(cp) for cp in chokepoints],
            "suspicious_routes": [asdict(r) for r in suspicious_routes],
            "timing_patterns": [asdict(tp) for tp in timing_patterns],
            "disruption_recommendations": recommendations
        }

    def save_report(self, output_path: Path):
        report = self.analyze()
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path

if __name__ == "__main__":
    print("Supply Chain Analyzer — Tool 3 (Prototype)")
    print("Waiting for network data from tracker...")
