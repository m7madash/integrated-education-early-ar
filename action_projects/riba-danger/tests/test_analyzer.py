#!/usr/bin/env python3
"""Test Riba Analyzer core functions"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/action_projects/riba-danger/src')

from riba_detector.analyze import RibaAnalyzer, LoanTerms

def test_loan_detection():
    # Loan with riba
    loan = LoanTerms(principal=100000, term_months=60, monthly_payment=2500, fees=500)
    analyzer = RibaAnalyzer(loan)
    
    assert not analyzer.is_halal(), "Should detect riba"
    assert analyzer.riba_amount() > 0, "Riba amount should be positive"
    assert analyzer.apr() > 0, "APR should be positive"
    
    print("✅ Riba detection works")
    
def test_halal_loan():
    # Loan with no fees, payment equals principal/term (no interest)
    principal = 120000
    term = 60
    payment = principal / term  # exactly principal/term -> no interest
    loan = LoanTerms(principal=principal, term_months=term, monthly_payment=payment, fees=0)
    analyzer = RibaAnalyzer(loan)
    
    assert analyzer.is_halal(), "Should be halal when no interest/fees"
    assert analyzer.riba_amount() == 0, "Riba should be zero"
    assert analyzer.apr() == 0, "APR should be zero"
    
    print("✅ Halal loan recognized")

def test_halal_alternatives():
    from riba_detector.halal_alternatives import generate_alternatives
    alts = generate_alternatives(100000, 60)
    
    assert alts['murabaha'].is_halal()
    assert alts['ijarah'].is_halal()
    assert alts['musharaka'].is_halal()
    
    print("✅ Halal alternatives generated")
    print(f"Murabaha total: {alts['murabaha'].total_price:,.2f}")
    print(f"Ijarah total: {alts['ijarah'].total_cost:,.2f}")
    print(f"Musharaka total: {alts['musharaka'].total_client_cost:,.2f}")

if __name__ == "__main__":
    test_loan_detection()
    test_halal_loan()
    test_halal_alternatives()
    print("\n✅ All tests passed!")
