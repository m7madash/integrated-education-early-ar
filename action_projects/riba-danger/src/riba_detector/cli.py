#!/usr/bin/env python3
"""
Riba Danger — Unified CLI
Uses analyzer for detection + calculator/halal_alternatives for comparison.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .analyze import RibaAnalyzer, LoanTerms
from .halal_alternatives import compare_loan_vs_halal

def print_header():
    print("""
🛡️ ================================
   RIBA DANGER — محارب الربا
   كشف الفائدة المحرمة في القروض
   ================================
""")

def interactive_mode():
    """Interactive CLI — ask user for loan details."""
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

    loan = LoanTerms(principal=principal, term_months=term_months,
                     monthly_payment=monthly_payment, fees=fees)
    analyzer = RibaAnalyzer(loan)
    print("\n" + analyzer.report())

    # Show halal alternatives if riba detected
    if not analyzer.is_halal():
        total_repayment = analyzer.total_paid()
        term_years = term_months / 12
        comparison = compare_loan_vs_halal(principal, total_repayment, term_years, fees=[fees])
        print("\n🔍 مقارنة مع البديل الحلال:")
        conv = comparison["conventional"]
        print(f"   القرض التقليدي: ربا={conv['is_riba']}, APR={conv['apr_percent']}%")
        print("   البدائل الحلال:")
        for alt in comparison["halal_alternatives"]:
            print(f"     • {alt['name']}: التكلفة الإجمالية ≈ {alt['total_cost']:,.2f}, معدل فعلي ≈ {alt['effective_rate']}%")

    # Save?
    save = input("\nهل تريد حفظ النتيجة؟ (y/n): ").lower()
    if save == 'y':
        filename = f"riba_report_{principal}_{term_months}months.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(analyzer.report())
            if not analyzer.is_halal():
                f.write("\n\n=== البديل الحلال ===\n")
                f.write(json.dumps(comparison, indent=2, ensure_ascii=False))
        print(f"✅ تم الحفظ في {filename}")

def single_analysis(args):
    """One-shot analysis from command line."""
    loan = LoanTerms(
        principal=args.principal,
        term_months=args.term,
        monthly_payment=args.payment,
        fees=args.fees or 0.0
    )
    analyzer = RibaAnalyzer(loan)
    print(analyzer.report())

    if not analyzer.is_halal():
        total_repayment = analyzer.total_paid()
        term_years = args.term / 12
        comparison = compare_loan_vs_halal(args.principal, total_repayment, term_years, fees=[args.fees])
        print("\n🔍 مقارنة البديل الحلال:")
        for alt in comparison["halal_alternatives"]:
            print(f"   • {alt['name']}: {alt['total_cost']:,.2f} (معدل {alt['effective_rate']}%)")

def batch_mode(filename: str):
    """Analyze multiple loans from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            loans = json.load(f)
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")
        return

    print(f"تحليل {len(loans)} قرض...\n")
    results = []
    for i, loan_data in enumerate(loans, 1):
        print(f"\n{'='*50}")
        print(f"القرض #{i}:")
        loan = LoanTerms(**loan_data)
        analyzer = RibaAnalyzer(loan)
        print(analyzer.report())
        results.append({
            "principal": loan.principal,
            "halal": analyzer.is_halal(),
            "apr": round(analyzer.apr(), 2)
        })
    print("\n✅ تحليل Batch مكتمل")
    # Summary
    riba_count = sum(1 for r in results if not r['halal'])
    print(f"ملخص: {riba_count}/{len(results)} قروض تحتوي ربا")

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

    if args.interactive:
        interactive_mode()
    elif args.batch:
        batch_mode(args.batch)
    elif args.principal and args.term and args.payment:
        single_analysis(args)
    else:
        print("لا توجد متغيرات كافية — سيبدأ الوضع التفاعلي")
        interactive_mode()

if __name__ == "__main__":
    main()
