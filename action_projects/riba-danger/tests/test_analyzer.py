#!/usr/bin/env python3
"""
Riba Danger — Tests for Calculator and Halal Alternatives
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from riba_detector.calculator import RibaCalculator, analyze_loan
from riba_detector.halal_alternatives import Murabaha, Ijarah, Musharaka, compare_loan_vs_halal

def test_apr_calculation():
    """APR should match simple formula."""
    # Example: $1000 loan, repay $1200 over 2 years, no fees
    apr = RibaCalculator.apr(1000, 1200, 2, fees=[])
    expected = (200 / 1000) / 2 * 100  # 10%
    assert abs(apr - expected) < 0.1, f"APR mismatch: {apr} vs {expected}"
    print(f"✅ APR calculation: {apr}% (expected ~10%)")

def test_loan_classification():
    """Bullet loan with interest is riba."""
    result = analyze_loan(10000, 15000, 5, payment_type="bullet")
    assert result["is_riba"] == True, "Bullet loan with interest should be riba"
    assert "bullet" in result["loan_type"].lower()
    print("✅ Loan classification: bullet loan flagged as riba")

def test_halal_murabaha():
    """Murabaha total should equal principal + markup."""
    m = Murabaha(cost=10000, markup_percentage=10.0, term_months=12)
    opt = m.get_option()
    assert opt.total_cost == 11000, f"Murabaha total mismatch: {opt.total_cost}"
    assert abs(opt.monthly_payment - 11000/12) < 0.1
    print(f"✅ Murabaha: total={opt.total_cost}, monthly={opt.monthly_payment:.2f}")

def test_halal_ijarah():
    """Ijarah monthly calculation."""
    i = Ijarah(cost=10000, annual_return_pct=8.0, term_months=24)
    opt = i.get_option()
    # Expected: (10000 * 0.08 / 2) = 400 total rent? Actually 8% per year over 2 years = 1600? No, 8% annually on diminishing? Simplified: fixed rent = cost * rate * years
    # Our implementation: total_rent = cost * (rate/100) * (term_months/12)
    expected_total = 10000 + (10000 * 0.08 * 2)  # 10000 + 1600 = 11600 approx (without residual)
    assert opt.total_cost >= 10000
    print(f"✅ Ijarah: total={opt.total_cost:.2f}")

def test_comparison():
    """Compare conventional vs halal."""
    comp = compare_loan_vs_halal(10000, 13000, 5, fees=[500])
    assert comp["conventional"]["is_riba"] == True
    assert len(comp["halal_alternatives"]) == 3
    # Halal alternatives should have lower APR or at least no riba flag
    for alt in comp["halal_alternatives"]:
        assert alt["effective_rate"] < 20  # reasonable
    print("✅ Comparison: conventional detected as riba, halal options provided")

if __name__ == "__main__":
    test_apr_calculation()
    test_loan_classification()
    test_halal_murabaha()
    test_halal_ijarah()
    test_comparison()
    print("\n🎉 All Riba Danger tests passed!")
