"""Tests for JusticeLens — validate bias detection accuracy."""
import sys
sys.path.insert(0, 'src')
from justice_lens.audit import BiasAuditor
import pandas as pd

def test_audit_detects_known_bias():
    """Auditor must detect 30% bias against 'Palestinian' group."""
    np.random.seed(42)
    n = 1000
    # Create dataset: Palestinian approval rate 30% lower than Local
    data = pd.DataFrame({
        'ethnicity': ['Local']*600 + ['Palestinian']*300 + ['Other']*100,
        'gender': np.random.choice(['Male', 'Female'], n),
        'decision': 0
    })
    # Local: 50% approval, Palestinian: 35% (30% relative reduction)
    for i in range(600):
        data.at[i, 'decision'] = np.random.binomial(1, 0.50)
    for i in range(600, 900):
        data.at[i, 'decision'] = np.random.binomial(1, 0.35)
    for i in range(900, 1000):
        data.at[i, 'decision'] = np.random.binomial(1, 0.50)

    auditor = BiasAuditor(data, 'decision', ['ethnicity'])
    report = auditor.generate_report()

    # Check disparate impact ratio
    di = report['disparate_impact']['ethnicity']
    palestinian_ratio = di['Palestinian']['ratio']
    local_ratio = di['Local']['ratio']

    print(f"Palestinian approval ratio: {palestinian_ratio:.3f}")
    print(f"Local approval ratio: {local_ratio:.3f}")

    # Palestinian should have lower ratio (<0.8 relative to overall or Local)
    assert palestinian_ratio < 0.8, "Bias detection failed: Palestinian ratio should be <0.8"
    assert di['Palestinian']['violates_80_percent_rule'] == True, "Should flag 80% violation"

    print("✅ Bias detection test PASSED — JusticeLens correctly identifies discrimination")

def test_fairness_metrics_output():
    """Verify report structure."""
    df = pd.DataFrame({
        'group': ['A','A','B','B'] * 50,
        'decision': [1,0,1,0] * 50
    })
    auditor = BiasAuditor(df, 'decision', ['group'])
    report = auditor.generate_report()
    assert 'statistical_parity' in report
    assert 'disparate_impact' in report
    assert 'recommendations' in report
    print("✅ Report structure test PASSED")

if __name__ == "__main__":
    try:
        test_audit_detects_known_bias()
        test_fairness_metrics_output()
        print("\n🎉 All tests passed! JusticeLens is ready for integration.")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
