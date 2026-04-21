# Academic Prosecutor — Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-04-21 (Initial Release)

### Added
- **Investigator module**: core detection engine
  - `detector.py`: plagiarism, duplicate submission, authorship fraud, data fabrication checks
  - `sources.py`: fetch papers from Crossref, PubMed, arXiv, local PDFs
  - `similarity.py`: advanced text similarity (Jaccard, TF-IDF, phrase matching)
- **Sanctions module**: enforcement and registry
  - `registry.py`: persistent offense database (JSON), offender profiling, risk escalation
  - `enforcer.py`: rule-based penalty application (retract, report, block funding, etc.)
- **Notifier module**: alerts and templates
  - `templates.py`: pre-approved messages (retraction, institution alert, author warning)
  - `alert.py`: email (SMTP) and webhook delivery
- **CLI scripts**
  - `prosecute.py`: single-paper investigation end-to-end
  - `batch_scan.py`: directory-wide scanning of paper metadata
- **Data files**
  - `data/lexicon.json`: known plagiarized phrases, suspicious patterns
  - `data/sanctions_rules.json`: penalty matrix by violation type/severity
- **Tests**
  - `tests/test_detector.py`: basic Investigator tests (jaccard, plagiarism detection)
  - `tests/test_sanctions.py`: registry, escalation, enforcer, rule selection
- **Documentation**
  - `README.md`: full project overview, installation, usage
  - `requirements.txt`: Python dependencies

### Technical Notes
- Requires Python 3.8+
- Optional: scikit-learn for TF-IDF similarity (falls back to Jaccard if unavailable)
- Storage: JSON file (data/registry.json) — can be upgraded to SQLite later

---

## [Planned] — Future Releases

### [0.2.0] — Enhanced Forensics
- Image forensics for figure duplication detection
- Citation anomaly analysis (unusual self-citation patterns)
- Integration with Crossref/PubMed APIs for real-time verification

### [0.3.0] — Distributed Registry
- Multi-agent consensus on offenses
- Blockchain-based immutable logging (optional)
- Reputation scoring across institutions

### [1.0.0] — Production Ready
- Web dashboard for investigations
- REST API for external integrations
- Plugin system for custom violation detectors

---

**Note**: This project is developed under Islamic ethical constraints:
- No fabrication of evidence
- No false accusations — verification required before any sanction
- Right to appeal (14-day window)
- Transparency: all actions logged and auditable
