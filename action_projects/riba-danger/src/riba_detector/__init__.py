"""Riba Danger — Detect and eliminate riba in financial contracts"""

from .analyze import RibaAnalyzer, LoanTerms
from .calculator import RibaCalculator, analyze_loan
from .halal_alternatives import (
    Murabaha, Ijarah, Musharaka,
    compare_loan_vs_halal
)
from .cli import main, interactive_mode, single_analysis, batch_mode

__version__ = "0.2.0"
__all__ = [
    'RibaAnalyzer', 'LoanTerms',
    'RibaCalculator', 'analyze_loan',
    'Murabaha', 'Ijarah', 'Musharaka',
    'compare_loan_vs_halal',
    'main', 'interactive_mode', 'single_analysis', 'batch_mode'
]
