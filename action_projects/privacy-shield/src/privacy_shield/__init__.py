"""Privacy Shield — Protect your privacy from surveillance."""

from .crypto import CryptoEngine, encrypt_file, decrypt_file
from .breach import BreachChecker, quick_check
from .browser import FirefoxHardener, ChromeHardener, harden_firefox, harden_chrome
from .vpn import VPNChecker, check_vpn_status

__all__ = [
    "CryptoEngine",
    "encrypt_file",
    "decrypt_file",
    "BreachChecker",
    "quick_check",
    "FirefoxHardener",
    "ChromeHardener",
    "harden_firefox",
    "harden_chrome",
    "VPNChecker",
    "check_vpn_status",
]

__version__ = "0.1.0"
__author__ = "Abdullah Haqq (m7mad ASH)"
