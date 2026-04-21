#!/usr/bin/env python3
"""
Media Integrity — Source Reputation Scoring
Evaluate credibility of news sources, authors, and domains.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from urllib.parse import urlparse
import json

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

@dataclass
class SourceReputationResult:
    """Results from source reputation analysis."""
    url: str
    domain: str
    reputation_score: float  # 0-1 (higher = more credible)
    domain_age_days: Optional[int]
    has_ssl: bool
    has_contact_info: bool
    has_corrections_policy: bool
    author_credentials: float  # 0-1
    citation_rate: float  # 0-1 (does it cite sources?)
    fact_check_partners: List[str]
    red_flags: List[str]
    green_signals: List[str]
    overall_assessment: str

class SourceReputation:
    """Assess source credibility via multiple signals."""

    def __init__(self, reliable_domains_path: Optional[Path] = None):
        self.reliable_domains = self._load_reliable_domains(reliable_domains_path)
        # Known unreliable domains (can be expanded)
        self.unreliable_patterns = [
            'wordpress.com', 'blogspot.com', 'wixsite.com', 'weebly.com',
            'infowars.com', 'naturalnews.com', 'dailymail.co.uk', 'tmz.com',
            'rumormillnews.com', 'globaleconomicanalysis.com'
        ]
        # Domains with known fact-check partnerships
        self.fact_check_partners = {
            'reuters.com': ['IFCN', 'PolitiFact'],
            'apnews.com': ['AP Fact Check'],
            'bbc.com': ['BBC Reality Check'],
            'bbc.co.uk': ['BBC Reality Check'],
            'nytimes.com': ['NYT Fact Check'],
            'washingtonpost.com': ['WaPo Fact Checker']
        }

    def _load_reliable_domains(self, path: Optional[Path]) -> List[str]:
        defaults = [
            'reuters.com', 'apnews.com', 'bbc.com', 'bbc.co.uk',
            'who.int', 'un.org', 'worldbank.org', 'imf.org',
            'nejm.org', 'thelancet.com', 'nature.com', 'sciencemag.org',
            'pnas.org', 'science.org', 'ieee.org', 'acm.org',
            'bloomberg.com', 'wsj.com', 'economist.com', 'ft.com',
            'npr.org', 'pbs.org', 'aljazeera.com', 'dw.com'
        ]
        if path and path.exists():
            with open(path) as f:
                return [line.strip().lower() for line in f if line.strip()]
        return defaults

    def analyze(self, url: str, author: Optional[str] = None, content: Optional[str] = None) -> SourceReputationResult:
        """
        Analyze a news source URL and optional content.
        Args:
            url: Article URL
            author: Author name (optional)
            content: Article text (optional, for citation analysis)
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]

        # 1. SSL check
        has_ssl = parsed.scheme == 'https'

        # 2. Domain age (whois) — skip for now (requires external service)
        # We'll approximate via known list or just mark unknown
        domain_age_days = None  # placeholder

        # 3. Check if reliable domain
        is_reliable = any(domain == d or domain.endswith('.' + d) for d in self.reliable_domains)
        is_unreliable = any(pat in domain for pat in self.unreliable_patterns)

        # 4. Contact info (heuristic: look for 'contact', 'about', 'editor' in URL or content)
        has_contact = self._check_contact_info(url, content)

        # 5. Corrections policy (look for 'corrections' in page)
        has_corrections = False  # would need to fetch page; placeholder heuristics
        # We can infer: if domain is known reliable, assume corrections policy exists
        if is_reliable:
            has_corrections = True

        # 6. Author credentials (simple: is author listed in known journalists? placeholder)
        author_score = 0.5
        if author:
            # If domain is reliable, assume author is credentialed
            if is_reliable:
                author_score = 0.9
            else:
                author_score = 0.3

        # 7. Citations (count external links if content available)
        citation_score = 0.5
        if content:
            # Count HTTP links in content that go to other domains
            external_links = len(re.findall(r'https?://(?!' + re.escape(domain) + ')', content))
            total_links = len(re.findall(r'https?://', content))
            if total_links > 0:
                citation_score = min(external_links / max(total_links, 1), 1.0)

        # 8. Fact-check partners
        partners = self.fact_check_partners.get(domain, [])

        # 9. Red flags & green signals
        red_flags = []
        green_signals = []

        if not has_ssl:
            red_flags.append("No HTTPS (insecure connection)")
        if is_unreliable:
            red_flags.append("Domain known for unreliable content")
        if domain in self.unreliable_patterns:
            red_flags.append("Domain is user-generated platform (blog/opinion)")
        if not has_contact:
            red_flags.append("No visible contact information")
        if author_score < 0.4:
            red_flags.append("Author credentials unclear")

        if is_reliable:
            green_signals.append("Domain is established reliable source")
        if partners:
            green_signals.append(f"Has fact-check partnership: {', '.join(partners)}")
        if has_corrections:
            green_signals.append("Corrections policy visible")
        if citation_score > 0.3:
            green_signals.append("Content cites external sources")
        if has_contact:
            green_signals.append("Contact information available")

        # Compute final reputation score (0-1)
        score = 0.5  # base
        adjustments = 0.0
        adjustments += 0.3 if is_reliable else -0.3 if is_unreliable else 0
        adjustments += 0.1 if has_ssl else -0.2
        adjustments += 0.1 if has_contact else -0.1
        adjustments += 0.1 if has_corrections else 0
        adjustments += (author_score - 0.5) * 0.2
        adjustments += (citation_score - 0.5) * 0.2
        # domain age: unknown, skip

        reputation_score = max(0.0, min(1.0, score + adjustments))

        # Assessment
        if reputation_score >= 0.8:
            assessment = "HIGH CREDIBILITY — Trusted source"
        elif reputation_score >= 0.6:
            assessment = "MODERATE CREDIBILITY — Generally reliable, verify claims"
        elif reputation_score >= 0.4:
            assessment = "LOW CREDIBILITY — Use caution; corroborate with other sources"
        else:
            assessment = "VERY LOW CREDIBILITY — Unreliable; avoid citing"

        return SourceReputationResult(
            url=url,
            domain=domain,
            reputation_score=round(reputation_score, 2),
            domain_age_days=domain_age_days,
            has_ssl=has_ssl,
            has_contact_info=has_contact,
            has_corrections_policy=has_corrections,
            author_credentials=round(author_score, 2),
            citation_rate=round(citation_score, 2),
            fact_check_partners=partners,
            red_flags=red_flags,
            green_signals=green_signals,
            overall_assessment=assessment
        )

    def _check_contact_info(self, url: str, content: Optional[str]) -> bool:
        """Heuristic: look for contact/about/editor pages."""
        contact_keywords = ['contact', 'about', 'editor', 'staff', 'about-us', 'contact-us']
        if content:
            content_lower = content.lower()
            if any(kw in content_lower for kw in contact_keywords):
                return True
        # Also check URL path
        path = urlparse(url).path.lower()
        if any(kw in path for kw in contact_keywords):
            return True
        return False

