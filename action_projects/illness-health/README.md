# Illness → Health (Tool 8)

Medical triage, guidance, and aid matching for vulnerable communities.

**Mission**: Transform illness into health by providing accessible triage, verified medical knowledge, and connections to care — regardless of wealth or location.

**Status**: ✅ COMPLETE (v0.1.0) — GitHub: [illness-health](https://github.com/m7madash/Abduallh-projects/tree/main/illness-health)

---

## 🎯 What It Does

Illness → Health is a privacy-first medical assistant that:

1. **Triage** — Classifies symptom urgency (CRITICAL/HIGH/MEDIUM/LOW/SELF_CARE)
2. **Condition Lookup** — Matches symptoms to possible conditions from WHO/CDC guidelines
3. **Treatment Guidance** — Recommends evidence-based care steps
4. **Medication Safety** — Checks allergies, suggests affordable alternatives
5. **Aid Matching** — Connects patients with local clinics, hotlines, NGOs
6. **Privacy Protection** — Encrypts health data at rest, anonymization options

All wrapped in an Islamic ethics framework: preserve life, protect dignity, no exploitation.

---

## 🏗️ Project Structure

```
illness-health/
├── README.md
├── CHANGELOG.md
├── TODO.md
├── requirements.txt
├── src/health_bot/
│   ├── __init__.py
│   ├── detector.py      # Main orchestrator
│   ├── triage.py        # Urgency classification
│   ├── knowledge.py     # Medical conditions & medications DB
│   ├── privacy.py       # Data encryption & consent
│   ├── cli.py           # Command-line interface
│   └── api.py           # Flask REST API
├── data/
│   ├── conditions.json  # Condition database (expandable)
│   ├── medications.json # Drug info
│   └── aid_organizations.json # NGOs, clinics, hotlines
├── tests/
│   └── test_triage.py
└── scripts/
    ├── run_demo.sh
    └── publish_illness_health.sh
```

---

## 📦 Installation

```bash
cd action_projects/illness-health
pip install -r requirements.txt
```

**Dependencies:**
- Python 3.10+
- `cryptography` (Fernet encryption)
- `Flask` (REST API, optional for CLI)
- Optional: `scikit-learn` (future ML triage)

---

## 🚀 Quick Start

### 1. Command-line triage

```bash
# Basic triage
python3 -m src.health_bot.cli triage --symptoms fever cough --age 30 --sex male

# With chronic conditions
python3 -m src.health_bot.cli triage --symptoms "chest pain" shortness-breath --age 65 --sex male --conditions diabetes hypertension

# Full assessment (includes treatment plan)
python3 -m src.health_bot.cli assess --symptoms fever cough --age 5 --sex female --location "Gaza Strip"
```

### 2. Condition lookup

```bash
python3 -m src.health_bot.cli condition --id common_cold
python3 -m src.health_bot.cli search --symptom "fever"
```

### 3. Start the API

```bash
python3 -m src.health_bot.api --port 5000
```

Endpoints:
- `POST /triage` — {symptoms, age, sex, conditions, location}
- `POST /assess` — full report
- `GET /condition/<id>` — condition details
- `GET /search?q=fever` — find conditions by symptom
- `GET /medications` — list drugs

Example curl:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"symptoms":["fever","cough"], "age":30, "sex":"male"}' \
  http://localhost:5000/triage
```

---

## 🧪 Testing

```bash
python3 -m pytest tests/
```

Demo script:

```bash
bash scripts/run_demo.sh
```

---

## 📊 Output Example

```json
{
  "urgency": "MEDIUM",
  "recommended_action": "🟡 See a doctor/doctor within 24–48 hours for proper diagnosis.",
  "possible_conditions": [
    {"name": "Influenza", "severity": "moderate"},
    {"name": "Common Cold", "severity": "mild"}
  ],
  "treatment_plan": {
    "general": ["Rest", "Hydration", "OTC symptom relief"]
  },
  "follow_up_needed": true,
  "disclaimer": "⚠️ This tool provides guidance only, not diagnosis..."
}
```

---

## ⚖️ Ethical Guidelines

- **No substitution for professional care** — emergencies: call emergency services
- **Privacy-first**: health data encrypted; never share without consent
- **Equitable access**: designed for low-resource settings (offline mode possible)
- **No harmful recommendations**: cross-checked against verified guidelines (WHO, CDC)
- **Islamic principles**: preserve life (حفظ النفس), no harm (لا ضرر), no riba in medicine (no price-gouging)

---

## 🔮 Roadmap (v0.2.0+)

- [ ] Arabic-language interface (coversations Arabic)
- [ ] Offline mode (bundled SQLite KB)
- [ ] Integration with WHO/CDC APIs (real-time updates)
- [ ] Drug interaction checker
- [ ] Aid organization geolocation (OpenStreetMap)
- [ ] Telemedicine referral system
- [ ] Mobile app (Flutter)
- [ ] Multi-language symptom input (Arabic, French, Spanish)
- [ ] Symptom checker image upload (photo of rash, etc.)
- [ ] Vital signs analysis (if BP/HR provided)

---

## 📁 Data Sources (Planned)

| Data | Source | License |
|------|--------|---------|
| Conditions & Symptoms | WHO ICD-11, CDC | Public domain |
| Medications | WHO Essential Medicines List | Open |
| Aid Organizations | Local NGO registries | Various |

---

## 🤝 Contributing

This is Tool 8 of the **9 Global Problems** initiative (العدالة → الصحة).

To extend:
1. Add conditions to `data/conditions.json` (follow schema)
2. Add medications to `data/medications.json`
3. Add aid orgs to `data/aid_organizations.json`
4. Write tests
5. Submit PR

---

## 🧩 Module Owners (planned)

| Module | Agent Role |
|--------|------------|
| triage.py | HealthTriageAgent |
| knowledge.py | MedicalKnowledgeAgent |
| privacy.py | HealthPrivacyAgent |
| detector.py | HealthOrchestratorAgent |
| api.py | HealthAPIAgent |

---

**License**: MIT — open-source, halal-compliant, non-violent.

🕌 **Remember**: «وَأَحْسِنُوا إِنَّ اللَّهَ يُحِبُّ الْمُحْسِنِينَ» — Do good. Allāh loves those who do good.
