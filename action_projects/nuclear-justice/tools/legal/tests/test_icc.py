"""
Tests for Legal Qaeda — ICC Indictment Builder (Tool 2 of Nuclear Justice)

Run with: python3 -m unittest discover -s tests -p 'test_*.py' -v
Or: pytest (if installed)
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from icc.indictment_builder import ICCIndictmentBuilder, Person as Suspect, Charge

class TestICCIndictmentBuilder(unittest.TestCase):
    """Test suite for ICC indictment generation."""

    def test_suspect_creation(self):
        suspect = Suspect(
            name="General X",
            title="Head of Strategic Forces",
            position="Commander, Nuclear Missile Command",
            nationality="State X"
        )
        self.assertEqual(suspect.name, "General X")
        self.assertEqual(suspect.nationality, "State X")

    def test_charge_creation(self):
        charge = Charge(
            article="5(2)",
            description="Test charge",
            elements=["elem1", "elem2"]
        )
        self.assertEqual(charge.article, "5(2)")
        self.assertEqual(charge.description, "Test charge")
        self.assertEqual(charge.elements, ["elem1", "elem2"])

    def test_builder_add_charge(self):
        suspect = Suspect("Gen X", "Head", "Cmd", "State X")
        builder = ICCIndictmentBuilder(suspect)
        builder.add_charge("5(2)", "Threat", ["elem1", "elem2"])
        self.assertEqual(len(builder.charges), 1)
        self.assertEqual(builder.charges[0].article, "5(2)")
        self.assertEqual(builder.charges[0].elements, ["elem1", "elem2"])

    def test_generate_markdown_contains_sections(self):
        suspect = Suspect(
            name="General X",
            title="Head of Strategic Forces",
            position="Commander, Nuclear Missile Command",
            nationality="State X"
        )
        builder = ICCIndictmentBuilder(suspect)
        builder.add_charge("5(2)", "Planning nuclear attack", ["Element 1", "Element 2"])
        md = builder.generate_markdown()
        self.assertIn("# International Criminal Court — Prosecution Request", md)
        self.assertIn("## I. Jurisdiction", md)
        self.assertIn("## II. Charges", md)
        self.assertIn("## III. Summary of Evidence", md)
        self.assertIn("## IV. Prayer for Relief", md)
        self.assertIn("Submitted by the Office of the Prosecutor", md)

    def test_save_output_file(self):
        suspect = Suspect("General Y", "Chief", "Nuclear Cmd", "State Y")
        builder = ICCIndictmentBuilder(suspect)
        builder.add_charge("8", "Test charge", ["elem"])
        test_file = Path("test_icc_output.md")
        if test_file.exists():
            test_file.unlink()
        builder.save(test_file)
        self.assertTrue(test_file.exists())
        content = test_file.read_text()
        self.assertIn("General Y", content)
        self.assertIn("Prosecution Request", content)
        test_file.unlink()

    def test_multiple_charges_rendered(self):
        suspect = Suspect("Gen", "Title", "Pos", "Country")
        builder = ICCIndictmentBuilder(suspect)
        builder.add_charge("5(2)", "Desc1", ["e1"])
        builder.add_charge("8", "Desc2", ["e2"])
        md = builder.generate_markdown()
        self.assertIn("Desc1", md)
        self.assertIn("Desc2", md)

class TestICCIndictmentIntegration(unittest.TestCase):
    """Integration test for ICC builder convenience function."""

    def test_build_icc_indictment_function(self):
        # This function is an alias to build_nuclear_aggression_indictment
        from icc.indictment_builder import build_icc_indictment
        out_file = Path("integ_test_icc.md")
        if out_file.exists():
            out_file.unlink()
        result_path = build_icc_indictment(
            suspect_name="General X",
            title="Head of Strategic Forces",
            position="Commander, Nuclear Missile Command",
            nationality="State X",
            output_file=str(out_file)
        )
        self.assertTrue(out_file.exists())
        content = out_file.read_text()
        self.assertIn("General X", content)
        self.assertIn("Rome Statute", content)
        self.assertIn("Crime of Aggression", content)
        out_file.unlink()

if __name__ == "__main__":
    unittest.main()
