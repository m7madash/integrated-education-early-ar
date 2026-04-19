"""Riba Danger — Detect and eliminate riba in financial contracts"""

from .analyze import RibaAnalyzer, LoanTerms
from .halal_alternatives import (
    MurabahaOption, IjarahOption, MusharakaOption,
    generate_alternatives, compare_halal_vs_riba
)
from .cli import main, interactive_mode, single_analysis, batch_mode

__version__ = "0.1.0"
__all__ = [
    'RibaAnalyzer', 'LoanTerms',
    'MurabahaOption', 'IjarahOption', 'MusharakaOption',
    'generate_alternatives', 'compare_halal_vs_riba',
    'main', 'interactive_mode', 'single_analysis', 'batch_mode'
]
