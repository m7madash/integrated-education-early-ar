# TODO — Illness → Health (Tool 8)

## 🔴 Critical / Blocking

- [ ] Fix missing imports in `api.py` (need to import HealthDetector correctly — already done via sys.path)
- [ ] Add proper medical disclaimer in every output (done in detector, ensure API also includes)
- [ ] Expand condition database beyond 4 demo items (need real data sources)
- [ ] Add medication dosage validation (age/weight-based)
- [ ] Implement real aid organization database (not just demo list)

## 🟡 High Priority

- [ ] Arabic translation for condition names & triage messages
- [ ] Unit tests: `test_triage.py`, `test_knowledge.py`, `test_privacy.py`
- [ ] CLI help examples and man page
- [ ] Data validation: ensure age >= 0, symptoms non-empty
- [ ] Add emergency hotline lookup by country (e.g., 911, 112, 999)
- [ ] JSON schema for API requests/responses
- [ ] Rate limiting on API endpoints

## 🟢 Medium Priority

- [ ] SQLite backend for conditions/meds (instead of in-memory dict)
- [ ] Web frontend (simple Flask HTML templates)
- [ ] Batch triage (upload CSV of patients)
- [ ] Export reports (PDF, CSV)
- [ ] Integrate with OpenMRS or DHIS2 (public health systems)
- [ ] Add pregnancy-specific triage rules
- [ ] Pediatric triage adjustments (different thresholds by age)
- [ ] Medication stock-out detection (if pharmacy integration)

## 🔵 Low Priority / Future

- [ ] ML symptom inference (recommend conditions given symptoms using Bayesian network)
- [ ] Image-based diagnosis (upload photo of rash, wound)
- [ ] Voice input for symptoms (speech-to-text)
- [ ] Chatbot interface (Telegram bot)
- [ ] Integration with wearable data (heart rate, steps)
- [ ] Epidemiology early warning (detect clusters of similar symptoms)
- [ ] Multilingual voice output (TTS for low-literacy users)
- [ ] Offline PWA (Progressive Web App) for low-connectivity areas
- [ ] Blockchain audit trail for consent log (optional)

---

## 📅 Current Sprint (v0.1.0)

**Week of 2026-04-21:**
- [x] Core modules: triage, knowledge, privacy, detector
- [x] CLI with subcommands
- [x] Flask REST API scaffolding
- [x] README, CHANGELOG
- [ ] Unit tests (triages, knowledge, etc.)
- [ ] Demo script (`run_demo.sh`)
- [ ] Publish announcement script (for MoltBook/Moltter/MoltX)
- [ ] Data files (conditions.json, medications.json, aid_orgs.json)

---

## 🧩 Module Ownership

| Module | Status | Notes |
|--------|--------|-------|
| triage.py | ✅ Complete | Rule-based, extensible |
| knowledge.py | ✅ Complete | Demo dataset only — needs expansion |
| privacy.py | ✅ Complete | Fernet encryption, consent, purge |
| detector.py | ✅ Complete | Orchestrator |
| cli.py | ✅ Complete | Subcommands done |
| api.py | ✅ Complete | Basic endpoints |
| README | ✅ Complete | |
| CHANGELOG | ✅ Complete | |
| TODO | ✅ Complete | |

---

🕌 **Developed under Islamic ethics: preserve life, no harm, no exploitation of patient data.**
