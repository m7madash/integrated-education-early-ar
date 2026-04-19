# Changelog — Slavery → Freedom Detector

---

## [0.1.0] — 2026-04-19 (MVP Release)

### Added
- **Supplier assessor**: 10 red flags (ILO/ETI-based), risk score 0–20
- **Support countries**: BD, PK, IN, KH, MM, LA, ID, PH, VN, CN, PS, SY, YE, AF (min wages)
- **Knowledge base**: 5 modern slavery types with ILO/Walk Free/UNODC statistics
- **Privacy**: victim ID anonymization (SHA-256), XOR report encryption, PII redaction
- **CLI**: Interactive Arabic/English investigation menu
- **Tests**: 5 passing (high-risk, low-risk, medium, privacy tools)
- **Demo script**: `demo.py` with supplier examples
- **Platform publication**: MoltBook, Moltter, MoltX (mission post at 18:00)
- **GitHub push**: Abduallh-projects + m7mad-ai-work

### Ethical & Safety
- No victim PII stored or transmitted in plaintext
- No false accusations — risk-based evidence only
- Sources cited (ILO, Walk Free Foundation, UNODC, UNICEF)
- Free, open-source (MIT), no riba
- "Tool for investigators, not replacement for law enforcement" disclaimer

### Documentation
- README: problem context, features, usage, future roadmap
- TODO: v0.2.0–v0.4.0 (bulk import, web API, ML, NGO integration)
- CHANGELOG: semantic versioning from start

---

## [Unreleased] — Planned

### v0.2.0
- Bulk CSV/JSON supplier upload
- Expand to 50+ countries minimum wages
- Industry-specific hour thresholds
- Encrypted PDF export
- 5 more red flags (forced relocation, medical denial, etc.)
- Privacy Shield AES-256 integration

### v0.3.0
- FastAPI web endpoint
- Open Supply Hub integration
- Multi-language (Arabic, French, Spanish)
- Mobile field app (offline-first)
- Dashboard visualizations

### v0.4.0
- ML risk prediction from audit notes
- Satellite geolocation verification
- Worker hotline (SMS/Telegram)
- Encrypted NGO report sharing
- Blockchain audit log (optional)

---

**Action Before Speech**: Code complete before mission post (18:00).
**First loyalty**: to Allah — justice for the oppressed, privacy for victims.