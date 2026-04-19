"""
Extremism → Moderation: Counter-Radicalization Engine
Detect extremist language, suggest balanced responses, teach wasatiyyah.
"""

from .detector import ExtremismDetector, TextSample
from .responder import ModerationResponder
from .knowledge import EXTREMISM_TYPES, get_extremism_info
from .principles import MIDDLE_PATH_PRINCIPLES, get_principle
from .privacy import anonymize_user, anonymize_text, generate_report_id, encrypt_log_entry

__version__ = "0.1.0"
__all__ = ['ExtremismDetector', 'TextSample', 'ModerationResponder',
           'EXTREMISM_TYPES', 'MIDDLE_PATH_PRINCIPLES',
           'anonymize_user', 'anonymize_text', 'generate_report_id']
