#!/usr/bin/env python3
"""Slavery → Freedom: Modern Slavery Detector for Supply Chains
Mission: End forced labor, human trafficking, debt bondage.
Focus: Supply chain transparency, red flag detection, victim protection.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Supplier:
    """A company or factory in the supply chain."""
    id: str
    name: str
    country: str
    industry: str
    workers: int
    avg_hours_per_week: float
    average_wage: float  # local currency
    has_contracts: bool
    unionized: bool
    audit_date: Optional[str]

class SlaveryDetector:
    """Detect modern slavery indicators in supplier data."""

    # Thresholds (based on ILO, Walk Free Foundation standards)
    MAX_HOURS_WEEK = 60          # Exceeding = risk
    MIN_WAGE_RATIO = 0.5         # Below 50% of national min wage = risk
    CONTRACT_REQUIRED = True     # No contracts = high risk
    FREEDOM_TO_LEAVE = True      # Workers cannot quit = slavery

    def __init__(self):
        self.red_flags = self._load_red_flags()
        self.country_min_wages = self._load_min_wages()

    def _load_red_flags(self) -> Dict[str, str]:
        """Known red flag patterns."""
        return {
            "excessive_hours": "Workers exceed 60 hours/week regularly",
            "withhold_wages": "Employer holds back pay as control",
            "no_contracts": "No written contracts or illegal contracts",
            "passport_retention": "Employer holds identity documents",
            "debt_bondage": "Workers indebted to employer, cannot leave",
            "threats_violence": "Threats or actual violence reported",
            "child_labor": "Workers under 18 in hazardous conditions",
            "forced_overtime": "Overtime mandatory without consent",
            "unfree_recruitment": "Recruiters charge exorbitant fees",
            "no_union": "Workers prohibited from unionizing"
        }

    def _load_min_wages(self) -> Dict[str, float]:
        """National minimum wages (monthly, USD equivalent)."""
        return {
            "BD": 95,     # Bangladesh
            "PK": 110,    # Pakistan
            "IN": 130,    # India
            "KH": 190,    # Cambodia
            "MM": 110,    # Myanmar
            "LA": 130,    # Laos
            "ID": 160,    # Indonesia
            "PH": 160,    # Philippines
            "VN": 180,    # Vietnam
            "CN": 310,    # China
            "PS": 450,    # Palestine ( Gaza economy distinct)
            "SY": 50,     # Syria (wartime)
            "YE": 60,     # Yemen
            "AF": 70      # Afghanistan
        }

    def assess_supplier(self, supplier: Supplier) -> Dict:
        """Return risk assessment for a supplier."""
        risks = []
        risk_score = 0

        # Indicator 1: Excessive hours
        if supplier.avg_hours_per_week > self.MAX_HOURS_WEEK:
            risks.append({
                "flag": "excessive_hours",
                "description": self.red_flags["excessive_hours"],
                "severity": "high",
                "detail": f"{supplier.avg_hours_per_week} hrs/week (threshold: {self.MAX_HOURS_WEEK})"
            })
            risk_score += 3

        # Indicator 2: Low wage
        min_wage = self.country_min_wages.get(supplier.country, 100)
        if supplier.average_wage < min_wage * self.MIN_WAGE_RATIO:
            risks.append({
                "flag": "low_wage",
                "description": "Wage below subsistence level",
                "severity": "high",
                "detail": f"Avg: ${supplier.average_wage:.2f} vs min: ${min_wage:.2f}"
            })
            risk_score += 3

        # Indicator 3: No contracts
        if not supplier.has_contracts:
            risks.append({
                "flag": "no_contracts",
                "description": self.red_flags["no_contracts"],
                "severity": "critical",
                "detail": "No written contracts found"
            })
            risk_score += 5

        # Indicator 4: No unionization (potential suppression)
        if not supplier.unionized:
            risks.append({
                "flag": "no_union",
                "description": self.red_flags["no_union"],
                "severity": "medium",
                "detail": "Workers cannot form union"
            })
            risk_score += 2

        # Overall verdict
        if risk_score >= 10:
            verdict = "CRITICAL — Immediate investigation needed"
        elif risk_score >= 5:
            verdict = "HIGH RISK — Audit within 30 days"
        elif risk_score >= 2:
            verdict = "MEDIUM RISK — Audit within 90 days"
        else:
            verdict = "LOW RISK — Continue monitoring"

        return {
            "supplier": supplier.name,
            "risk_score": risk_score,
            "verdict": verdict,
            "flags": risks,
            "recommendation": self._recommend_action(risk_score)
        }

    def _recommend_action(self, score: int) -> str:
        if score >= 10:
            return "Stop orders immediately. Investigate. Support worker exit."
        elif score >= 5:
            return "要求改善 (corrective action plan). 90-day audit."
        elif score >= 2:
            return "مراقبة (monitor). Annual audit."
        else:
            return "Continue business with regular reviews."

if __name__ == "__main__":
    detector = SlaveryDetector()

    # Demo: Test supplier
    test_supplier = Supplier(
        id="SUP-001",
        name="Textile Factory A",
        country="BD",
        industry="garment",
        workers=500,
        avg_hours_per_week=68,
        average_wage=80,        # Below Bangladesh min (~95) + 50% threshold
        has_contracts=False,
        unionized=False,
        audit_date="2025-06-01"
    )

    result = detector.assess_supplier(test_supplier)
    print(f"Assessment: {result['verdict']}")
    print(f"Score: {result['risk_score']}/20")
    print(f"Recommendation: {result['recommendation']}")
    for flag in result['flags']:
        print(f"  ⚠️  {flag['flag']}: {flag['description']}")
