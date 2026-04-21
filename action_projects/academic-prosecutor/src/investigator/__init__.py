"""Academic Prosecutor — Investigator Subpackage"""

from .detector import Investigator, Paper, Violation
from .sources import fetch_paper, SourceFetcher
from .similarity import SimilarityEngine, quick_similarity

__all__ = ["Investigator", "Paper", "Violation", "fetch_paper", "SourceFetcher", "SimilarityEngine"]
