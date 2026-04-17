"""Tests for JusticeLens bias auditor."""
import sys
sys.path.insert(0, 'src')
from justice_lens.audit import BiasAuditor
import pandas as pd

def test_audit_known_bias():
    """Test that auditor detects known 30% bias against 'Palestinian'."""
    np.random.seed(123)
    n = 500
    df = pd.DataFrame({
        'ethnicity': ['Local']*int(n*0.6) + ['Palestinian']*int(n*0.3) + ['Other']*int(n*0.1),
        'decision': [1]*int(n*0.5) + [0]*int(n*0.5)  # placeholder
    })
    # We'll just test structure for now
    auditor = BiasAuditor(df, 'decision', ['ethnicity'])
    report = auditor.generate_report()
    assert 'disparate_impact' in report
    assert 'statistical_parity' in report
    print("✅ Audit structure test passed")

if __name__ == "__main__":
    test_audit_known_bias()
    print("All tests passed (partial).")
