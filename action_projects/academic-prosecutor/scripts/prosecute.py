#!/usr/bin/env python3
"""
Academic Prosecutor — CLI Entrypoint
Prosecute a single paper: fetch, analyze, sanction, notify.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from investigator.detector import Investigator, Paper
from investigator.sources import fetch_paper
from sanctions.enforcer import SanctionEnforcer, sanction_offense
from notifier.alert import Notifier

def main():
    parser = argparse.ArgumentParser(description="Prosecute an academic paper for misconduct")
    parser.add_argument("--identifier", required=True, help="DOI, PMID, arXiv ID, or local PDF path")
    parser.add_argument("--source", choices=["crossref","pubmed","arxiv","local","auto"], default="auto", help="Source type")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, do not sanction/notify")
    parser.add_argument("--output", default="prosecution_report.json", help="Output report file")
    args = parser.parse_args()

    print(f"🔍 Fetching paper: {args.identifier}")
    paper_data = fetch_paper(args.identifier, args.source)
    if not paper_data:
        print(f"❌ Failed to fetch paper. Check identifier and source.")
        sys.exit(1)

    paper = Paper(
        id=paper_data["id"],
        title=paper_data["title"],
        authors=paper_data.get("authors", []),
        abstract=paper_data.get("abstract", ""),
        text=paper_data.get("text", ""),
        source=paper_data["source"]
    )

    print(f"📄 Paper: {paper.title}")
    print(f"   Authors: {', '.join(paper.authors)}")
    print(f"   Source: {paper.source}")

    # Investigation
    print("\n🔎 Running investigation...")
    inv = Investigator()
    violations = inv.analyze(paper)

    if not violations:
        print("✅ No violations found. Case closed.")
        report = {"paper": paper_data, "violations": [], "status": "clean"}
    else:
        print(f"❌ Found {len(violations)} violation(s):")
        for v in violations:
            print(f"   [{v.severity}] {v.type}: {v.evidence}")

        if args.dry_run:
            print("🏃 Dry-run mode: no sanctions applied")
            report = {"paper": paper_data, "violations": [v.__dict__ for v in violations], "status": "dry_run"}
        else:
            print("\n⚖️ Applying sanctions...")
            enforcer = SanctionEnforcer()
            for violation in violations:
                # Create offense record
                from sanctions.registry import Offense
                offense_id = f"{paper.id}-{violation.type}-{abs(hash(paper.id))%10000}"
                offense = Offense(
                    id=offense_id,
                    offender_id=paper.authors[0] if paper.authors else "unknown",
                    offender_name=paper.authors[0] if paper.authors else "Unknown",
                    paper_id=paper.id,
                    violation_type=violation.type,
                    severity=violation.severity,
                    evidence=violation.evidence,
                    discovered_at="2025-01-01T00:00:00Z",  # TODO: use real timestamp
                    sanction_applied="",
                    status="pending"
                )
                enforcer.registry.add_offense(offense)
                enforcer.apply(offense)

            # Notify (placeholder — would need config)
            print("\n📣 Notifying stakeholders (demo mode)...")
            # In real deployment, call notifier.alert_publisher(...)

            report = {
                "paper": paper_data,
                "violations": [v.__dict__ for v in violations],
                "status": "prosecuted",
                "sanctions_applied": True
            }

    # Save report
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📝 Report saved to: {out_path}")

if __name__ == "__main__":
    main()
