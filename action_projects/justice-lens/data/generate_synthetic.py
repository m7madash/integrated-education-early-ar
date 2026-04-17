"""Generate synthetic biased datasets for testing JusticeLens."""
import pandas as pd
import numpy as np

def generate_hiring_data(n: int = 1000, bias_against: str = 'Palestinian') -> pd.DataFrame:
    """Generate synthetic hiring data with known bias."""
    np.random.seed(42)
    data = pd.DataFrame({
        'applicant_id': range(n),
        'gender': np.random.choice(['Male', 'Female'], n),
        'ethnicity': np.random.choice(['Local', bias_against, 'Other'], n, p=[0.6, 0.3, 0.1]),
        'education_years': np.random.randint(8, 20, n),
        'experience_years': np.random.randint(0, 15, n),
    })
    base_probs = 0.3 + (data['education_years'] - 8) * 0.05 + (data['experience_years'] * 0.02)
    base_probs = base_probs.clip(0, 0.95)
    bias_multiplier = 0.6
    data['base_prob'] = base_probs
    data.loc[data['ethnicity'] == bias_against, 'base_prob'] *= bias_multiplier
    data['hired'] = np.random.binomial(1, data['base_prob'])
    return data

if __name__ == "__main__":
    df = generate_hiring_data(1000)
    df.to_csv('data/synthetic_hiring_biased.csv', index=False)
    print("✅ Generated synthetic_hiring_biased.csv")
    local_rate = df[df['ethnicity']=='Local']['hired'].mean()
    pal_rate = df[df['ethnicity']=='Palestinian']['hired'].mean()
    print(f"Bias: Local={local_rate:.2%}, Palestinian={pal_rate:.2%}")
