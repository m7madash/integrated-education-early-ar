"""
Riba Analyzer — Core detection engine
Calculates APR, detects hidden fees, identifies riba in loan contracts
"""

import argparse
from dataclasses import dataclass
from typing import Optional

@dataclass
class LoanTerms:
    principal: float  # Original amount
    term_months: int  # Loan duration in months
    monthly_payment: float  # Fixed monthly payment
    fees: float = 0.0  # Additional fees (origination, processing, etc.)
    loan_type: str = "amortizing"  # amortizing, bullet, interest-only

class RibaAnalyzer:
    """Detect riba (interest) in loan contracts"""
    
    def __init__(self, loan: LoanTerms):
        self.loan = loan
        
    def total_paid(self) -> float:
        """Total amount paid over loan lifetime"""
        return self.loan.monthly_payment * self.loan.term_months + self.loan.fees
    
    def riba_amount(self) -> float:
        """Total riba (interest + fees) paid"""
        total = self.total_paid()
        return max(0.0, total - self.loan.principal)
    
    def apr(self) -> float:
        """
        Annual Percentage Rate (APR)
        Formula: (Total Interest + Fees) / Principal / Years
        """
        years = self.loan.term_months / 12
        riba = self.riba_amount()
        if years == 0:
            return 0.0
        return (riba / self.loan.principal / years) * 100
    
    def monthly_riba(self) -> float:
        """Average riba per month"""
        total_riba = self.riba_amount()
        if self.loan.term_months == 0:
            return 0.0
        return total_riba / self.loan.term_months
    
    def is_halal(self) -> bool:
        """
        Determine if loan is halal (no riba)
        In Islamic finance, any guaranteed return on principal is riba.
        """
        return self.riba_amount() == 0.0
    
    def report(self) -> str:
        """Generate a human-readable report"""
        loan = self.loan
        total = self.total_paid()
        riba = self.riba_amount()
        apr = self.apr()
        monthly_riba = self.monthly_riba()
        
        lines = []
        lines.append("=" * 50)
        lines.append("🛡️ Riba Danger Analysis")
        lines.append("=" * 50)
        lines.append(f"Principal: {loan.principal:,.2f}")
        lines.append(f"Term: {loan.term_months} months ({loan.term_months/12:.1f} years)")
        lines.append(f"Monthly Payment: {loan.monthly_payment:,.2f}")
        if loan.fees > 0:
            lines.append(f"Additional Fees: {loan.fees:,.2f}")
        lines.append("")
        lines.append("📊 Results:")
        lines.append(f"Total Paid: {total:,.2f}")
        lines.append(f"Riba Amount: {riba:,.2f} ({riba/loan.principal*100:.1f}% of principal)")
        lines.append(f"APR: {apr:.2f}%")
        lines.append(f"Average Monthly Riba: {monthly_riba:,.2f}")
        lines.append("")
        
        if self.is_halal():
            lines.append("✅ This contract appears to be Riba-FREE (halal)")
        else:
            lines.append("🚨 RIBAB DETECTED!")
            lines.append("")
            lines.append("📖 Quranic Warning:")
            lines.append("   ﴿الَّذِينَ يَأْكُلُونَ الرِّبَا لَا يَقُومُونَ إِلَّا كَمَا يَقُومُ الَّذِي يَتَخَبَّطُهُ الشَّيْطَانُ مِنَ الْمَسِّ﴾ (البقرة: 275)")
            lines.append("")
            lines.append("🔄 Halal Alternatives:")
            lines.append("   • Murabaha: Cost + fixed markup, no interest")
            lines.append("   • Ijarah: Leasing with purchase option")
            lines.append("   • Musharaka: Partnership (profit-sharing, loss-sharing)")
            lines.append("")
            lines.append("💡 Action: Convert this loan to a Sharia-compliant structure.")
        
        lines.append("=" * 50)
        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Detect riba in loan contracts")
    parser.add_argument("--principal", type=float, required=True, help="Loan amount")
    parser.add_argument("--term", type=int, required=True, help="Term in months")
    parser.add_argument("--payment", type=float, required=True, help="Monthly payment")
    parser.add_argument("--fees", type=float, default=0.0, help="Additional fees")
    
    args = parser.parse_args()
    
    loan = LoanTerms(
        principal=args.principal,
        term_months=args.term,
        monthly_payment=args.payment,
        fees=args.fees
    )
    
    analyzer = RibaAnalyzer(loan)
    print(analyzer.report())

if __name__ == "__main__":
    main()
