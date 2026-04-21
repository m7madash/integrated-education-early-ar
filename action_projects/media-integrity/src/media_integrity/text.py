#!/usr/bin/env python3
"""
Media Integrity — Fake News Detection
Detect fake news, misinformation, and disinformation in text.
"""

import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

@dataclass
class TextAnalysisResult:
    """Result of fake news analysis."""
    text: str
    is_likely_fake: bool
    manipulation_score: float  # 0-1
    matched_patterns: List[str]
    source_credibility: float  # 0-1 (higher = more credible)
    emotional_language: float  # 0-1
    factual_claims: int  # number of verifiable claims (if any)
    recommendations: List[str]
    matched_known_fakes: List[str] = None  # titles/IDs of known fakes

class FakeNewsDetector:
    """Detect fake news using multiple signals."""

    def __init__(self, known_fakes_path: Optional[Path] = None, reliable_domains_path: Optional[Path] = None):
        self.known_fakes = self._load_known_fakes(known_fakes_path)
        self.reliable_domains = self._load_reliable_domains(reliable_domains_path)
        self.vectorizer = None
        if HAS_SKLEARN:
            self._build_index()

    def _load_known_fakes(self, path: Optional[Path]) -> List[Dict]:
        """Load known fake news items (title, content, source, date)."""
        defaults = [
            {"title": "Pilots Refuse to Fly Vaccine Shipments — Hoax", "pattern": "pilots refuse vaccine", "source": "various", "date": "2021-07-15"},
            {"title": "5G Causes Coronavirus — Debunked", "pattern": "5g causes corona", "source": "various", "date": "2020-03-24"},
            {"title": "Bill Gates Microchip Vaccine — Conspiracy", "pattern": "gates microchip", "source": "various", "date": "2020-05-10"},
            {"title": "COVID-19 is a Bioweapon — Unproven", "pattern": "bioweapon", "source": "various", "date": "2020-02-05"},
        ]
        if path and path.exists():
            with open(path) as f:
                return json.load(f)
        return defaults

    def _load_reliable_domains(self, path: Optional[Path]) -> List[str]:
        """List of domains considered reliable."""
        defaults = [
            "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
            "who.int", "un.org", "worldbank.org", "imf.org",
            "nejm.org", "thelancet.com", "nature.com", "sciencemag.org"
        ]
        if path and path.exists():
            with open(path) as f:
                return [line.strip() for line in f if line.strip()]
        return defaults

    def _build_index(self):
        """Build TF-IDF index of known fake titles/content."""
        if not HAS_SKLEARN:
            return
        corpus = [item.get("title", "") + " " + item.get("pattern", "") for item in self.known_fakes]
        if corpus:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.vectorizer.fit(corpus)

    def analyze(self, text: str, source_url: Optional[str] = None) -> TextAnalysisResult:
        """
        Analyze text for fake news signals.
        Args:
            text: Article text or claim
            source_url: Optional URL to assess domain credibility
        """
        text_lower = text.lower()

        # 1. Pattern matching (simple substring)
        matched_patterns = []
        for fake in self.known_fakes:
            pattern = fake.get("pattern", "").lower()
            if pattern and pattern in text_lower:
                matched_patterns.append(fake["title"])

        # 2. Source credibility
        source_score = self._assess_source(source_url) if source_url else 0.5  # unknown

        # 3. Emotional language detection (simple heuristics)
        emotional_words = ['shocking', 'outrage', 'terrible', 'amazing', 'unbelievable', 'secret', 'hidden', 'exposed', 'urgent', 'must-read']
        emotional_count = sum(1 for w in emotional_words if w in text_lower)
        emotional_ratio = emotional_count / max(len(text.split()), 1)

        # 4. Factual claims: count numbers, dates, proper nouns (rough)
        factual_count = len(re.findall(r'\b\d{4}\b', text)) + len(re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text))

        # 5. Similarity to known fakes (TF-IDF)
        similarity_score = 0.0
        if HAS_SKLEARN and self.vectorizer and matched_patterns:
            try:
                vec = self.vectorizer.transform([text])
                # Compare to each known fake? We can just use max similarity if we kept individual vectors.
                # For simplicity, if matched_patterns exist, treat as high suspicion.
                similarity_score = 0.8
            except:
                pass

        # Combine signals
        manipulation = 0.0
        if matched_patterns:
            manipulation += 0.5
        manipulation += emotional_ratio * 0.3
        if source_score < 0.4 and source_url:
            manipulation += 0.2
        if factual_count < 2:  # too few factual anchors
            manipulation += 0.1
        if similarity_score > 0.5:
            manipulation += 0.3

        manipulation = min(manipulation, 1.0)
        likely_fake = manipulation > 0.5

        recommendations = self._generate_recommendations(likely_fake, matched_patterns, source_score, emotional_ratio)

        return TextAnalysisResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            is_likely_fake=likely_fake,
            manipulation_score=round(manipulation, 3),
            matched_patterns=matched_patterns,
            source_credibility=round(source_score, 2),
            emotional_language=round(emotional_ratio, 3),
            factual_claims=factual_count,
            recommendations=recommendations,
            matched_known_fakes=matched_patterns
        )

    def _assess_source(self, url: str) -> float:
        """Rate source credibility 0-1 based on domain."""
        if not url:
            return 0.5
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if not domain_match:
            return 0.5
        domain = domain_match.group(1).lower()
        # Exact match or suffix match
        for reliable in self.reliable_domains:
            if domain == reliable or domain.endswith('.' + reliable):
                return 0.9
        # Known unreliable patterns (can expand)
        unreliable_patterns = ['wordpress.com', 'blogspot.com', 'tripod.com', 'infowars.com']
        if any(pat in domain for pat in unreliable_patterns):
            return 0.2
        return 0.5  # neutral

    @staticmethod
    def _generate_recommendations(is_fake: bool, patterns: List[str], source_score: float, emotional_ratio: float) -> List[str]:
        recs = []
        if is_fake:
            recs.append("High likelihood of misinformation — do not share")
            if patterns:
                recs.append(f"Matches known fake patterns: {', '.join(patterns)[:100]}")
            if source_score < 0.4:
                recs.append("Source domain is not reputable — verify with established news outlets")
            if emotional_ratio > 0.05:
                recs.append("Excessive emotional language detected — seek factual, neutral reporting")
            recs.append("Cross-check with fact-checking services (Snopes, AFP Fact Check, etc.)")
        else:
            recs.append("Content appears credible — but always verify with multiple sources")
        return recs

# Convenience
def analyze_text(text: str, source_url: Optional[str] = None) -> Dict:
    detector = FakeNewsDetector()
    result = detector.analyze(text, source_url)
    return asdict(result)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fake News Detector")
    parser.add_argument("text", help="Text to analyze (quote with quotes)")
    parser.add_argument("--url", help="Source URL (optional)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = analyze_text(args.text, args.url)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"🔍 Fake News Analysis")
        print(f"Likely fake? {result['is_likely_fake']}")
        print(f"Manipulation score: {result['manipulation_score']}")
        print(f"Source credibility: {result['source_credibility']}")
        print(f"Emotional language: {result['emotional_language']}")
        print(f"Matched patterns: {', '.join(result['matched_patterns'])}")
        print("\nRecommendations:")
        for r in result['recommendations']:
            print(f" • {r}")
