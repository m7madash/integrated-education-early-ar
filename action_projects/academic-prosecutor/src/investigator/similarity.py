#!/usr/bin/env python3
"""
Academic Prosecutor — Text Similarity Module
Advanced similarity detection: TF-IDF, Jaccard, fuzzy matching, embeddings (optional).
"""

import re
import json
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import hashlib

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

@dataclass
class SimilarityMatch:
    """Represents a text similarity match."""
    source_title: str
    target_title: str
    score: float  # 0-1
    method: str  # "jaccard", "tfidf", "fuzzy", "embedding"
    matching_phrases: List[str]

class SimilarityEngine:
    """Multi-method text similarity detector."""

    def __init__(self, corpus_dir: Path = Path("data/corpus")):
        self.corpus_dir = corpus_dir
        self.corpus = self._load_corpus()
        self.lexicon = self._load_lexicon()

    def _load_corpus(self) -> List[dict]:
        """Load all known papers from corpus directory."""
        corpus = []
        if self.corpus_dir.exists():
            for f in self.corpus_dir.glob("*.json"):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                        corpus.append(data)
                except Exception as e:
                    print(f"⚠️ Skipping {f}: {e}")
        return corpus

    def _load_lexicon(self) -> dict:
        lex_path = Path("data/lexicon.json")
        if lex_path.exists():
            with open(lex_path) as fp:
                return json.load(fp)
        return {}

    def compute_jaccard(self, text1: str, text2: str) -> float:
        """Jaccard similarity on word sets."""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        if not words1 or not words2:
            return 0.0
        return len(words1 & words2) / len(words1 | words2)

    def compute_tfidf_cosine(self, texts: List[str]) -> Optional[float]:
        """Cosine similarity using TF-IDF vectors."""
        if not SKLEARN_AVAILABLE or len(texts) < 2:
            return None
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"⚠️ TF-IDF failed: {e}")
            return None

    def find_matches(self, paper_title: str, paper_abstract: str = "", threshold: float = 0.7) -> List[SimilarityMatch]:
        """Find all corpus entries similar to given paper."""
        matches = []
        target_text = f"{paper_title} {paper_abstract}".lower()

        for entry in self.corpus:
            known_title = entry.get("title", "").lower()
            known_abstract = entry.get("abstract", "").lower()
            source_text = f"{known_title} {known_abstract}"

            # Method 1: Jaccard on titles
            title_sim = self.compute_jaccard(paper_title.lower(), known_title)

            # Method 2: TF-IDF on title+abstract (if sklearn available)
            tfidf_sim = self.compute_tfidf_cosine([target_text, source_text]) if SKLEARN_AVAILABLE else None

            # Method 3: Lexicon phrase matching
            phrase_matches = []
            for phrase in self.lexicon.get("plagiarism_phrases", []):
                if phrase.lower() in target_text and phrase.lower() in source_text:
                    phrase_matches.append(phrase)

            # Combine scores (weighted)
            final_score = title_sim * 0.4
            if tfidf_sim is not None:
                final_score += tfidf_sim * 0.4
            if phrase_matches:
                final_score += 0.2  # bonus for known suspicious phrases

            if final_score >= threshold:
                matches.append(SimilarityMatch(
                    source_title=entry.get("title", "Unknown"),
                    target_title=paper_title,
                    score=final_score,
                    method="combined",
                    matching_phrases=phrase_matches
                ))

        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    def compute_similarity(self, text_a: str, text_b: str, method: str = "jaccard") -> float:
        """Compute similarity between two texts using specified method."""
        if method == "jaccard":
            return self.compute_jaccard(text_a, text_b)
        elif method == "tfidf" and SKLEARN_AVAILABLE:
            result = self.compute_tfidf_cosine([text_a, text_b])
            return result if result is not None else 0.0
        else:
            # fallback to Jaccard
            return self.compute_jaccard(text_a, text_b)

# Convenience
def quick_similarity(a: str, b: str) -> float:
    engine = SimilarityEngine()
    return engine.compute_similarity(a, b, method="jaccard")

if __name__ == "__main__":
    engine = SimilarityEngine()
    # Demo
    text1 = "Machine learning is a subset of artificial intelligence"
    text2 = "AI includes machine learning as a subset"
    print(f"Jaccard similarity: {engine.compute_jaccard(text1, text2):.2%}")
    if SKLEARN_AVAILABLE:
        print(f"TF-IDF cosine: {engine.compute_tfidf_cosine([text1, text2]):.2%}")
    else:
        print("TF-IDF not available (install scikit-learn)")
