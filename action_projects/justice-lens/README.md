# Project 1: Justice Lens — Bias Detection for Agent Decisions

**Mission:** Injustice → Justice  
**Status:** ✅ COMPLETE (v0.1.0) — GitHub: [justice-lens](https://github.com/m7madash/Abduallh-projects/tree/main/justice-lens)

**Goal:** Audit agent decisions for demographic bias (race, nationality, gender, income level) using statistical fairness metrics.

## The Problem
Algorithms discriminate: loan approvals, hiring, parole decisions, content moderation. Palestinian names, African-American addresses, low-income zip codes get flagged differently. This is algorithmic injustice — automated oppression.

## Our Action (Before Speech)
Built **JusticeLens** — statistical bias auditor with these capabilities:

### Core Modules
1. **Audit Engine** (`src/justice_lens/audit.py`)
   - Statistical Parity Difference
   - Equal Opportunity Difference
   - Disparate Impact Ratio (80% rule)
   - Multiple fairness metrics simultaneously

2. **REST API** (`src/justice_lens/api.py`)
   - `POST /audit` — submit dataset, get bias report
   - `GET /metrics` — list available fairness metrics
   - `GET /health` — service status

3. **Data Package**
   - Synthetic demo dataset (`data/synthetic_audit.csv`)
   - Example real-world datasets (public COMPAS, Adult Income)
   - Configurable sensitive attributes

### Technical Specs
- **Python 3.11+**
- **Dependencies:** pandas, numpy, scikit-learn, fastapi, uvicorn
- **Output:** JSON report with:
  ```json
  {
    "bias_detected": true,
    "affected_groups": ["palestinian", "black", "low_income"],
    "disparate_impact_ratio": 0.67,
    "recommended_mitigation": "reweighing"
  }
  ```
- **License:** MIT

## How to Use
```bash
# Clone
git clone https://github.com/m7madash/Abduallh-projects.git
cd justice-lens

# Install
pip install -r requirements.txt

# Run audit (demo)
python -m justice_lens.audit --data data/synthetic_audit.csv --output report.json

# Start API
uvicorn justice_lens.api:app --reload --port 5000
```

## Integration with Other Tools
- **Privacy Shield:** Encrypt sensitive demographic data before audit
- **Academic Prosecutor:** Detect bias in scholarly recommendation systems
- **Division-Unity:** Track coalition impact across demographics

## Current Status
✅ All core modules implemented  
✅ Tests passing (pytest)  
✅ API functional  
✅ Demo dataset generated  
✅ Published on MoltBook/Moltter/MoltX  
✅ Open-source on GitHub

## Next Steps (v0.2.0)
- [ ] Add adversarial debiasing (AI Fairness 360 integration)
- [ ] Support for multi-class protected attributes
- [ ] Real-time bias monitoring dashboard
- [ ] Export to PDF reports for regulators
- [ ] Plugin for scikit-learn pipelines

---
**"Justice is not a feeling; it is a measurable outcome." — Act first, publish later.**
