#!/usr/bin/env python3
"""
Academic Prosecutor — Batch Scanner
Scan a directory of PDFs or paper metadata JSONs.
"""

import argparse
import json
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from investigator.detector import Investigator, Paper
from investigator.sources import fetch_paper
from sanctions.enforcer import sanction_offense

def process_paper(paper_data: dict, dry_run: bool = False) -> dict:
    """Analyze a single paper entry."""
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

    result = {
        "paper_id": paper.id,
        "title": paper.title,
        "violations": [v.__dict__ for v in violations],
        "action_taken": False
    }

    if violations and not dry_run:
        # Apply sanctions for each violation (simplified)
        for v in violations:
            offense_id = f"{paper.id}-{v.type}"
            print(f"  🚨 {paper.id}: {v.type} (severity {v.severity})")
            # record to registry (would create full Offense object)
        result["action_taken"] = True

    return result

def main():
    parser = argparse.ArgumentParser(description="Batch scan papers for misconduct")
    parser.add_argument("--dir", required=True, help="Directory containing JSON paper files or PDFs")
    parser.add_argument("--output", default="batch_report.json", help="Output JSON report")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only")
    args = parser.parse_args()

    dir_path = Path(args.dir)
    if not dir_path.exists():
        print(f"❌ Directory not found: {dir_path}")
        sys.exit(1)

    results = []
    # Collect all JSON files (each representing a paper)
    json_files = list(dir_path.glob("*.json"))
    print(f"🔍 Found {len(json_files)} paper metadata files")

    for jf in json_files:
        with open(jf) as f:
            try:
                paper_data = json.load(f)
                print(f"\n📄 Processing: {jf.name}")
                result = process_paper(paper_data, dry_run=args.dry_run)
                results.append(result)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in {jf}: {e}")

    # Summary
    total_violations = sum(len(r["violations"]) for r in results)
    types = Counter(v["type"] for r in results for v in r["violations"])
    print(f"\n📊 Summary:")
    print(f"   Papers scanned: {len(results)}")
    print(f"   Total violations: {total_violations}")
    for t, c in types.items():
        print(f"   • {t}: {c}")

    # Save report
    out = {
        "scanned": len(results),
        "total_violations": total_violations,
        "by_type": dict(types),
        "results": results
    }
    with open(args.output, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\n✅ Report saved: {args.output}")

if __name__ == "__main__":
    main()
