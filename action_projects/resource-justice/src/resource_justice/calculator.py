#!/usr/bin/env python3
"""
Resource Justice — Impact Calculator
Computes the human impact of reallocating military budgets to basic needs.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
INDICATORS_FILE = DATA_DIR / "indicators.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"

def load_indicators() -> dict:
    with open(INDICATORS_FILE, 'r') as f:
        return json.load(f)

def load_budgets() -> dict:
    with open(BUDGETS_FILE, 'r') as f:
        return json.load(f)

def calculate_impact(country: str, percent_reallocated: float) -> dict:
    """
    Calculate the impact of reallocating X% of military budget to:
    - Meals (food security)
    - Schools (education infrastructure)
    - Healthcare (basic coverage)

    Args:
        country: Country name (must exist in budgets.json)
        percent_reallocated: Percentage of military budget to redirect (0-100)

    Returns:
        dict with keys: meals, schools, healthcare_people, lives_saved
    """
    budgets = load_budgets()
    indicators = load_indicators()

    if country not in budgets:
        raise ValueError(f"Country '{country}' not found. Available: {list(budgets.keys())}")

    military_budget = budgets[country]["military_budget_usd"]
    reallocation_amount = military_budget * (percent_reallocated / 100.0)

    cost_per_meal = indicators["cost_per_meal_usd"]
    cost_per_school = indicators["cost_per_school_usd"]
    cost_per_person_healthcare = indicators["cost_per_healthcare_usd_per_person"]

    meals = reallocation_amount / cost_per_meal
    schools = reallocation_amount / cost_per_school
    healthcare_people = reallocation_amount / cost_per_person_healthcare

    # Rough estimate: 1 life saved per 1000 meals provided (conservative)
    lives_saved = meals / 1000.0

    return {
        "meals": int(meals),
        "schools": int(schools),
        "healthcare_people": int(healthcare_people),
        "lives_saved": int(lives_saved),
        "reallocation_amount_usd": int(reallocation_amount)
    }

if __name__ == "__main__":
    # Demo: calculate for Saudi Arabia, 5% reallocation
    demo_country = "Saudi Arabia"
    demo_percent = 5.0
    result = calculate_impact(demo_country, demo_percent)
    print(f"\n📊 Demo: {demo_country} @ {demo_percent}% reallocation")
    print(f"   💰 Amount: ${result['reallocation_amount_usd']:,.0f}")
    print(f"   🍛 Meals: {result['meals']:,.0f}")
    print(f"   🏫 Schools: {result['schools']:,.0f}")
    print(f"   💊 Healthcare people: {result['healthcare_people']:,.0f}")
    print(f"   ❤️  Lives saved (est.): {result['lives_saved']:,.0f}")
