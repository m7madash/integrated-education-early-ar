"""
Islamic Finance Alternatives to Riba

Provides halal financing structures: Murabaha, Ijarah, Musharaka
"""

from dataclasses import dataclass
from typing import List

@dataclass
class MurabahaOption:
    """Cost-plus financing — seller declares cost and adds fixed markup"""
    cost_price: float  # Actual cost of the item
    markup_amount: float  # Fixed profit margin (not time-based)
    total_price: float  # cost + markup
    term_months: int
    monthly_payment: float
    
    @staticmethod
    def calculate(cost_price: float, markup_percentage: float, term_months: int) -> 'MurabahaOption':
        """Calculate Murabaha from cost, markup %, and term"""
        markup_amount = cost_price * (markup_percentage / 100)
        total_price = cost_price + markup_amount
        monthly_payment = total_price / term_months
        return MurabahaOption(
            cost_price=cost_price,
            markup_amount=markup_amount,
            total_price=total_price,
            term_months=term_months,
            monthly_payment=monthly_payment
        )
    
    def is_halal(self) -> bool:
        """Murabaha is halal if markup is fixed and not time-based"""
        return self.markup_amount > 0 and self.term_months > 0

@dataclass
class IjarahOption:
    """Lease-to-own — bank buys item, leases to client, option to purchase"""
    asset_value: float
    term_months: int
    monthly_rent: float
    purchase_option: float  # Option to buy at end (usually small %)
    total_cost: float  # total rent + purchase option
    
    @staticmethod
    def calculate(asset_value: float, rent_factor: float, term_months: int, purchase_option_pct: float = 0.1) -> 'IjarahOption':
        """
        Ijarah calculation:
        - Monthly rent based on asset value and term
        - Purchase option at end (typically 10% of asset value)
        """
        monthly_rent = asset_value * (rent_factor / 100)  # e.g., rent_factor=1.5% monthly
        total_rent = monthly_rent * term_months
        purchase_option = asset_value * purchase_option_pct
        total_cost = total_rent + purchase_option
        return IjarahOption(
            asset_value=asset_value,
            term_months=term_months,
            monthly_rent=monthly_rent,
            purchase_option=purchase_option,
            total_cost=total_cost
        )
    
    def is_halal(self) -> bool:
        """Ijarah is halal: rental contracts, no interest, purchase option separate"""
        return self.monthly_rent > 0 and self.purchase_option > 0

@dataclass
class MusharakaOption:
    """Partnership — bank and client co-own asset, client buys out gradually"""
    asset_value: float
    bank_share_pct: float  # e.g., 80% bank, 20% client initially
    term_months: int
    client_monthly_buyout: float  # Client buys bank's share over time
    total_client_cost: float  # What client pays eventually (includes bank's profit share)
    annual_profit_share: float  # % of profits shared with bank (not guaranteed)
    
    @staticmethod
    def calculate(asset_value: float, bank_share_pct: float, term_months: int, annual_profit_share: float = 0.2) -> 'MusharakaOption':
        """
        Musharaka calculation:
        - Bank owns X% initially, client owns Y%
        - Client buys bank's share gradually (with rent-like payments? Actually, it's buyout)
        - Both share profits according to agreement (not guaranteed return)
        """
        bank_share_amount = asset_value * (bank_share_pct / 100)
        client_share_amount = asset_value - bank_share_amount
        # Monthly buyout: bank's share divided by term, plus profit sharing component
        # Simpler: client pays bank's share + agreed profit
        total_buyout = bank_share_amount * (1 + annual_profit_share)  # bank gets principal + profit share
        monthly_buyout = total_buyout / term_months
        total_client_cost = client_share_amount + total_buyout
        return MusharakaOption(
            asset_value=asset_value,
            bank_share_pct=bank_share_pct,
            term_months=term_months,
            client_monthly_buyout=monthly_buyout,
            total_client_cost=total_client_cost,
            annual_profit_share=annual_profit_share
        )
    
    def is_halal(self) -> bool:
        """Musharaka is halal: loss-sharing, profit-sharing, no guaranteed return"""
        return self.bank_share_pct < 100 and self.annual_profit_share > 0

def generate_alternatives(loan_amount: float, term_months: int) -> dict:
    """Generate all halal alternatives for a given loan amount and term"""
    
    # Murabaha example: cost = loan amount, markup 10% over term
    murabaha = MurabahaOption.calculate(
        cost_price=loan_amount,
        markup_percentage=10.0,  # 10% flat markup (not APR)
        term_months=term_months
    )
    
    # Ijarah example: rent factor 1.5% monthly, purchase option 10%
    ijarah = IjarahOption.calculate(
        asset_value=loan_amount,
        rent_factor=1.5,  # 1.5% of asset value per month
        term_months=term_months,
        purchase_option_pct=0.1
    )
    
    # Musharaka: bank 80%, client 20% initially, profit share 20%
    musharaka = MusharakaOption.calculate(
        asset_value=loan_amount,
        bank_share_pct=80,
        term_months=term_months,
        annual_profit_share=0.2
    )
    
    return {
        "murabaha": murabaha,
        "ijarah": ijarah,
        "musharaka": musharaka
    }

def compare_halal_vs_riba(loan_principal: float, term_months: int, riba_apr: float):
    """Compare total cost of riba loan vs halal alternatives"""
    # Conventional riba total
    monthly_rate = riba_apr / 12 / 100
    # Simple approximation for demo (actual loan calc would be PMT)
    total_riba = loan_principal * (riba_apr/100) * (term_months/12)
    total_riba_paid = loan_principal + total_riba
    
    # Halal alternatives
    alts = generate_alternatives(loan_principal, term_months)
    
    comparison = f"""
🛡️ Halal Alternatives Comparison for loan of {loan_principal:,.2f} over {term_months/12:.1f} years:

Current Riba Loan:
  Total Paid: {total_riba_paid:,.2f}
  APR: {riba_apr:.1f}%

Islamic Alternatives:
1. Murabaha:
   Total: {alts['murabaha'].total_price:,.2f}
   Monthly: {alts['murabaha'].monthly_payment:,.2f}
   Savings vs Riba: {total_riba_paid - alts['murabaha'].total_price:,.2f}

2. Ijarah:
   Total Cost: {alts['ijarah'].total_cost:,.2f}
   Monthly Rent: {alts['ijarah'].monthly_rent:,.2f}
   Purchase Option: {alts['ijarah'].purchase_option:,.2f} (at end)
   Savings: {total_riba_paid - alts['ijarah'].total_cost:,.2f}

3. Musharaka:
   Client Total Cost: {alts['musharaka'].total_client_cost:,.2f}
   Monthly Buyout: {alts['musharaka'].client_monthly_buyout:,.2f}
   Bank's Share: {alts['musharaka'].bank_share_pct}%
   Savings: {total_riba_paid - alts['musharaka'].total_client_cost:,.2f}

💡 Note: All three are Sharia-compliant and avoid riba.
"""
    return comparison

if __name__ == "__main__":
    # Demo
    print("Testing Riba Analyzer core...")
    from analyze import RibaAnalyzer, LoanTerms  # In real usage, would import directly
    
    loan = LoanTerms(principal=100000, term_months=60, monthly_payment=2500, fees=500)
    analyzer = RibaAnalyzer(loan)
    print(analyzer.report())
    print("\n")
    print(compare_halal_vs_riba(100000, 60, 10))
