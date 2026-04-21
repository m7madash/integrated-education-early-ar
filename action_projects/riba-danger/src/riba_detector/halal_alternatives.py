#!/usr/bin/env python3
"""
Riba Danger — Halal Alternatives
Islamic financing models: Murabaha, Ijarah, Musharaka.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FinancingOption:
    """Represents a halal financing structure."""
    name: str
    description: str
    total_cost: float
    effective_rate: float  # not riba, but markup/profit share
    monthly_payment: float
    requirements: List[str]  # conditions for validity

class Murabaha:
    """
    Cost-plus financing: Bank buys asset, sells to client at marked-up price.
    Permissible if:
    - Bank owns asset first (takes possession)
    - Markup is agreed upfront (fixed)
    - Installments allowed (but still fixed total)
    """
    def __init__(self, cost: float, markup_percentage: float, term_months: int):
        self.cost = cost
        self.markup_pct = markup_percentage
        self.term = term_months
        self.total_price = cost * (1 + markup_percentage / 100)
        self.monthly = self.total_price / term_months

    def get_option(self) -> FinancingOption:
        return FinancingOption(
            name="Murabaha (Cost-plus)",
            description="Bank purchases item and sells to you at agreed markup. Fixed total.",
            total_cost=self.total_price,
            effective_rate=self.markup_pct,  # profit rate, not interest
            monthly_payment=self.monthly,
            requirements=[
                "Bank must own asset before sale",
                "Markup disclosed upfront (no hidden fees)",
                "Payment schedule fixed (no penalties for early payment)",
                "Asset must be tangible (commodity or property)"
            ]
        )

class Ijarah:
    """
    Leasing: Bank buys asset, leases to client, then transfers ownership at end.
    """
    def __init__(self, cost: float, annual_return_pct: float, term_months: int, residual_value: float = 0):
        self.cost = cost
        self.return_pct = annual_return_pct
        self.term = term_months
        self.residual = residual_value
        # Bank's profit: annual % of cost (diminishing as asset ages?)
        self.total_rent = (cost * (annual_return_pct / 100) * (term_months / 12))
        self.monthly = (cost - residual_value) / term_months + (self.total_rent / term_months)

    def get_option(self) -> FinancingOption:
        return FinancingOption(
            name="Ijarah (Leasing)",
            description="Bank leases asset to you; ownership transfers after final payment.",
            total_cost=self.cost + self.total_rent,
            effective_rate=self.return_pct,
            monthly_payment=self.monthly,
            requirements=[
                "Bank bears major risks (damage, depreciation)",
                "Lease payments fixed; no penalty for early termination",
                "Ownership transferagreed at contract start",
                "Asset must be used by lessee (not just financial)"
            ]
        )

class Musharaka:
    """
    Partnership: Bank and client co-own asset; client gradually buys out bank's share.
    """
    def __init__(self, cost: float, bank_share_pct: float, client_share_pct: float, term_months: int):
        self.cost = cost
        self.bank_share = bank_share_pct / 100
        self.client_share = client_share_pct / 100
        self.term = term_months
        # Bank's profit: agreed-upon rate on its capital portion
        # Simplified: fixed monthly buyout + service fee
        self.bank_capital = cost * self.bank_share
        self.client_capital = cost * self.client_share
        # Monthly buyout: bank capital / term + small service fee (e.g., 5%)
        service_fee_rate = 0.05  # fixed 5% for management
        self.buyout_total = self.bank_capital * (1 + service_fee_rate)
        self.monthly_buyout = self.buyout_total / term_months

    def get_option(self) -> FinancingOption:
        return FinancingOption(
            name="Musharaka (Partnership)",
            description="Joint ownership; you gradually buy out bank's share. Risk-sharing.",
            total_cost=self.cost + (self.buyout_total - self.bank_capital),
            effective_rate=5.0,  # service fee only
            monthly_payment=self.monthly_buyout,
            requirements=[
                "Both parties share in profit/loss according to ratio",
                "Bank's capital at risk (not guaranteed return)",
                "Client responsible for asset management",
                "Buyout schedule fixed; no interest on late payments"
            ]
        )

# Comparison CLI
def compare_loan_vs_halal(principal: float, total_repayment: float, term_years: int,
                          fees: List[float] = None) -> dict:
    """Compare conventional loan (possibly riba) vs halal alternatives."""
    from riba_detector.calculator import analyze_loan
    conventional = analyze_loan(principal, total_repayment, term_years, fees=fees)

    # Murabaha (5% markup)
    m = Murabaha(principal, markup_percentage=5.0, term_months=term_years*12).get_option()
    # Ijarah (8% annual return)
    i = Ijarah(principal, annual_return_pct=8.0, term_months=term_years*12).get_option()
    # Musharaka (5% service fee, bank 70%, client 30%)
    mu = Musharaka(principal, bank_share_pct=70, client_share_pct=30, term_months=term_years*12).get_option()

    alternatives = [
        {"name": m.name, "total_cost": m.total_cost, "monthly": m.monthly_payment, "effective_rate": m.effective_rate},
        {"name": i.name, "total_cost": i.total_cost, "monthly": i.monthly_payment, "effective_rate": i.effective_rate},
        {"name": mu.name, "total_cost": mu.total_cost, "monthly": mu.monthly_payment, "effective_rate": mu.effective_rate},
    ]

    return {
        "conventional": conventional,
        "halal_alternatives": alternatives
    }

if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="Compare loan vs Islamic alternatives")
    parser.add_argument("--principal", type=float, required=True)
    parser.add_argument("--total", type=float, required=True)
    parser.add_argument("--term", type=int, required=True, help="Years")
    parser.add_argument("--fees", nargs="*", type=float, default=[])
    args = parser.parse_args()

    result = compare_loan_vs_halal(args.principal, args.total, args.term, args.fees)
    print(json.dumps(result, indent=2))

    if result["conventional"]["is_riba"]:
        print(f"\n⚠️ Conventional loan is riba: {result['conventional']['reason']}")
        print("✅ Islamic alternatives (lower total cost, risk-sharing):")
        for alt in result["halal_alternatives"]:
            print(f"   • {alt['name']}: total ≈ {alt['total_cost']:,.2f}")
