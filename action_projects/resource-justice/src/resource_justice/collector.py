#!/usr/bin/env python3
"""
Resource Justice — Data Collector
Fetches military and development budgets (sample data + live API stubs)
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
BUDGETS_FILE = DATA_DIR / "budgets.json"

def load_budgets() -> dict:
    """Load sample budgets from JSON file."""
    with open(BUDGETS_FILE, 'r') as f:
        return json.load(f)

def collect_sample_data() -> dict:
    """Return sample budget data (for demo)."""
    budgets = load_budgets()
    print(f"✅ Loaded budgets for {len(budgets)} countries.")
    for country, data in budgets.items():
        print(f"   {country}: ${data['military_budget_usd']:,.0f} military, ${data['development_budget_usd']:,.0f} development")
    return budgets

def fetch_live_budget(country: str) -> dict:
    """
    Fetch live data from external APIs (SIPRI, World Bank).
    Not implemented yet — requires API keys.
    """
    raise NotImplementedError("Live API fetching requires API keys and will be implemented in v0.2.0")

if __name__ == "__main__":
    collect_sample_data()
