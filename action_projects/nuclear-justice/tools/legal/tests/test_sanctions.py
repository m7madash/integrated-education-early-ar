"""
Tests for Legal Qaeda — Sanctions Generator (Tool 2 of Nuclear Justice)

Run with: python3 -m unittest discover -s tests -p 'test_*.py' -v
Or: pytest (if installed)
"""

import unittest
import sys
import os
import csv
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sanctions.updater import generate_sanctions_list, PersonEntity, Organization


class TestSanctionsGenerator(unittest.TestCase):
    """Test suite for sanctions list generation."""

    def setUp(self):
        self.sample_persons = [
            {"name":"Dr. Ahmad Vahidi","title":"Minister of Defense","org":"Ministry of Defense","country":"State X","risk_score":9,"sanction_type":"both"},
            {"name":"General Y","title":"Head of Nuclear Command","org":"Strategic Forces Command","country":"State X","risk_score":10,"sanction_type":"both"},
        ]
        self.sample_orgs = [
            {"name":"Atomic Energy Organization of State X","org_type":"state_enterprise","country":"State X","risk_score":8,"justification":"Controls all nuclear material"},
            {"name":"Bank X","org_type":"bank","country":"State X","risk_score":6,"justification":"Facilitates financial transactions"},
        ]
        self.evidence = "Satellite imagery + procurement records"
        self.prefix = "test_sanctions"

    def test_generate_sanctions_json_output(self):
        """Test that JSON output is created and contains expected fields."""
        gen = generate_sanctions_list(self.sample_persons, self.sample_orgs, self.evidence, self.prefix)
        json_path = f"{self.prefix}.json"
        self.assertTrue(os.path.exists(json_path))
        with open(json_path) as f:
            data = json.load(f)
        self.assertIn("persons", data)
        self.assertIn("organizations", data)
        self.assertEqual(len(data["persons"]), 2)
        self.assertEqual(len(data["organizations"]), 2)

    def test_generate_sanctions_csv_output(self):
        """Test that CSV files are created for persons and organizations."""
        gen = generate_sanctions_list(self.sample_persons, self.sample_orgs, self.evidence, self.prefix)
        persons_csv = f"{self.prefix}_persons.csv"
        orgs_csv = f"{self.prefix}_orgs.csv"
        self.assertTrue(os.path.exists(persons_csv))
        self.assertTrue(os.path.exists(orgs_csv))
        # Verify CSV content
        with open(persons_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertIn("name", rows[0])
            self.assertIn("risk_score", rows[0])

    def test_person_entity_creation(self):
        """Test PersonEntity dataclass creation."""
        p = PersonEntity(name="Test", title="Head", organization="Org", country="TC", risk_score=5, sanction_type="both")
        self.assertEqual(p.name, "Test")
        self.assertEqual(p.risk_score, 5)
        self.assertEqual(p.sanction_type, "both")

    def test_organization_creation(self):
        """Test Organization dataclass creation."""
        o = Organization(name="Test Org", org_type="bank", country="TC", risk_score=7, justification="Test")
        self.assertEqual(o.name, "Test Org")
        self.assertEqual(o.org_type, "bank")
        self.assertEqual(o.risk_score, 7)

    def test_empty_lists(self):
        """Test generation with empty persons and orgs."""
        prefix = "empty_test"
        gen = generate_sanctions_list([], [], "No evidence", prefix)
        json_path = f"{prefix}.json"
        self.assertTrue(os.path.exists(json_path))
        with open(json_path) as f:
            data = json.load(f)
        self.assertEqual(data["persons"], [])
        self.assertEqual(data["organizations"], [])

    def test_mixed_risk_scores(self):
        """Test that risk scores are preserved correctly."""
        persons = [{"name":"A","title":"T","org":"O","country":"C","risk_score":3,"sanction_type":"asset_freeze"}]
        orgs = [{"name":"B","org_type":"company","country":"C","risk_score":9,"justification":"J"}]
        prefix = "mixed"
        gen = generate_sanctions_list(persons, orgs, "ev", prefix)
        json_path = f"{prefix}.json"
        with open(json_path) as f:
            data = json.load(f)
        self.assertEqual(data["persons"][0]["risk_score"], 3)
        self.assertEqual(data["organizations"][0]["risk_score"], 9)

    def test_output_files_created(self):
        """Test that all expected output files are created."""
        prefix = "file_test"
        gen = generate_sanctions_list(self.sample_persons, self.sample_orgs, self.evidence, prefix)
        expected = [f"{prefix}.json", f"{prefix}_persons.csv", f"{prefix}_orgs.csv"]
        for path in expected:
            self.assertTrue(os.path.exists(path), f"Missing: {path}")


class TestSanctionsFileStructure(unittest.TestCase):
    """Validate output file naming and structure."""

    def test_output_prefix_used(self):
        """Ensure output files use the provided prefix."""
        prefix = "struct_test"
        gen = generate_sanctions_list([], [], "test", prefix)
        expected = [f"{prefix}.json", f"{prefix}_persons.csv", f"{prefix}_orgs.csv"]
        for path in expected:
            self.assertTrue(os.path.exists(path), f"Expected file not found: {path}")


if __name__ == "__main__":
    unittest.main()
