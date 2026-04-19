"""
Illness → Health: Telehealth Bot for Gaza
MVP: Triage bot for common conditions in Gaza strip.
"""

from .triage import TriageBot
from .knowledge import get_advice, CONDITIONS_GAZA
from .privacy import xor_encrypt, xor_decrypt, anonymize_name

__version__ = "0.1.0"
__all__ = ['TriageBot', 'get_advice', 'CONDITIONS_GAZA', 'xor_encrypt', 'xor_decrypt', 'anonymize_name']
