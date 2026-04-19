#!/usr/bin/env python3
"""Extremism → Moderation: Detector for extremist language
Mission: Prevent radicalization, promote balanced, middle-path thinking.
Focus: Religious, political, ideological extremism indicators.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class TextSample:
    """A piece of text to analyze for extremism."""
    content: str
    source: str = "user"
    context: str = ""

class ExtremismDetector:
    """Detect extremist language patterns in text."""

    def __init__(self):
        self.lexicon = self._load_lexicon()
        self.patterns = self._load_patterns()

    def _load_lexicon(self) -> Dict[str, float]:
        """Extreme words/phrases with severity weights (0-1)."""
        return {
            # Critical (0.8-1.0) — call to violence
            "kill all": 1.0,
            "exterminate": 1.0,
            "annihilate": 0.9,
            "cleansing": 0.9,
            "no mercy": 0.8,
            "death to": 0.9,
            "eliminate them": 0.9,
            "eradicate": 0.9,
            # High (0.5-0.7) — dehumanization, labeling
            "hate": 0.6,
            "enemy of allah": 0.7,
            "apostate": 0.6,
            "infidel": 0.6,
            "kafir": 0.6,
            "extremist": 0.5,
            "radical": 0.5,
            "conspiracy": 0.5,
            "they all lie": 0.5,
            "brainwashed": 0.5,
            "sheeple": 0.5,
            # Sectarian / ideological extremism
            "only our sect": 0.7,
            "everyone else is doomed": 0.6,
            "hellbound": 0.6,
            "doomed to hell": 0.7,
            "saved only": 0.6,
            "all others are": 0.5,
            # Medium (0.2-0.4) — strong bias
            "disgust": 0.3,
            "scum": 0.4,
            "idiots": 0.3,
            "fools": 0.3,
            "blind followers": 0.4
        }

    def _load_patterns(self) -> List[Tuple[str, float]]:
        """Regex patterns for extremist rhetoric."""
        return [
            (r'\b(they|them|those)\s+all\s+(should|must|have to)\s+(die|be killed|perish)\b', 1.0),
            (r'\b(only)\s+we\s+are\s+(right|correct|saved)\b', 0.8),
            (r'\b(everyone)\s+else\s+is\s+(wrong|misguided|evil)\b', 0.8),
            (r'\bno\s+compromise\b', 0.6),
            (r'\bzero\s+sum\b', 0.5),
            (r'\bcomplete\s+destruction\b', 0.9),
            (r'\bno\s+middle\s+ground\b', 0.7),
            (r'\bif\s+you\'re\s+not\s+with\s+us\s+you\'re\s+against\s+us\b', 0.7),
            (r'\b(all|every)\s+(infidel|kafir|disbeliever)\s+must\s+die\b', 1.0)
        ]

    def score_text(self, text: str) -> Dict:
        """Return extremism score (0-100) and breakdown."""
        text_lower = text.lower()
        matched_terms = []
        total_score = 0

        # 1. Lexicon matching
        for term, weight in self.lexicon.items():
            if term in text_lower:
                matched_terms.append({"term": term, "weight": weight, "type": "lexicon"})
                total_score += weight * 35

        # 2. Pattern matching
        for pattern, weight in self.patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matched_terms.append({"term": f"pattern:{pattern[:30]}", "weight": weight, "type": "pattern"})
                total_score += weight * 25

        total_score = min(total_score, 100)

        # Verdict
        if total_score >= 70:
            verdict = "CRITICAL — Immediate review needed"
        elif total_score >= 40:
            verdict = "HIGH — Moderate and re-educate"
        elif total_score >= 20:
            verdict = "MEDIUM — Guide towards balance"
        elif total_score > 0:
            verdict = "LOW — Minor bias, educate"
        else:
            verdict = "BALANCED — No extremism detected"

        return {
            "score": round(total_score, 1),
            "verdict": verdict,
            "matched_terms": matched_terms[:10],
            "term_count": len(matched_terms)
        }

    def suggest_moderation(self, score: float, text: str) -> str:
        """Suggest balanced, moderate response to extremist text."""
        if score >= 70:
            return ("⚠️ هذا المحتوى خطر ويُروّج للعنف. يجب الإبلاغ عنه للسلطات المختصة."
                    " لا تتفاعل معه — safety أولاً."
                    " احفظ الأدلة (سكرينشوت) وأبلغ platform.")
        elif score >= 40:
            return ("شكراً لك على مشاركتك. أودّ تصحيح بعض المفاهيم."
                    "تذكّر: الإسلام دين وسط، لا غلو ولا تساهل."
                    "نحن أمة وسطاً."
                    "لنتحاور باحترام.")
        elif score >= 20:
            return ("شكراً لك. أرى أنك تحمل رأياً قوياً."
                    " أتساءل: هل فكرت في وجهات النظر الأخرى؟"
                    "الإسلام يحث على التعقل والتأنّي قبل الحكم على الآخرين.")
        else:
            return ("نقاش متوازن — شكراً لك."
                    " تذكير: «إِنَّ الدِّينَ يُسْرٌ» — الدين يسر، لا عُسر."
                    " نحن نسعى لوسطية، لا انحياز.")

if __name__ == "__main__":
    detector = ExtremismDetector()
    tests = [
        "All infidels must die — they are enemies of Allah.",
        "I think the other political party is wrong but I'll debate them respectfully.",
        "Only our sect is saved; all others are hellbound.",
        "We need to find common ground and work together.",
        "Kill all infidels! Exterminate them."
    ]
    print("=== Extremism Detection Test ===\n")
    for text in tests:
        result = detector.score_text(text)
        print(f"Text: {text[:60]}...")
        print(f"Score: {result['score']}/100 — {result['verdict']}")
        print(f"Suggest: {detector.suggest_moderation(result['score'], text)}\n")
