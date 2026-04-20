"""
ICJ Case Generator — Tool 2 of Nuclear Justice (PROJECT OMAR)

Generates applications to the International Court of Justice (ICJ)
against nuclear-weapon states for breach of NPT Art VI, threat of use, etc.

Output format: Markdown (suitable for filing with ICJ Registry)
"""

import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "docs" / "templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Party:
    state: str
    representative: str
    address: str

@dataclass
class Fact:
    date: str
    description: str
    evidence_ref: Optional[str] = None

@dataclass
class LegalBasis:
    instrument: str  # e.g., "Nuclear Non-Proliferation Treaty"
    article: str
    para: Optional[str] = None
    summary: str = ""

@dataclass
class Remedy:
    description: str
    legal_basis: str

class ICJCaseBuilder:
    """Builds an ICJ application for nuclear justice cases."""

    def __init__(self, applicant: Party, respondent: Party):
        self.applicant = applicant
        self.respondent = respondent
        self.facts: List[Fact] = []
        self.legal_bases: List[LegalBasis] = []
        self.remedies: List[Remedy] = []
        self.evidence_annexes: List[dict] = []

    def add_fact(self, date: str, description: str, evidence_ref: str = None):
        self.facts.append(Fact(date, description, evidence_ref))

    def add_legal_basis(self, instrument: str, article: str, para: str = None, summary: str = ""):
        self.legal_bases.append(LegalBasis(instrument, article, para, summary))

    def add_remedy(self, description: str, legal_basis: str):
        self.remedies.append(Remedy(description, legal_basis))

    def add_annex(self, title: str, content: str, doc_type: str = "document"):
        self.evidence_annexes.append({"title": title, "content": content, "type": doc_type})

    def generate_markdown(self) -> str:
        """Render the case as Markdown."""
        lines = []
        today = datetime.date.today().isoformat()

        # Header
        lines.append(f"# Application to the International Court of Justice")
        lines.append(f"**Date:** {today}")
        lines.append(f"**Applicant:** {self.applicant.state}")
        lines.append(f"**Respondent:** {self.respondent.state}")
        lines.append("---")

        # 1. Jurisdiction
        lines.append("## 1. Jurisdiction of the Court")
        lines.append("The Court has jurisdiction under Article 36(1) of its Statute and the provisions of the Nuclear Non-Proliferation Treaty (NPT), particularly Article VI, which imposes obligations on all States Parties to pursue negotiations in good faith on effective measures relating to cessation of the nuclear arms race and to nuclear disarmament.")
        lines.append("")

        # 2. Facts
        lines.append("## 2. Statement of Facts")
        for i, fact in enumerate(self.facts, 1):
            lines.append(f"{i}. **{fact.date}** — {fact.description}")
            if fact.evidence_ref:
                lines.append(f"   *Evidence:* {fact.evidence_ref}")
        lines.append("")

        # 3. Legal Grounds
        lines.append("## 3. Legal Grounds")
        for i, lb in enumerate(self.legal_bases, 1):
            para_str = f", para. {lb.para}" if lb.para else ""
            lines.append(f"{i}. **{lb.instrument}, Article {lb.article}{para_str}**")
            if lb.summary:
                lines.append(f"   {lb.summary}")
        lines.append("")

        # 4. Arguments
        lines.append("## 4. Arguments")
        lines.append("The Respondent State is in breach of its obligations under international law:")
        lines.append("- It maintains an active nuclear weapons program in violation of NPT Article VI.")
        lines.append("- It has refused to join the Treaty on the Prohibition of Nuclear Weapons (TPNW).")
        lines.append("- Its possession and threat of use of nuclear weapons contravene International Humanitarian Law principles of distinction and proportionality (ICJ Advisory Opinion 1996).")
        lines.append("")

        # 5. Prayer for Relief
        lines.append("## 5. Prayer for Relief")
        for i, remedy in enumerate(self.remedies, 1):
            lines.append(f"{i}. {remedy.description}")
        lines.append("")

        # 6. Annexes
        if self.evidence_annexes:
            lines.append("## 6. Annexes")
            for i, annex in enumerate(self.evidence_annexes, 1):
                lines.append(f"{i}. {annex['title']} ({annex['type']})")
            lines.append("")

        # Signature
        lines.append("---")
        lines.append(f"Respectfully submitted,")
        lines.append(f"**{self.applicant.representative}**")
        lines.append(f"{self.applicant.address}")
        lines.append("")

        return "\n".join(lines)

    def save(self, output_path: Path):
        md = self.generate_markdown()
        output_path.write_text(md, encoding="utf-8")
        return output_path

# Convenience function for quick generation
def build_icj_case(applicant_state: str, respondent_state: str, facts_data: list, output_file: str):
    applicant = Party(
        state=applicant_state,
        representative="Agent for the Applicant",
        address="Permanent Mission to the United Nations, New York"
    )
    respondent = Party(
        state=respondent_state,
        representative="[To be served]",
        address="[Respondent's address]"
    )
    builder = ICJCaseBuilder(applicant, respondent)

    for f in facts_data:
        builder.add_fact(f["date"], f["description"], f.get("evidence"))

    # Default legal bases (customizable)
    builder.add_legal_basis(
        instrument="Nuclear Non-Proliferation Treaty (NPT)",
        article="VI",
        summary="Obligation to pursue negotiations in good faith on nuclear disarmament."
    )
    builder.add_legal_basis(
        instrument="United Nations Charter",
        article="2(4)",
        summary="Prohibition of threat or use of force."
    )
    builder.add_legal_basis(
        instrument="ICJ Advisory Opinion (1996)",
        article="",
        summary="Nuclear weapon use would generally be contrary to International Humanitarian Law."
    )

    # Remedies
    builder.add_remedy(
        description="Order the Respondent to immediately suspend its nuclear weapons program and commence good-faith negotiations towards total disarmament, under UN supervision.",
        legal_basis="NPT Art VI; ICJ 1996"
    )
    builder.add_remedy(
        description="Award costs of these proceedings to the Applicant.",
        legal_basis="ICJ Statute Art 64"
    )

    return builder.save(Path(output_file))

if __name__ == "__main__":
    # Demo: build a sample case
    sample_facts = [
        {
            "date": "2025-03-15",
            "description": "Respondent conducted a test of its centrifuge cascade, increasing enrichment to 90% U-235, indicating weapons-grade capability.",
            "evidence": "Satellite imagery (see Annex A)"
        },
        {
            "date": "2025-04-01",
            "description": "Respondent issued a public threat to use nuclear weapons against neighboring states.",
            "evidence": "Official statement transcript (see Annex B)"
        }
    ]

    out = "sample_icj_case.md"
    path = build_icj_case(
        applicant_state="Islamic Republic of Iran",
        respondent_state="State X",
        facts_data=sample_facts,
        output_file=out
    )
    print(f"✅ Sample ICJ case generated: {path}")
    print("   Preview:")
    with open(path) as f:
        print(f.read()[:800])
