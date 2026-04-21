# Package marker
from .detector import SlaveryDetector
from .indicators import INDICATORS, get_indicator_category, assess_risk
from .knowledge import get_local_resources, format_emergency_contacts
from .privacy import PrivacyShield, generate_report_html

__all__ = [
    "SlaveryDetector",
    "INDICATORS",
    "get_indicator_category",
    "assess_risk",
    "get_local_resources",
    "format_emergency_contacts",
    "PrivacyShield",
    "generate_report_html"
]
