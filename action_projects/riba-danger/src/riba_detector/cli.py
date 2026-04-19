#!/usr/bin/env python3
"""
Riba Danger — Command Line Interface
Entry point for analyzing loans and detecting riba
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .analyze import RibaAnalyzer, LoanTerms
from .halal_alternatives import generate_alternatives, compare_halal_vs_riba

def print_header():
    print("""
🛡️ ================================
   RIBA DANGER — محارب الربا
   كشف الفائدة المحرمة في القروض
   ================================
""")

def interactive_mode():
    """Interactive CLI — ask user for loan details"""
    print_header()
    print("💼 إدخال بيانات القرض:")
    
    try:
        principal = float(input("المبلغ الأصلي: "))
        term_months = int(input("المدة (بالأشهر): "))
        monthly_payment = float(input("الدفعة الشهرية: "))
        fees_input = input("الرسوم الإضافية (افتراضي 0): ")
        fees = float(fees_input) if fees_input.strip() else 0.0
    except ValueError as e:
        print(f"❌ خطأ في الإدخال: {e}")
        return
    
    loan = LoanTerms(
        principal=principal,
        term_months=term_months,
        monthly_payment=monthly_payment,
        fees=fees
    )
    
    analyzer = RibaAnalyzer(loan)
    print("\n" + analyzer.report())
    
    # Show halal alternatives
    if not analyzer.is_halal():
        print("\n" + compare_halal_vs_riba(principal, term_months, analyzer.apr()))
    
    # Optionally save result
    save = input("\nهل تريد حفظ النتيجة؟ (y/n): ").lower()
    if save == 'y':
        filename = f"riba_report_{principal}_{term_months}months.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(analyzer.report())
            if not analyzer.is_halal():
                f.write("\n" + compare_halal_vs_riba(principal, term_months, analyzer.apr()))
        print(f"✅ تم الحفظ في {filename}")

def single_analysis(args):
    """One-shot analysis from command line arguments"""
    loan = LoanTerms(
        principal=args.principal,
        term_months=args.term,
        monthly_payment=args.payment,
        fees=args.fees
    )
    
    analyzer = RibaAnalyzer(loan)
    print(analyzer.report())
    
    # Always show alternatives if riba detected
    if not analyzer.is_halal():
        print("\n" + compare_halal_vs_riba(args.principal, args.term, analyzer.apr()))

def batch_mode(filename: str):
    """Analyze multiple loans from a JSON file"""
    import json
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            loans = json.load(f)
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")
        return
    
    print(f"تحليل {len(loans)} قرض...\n")
    
    for i, loan_data in enumerate(loans, 1):
        print(f"\n{'='*50}")
        print(f"القرض #{i}:")
        loan = LoanTerms(**loan_data)
        analyzer = RibaAnalyzer(loan)
        print(analyzer.report())
    
    print("\n✅ تحليل Batch مكتمل")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Detect riba (interest) in loan contracts and provide halal alternatives",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('--principal', type=float, help='Loan amount')
    parser.add_argument('--term', type=int, help='Term in months')
    parser.add_argument('--payment', type=float, help='Monthly payment')
    parser.add_argument('--fees', type=float, default=0.0, help='Additional fees (origination, etc.)')
    parser.add_argument('--batch', type=str, help='JSON file with multiple loans to analyze')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode (prompt for input)')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.interactive:
        interactive_mode()
    elif args.batch:
        batch_mode(args.batch)
    elif args.principal and args.term and args.payment:
        single_analysis(args)
    else:
        # Default: interactive if no args
        print("لا توجد متغيرات كافية — سيبدأ الوضع التفاعلي")
        interactive_mode()

if __name__ == "__main__":
    main()
