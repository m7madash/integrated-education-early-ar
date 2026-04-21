# Changelog — Illness → Health

All notable changes will be documented.

## [0.1.0] — 2026-04-21 (In Development)

### Added
- **Triage module** (`triage.py`):
  - Critical/High/Medium/Low/Self_Care urgency levels
  - Symptom-based classification rules
  - Risk factor escalation (age, chronic conditions, pregnancy)
  - Aid organization matching by location
- **Knowledge Base** (`knowledge.py`):
  - Condition dataclass: symptoms, severity, contagiousness, treatment guidelines
  - Medication dataclass: dosing, contraindications, affordable alternatives
  - Demo dataset: common cold, influenza, COVID-19, diabetic emergency
  - Search-by-symptom functionality
- **Privacy Module** (`privacy.py`):
  - Fernet symmetric encryption (cryptography)
  - Consent recording & expiry
  - Data anonymization (hashing PII)
  - Auto-purge of old encrypted records
- **Orchestrator** (`detector.py`):
  - Combines triage + knowledge + treatment plan + medication safety
  - Full report with urgency, action, possible conditions, disclaimer
- **CLI** (`cli.py`):
  - Subcommands: `triage`, `condition`, `search`, `medication`, `assess`
  - JSON output support
- **REST API** (`api.py`):
  - Endpoints: `/triage`, `/assess`, `/condition/<id>`, `/search`, `/medications`
  - In-memory report storage
- **Project scaffolding**: tests/, scripts/, data/ placeholders

---

## [Planned] v0.2.0

- Arabic-language CLI/API interface
- Offline SQLite knowledge base (replace in-memory)
- Integration with WHO/CDC APIs (real-time guidelines)
- Drug interaction checker
- Geospatial aid matching (OpenStreetMap + clinics DB)
- Vital signs analysis (BP, HR, SpO2)
- Symptom image upload (dermatology, wound photos)
- Multi-language support (Arabic, French, Spanish)
- Telegram/Discord bot wrapper

---

## [Planned] v0.3.0

- Mobile app (Flutter/React Native)
- Telemedicine integration (video consult referral)
- Epidemiology dashboard (heatmaps of symptom clusters)
- ML-based diagnosis assistant (trained on public medical datasets)
- Prescription generation (with pharmacist review workflow)
- Integration with ACP: agents can query health data as service

---

**Ethical**: Designed for the oppressed — never replace doctor, always encourage professional care. No data exploitation.
