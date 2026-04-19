"""Privacy Shield — حماية الخصوصية للجميع

Mission: جعل كل شخص محمي ضد التجسس وانتهاك الخصوصية
Vision: Privacy is a human right, not a luxury

Tools:
- File encryption (AES-256)
- Breach monitoring (HaveIBeenPwned)
- Browser hardening guides
- VPN integration
- RTB/ad-tech blocking (Webloc countermeasure)

"""

__version__ = '0.1.0'
__author__ = 'Abdullah Haqq — KiloClaw'

from .cli import main

__all__ = ['main']
