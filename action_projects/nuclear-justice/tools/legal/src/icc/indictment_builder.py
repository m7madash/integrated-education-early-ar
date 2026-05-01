"""
ICC Indictment Generator — Tool 2 of Nuclear Justice

Creates draft indictments for ICC prosecution of individuals
responsible for nuclear weapons programs (crimes against humanity, aggression).

Reference: Rome Statute, Articles 5(2), 8(2)(b), 25.
"""

import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

@dataclass
class Person:
    name: str
    title: str
    position: str
    nationality: str

# Alias for compatibility with tests expecting 'Suspect'
Suspect = Person

@dataclass
class Charge:
    name: str
    title: str
    position: str
    nationality: str

@dataclass
class Charge:
    article: str  # Rome Statute article
    description: str
    elements: List[str]

@dataclass
class Evidence:
    type: str  # document, witness, video, satellite
    description: str
    source: str

class ICCIndictmentBuilder:
    """Builds a draft ICC indictment against named individuals."""

    def __init__(self, suspect: Person):
        self.suspect = suspect
        self.charges: List[Charge] = []
        self.evidence_list: List[Evidence] = []
        self.incident_period: tuple = ("", "")

    def add_charge(self, article: str, description: str, elements: List[str]):
        self.charges.append(Charge(article, description, elements))

    def add_evidence(self, etype: str, description: str, source: str):
        self.evidence_list.append(Evidence(etype, description, source))

    def set_incident_period(self, start: str, end: str):
        self.incident_period = (start, end)

    def generate_markdown(self) -> str:
        lines = []
        today = datetime.date.today().isoformat()

        lines.append(f"# International Criminal Court — Prosecution Request")
        lines.append(f"**Date:** {today}")
        lines.append(f"**Case:** Prosecutor v. {self.suspect.name}")
        lines.append(f"**Suspect:** {self.suspect.name}, {self.suspect.title}")
        lines.append(f"**Position:** {self.suspect.position}")
        lines.append(f"**Nationality:** {self.suspect.nationality}")
        lines.append("---")

        # Jurisdiction & Crimes
        lines.append("## I. Jurisdiction")
        lines.append("The International Criminal Court has jurisdiction over the crime of **aggression** (Rome Statute, Article 5(2)) and **war crimes** (Article 8) when committed as part of a plan or policy.")
        lines.append("")

        lines.append("## II. Charges")
        for i, ch in enumerate(self.charges, 1):
            lines.append(f"### Count {i}: {ch.description}")
            lines.append(f"**Legal basis:** Article {ch.article}, Rome Statute")
            lines.append("**Elements of the crime:**")
            for elem in ch.elements:
                lines.append(f"- {elem}")
            lines.append("")

        # Evidence
        lines.append("## III. Summary of Evidence")
        for i, ev in enumerate(self.evidence_list, 1):
            lines.append(f"{i}. **Type:** {ev.type}")
            lines.append(f"   **Description:** {ev.description}")
            lines.append(f"   **Source:** {ev.source}")
            lines.append("")

        # Prayer
        lines.append("## IV. Prayer for Relief")
        lines.append("The Prosecutor requests that the Pre-Trial Chamber:")
        lines.append("1. Issue a warrant of arrest for the suspect.")
        lines.append("2. Order the suspect's immediate surrender to the Court.")
        lines.append("3. Seize all assets related to the nuclear weapons program.")
        lines.append("")

        # Signature placeholder
        lines.append("---")
        lines.append("Submitted by the Office of the Prosecutor")
        lines.append("International Criminal Court")
        lines.append("")

        return "\n".join(lines)

    def save(self, output_path: Path):
        md = self.generate_markdown()
        output_path.write_text(md, encoding="utf-8")
        return output_path

# Convenience builder for nuclear-related crimes
def build_icc_indictment(suspect_name: str, title: str, position: str, nationality: str, output_file: str):
    """Alias for build_nuclear_aggression_indictment for consistency with other tools."""
    return build_nuclear_aggression_indictment(suspect_name, title, position, nationality, output_file)

def build_nuclear_aggression_indictment(suspect_name: str, title: str, position: str, nationality: str, output_file: str):
    suspect = Person(name=suspect_name, title=title, position=position, nationality=nationality)
    builder = ICCIndictmentBuilder(suspect)

    # Aggression (planning, preparation, initiation)
    builder.add_charge(
        article="5(2), 8 bis",
        description="Crime of Aggression — Planning and execution of a nuclear weapons program that threatens regional/international peace",
        elements=[
            "The perpetrator held a position of authority in the government or military",
            "He/she actively directed the development of nuclear weapons",
            "The program constitutes a manifest violation of the UN Charter",
            "The conduct was of such a scale that it threatened the peace, security, or sovereignty of states"
        ]
    )

    # War crimes (potentially, if used)
    builder.add_charge(
        article="8(2)(b)(xix), (xx)",
        description="War crimes — Using weapons inherently indiscriminate or causing superfluous injury",
        elements=[
            "The perpetrator employed nuclear weapons or threatened their use",
            "Such weapons cause unnecessary suffering and indiscriminate harm",
            "The act was not justified by military necessity"
        ]
    )

    # Persecution (if targeting specific groups)
    # Not core; skip.

    # Evidence placeholders
    builder.add_evidence(
        etype="satellite imagery",
        description="High-resolution images of enrichment facilities and missile tests",
        source="Commercial satellite providers (Maxar, Planet)"
    )
    builder.add_evidence(
        etype="official documents",
        description="Decrees, budget allocations, procurement orders for nuclear program",
        source=" whistleblower disclosures"
    )
    builder.add_evidence(
        etype="public statements",
        description="Threatening speeches by officials",
        source="State media archives"
    )

    builder.set_incident_period("2020-01-01", "2025-12-31")

    return builder.save(Path(output_file))

if __name__ == "__main__":
    # Demo
    out = "sample_icc_indictment.md"
    path = build_nuclear_aggression_indictment(
        suspect_name="General X",
        title="Head of Strategic Forces",
        position="Commander, Nuclear Missile Command",
        nationality="State X",
        output_file=out
    )
    print(f"✅ Sample ICC indictment generated: {path}")
    with open(path) as f:
        print(f.read()[:800])
