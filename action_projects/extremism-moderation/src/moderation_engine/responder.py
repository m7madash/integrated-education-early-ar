#!/usr/bin/env python3
"""Moderation responder — generate balanced, middle-path responses to extreme text.
Based on Islamic wasatiyyah principles and de-escalation techniques.
"""

from .detector import ExtremismDetector
from .knowledge import EXTREMISM_TYPES, get_extremism_info
from .principles import MIDDLE_PATH_PRINCIPLES, get_principle

class ModerationResponder:
    """Suggest balanced, ethical responses to extremist speech."""

    def __init__(self):
        self.detector = ExtremismDetector()
        self.principles = MIDDLE_PATH_PRINCIPLES

    def craft_response(self, text: str, score: float) -> str:
        """Generate a moderation response suitable for the detected extremism level."""
        if score >= 70:
            return ("⚠️ هذا المحتوى خطر ويُروّج للعنف. يجب الإبلاغ عنه للسلطات المختصة."
                    " لا تتفاعل معه — safety أولاً."
                    " احفظ الأدلة (سكرينشوت) وأبلغ platform.")
        elif score >= 40:
            return ("شكراً لك على مشاركتك. أودّ تصحيح بعض المفاهيم."
                    f"تذكّر: {self.principles['wasatiyyah_balance']['principle']}"
                    "نحن أمة وسطاً — لا غلو في الدين ولا تساهل."
                    "لنتحاور باحترام.")
        elif score >= 20:
            resp = ("شكراً لك. أرى أنك تحمل رأياً قوياً."
                    " أتساءل: هل فكرت في وجهات النظر الأخرى؟"
                    "الإسلام يحث على التعقل والتأنّي قبل الحكم على الآخرين.")
            # Add a principle reference if available
            p = self.principles.get('respectful_dialogue', {})
            if p:
                resp += f" تذكير: {p['principle']}"
            return resp
        else:
            quote = self.get_wasatiyyah_quote()
            return ("نقاش متوازن — شكراً لك."
                    f" تذكير: {quote}"
                    " نحن نسعى لوسطية، لا انحياز.")

    def get_wasatiyyah_quote(self) -> str:
        """Return a short, powerful middle-path quote."""
        quotes = [
            "«إِنَّ الدِّينَ يُسْرٌ» — الدين يسر، لا عُسر.",
            "الوسطية: فَالسَّمْحَةُ بَيْنَ الغُلُوّ وَالتَّراخِي.",
            "«كُلُّ مُبْتَدَعٍ ضَلَّ وَفِي النَّارِ» — Flex matter.",
            "لا إكراه في الدين. {Quran 2:256}"
        ]
        import random
        return random.choice(quotes)

    def suggest_platform_action(self, score: float) -> str:
        """What should the platform do with this content?"""
        if score >= 70:
            return "REMOVE — violates safety policies; report to authorities"
        elif score >= 40:
            return "FLAG — add warning label, require user confirmation to view"
        elif score >= 20:
            return "MONITOR — add to watchlist, no action yet"
        else:
            return "NO ACTION — balanced speech protected"

if __name__ == "__main__":
    responder = ModerationResponder()
    detector = ExtremismDetector()

    test_texts = [
        "All infidels must die — they are enemies of Allah.",
        "I think the other political party is wrong but I'll debate them respectfully.",
        "Only our sect is saved; all others are hellbound.",
        "We need to find common ground and work together."
    ]

    print("=== Moderation Responder Demo ===\n")
    for text in test_texts:
        result = detector.score_text(text)
        response = responder.craft_response(text, result['score'])
        action = responder.suggest_platform_action(result['score'])
        print(f"Text: {text[:60]}...")
        print(f"Score: {result['score']}/100")
        print(f"Suggested response: {response}")
        print(f"Platform action: {action}\n")
