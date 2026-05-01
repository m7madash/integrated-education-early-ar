"""
Tests for Legal Qaeda — ICJ Case Builder (Tool 2 of Nuclear Justice)

Run with: python3 -m unittest discover -s tests -p 'test_*.py' -v
Or: pytest (if installed)
"""

import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from icj.case_builder import ICJCaseBuilder, Party, Fact, LegalBasis, Remedy

class TestICJCaseBuilder(unittest.TestCase):
    """Test suite for ICJ case generation."""

    def test_party_creation(self):
        applicant = Party(state="Iran", representative="Agent", address="NYC")
        self.assertEqual(applicant.state, "Iran")
        self.assertEqual(applicant.representative, "Agent")

    def test_fact_creation(self):
        fact = Fact(date="2025-03-15", description="Test", evidence_ref="Annex A")
        self.assertEqual(fact.date, "2025-03-15")
        self.assertEqual(fact.evidence_ref, "Annex A")

    def test_legal_basis_creation(self):
        lb = LegalBasis(instrument="NPT", article="VI", summary="Obligation")
        self.assertEqual(lb.instrument, "NPT")
        self.assertEqual(lb.article, "VI")
        self.assertEqual(lb.summary, "Obligation")

    def test_remedy_creation(self):
        remedy = Remedy(description="Disarm", legal_basis="NPT Art VI")
        self.assertEqual(remedy.description, "Disarm")

    def test_builder_add_fact(self):
        applicant = Party("A", "Rep", "Addr")
        respondent = Party("B", "Rep2", "Addr2")
        builder = ICJCaseBuilder(applicant, respondent)
        builder.add_fact("2025-01-01", "Fact description", "Evidence")
        self.assertEqual(len(builder.facts), 1)
        self.assertEqual(builder.facts[0].date, "2025-01-01")

    def test_builder_add_legal_basis(self):
        applicant = Party("A", "Rep", "Addr")
        respondent = Party("B", "Rep2", "Addr2")
        builder = ICJCaseBuilder(applicant, respondent)
        builder.add_legal_basis("NPT", "VI", summary="Obligation to disarm")
        self.assertEqual(len(builder.legal_bases), 1)
        self.assertEqual(builder.legal_bases[0].instrument, "NPT")

    def test_builder_add_remedy(self):
        applicant = Party("A", "Rep", "Addr")
        respondent = Party("B", "Rep2", "Addr2")
        builder = ICJCaseBuilder(applicant, respondent)
        builder.add_remedy("Order disarmament", "NPT Art VI")
        self.assertEqual(len(builder.remedies), 1)

    def test_generate_markdown_contains_sections(self):
        applicant = Party(state="Iran", representative="Agent", address="Mission NY")
        respondent = Party(state="State X", representative="[To be served]", address="[Address]")
        builder = ICJCaseBuilder(applicant, respondent)
        builder.add_fact("2025-03-15", "Enrichment to 90%", "Satellite Annex A")
        builder.add_legal_basis("NPT", "VI", summary="Disarmament obligation")
        builder.add_remedy("Suspend nuclear program", "NPT Art VI")
        md = builder.generate_markdown()
        self.assertIn("# Application to the International Court of Justice", md)
        self.assertIn("## 1. Jurisdiction", md)
        self.assertIn("## 2. Statement of Facts", md)
        self.assertIn("## 3. Legal Grounds", md)
        self.assertIn("## 4. Arguments", md)
        self.assertIn("## 5. Prayer for Relief", md)
        self.assertIn("Respectfully submitted", md)

    def test_save_output_file(self):
        applicant = Party("Iran", "Agent", "NY")
        respondent = Party("State X", "Respondent", "Addr")
        builder = ICJCaseBuilder(applicant, respondent)
        builder.add_fact("2025-01-01", "Test fact", "Evidence")
        test_file = Path("test_icj_output.md")
        if test_file.exists():
            test_file.unlink()
        builder.save(test_file)
        self.assertTrue(test_file.exists())
        content = test_file.read_text()
        self.assertIn("Application to the International Court of Justice", content)
        test_file.unlink()

    def test_annexes_included(self):
        applicant = Party("Iran", "Agent", "NY")
        respondent = Party("State X", "Resp", "Addr")
        builder = ICJCaseBuilder(applicant, respondent)
        builder.add_annex("Annex A", "Content A", "satellite")
        builder.add_annex("Annex B", "Content B", "transcript")
        md = builder.generate_markdown()
        self.assertIn("## 6. Annexes", md)
        self.assertIn("Annex A", md)
        self.assertIn("Annex B", md)

class TestICJCaseBuilderIntegration(unittest.TestCase):
    """Integration tests using sample data from demo."""

    def test_build_icj_case_function(self):
        from icj.case_builder import build_icj_case
        sample_facts = [
            {"date":"2025-03-15","description":"Test enrichment","evidence":"Satellite Annex A"},
            {"date":"2025-04-01","description":"Threat","evidence":"Transcript Annex B"}
        ]
        out_file = Path("integ_test_icj.md")
        if out_file.exists():
            out_file.unlink()
        result_path = build_icj_case(
            applicant_state="Islamic Republic of Iran",
            respondent_state="State X",
            facts_data=sample_facts,
            output_file=str(out_file)
        )
        self.assertTrue(out_file.exists())
        content = out_file.read_text()
        self.assertIn("Islamic Republic of Iran", content)
        self.assertIn("State X", content)
        self.assertIn("Nuclear Non-Proliferation Treaty", content)
        out_file.unlink()

if __name__ == "__main__":
    unittest.main()
