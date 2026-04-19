#!/usr/bin/env python3
"""Red flag indicators for modern slavery in supply chains."""

# 10 Red Flags (ethical auditing standards: SA8000, ETI, ILO)
RED_FLAGS = {
    "excessive_hours": {
        "condition": lambda s: s.avg_hours_per_week > 60,
        "evidence": " overtime logs, worker interviews",
        "question": "Are workers forced to work overtime beyond legal limits?"
    },
    "withhold_wages": {
        "condition": lambda s: s.wage_withheld_months > 0,
        "evidence": " payroll records, worker testimony",
        "question": "Are wages withheld as punishment or control?"
    },
    "no_contracts": {
        "condition": lambda s: not s.has_contracts,
        "evidence": " document review, worker interviews",
        "question": "Do workers have written contracts in a language they understand?"
    },
    "passport_retention": {
        "condition": lambda s: s.ids_retained,
        "evidence": " facility inspection, personal belongings check",
        "question": "Are identity documents held by employer?"
    },
    "debt_bondage": {
        "condition": lambda s: s.debt_to_employer > s.monthly_wage * 3,
        "evidence": " accounting ledgers, worker debt statements",
        "question": "Do workers owe money to employer that they cannot repay?"
    },
    "threats_violence": {
        "condition": lambda s: s.violence_threats_reported,
        "evidence": " incident reports, interview transcripts",
        "question": "Are threats of violence or actual violence used to control workers?"
    },
    "child_labor": {
        "condition": lambda s: s.underage_workers > 0,
        "evidence": " age verification documents, school attendance records",
        "question": "Are workers under 18 performing hazardous work?"
    },
    "forced_overtime": {
        "condition": lambda s: s.overtime_required,
        "evidence": " work schedules, worker testimony",
        "question": "Is overtime mandatory without consent or extra pay?"
    },
    "unfree_recruitment": {
        "condition": lambda s: s.recruitment_fee_paid > s.monthly_wage * 0.5,
        "evidence": " recruitment agency records, worker receipts",
        "question": "Did workers pay high recruitment fees that bind them to employer?"
    },
    "no_union": {
        "condition": lambda s: not s.unionized and s.union_banned,
        "evidence": " union membership records, policy documents",
        "question": "Are workers prevented from forming or joining unions?"
    }
}

# Risk weights (0-5 per flag)
FLAG_WEIGHTS = {
    "excessive_hours": 2,
    "withhold_wages": 4,
    "no_contracts": 5,
    "passport_retention": 5,
    "debt_bondage": 5,
    "threats_violence": 5,
    "child_labor": 5,
    "forced_overtime": 3,
    "unfree_recruitment": 4,
    "no_union": 2
}

def calculate_risk_score(supplier_claims: Dict) -> int:
    """Calculate total risk score (0-20)."""
    total = 0
    for flag_name, flag_def in RED_FLAGS.items():
        if flag_def["condition"](supplier_claims):
            total += FLAG_WEIGHTS[flag_name]
    return total
