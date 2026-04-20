#!/usr/bin/env python3
"""
Legal Qaeda CLI — Unified command-line for Nuclear Justice legal tools

Usage:
  legal-qaeda --tool icj --applicant "Iran" --respondent "State X" --facts facts.json --output case.md
  legal-qaeda --tool icc --suspect "General X" --title "Commander" --position "Head of Missiles" --output indictment.md
  legal-qaeda --tool sanctions --persons persons.csv --organizations orgs.csv --evidence "text" --prefix sanctions
  legal-qaeda --demo  (run all demos)

All outputs are in Markdown/JSON for filing with international bodies.
"""

import argparse, json, sys, os, csv
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from icj.case_builder import build_icj_case
from icc.indictment_builder import build_nuclear_aggression_indictment
from sanctions.updater import generate_sanctions_list
from icc.indictment_builder import build_nuclear_aggression_indictment
from sanctions.updater import generate_sanctions_list

def run_demo():
    print("=" * 60)
    print("LEGAL QAEDA — DEMO (PROJECT OMAR TOOL 2)")
    print("=" * 60)

    print("\n[1] Generating sample ICJ case...")
    facts = [
        {"date":"2025-03-15","description":" test enrichment to weapons-grade","evidence":"Satellite Annex A"},
        {"date":"2025-04-01","description":"Public threat to use nuclear weapons","evidence":"Transcript Annex B"}
    ]
    case_path = build_icj_case(
        applicant_state="Islamic Republic of Iran",
        respondent_state="State X",
        facts_data=facts,
        output_file="demo_icj_case.md"
    )
    print(f"    ICJ case: {case_path}")

    print("\n[2] Generating sample ICC indictment...")
    ind_path = build_nuclear_aggression_indictment(
        suspect_name="General X",
        title="Head of Strategic Forces",
        position="Commander, Nuclear Missile Command",
        nationality="State X",
        output_file="demo_icc_indictment.md"
    )
    print(f"    ICC indictment: {ind_path}")

    print("\n[3] Generating sample sanctions list...")
    persons = [
        {"name":"Dr. Ahmad Vahidi","title":"Minister of Defense","org":"Ministry of Defense","country":"State X","risk":9,"stype":"both"},
        {"name":"General Y","title":"Head of Nuclear Command","org":"Strategic Forces Command","country":"State X","risk":10,"stype":"both"},
    ]
    orgs = [
        {"name":"Atomic Energy Organization of State X","otype":"state_enterprise","country":"State X","risk":8,"justification":"Controls all nuclear material"},
        {"name":"Bank X","otype":"bank","country":"State X","risk":6,"justification":"Facilitates financial transactions"}
    ]
    gen = generate_sanctions_list(persons, orgs, "Sample evidence", "demo_sanctions")
    print(f"    Sanctions JSON: demo_sanctions.json")
    print(f"    Persons CSV: demo_sanctions_persons.csv")
    print(f"    Orgs CSV: demo_sanctions_orgs.csv")

    print("\n" + "=" * 60)
    print("✅ Demo complete. All files generated in current directory.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Legal Qaeda — Nuclear Justice legal toolkit")
    parser.add_argument("--tool", choices=["icj", "icc", "sanctions"], help="Tool to run")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--applicant", help="Applicant state (for ICJ)")
    parser.add_argument("--respondent", help="Respondent state (for ICJ)")
    parser.add_argument("--facts", help="JSON file with facts array")
    parser.add_argument("--output", default="output.md", help="Output file")
    parser.add_argument("--suspect", help="Suspect name (for ICC)")
    parser.add_argument("--title", help="Suspect title")
    parser.add_argument("--position", help="Suspect position")
    parser.add_argument("--nationality", help="Suspect nationality")
    parser.add_argument("--persons", help="CSV of persons (sanctions)")
    parser.add_argument("--organizations", help="CSV of organizations (sanctions)")
    parser.add_argument("--evidence", help="Evidence summary (sanctions)")
    parser.add_argument("--prefix", help="Output prefix (sanctions)")

    args = parser.parse_args()

    if args.demo:
        run_demo()
        return 0

    if not args.tool:
        parser.print_help()
        return 1

    if args.tool == "icj":
        if not all([args.applicant, args.respondent, args.facts, args.output]):
            print("❌ Missing required arguments for ICJ tool")
            return 1
        with open(args.facts) as f:
            facts = json.load(f)
        path = build_icj_case(args.applicant, args.respondent, facts, args.output)
        print(f"✅ ICJ case generated: {path}")

    elif args.tool == "icc":
        if not all([args.suspect, args.title, args.position, args.nationality, args.output]):
            print("❌ Missing required arguments for ICC tool")
            return 1
        path = build_nuclear_aggression_indictment(
            suspect_name=args.suspect,
            title=args.title,
            position=args.position,
            nationality=args.nationality,
            output_file=args.output
        )
        print(f"✅ ICC indictment generated: {path}")

    elif args.tool == "sanctions":
        if not all([args.persons, args.organizations, args.evidence, args.prefix]):
            print("❌ Missing required arguments for sanctions tool")
            return 1
        # Load CSVs
        persons = []
        with open(args.persons, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                persons.append(dict(row))
        orgs = []
        with open(args.organizations, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                orgs.append(dict(row))
        gen = generate_sanctions_list(persons, orgs, args.evidence, args.prefix)
        print(f"✅ Sanctions lists generated with prefix: {args.prefix}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