# Convenience
def analyze_source(url: str, author: Optional[str] = None, content: Optional[str] = None) -> Dict:
    evaluator = SourceReputation()
    result = evaluator.analyze(url, author, content)
    return asdict(result)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Source Reputation Analyzer")
    parser.add_argument("url", help="URL to evaluate")
    parser.add_argument("--author", help="Author name (optional)")
    parser.add_argument("--content", help="Article content file (optional)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    content_text = None
    if args.content:
        try:
            with open(args.content) as f:
                content_text = f.read()
        except:
            pass

    result = analyze_source(args.url, args.author, content_text)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"🏛️ Source Reputation Analysis: {args.url}")
        print(f"Domain: {result['domain']}")
        print(f"Score: {result['reputation_score']}/1.0 — {result['overall_assessment']}")
        print(f"SSL: {'✅' if result['has_ssl'] else '❌'}")
        print(f"Contact info: {'✅' if result['has_contact_info'] else '❌'}")
        print(f"Corrections policy: {'✅' if result['has_corrections_policy'] else '❌'}")
        print(f"Author credentials: {result['author_credentials']}")
        print(f"Citation rate: {result['citation_rate']}")
        if result['fact_check_partners']:
            print(f"Fact-check partners: {', '.join(result['fact_check_partners'])}")
        if result['red_flags']:
            print("\n🚩 Red flags:")
            for flag in result['red_flags']:
                print(f" • {flag}")
        if result['green_signals']:
            print("\n✅ Green signals:")
            for sig in result['green_signals']:
                print(f" • {sig}")
