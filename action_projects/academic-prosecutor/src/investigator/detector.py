#!/usr/bin/env python3
"""
Academic Prosecutor — Investigator Module
Detects plagiarism, data fabrication, and unethical research practices.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple
import hashlib

from .similarity import SimilarityEngine

@dataclass
class Paper:
    """Represents a paper to investigate."""
    id: str  # DOI or identifier
    title: str
    authors: List[str]
    abstract: str
    text: str  # full text (if available)
    source: str  # Crossref, PubMed, arXiv, local PDF

@dataclass
class Violation:
    """Detected violation."""
    type: str  # plagiarism, data_fabrication, duplicate_submission, authorship_fraud
    severity: int  # 1-5
    evidence: str
    source_paper: Paper
    source_corpus: List[str]  # matching sources

class Investigator:
    """Main investigation engine."""

    def __init__(self, corpus_dir: Path = Path("data/corpus")):
        self.corpus_dir = corpus_dir
        self.known_papers = self._load_corpus()
        self.lexicon = self._load_lexicon()
        self.sim_engine = SimilarityEngine(corpus_dir)

    def _load_corpus(self) -> Dict[str, str]:
        """Load known papers (titles + abstracts) for matching."""
        corpus = {}
        if self.corpus_dir.exists():
            for f in self.corpus_dir.glob("*.json"):
                with open(f) as fp:
                    data = json.load(fp)
                    corpus[data["title"].lower()] = data
        return corpus

    def _load_lexicon(self) -> Dict[str, List[str]]:
        """Load known plagiarized phrases, patterns."""
        lex_path = Path("data/lexicon.json")
        if lex_path.exists():
            with open(lex_path) as fp:
                return json.load(fp)
        return {"plagiarism_phrases": [], "suspicious_patterns": []}

    def analyze(self, paper: Paper) -> List[Violation]:
        """Run full analysis on a paper."""
        violations = []
        violations.extend(self._check_plagiarism(paper))
        violations.extend(self._check_duplicate_submission(paper))
        violations.extend(self._check_authorship_fraud(paper))
        violations.extend(self._check_data_fabrication(paper))
        return violations

    def _check_plagiarism(self, paper: Paper) -> List[Violation]:
        """Check for text similarity against known corpus."""
        violations = []
        paper_text = paper.text if paper.text else paper.abstract
        if not paper_text.strip():
            paper_text = paper.title

        # Convert known_papers dict to list if needed
        if isinstance(self.known_papers, dict):
            corpus_list = list(self.known_papers.values())
        else:
            corpus_list = self.known_papers

        # FIRST: Exact title match (strongest signal)
        paper_title_lower = paper.title.lower()
        for entry in corpus_list:
            known_title = entry.get("title", "").lower()
            if paper_title_lower == known_title:
                source_authors = entry.get("authors", [])
                if not source_authors or source_authors != paper.authors:
                    violations.append(Violation(
                        type="plagiarism",
                        severity=5,
                        evidence=f"Exact title match with different authors: {entry.get('id','unknown')}",
                        source_paper=paper,
                        source_corpus=[entry.get("id", "")]
                    ))
                    return violations  # caught definitively

        # SECOND: Similarity engine for fuzzy matches
        matches = self.sim_engine.find_matches(paper.title, paper.abstract, threshold=0.6)
        for match in matches:
            source_entry = next((p for p in corpus_list if p.get("title", "").lower() == match.source_title.lower()), {})
            source_authors = source_entry.get("authors", [])

            severity = 4 if match.score >= 0.85 else 3
            if not source_authors or source_authors != paper.authors:
                evidence = f"High similarity ({match.score:.1%}) to existing paper: {match.source_title}"
                violations.append(Violation(
                    type="plagiarism",
                    severity=severity,
                    evidence=evidence,
                    source_paper=paper,
                    source_corpus=[match.source_title]
                ))

        # THIRD: Lexicon phrase matching
        paper_lower = paper_text.lower()
        for phrase in self.lexicon.get("plagiarism_phrases", []):
            if phrase.lower() in paper_lower:
                violations.append(Violation(
                    type="plagiarism",
                    severity=2,
                    evidence=f"Matched suspicious phrase: '{phrase}'",
                    source_paper=paper,
                    source_corpus=[]
                ))

        return violations

    def _check_duplicate_submission(self, paper: Paper) -> List[Violation]:
        """Check if same paper submitted to multiple venues."""
        # Placeholder: would need access to submission database
        # For now, check if DOI already exists in corpus
        if paper.id in self.known_papers:
            return [Violation(
                type="duplicate_submission",
                severity=4,
                evidence=f"Paper ID already exists in corpus",
                source_paper=paper,
                source_corpus=[paper.id]
            )]
        return []

    def _check_authorship_fraud(self, paper: Paper) -> List[Violation]:
        """Detect ghost/guest authorship."""
        # Placeholder: would need author contribution database
        return []

    def _check_data_fabrication(self, paper: Paper) -> List[Violation]:
        """Basic image/text inconsistency detection."""
        # Placeholder: advanced forensics require image analysis
        return []

    @staticmethod
    def _jaccard_similarity(a: str, b: str) -> float:
        """Simple Jaccard similarity on word sets."""
        set_a = set(a.split())
        set_b = set(b.split())
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union

# CLI entrypoint
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Investigate a paper for misconduct")
    parser.add_argument("--paper-json", required=True, help="Paper metadata as JSON file")
    args = parser.parse_args()

    with open(args.paper_json) as fp:
        paper_data = json.load(fp)

    paper = Paper(
        id=paper_data.get("id", "unknown"),
        title=paper_data.get("title", ""),
        authors=paper_data.get("authors", []),
        abstract=paper_data.get("abstract", ""),
        text=paper_data.get("text", ""),
        source=paper_data.get("source", "unknown")
    )

    inv = Investigator()
    violations = inv.analyze(paper)

    if violations:
        print(f"❌ Paper {paper.id} — {len(violations)} violation(s) found:")
        for v in violations:
            print(f"  [{v.severity}] {v.type}: {v.evidence}")
    else:
        print(f"✅ Paper {paper.id} — No violations detected")
