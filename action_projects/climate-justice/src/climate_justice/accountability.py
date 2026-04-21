#!/usr/bin/env python3
"""
Climate Justice — Carbon Polluter Accountability
Track and score corporate/national carbon emissions.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

@dataclass
class PolluterRecord:
    """A single polluter entity."""
    id: str
    name: str
    type: str  # 'corporation' | 'country' | 'city'
    sector: str  # 'energy', 'transport', 'agriculture', etc.
    emissions_mt: float  # metric tons CO2e (current year)
    emissions_historical: float  # total since 1850
    population: Optional[float] = None  # millions (for per-capita)
    revenue_usd: Optional[float] = None  # annual revenue (corporate)
    gdp_usd: Optional[float] = None  # GDP (country)
    has_netzero_pledge: bool = False
    pledge_year: Optional[int] = None
    compliance_score: float = 0.0  # 0-1 (how well meeting pledges)
    last_updated: str = ""

@dataclass
class AccountabilityReport:
    """Full accountability assessment."""
    polluter: PolluterRecord
    risk_level: str  # 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME'
    justice_score: float  # 0-1 (higher = more just/environmentally friendly)
    per_capita_emissions: Optional[float]  # mt/year/person
    emissions_intensity: float  # emissions per $ revenue or per $ GDP
    historical_contribution: float  # % of global total
    recommendations: List[str]
    verdict: str  # 'EXCELLENT' | 'COMPLIANT' | 'NON_COMPLIANT' | 'CRIMINAL_NEGLECT'

class CarbonAccountability:
    """Assess and rank carbon polluters."""

    def __init__(self, data_path: Optional[Path] = None):
        """
        Load polluter database.
        Data format: JSON list of PolluterRecord dicts.
        """
        self.polluters: List[PolluterRecord] = []
        if data_path and data_path.exists():
            self._load_data(data_path)
        else:
            # Load default synthetic data (for demo)
            self._load_default_data()

    def _load_data(self, path: Path):
        with open(path) as f:
            data = json.load(f)
        self.polluters = [PolluterRecord(**item) for item in data]

    def _load_default_data(self):
        """Synthetic dataset of top corporate & national polluters (public data estimates)."""
        # Based on public data (CDP, IEA, EPA). For demo only — replace with official DB.
        self.polluters = [
            PolluterRecord(
                id="corp_001",
                name="Saudi Aramco",
                type="corporation",
                sector="energy",
                emissions_mt=586.0,  # 2022 estimate
                emissions_historical=17000.0,
                revenue_usd=400000000000,
                has_netzero_pledge=True,
                pledge_year=2050,
                compliance_score=0.2,
                last_updated="2026-04-21"
            ),
            PolluterRecord(
                id="corp_002",
                name="Chevron",
                type="corporation",
                sector="energy",
                emissions_mt=504.0,
                emissions_historical=12000.0,
                revenue_usd=246000000000,
                has_netzero_pledge=True,
                pledge_year=2050,
                compliance_score=0.3,
                last_updated="2026-04-21"
            ),
            PolluterRecord(
                id="corp_003",
                name="Gazprom",
                type="corporation",
                sector="energy",
                emissions_mt=480.0,
                emissions_historical=11000.0,
                revenue_usd=150000000000,
                has_netzero_pledge=False,
                compliance_score=0.0,
                last_updated="2026-04-21"
            ),
            PolluterRecord(
                id="country_001",
                name="China",
                type="country",
                sector="total",
                emissions_mt=11000.0,
                emissions_historical=300000.0,
                population=1412.0,
                gdp_usd=18000000000000,
                has_netzero_pledge=True,
                pledge_year=2060,
                compliance_score=0.4,
                last_updated="2026-04-21"
            ),
            PolluterRecord(
                id="country_002",
                name="United States",
                type="country",
                sector="total",
                emissions_mt=5200.0,
                emissions_historical=500000.0,
                population=332.0,
                gdp_usd=25000000000000,
                has_netzero_pledge=True,
                pledge_year=2050,
                compliance_score=0.5,
                last_updated="2026-04-21"
            ),
            PolluterRecord(
                id="country_003",
                name="India",
                type="country",
                sector="total",
                emissions_mt=2700.0,
                emissions_historical=60000.0,
                population=1380.0,
                gdp_usd=3200000000000,
                has_netzero_pledge=True,
                pledge_year=2070,
                compliance_score=0.3,
                last_updated="2026-04-21"
            ),
        ]

    def analyze(self, polluter_id: str) -> AccountabilityReport:
        """Generate accountability report for a given polluter."""
        polluter = next((p for p in self.polluters if p.id == polluter_id), None)
        if not polluter:
            raise ValueError(f"Polluter {polluter_id} not found")

        # 1. Per-capita emissions (if population known)
        per_capita = None
        if polluter.population and polluter.population > 0:
            per_capita = polluter.emissions_mt / polluter.population

        # 2. Emissions intensity (per $经济活动)
        intensity = 0.0
        if polluter.type == 'corporation' and polluter.revenue_usd:
            intensity = polluter.emissions_mt / (polluter.revenue_usd / 1e9)  # mt per $1B revenue
        elif polluter.type == 'country' and polluter.gdp_usd:
            intensity = polluter.emissions_mt / (polluter.gdp_usd / 1e12)  # mt per $1T GDP

        # 3. Historical contribution (% global approx) — simplified
        # Assume global historical ~ 2.4 trillion mt CO2e since 1850
        historical_global = 2400000.0  # Gt = billion metric tons
        historical_pct = polluter.emissions_historical / historical_global * 100

        # 4. Justice score (higher = better/environmentally just)
        # Factors: low emissions, high compliance, clean intensity
        # Baseline normalization (rough)
        max_emissions = max(p.emissions_mt for p in self.polluters)
        max_intensity = max(
            p.emissions_mt / (p.revenue_usd/1e9) if p.revenue_usd else 0
            for p in self.polluters
        )
        # Normalize 0-1
        emissions_norm = 1 - (polluter.emissions_mt / max_emissions)
        intensity_norm = 1 - (intensity / max_intensity) if max_intensity > 0 else 0.5
        compliance_norm = polluter.compliance_score
        justice_score = (emissions_norm * 0.4 + intensity_norm * 0.3 + compliance_norm * 0.3)

        # 5. Risk level based on emissions + compliance
        if polluter.emissions_mt > 1000 or intensity > 50:
            risk = "EXTREME"
        elif polluter.emissions_mt > 500 or intensity > 20:
            risk = "HIGH"
        elif polluter.emissions_mt > 100:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # 6. Recommendations
        recommendations = self._generate_recommendations(polluter, per_capita, intensity, risk)

        # 7. Verdict
        verdict = self._verdict(justice_score, polluter.compliance_score, risk)

        return AccountabilityReport(
            polluter=polluter,
            risk_level=risk,
            justice_score=round(justice_score, 2),
            per_capita_emissions=round(per_capita, 2) if per_capita else None,
            emissions_intensity=round(intensity, 2),
            historical_contribution=round(historical_pct, 2),
            recommendations=recommendations,
            verdict=verdict
        )

    def _generate_recommendations(self, polluter: PolluterRecord, per_capita: Optional[float], intensity: float, risk: str) -> List[str]:
        recs = []
        if polluter.type == 'corporation':
            if not polluter.has_netzero_pledge:
                recs.append("Set a public, science-based net-zero target (by 2050 or sooner)")
            if polluter.compliance_score < 0.5:
                recs.append("Publish annual emissions audit (third-party verified)")
            if intensity > 20:
                recs.append("Invest in renewable energy and efficiency to reduce emissions per $ revenue")
            recs.append("Transition Just: support affected workers and communities")
        else:  # country
            if not polluter.has_netzero_pledge:
                recs.append("Commit to net-zero emissions nationally (legally binding)")
            if per_capita and per_capita > 5:
                recs.append("Reduce per-capita consumption through clean public transit and green buildings")
            recs.append("Finance climate adaptation for vulnerable nations (loss & damage)")
            recs.append("End fossil fuel subsidies ($7 trillion globally in 2022)")

        if risk in ['HIGH', 'EXTREME']:
            recs.append("Immediate action required: publish quarterly progress reports")
            recs.append("Subject to carbon tax or border adjustment if no progress")
        recs.append("Align with Paris Agreement 1.5°C pathway")
        return recs

    def _verdict(self, justice_score: float, compliance: float, risk: str) -> str:
        if justice_score >= 0.8 and compliance >= 0.8:
            return "EXCELLENT — Climate leader"
        elif justice_score >= 0.6 and compliance >= 0.5:
            return "COMPLIANT — On track, but needs acceleration"
        elif justice_score >= 0.4 or compliance >= 0.3:
            return "NON_COMPLIANT — Insufficient effort"
        else:
            return "CRIMINAL_NEGLECT — Willful disregard for planetary boundaries"

    def rank(self, top_n: int = 10) -> List[Dict]:
        """Return ranked list of polluters by emissions intensity."""
        rankings = []
        for p in self.polluters:
            intensity = (p.emissions_mt / (p.revenue_usd/1e9)) if p.revenue_usd else 0
            rankings.append({
                'id': p.id,
                'name': p.name,
                'type': p.type,
                'emissions_mt': p.emissions_mt,
                'intensity': round(intensity, 2),
                'risk': self.analyze(p.id).risk_level
            })
        rankings.sort(key=lambda x: x['intensity'], reverse=True)
        return rankings[:top_n]

# Convenience
def analyze_polluter(polluter_id: str, data_path: Optional[Path] = None) -> Dict:
    evaluator = CarbonAccountability(data_path)
    report = evaluator.analyze(polluter_id)
    return asdict(report)

def rank_polluters(data_path: Optional[Path] = None, top_n: int = 10) -> List[Dict]:
    evaluator = CarbonAccountability(data_path)
    return evaluator.rank(top_n)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Carbon Polluter Accountability")
    parser.add_argument("polluter_id", nargs="?", help="Polluter ID to analyze")
    parser.add_argument("--rank", action="store_true", help="Show ranked top polluters")
    parser.add_argument("--data", type=Path, help="Path to polluters JSON data")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.rank:
        results = rank_polluters(args.data)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("🏆 Top Carbon Polluters (by emissions intensity):")
            for r in results:
                print(f" {r['rank'] if 'rank' in r else ''} {r['name']} — {r['emissions_mt']} Mt CO2e — intensity {r['intensity']} — {r['risk']}")
    elif args.polluter_id:
        result = analyze_polluter(args.polluter_id, args.data)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            pr = result['polluter']
            print(f"📊 Accountability Report: {pr['name']} ({pr['type']}, {pr['sector']})")
            print(f"Justice Score: {result['justice_score']}/1.0")
            print(f"Risk Level: {result['risk_level']}")
            print(f"Verdict: {result['verdict']}")
            if result['per_capita_emissions']:
                print(f"Per-capita emissions: {result['per_capita_emissions']} mt/year/person")
            print(f"Emissions intensity: {result['emissions_intensity']} mt per $B revenue (corp) or $T GDP (country)")
            print(f"Historical contribution: {result['historical_contribution']}% of global total")
            print("\nRecommendations:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f" {i}. {rec}")
    else:
        parser.print_help()
