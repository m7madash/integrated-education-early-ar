#!/usr/bin/env python3
"""
Riba Danger — Financial Calculator
Compute APR, detect hidden fees, identify loan type.
"""

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class LoanTerms:
    """Represents a loan offer."""
    principal: float         # Original amount borrowed
    total_repayment: float   # Total to be paid back (principal + all charges)
    term_years: int          # Loan term in years
    payment_type: str        # "amortizing", "bullet", "interest_only"
    fees: List[float]        # Additional fees (origination, processing, etc.)
    interest_rate_stated: Optional[float] = None  # If explicitly stated

    @property
    def total_interest(self) -> float:
        return self.total_repayment - self.principal

    @property
    def total_fees(self) -> float:
        return sum(self.fees)

    @property
    def total_cost(self) -> float:
        return self.total_repayment + self.total_fees

class RibaCalculator:
    """Calculate riba metrics: APR, effective rate, hidden fees."""

    @staticmethod
    def apr(principal: float, total_repayment: float, term_years: int, fees: List[float] = None) -> float:
        """
        Calculate Annual Percentage Rate (APR).
        Simplified formula: (Total Interest + Fees) / Principal / TermYears
        More accurate: solve for r in NPV equation (using Newton-Raphson).
        """
        fees = fees or []
        total_interest = total_repayment - principal
        total_charges = total_interest + sum(fees)
        # Simple APR (approximate):
        simple_apr = (total_charges / principal) / term_years
        # For accurate APR, we solve: principal = sum_{t=1}^{n} (payment_t / (1+r)^t)
        # For now, return simple APR (close enough for comparison)
        return simple_apr * 100  # percentage

    @staticmethod
    def effective_interest_rate(principal: float, total_repayment: float, term_years: int) -> float:
        """Total interest as percentage of principal."""
        total_interest = total_repayment - principal
        return (total_interest / principal) * 100

    @staticmethod
    def classify_loan(principal: float, total_repayment: float, term_years: int, payment_type: str) -> str:
        """Classify loan type based on structure."""
        if payment_type == "bullet":
            return "Bullet loan (interest accrued, principal due at end) — riba if interest charged"
        elif payment_type == "interest_only":
            return "Interest-only loan — riba if interest exceeds actual cost of funds"
        elif payment_type == "amortizing":
            return "Amortizing loan (regular principal+interest payments)"
        else:
            return "Unknown loan type"

    @staticmethod
    def is_riba_detected(apr: float, loan_type: str, hidden_fees_ratio: float) -> tuple:
        """
        Decide if loan is riba based on APR and structure.
        Returns (is_riba: bool, reason: str).
        """
        thresholds = {
            "bullet": 0.0,       # Any interest on bullet is riba
            "interest_only": 0.0,
            "amortizing": 15.0,  # >15% APR might be riba (depending on jurisdiction)
        }
        threshold = thresholds.get(loan_type, 15.0)

        if loan_type in ("bullet", "interest_only"):
            return True, f"{loan_type} loan with any interest is considered riba"
        if apr > threshold:
            return True, f"APR {apr:.1f}% exceeds threshold {threshold}% for {loan_type}"
        if hidden_fees_ratio > 0.10:  # >10% fees on principal
            return True, f"Hidden fees represent {hidden_fees_ratio:.1%} of principal — excessive"
        return False, "Loan appears within acceptable bounds (but verify with scholar)"

# Convenience
def analyze_loan(principal: float, total_repayment: float, term_years: int,
                 payment_type: str = "amortizing", fees: List[float] = None) -> dict:
    calc = RibaCalculator()
    apr_val = calc.apr(principal, total_repayment, term_years, fees or [])
    effective = calc.effective_interest_rate(principal, total_repayment, term_years)
    loan_type = calc.classify_loan(principal, total_repayment, term_years, payment_type)
    fee_ratio = (sum(fees or []) / principal) if principal > 0 else 0
    is_riba, reason = calc.is_riba_detected(apr_val, payment_type, fee_ratio)

    return {
        "principal": principal,
        "total_repayment": total_repayment,
        "term_years": term_years,
        "apr_percent": round(apr_val, 2),
        "effective_interest_percent": round(effective, 2),
        "loan_type": loan_type,
        "total_fees": sum(fees or []),
        "fees_ratio": round(fee_ratio, 4),
        "is_riba": is_riba,
        "reason": reason
    }

if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="Analyze loan for riba")
    parser.add_argument("--principal", type=float, required=True)
    parser.add_argument("--total", type=float, required=True)
    parser.add_argument("--term", type=int, required=True)
    parser.add_argument("--type", choices=["amortizing","bullet","interest_only"], default="amortizing")
    parser.add_argument("--fees", nargs="*", type=float, default=[], help="Additional fees (origination, etc.)")
    args = parser.parse_args()

    result = analyze_loan(args.principal, args.total, args.term, args.type, args.fees)
    print(json.dumps(result, indent=2))
    if result["is_riba"]:
        print(f"\n⚠️ Riba detected: {result['reason']}")
    else:
        print("\n✅ No riba detected (but consult scholar for final ruling)")
