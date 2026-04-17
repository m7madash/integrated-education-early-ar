"""JusticeLens Core: Audit decisions for demographic bias."""

import pandas as pd
import numpy as np
from typing import Dict, List
import json

class BiasAuditor:
    """Detect disparate impact in binary decisions."""
    
    def __init__(self, data: pd.DataFrame, decision_col: str, 
                 protected_cols: List[str], favorable_outcome=1):
        self.data = data.copy()
        self.decision_col = decision_col
        self.protected_cols = protected_cols
        self.favorable = favorable_outcome
    
    def statistical_parity_difference(self) -> Dict:
        results = {}
        overall_rate = self.data[self.decision_col].mean()
        for col in self.protected_cols:
            group_rates = {}
            for group in self.data[col].unique():
                subset = self.data[self.data[col] == group]
                rate = subset[self.decision_col].mean()
                group_rates[str(group)] = {
                    'selection_rate': float(rate),
                    'disparity': float(rate - overall_rate)
                }
            results[col] = group_rates
        return results
    
    def disparate_impact_ratio(self) -> Dict:
        results = {}
        overall_rate = self.data[self.decision_col].mean()
        for col in self.protected_cols:
            group_ratios = {}
            for group in self.data[col].unique():
                subset = self.data[self.data[col] == group]
                rate = subset[self.decision_col].mean()
                if overall_rate > 0:
                    ratio = rate / overall_rate
                    group_ratios[str(group)] = {
                        'ratio': float(ratio),
                        'violates_80_percent_rule': ratio < 0.8
                    }
            results[col] = group_ratios
        return results
    
    def generate_report(self) -> Dict:
        report = {
            'total_decisions': int(len(self.data)),
            'overall_approval_rate': float(self.data[self.decision_col].mean()),
            'protected_attributes': self.protected_cols,
            'statistical_parity': self.statistical_parity_difference(),
            'disparate_impact': self.disparate_impact_ratio(),
            'recommendations': []
        }
        for col, groups in report['disparate_impact'].items():
            for group, metrics in groups.items():
                if metrics.get('violates_80_percent_rule'):
                    report['recommendations'].append(
                        f"Group '{group}' in '{col}' violates 80% rule (ratio={metrics['ratio']:.2f}). "
                        f"Consider: reweighing, adversarial debiasing, or collect more data."
                    )
        return report

def audit_dataset(csv_path: str, decision_col: str, protected_cols: List[str]) -> Dict:
    df = pd.read_csv(csv_path)
    auditor = BiasAuditor(df, decision_col, protected_cols)
    return auditor.generate_report()

if __name__ == "__main__":
    print("JusticeLens v0.1 — Bias Audit Tool")
    print("=== Generating synthetic demo dataset ===")
    np.random.seed(42)
    n = 1000
    data = pd.DataFrame({
        'gender': np.random.choice(['Male', 'Female'], n),
        'ethnicity': np.random.choice(['Local', 'Palestinian', 'Other'], n, p=[0.6, 0.3, 0.1]),
        'experience_years': np.random.randint(0, 20, n),
        'decision': 0
    })
    for idx, row in data.iterrows():
        base_prob = 0.5 + (row['experience_years'] * 0.02)
        if row['ethnicity'] == 'Palestinian':
            base_prob *= 0.7
        data.at[idx, 'decision'] = int(np.random.binomial(1, base_prob))
    
    print(f"Dataset: {data.shape}, Overall approval: {data['decision'].mean():.2%}")
    auditor = BiasAuditor(data, 'decision', ['ethnicity', 'gender'])
    report = auditor.generate_report()
    print("\n=== AUDIT REPORT ===")
    print(json.dumps(report, indent=2))
    print("\n✅ JusticeLens demo complete.")
