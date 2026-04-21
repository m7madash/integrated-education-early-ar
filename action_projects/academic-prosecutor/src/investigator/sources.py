#!/usr/bin/env python3
"""
Academic Prosecutor — Sources Module
Fetch papers from Crossref, PubMed, arXiv, and local PDFs.
"""

import json
import urllib.request
from pathlib import Path
from typing import Dict, Optional

class SourceFetcher:
    """Fetch paper metadata from various APIs."""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}

    def fetch_crossref(self, doi: str) -> Optional[Dict]:
        """Fetch paper metadata from Crossref API."""
        url = f"https://api.crossref.org/works/{doi}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                message = data.get("message", {})
                return {
                    "id": doi,
                    "title": message.get("title", [""])[0],
                    "authors": [a.get("given", "") + " " + a.get("family", "") for a in message.get("author", [])],
                    "abstract": message.get("abstract", ""),
                    "source": "crossref",
                    "published": message.get("created", {}).get("date-parts", [[None]])[0][0]
                }
        except Exception as e:
            print(f"❌ Crossref fetch failed for {doi}: {e}")
            return None

    def fetch_pubmed(self, pmid: str) -> Optional[Dict]:
        """Fetch from PubMed via NCBI E-utilities."""
        base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        # First: esummary to get title/authors
        summary_url = f"{base}/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        try:
            with urllib.request.urlopen(summary_url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                result = data.get("result", {})
                article = result.get(pmid, {})
                return {
                    "id": f"PubMed:{pmid}",
                    "title": article.get("title", ""),
                    "authors": [a.get("name", "") for a in article.get("authors", [])],
                    "abstract": "",  # would need efetch
                    "source": "pubmed",
                    "published": article.get("pubdate", "")
                }
        except Exception as e:
            print(f"❌ PubMed fetch failed for {pmid}: {e}")
            return None

    def fetch_arxiv(self, arxiv_id: str) -> Optional[Dict]:
        """Fetch from arXiv API."""
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                xml = resp.read().decode()
                # Very simple extraction (use xml.etree for real)
                title_match = re.search(r"<title[^>]*>([^<]+)</title>", xml)
                summary_match = re.search(r"<summary[^>]*>([^<]+)</summary>", xml)
                return {
                    "id": f"arXiv:{arxiv_id}",
                    "title": title_match.group(1).strip() if title_match else "",
                    "authors": [],  # parse properly
                    "abstract": summary_match.group(1).strip() if summary_match else "",
                    "source": "arxiv",
                    "published": ""
                }
        except Exception as e:
            print(f"❌ arXiv fetch failed for {arxiv_id}: {e}")
            return None

    def fetch_local_pdf(self, pdf_path: Path) -> Optional[Dict]:
        """Extract text from local PDF using pdfminer (if available)."""
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(str(pdf_path))
            # Very naive title extraction: first non-empty line
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = lines[0] if lines else pdf_path.stem
            return {
                "id": f"local:{pdf_path.name}",
                "title": title,
                "authors": [],  # would need metadata extraction
                "abstract": text[:1000],
                "text": text,
                "source": "local_pdf",
                "path": str(pdf_path)
            }
        except ImportError:
            print("❌ pdfminer not installed — cannot extract PDF text")
            return None
        except Exception as e:
            print(f"❌ PDF extraction failed for {pdf_path}: {e}")
            return None

# Convenience function
def fetch_paper(identifier: str, source: str = "auto") -> Optional[Dict]:
    fetcher = SourceFetcher()
    if source == "crossref" or source == "auto" and identifier.startswith("10."):
        return fetcher.fetch_crossref(identifier)
    elif source == "pubmed" or source == "auto" and identifier.isdigit():
        return fetcher.fetch_pubmed(identifier)
    elif source == "arxiv" or source == "auto" and "arXiv" in identifier:
        arxiv_id = identifier.replace("arXiv:", "")
        return fetcher.fetch_arxiv(arxiv_id)
    elif Path(identifier).exists():
        return fetcher.fetch_local_pdf(Path(identifier))
    else:
        print(f"❌ Unknown identifier format: {identifier}")
        return None

if __name__ == "__main__":
    import argparse, re
    parser = argparse.ArgumentParser()
    parser.add_argument("identifier", help="DOI, PMID, arXiv ID, or PDF path")
    parser.add_argument("--source", choices=["crossref","pubmed","arxiv","local"], default="auto")
    args = parser.parse_args()

    paper = fetch_paper(args.identifier, args.source)
    if paper:
        print(json.dumps(paper, indent=2))
    else:
        print("❌ Failed to fetch paper")
